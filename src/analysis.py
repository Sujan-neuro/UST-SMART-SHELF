import torch
import torch.nn as nn
from processor import ImagePreprocessor
from utils import DestandardizeAge
from torchvision import transforms, models
from config import (GENDER_DETECTOR, 
                    AGE_DETECTOR_WEIGHTS,
                    # GENDER_DETECTOR_WEIGHTS
)
from transformers import (
    AutoImageProcessor,
    AutoModelForImageClassification,
)

# Load the model architecture
class ResNet50Regressor:
    def __init__(self, weight_path, device=None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._build_model()
        self._load_weights(weight_path)

    def _build_model(self):
        model = models.resnet50(pretrained = False)  # Corrected pretrained argument
        model.fc = nn.Linear(model.fc.in_features, 1)  # Directly replace fc
        return model.to(self.device)

    def _load_weights(self, weight_path):
        state_dict = torch.load(weight_path, map_location=self.device)
        
        # Rename keys if needed
        new_state_dict = {}
        for key, value in state_dict.items():
            new_key = key.replace("fc.0", "fc")  # Adjust for sequential mismatch
            new_state_dict[new_key] = value

        self.model.load_state_dict(new_state_dict)
        self.model.eval()

    def predict(self, image_tensor):
        image_tensor = image_tensor.to(self.device)  # Ensure tensor is on the correct device
        with torch.no_grad():
            output = self.model(image_tensor)
        return output.cpu().numpy()


class ResNet50Classifier:
    def __init__(self, weight_path, device=None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._build_model()
        self._load_weights(weight_path)

    def _build_model(self):
        model = models.resnet50(pretrained=False)
        model.fc = nn.Sequential(
            nn.Linear(model.fc.in_features, 1),
            nn.Sigmoid()  # Ensure Sigmoid is applied in the model
        )
        return model.to(self.device)

    def _load_weights(self, weight_path):
        state_dict = torch.load(weight_path, map_location=self.device)

        # Rename keys to match Sequential format
        new_state_dict = {}
        for key, value in state_dict.items():
            new_key = key.replace("fc", "fc.0")  # Change fc → fc.0
            new_state_dict[new_key] = value

        self.model.load_state_dict(new_state_dict, strict=False)
        self.model.eval()

    def predict(self, image_tensor):
        image_tensor = image_tensor.to(self.device)
        with torch.no_grad():
            output = self.model(image_tensor)  # Sigmoid is already inside the model
        return output.cpu().numpy()


class Analyzer:
    def __init__(self, identify_age = False, identify_gender = False):
        self.identify_age = identify_age
        self.identify_gender = identify_gender
        if identify_age:
            self.preprocessor = ImagePreprocessor()
            self.age_model = ResNet50Regressor(AGE_DETECTOR_WEIGHTS)

        if identify_gender:
            self.gender_preprocessor = AutoImageProcessor.from_pretrained(GENDER_DETECTOR, use_fast = True)
            self.gender_model = AutoModelForImageClassification.from_pretrained(GENDER_DETECTOR)
            # self.preprocessor = ImagePreprocessor()
            # self.gender_model = ResNet50Classifier(GENDER_DETECTOR_WEIGHTS)

        resnet = models.resnet50(weights = models.ResNet50_Weights.IMAGENET1K_V1)
        self.embedding_model = torch.nn.Sequential(*list(resnet.children())[:-1])  # Remove FC layer
        self.embedding_model.eval()
        self.destandardizer = DestandardizeAge()

    def get_age_gender(self, image):
        """
        Predict age and gender for a given image.
        """
        age = 0 # Default
        gender = 'Neutral' # Default

        if self.identify_age:
            inputs = self.preprocessor.preprocess(image)

            age_output = self.age_model.predict(inputs)
            age = round(self.destandardizer.destandardize_age(age_output[0][0]))

        # Gender prediction
        if self.identify_gender:
            inputs = self.gender_preprocessor(image, return_tensors = "pt")
            gender_output = self.gender_model(**inputs)
            gender = ["Female", "Male"][gender_output.logits.argmax(1).item()]

            # gender_output = self.gender_model.predict(inputs)
            # gender = ["Male", "Female"][1 if gender_output[0][0] > 0.5 else 0]
        return age, gender

    def get_embedding(self, image):
        """
        Generate embeddings for a given image.
        """
        transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean = [0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225]),
            ]
        )
        preprocessed_image = transform(image).unsqueeze(0)
        with torch.no_grad():
            embedding = self.embedding_model(preprocessed_image).squeeze().numpy()
        return embedding