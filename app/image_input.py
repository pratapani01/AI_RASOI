from ultralytics import YOLO
import cv2
import tempfile
import os

def detect_ingredients_from_image(uploaded_image):
    """
    Takes an uploaded image and returns a list of detected ingredient names.
    """
    try:
        # Save uploaded image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(uploaded_image.read())
            image_path = tmp.name

        # Load YOLOv8 model (assume pretrained on food/ingredients)
        model = YOLO("yolov8n.pt")  # Replace with custom food model if needed

        # Perform detection
        results = model(image_path)
        labels = results[0].names
        detected_classes = results[0].boxes.cls.tolist()
        detected_labels = list(set([labels[int(cls)] for cls in detected_classes]))

        # Cleanup temp file
        os.remove(image_path)

        return detected_labels

    except Exception as e:
        return [f"Error in detection: {str(e)}"]
