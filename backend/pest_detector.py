from ultralytics import YOLO
import random
import os


class PestDetector:
    def __init__(self, model_path=None):  # <-- fixed here
        if model_path is None:
            model_path = os.path.join("models", "whitefly.pt")
        self.model = YOLO(model_path)

    def detect(self, image_file):
        # Run YOLO prediction
        results = self.model.predict(
            source=image_file,
            save=True,          # saves annotated image
            save_txt=False,     # disable YOLO txt outputs if not needed
            imgsz=640,
            conf=0.25           # adjust confidence threshold if needed
        )

        counts = {
            "whitefly": 0,
            "thrips": 0,
            "tuta_miner_traces": 0
        }

        # Loop through detections
        for d in results[0].boxes.cls.tolist():
            label = self.model.names[int(d)].lower().strip()
            if label == "whitefly":
                counts["whitefly"] += 1

        # Simulate other pests
        counts["thrips"] = random.randint(0, 2)
        counts["tuta_miner_traces"] = random.randint(0, 1)

        # Get path of YOLO's saved annotated image
        saved_path = results[0].save_dir
        print(f"Annotated image saved at: {saved_path}")

        return counts
