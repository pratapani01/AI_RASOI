from PIL import Image
import torch
import timm
import torchvision.transforms as transforms
import requests

# Load model and labels globally
model = timm.create_model('resnet50', pretrained=True)
model.eval()

# Load ImageNet labels
LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
imagenet_labels = requests.get(LABELS_URL).text.split("\n")

# Image transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def detect_dish_from_image(uploaded_image):
    try:
        img = Image.open(uploaded_image).convert("RGB")
        img_tensor = transform(img).unsqueeze(0)

        with torch.no_grad():
            outputs = model(img_tensor)
            _, predicted = outputs.max(1)

        dish_name = imagenet_labels[predicted.item()]
        return dish_name

    except Exception as e:
        return f"Error in classification: {str(e)}"
