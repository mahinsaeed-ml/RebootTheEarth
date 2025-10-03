import os
import requests

# Small sample images of whiteflies (sticky traps)
sample_urls = [
    "https://i.ibb.co/sQ7Q6sB/whitefly1.jpg",
    "https://i.ibb.co/LtnprHC/whitefly2.jpg",
    "https://i.ibb.co/WkXDycf/whitefly3.jpg",
    "https://i.ibb.co/K7DCM3D/whitefly4.jpg",
    "https://i.ibb.co/q7pRcpn/whitefly5.jpg",
]

base_dir = "datasets/pests"
img_dir = os.path.join(base_dir, "images", "val")
lbl_dir = os.path.join(base_dir, "labels", "val")
os.makedirs(img_dir, exist_ok=True)
os.makedirs(lbl_dir, exist_ok=True)

# Download images
for i, url in enumerate(sample_urls, start=1):
    img_path = os.path.join(img_dir, f"whitefly{i}.jpg")
    r = requests.get(url)
    with open(img_path, "wb") as f:
        f.write(r.content)

    # Minimal YOLO labels (fake bounding boxes for demo)
    label_path = os.path.join(lbl_dir, f"whitefly{i}.txt")
    with open(label_path, "w") as f:
        # YOLO format: class_id x_center y_center width height (normalized 0-1)
        f.write("0 0.5 0.5 0.3 0.3\n")  # one whitefly box in the center

# Write data.yaml
yaml_path = os.path.join(base_dir, "data.yaml")
with open(yaml_path, "w") as f:
    f.write("train: datasets/pests/images/val\n")
    f.write("val: datasets/pests/images/val\n")
    f.write("\n")
    f.write("nc: 1\n")
    f.write("names: ['whitefly']\n")

print("Sample dataset created at datasets/pests/")
