from transformers import (
    ViTImageProcessor,
    ViTForImageClassification,
    AutoImageProcessor,
    AutoModelForImageClassification,
)
from torchvision import transforms
import torch
from torchvision.models import resnet50, ResNet50_Weights

from config import AGE_DETECTOR, GENDER_DETECTOR, ID2LABEL


class Analyzer:
    def __init__(self):
        # Load models
        self.age_preprocessor = ViTImageProcessor.from_pretrained(AGE_DETECTOR, use_fast = True)
        self.age_model = ViTForImageClassification.from_pretrained(AGE_DETECTOR)

        self.gender_preprocessor = AutoImageProcessor.from_pretrained(GENDER_DETECTOR, use_fast = True)
        self.gender_model = AutoModelForImageClassification.from_pretrained(GENDER_DETECTOR)

        resnet = resnet50(weights = ResNet50_Weights.IMAGENET1K_V1)
        self.embedding_model = torch.nn.Sequential(*list(resnet.children())[:-1])  # Remove FC layer
        self.embedding_model.eval()

    def get_age_gender(self, image):
        """
        Predict age and gender for a given image.
        """
        # Age prediction
        inputs = self.age_preprocessor(image, return_tensors = "pt")
        age_output = self.age_model(**inputs)
        age = ID2LABEL[age_output.logits.argmax(1).item()]

        # Gender prediction
        inputs = self.gender_preprocessor(image, return_tensors = "pt")
        gender_output = self.gender_model(**inputs)
        gender = ["Female", "Male"][gender_output.logits.argmax(1).item()]

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
