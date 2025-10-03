from ultralytics import YOLO
import random
import os


class PestDetector:
    def __init__(self, model_path=None):
        # Default to your trained model if available
        if model_path is None:
            model_path = os.path.join("models", "whitefly.pt")  # update if stored elsewhere
        self.model = YOLO(model_path)

    def detect(self, image_file):
        # Run detection
        results = self.model.predict(image_file, save=True, imgsz=640)

        # Initialize counts
        counts = {"whitefly": 0, "thrips": 0, "tuta_miner_traces": 0}

        # Go through detected classes
        for d in results[0].boxes.cls.tolist():
            label = self.model.names[int(d)]
            if label.lower() in ["whitefly", "white_fly"]:  # handle naming in your dataset
                counts["whitefly"] += 1

        # Simulate detections for other pests
        counts["thrips"] = random.randint(0, 2)
        counts["tuta_miner_traces"] = random.randint(0, 1)

        return counts
