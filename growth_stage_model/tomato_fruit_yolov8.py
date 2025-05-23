# -*- coding: utf-8 -*-
"""tomato_fruit_YOLOV8

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/#fileId=https%3A//storage.googleapis.com/kaggle-colab-exported-notebooks/ahmednasser83/tomato-fruit-yolov8.81f59f8f-b614-47bd-b6d4-f1a00e8d6dfe.ipynb%3FX-Goog-Algorithm%3DGOOG4-RSA-SHA256%26X-Goog-Credential%3Dgcp-kaggle-com%2540kaggle-161607.iam.gserviceaccount.com/20250513/auto/storage/goog4_request%26X-Goog-Date%3D20250513T172602Z%26X-Goog-Expires%3D259200%26X-Goog-SignedHeaders%3Dhost%26X-Goog-Signature%3D23614b7fc59b73243b8588905a760373f33f6c3c983c7be0fe2b821edec43d62fb96e06d3a4b43407204c233f90e5a34045a657ee4678f68104cfd2ad987a06b5494f8fa1fa1a9bc1775e46db6ef1d07bc6ddd92832996f30bcae07b62f4afe969bc31c51732f1b53c2419fc41b967d51e17dadb9da3ee4d32657988dafe918e403b78e0b086e61cf7b61fcccdd1c041484a623ee727d86bcf1eec913d39faa0272394e765b0abf69923534676cd44802953f18bccc14cf2efbc41477d21905c37dfe2c264e00af46d0e0683967fc2f5a4598a171a88a2bdec9a59e73628dac7ea9437c18da8ad0ee8a914f0c24ed48051bbdc9a72dac6f3e3f8d8fa3955a1aa
"""

!pip install ultralytics

from ultralytics import YOLO
from IPython.display import display, Image
from IPython import display
import os
import cv2
import matplotlib.pyplot as plt

model = YOLO('yolov8n.pt')

!cp -r "/kaggle/input/laboro-tomato/train" "/kaggle/working/train"

!cp -r "/kaggle/input/laboro-tomato/val" "/kaggle/working/val"

data = """
names:
  - b_fully_ripened
  - b_half_ripened
  - b_green
  - l_fully_ripened
  - l_half_ripened
  - l_green
nc: 6
path: /kaggle/working/
train: train/images
val: val/images
"""

# Specify the file path where you want to save the text
file_path = "/kaggle/working/dataset.yaml"

# Open the file in write mode and write the text
with open(file_path, "w") as file:
    file.write(data)

print("ready")

results = model.train(
    data='/kaggle/working/dataset.yaml',
    epochs=100,
    imgsz=640,
    model="yolov8n.pt",
    batch=16)

validate = model.val(
    data='/kaggle/working/dataset.yaml',
    imgsz=640,
    batch=16
)

test_images_path='/kaggle/input/laboro-tomato/val/images'

predictions = model.predict(
    source=test_images_path,
    conf=0.5,
    imgsz=640
)

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Define class_names for tomato leaf diseases
class_names = {
    0: "b_fully_ripened",
    1: "b_half_ripened",
    2: "b_green",
    3: "l_fully_ripened",
    4: "l_half_ripened",
    5: "l_green",
}

# Dictionary to store defect counts, confidence sums, and other metrics per class
defect_data = {}
detection_results = []  # To store individual detection results for CSV export

# Total number of detections
total_detections = 0
# Sum of all confidence scores
total_confidence = 0.0

# False Positives and False Negatives for each class (if ground truth is available)
false_positives = {cid: 0 for cid in range(len(class_names))}
false_negatives = {cid: 0 for cid in range(len(class_names))}

# Iterate through predictions
for i, result in enumerate(predictions):
    print(f"\nImage {i + 1} Predictions:")
    if result.boxes is not None and len(result.boxes) > 0:
        for box in result.boxes:
            # Extract details
            class_id = int(box.cls.item())
            confidence = box.conf.item()
            coordinates = box.xyxy.tolist()
            # Use get() with default to handle unexpected class IDs
            defect_name = class_names.get(class_id, f"Unknown Class {class_id}")

            # Update defect data
            if class_id not in defect_data:
                defect_data[class_id] = {
                    "count": 0,
                    "confidence_sum": 0.0,
                    "confidence_list": [],
                    "tp": 0,  # True Positives
                    "fp": 0,  # False Positives
                    "fn": 0,  # False Negatives
                }
            defect_data[class_id]["count"] += 1
            defect_data[class_id]["confidence_sum"] += confidence
            defect_data[class_id]["confidence_list"].append(confidence)

            # Update totals
            total_detections += 1
            total_confidence += confidence

            # Print box details
            print(f" - Class: {defect_name}, Confidence: {confidence:.2f}, Coordinates: {coordinates}")

            # Append to results for CSV export
            detection_results.append({
                "Image ID": i + 1,
                "Class": defect_name,
                "Confidence": confidence,
                "Bounding Box": coordinates
            })
    else:
        print(f" - No detections.")

# Summarize results
print("\n--- Total Disease Counts, Averages, and Percentages Across All Images ---")
summary_data = []  # To hold summary for each disease class
for class_id, data in defect_data.items():
    disease_name = class_names.get(class_id, f"Unknown Class {class_id}")
    disease_count = data["count"]
    average_confidence = data["confidence_sum"] / disease_count if disease_count > 0 else 0
    percentage_share = (disease_count / total_detections) * 100 if total_detections > 0 else 0
    min_confidence = np.min(data["confidence_list"]) if data["confidence_list"] else 0
    max_confidence = np.max(data["confidence_list"]) if data["confidence_list"] else 0

    # False Positives and False Negatives (example logic)
    false_positive_count = data["fp"]
    false_negative_count = data["fn"]

    # Print disease summary
    print(f"Disease: {disease_name}")
    print(f"  Count: {disease_count}")
    print(f"  Average Confidence: {average_confidence:.2f}")
    print(f"  Confidence Range: [{min_confidence:.2f} - {max_confidence:.2f}]")
    print(f"  Percentage Share: {percentage_share:.2f}%")
    print(f"  False Positives: {false_positive_count}")
    print(f"  False Negatives: {false_negative_count}\n")

    # Append to summary data
    summary_data.append({
        "Class": disease_name,
        "Disease Count": disease_count,
        "Average Confidence": average_confidence,
        "Confidence Range": f"[{min_confidence:.2f} - {max_confidence:.2f}]",
        "Percentage Share (%)": percentage_share,
        "False Positives": false_positive_count,
        "False Negatives": false_negative_count
    })

# Overall statistics
if total_detections > 0:
    overall_average_confidence = total_confidence / total_detections
    print(f"\nOverall Total Detections: {total_detections}")
    print(f"Overall Average Confidence: {overall_average_confidence:.2f}")
else:
    print("\nNo detections made. Cannot calculate averages.")

# Save detailed detection results to CSV
detection_df = pd.DataFrame(detection_results)
detection_df.to_csv("tomato_disease_detection_results.csv", index=False)
print("\nDetailed detection results saved to 'tomato_disease_detection_results.csv'.")

# Save disease summary to CSV
summary_df = pd.DataFrame(summary_data)
summary_df.to_csv("tomato_disease_summary.csv", index=False)
print("Disease summary saved to 'tomato_disease_summary.csv'.")

# Visualize disease counts
plt.figure(figsize=(10, 6))
summary_df.set_index("Class")["Disease Count"].plot(kind="bar", color="skyblue")
plt.title("Tomato Leaf Disease Count by Class")
plt.xlabel("Disease Class")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()

# Visualize percentages
plt.figure(figsize=(10, 6))
summary_df.set_index("Class")["Percentage Share (%)"].plot(kind="bar", color="orange")
plt.title("Percentage Share by Disease Class")
plt.xlabel("Disease Class")
plt.ylabel("Percentage Share (%)")
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()

import matplotlib.pyplot as plt
import cv2  # Only needed for color conversion

for i, result in enumerate(predictions):
    num_objects = len(result.boxes)

    # Convert BGR to RGB
    img = result.plot()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(12, 12))
    plt.imshow(img_rgb)
    plt.axis('off')
    plt.title(f"Image {i + 1} - {num_objects} Objects Detected", fontsize=16, fontweight='bold')
    plt.show()

from ultralytics import YOLO
import os

# Your class names (for reference)
class_names = {
    0: "b_fully_ripened",
    1: "b_half_ripened",
    2: "b_green",
    3: "l_fully_ripened",
    4: "l_half_ripened",
    5: "l_green",
}

def save_yolov8_model(model, path="tomato_fruit_yolov8n.pt"):
    try:
        # Save the model in PyTorch format
        model.save(path)
        print(f"YOLOv8n model saved to {path}")

        # Verify file size
        file_size = os.path.getsize(path) / (1024 * 1024)  # Size in MB
        print(f"Model file size: {file_size:.2f} MB")

        # Export to other formats (optional)
        # ONNX format for broader compatibility
        model.export(format="onnx", imgsz=[640, 640])
        onnx_path = path.replace(".pt", ".onnx")
        if os.path.exists(onnx_path):
            onnx_size = os.path.getsize(onnx_path) / (1024 * 1024)
            print(f"ONNX model saved to {onnx_path} ({onnx_size:.2f} MB)")

    except Exception as e:
        print(f"Error saving YOLOv8n model: {e}")

# Load your trained model
# Replace this with your actual model loading code
try:
    # If you have a trained model
    model = YOLO("/kaggle/working/yolov8n.pt")
except:
    # If starting fresh or loading pre-trained
    model = YOLO("yolov8n.pt")  # Load pre-trained YOLOv8n
    print("Loaded pre-trained YOLOv8n model - replace with your trained model")

# Save the model
save_yolov8_model(model)