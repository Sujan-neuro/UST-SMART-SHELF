import json

class FootfallCounter:
    def __init__(self, file_path):
        self.file_path = file_path

    def count_unique_visitors(self):
        unique_visitors = set()
        
        with open(self.file_path, 'r') as file:
            for line in file:
                data = json.loads(line.strip())
                unique_visitors.add(data["visitorId"])
        
        return len(unique_visitors)