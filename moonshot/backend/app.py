# C:\Users\Sitora Bakhronova\moonshot\backend\app.py

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import Optional
import torch
import torch.nn as nn  # <-- This line is crucial for 'nn'
from torchvision import transforms, models
from PIL import Image
import io
import os

app = FastAPI()

# --- Global Variables for Model and Transforms ---
model = None  # This will hold our loaded AI model
# Define the same validation transforms as used in train_model.py
inference_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])  # ImageNet normalization
])

# IMPORTANT: These class names MUST be in the exact same order as they were learned during training.
# Based on your data structure ('Baikiaea_Plurijuga' and 'what not to pick' alphabetically sorted):
CLASS_NAMES = ["Baikiaea_Plurijuga", "what not to pick"]


# --- Load Model on Server Startup ---
@app.on_event("startup")
async def load_model():
    global model
    model_path = "trained_model.pth"  # Path to your saved model weights (relative to app.py)

    if not os.path.exists(model_path):
        print(f"Error: Model file '{model_path}' not found. Please train the model first using train_model.py.")
        print("Server will start, but AI detection will not function until the model is present.")
        model = None  # Ensure model is None if not found
        return

    try:
        # Load the same model architecture as trained (ResNet18)
        loaded_model = models.resnet18(weights=None)  # Load without pre-trained weights initially
        num_ftrs = loaded_model.fc.in_features
        loaded_model.fc = nn.Linear(num_ftrs, len(CLASS_NAMES))  # Ensure output layer matches your classes

        # Load the trained state_dict (the weights)
        # map_location='cpu' ensures it loads even if you trained on GPU but are running on CPU
        loaded_model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        loaded_model.eval()  # Set model to evaluation mode for inference

        model = loaded_model
        print(f"AI model loaded successfully from {model_path}")
    except Exception as e:
        print(f"Failed to load AI model: {e}")
        model = None


# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    """
    A simple endpoint to check if the server is running and model is loaded.
    """
    model_status = "loaded" if model else "not loaded (check server logs for errors)"
    return {"status": "OK", "message": "Backend server is up and running!", "model_status": model_status}


# --- Main POST Endpoint for Plant Detection ---
@app.post("/api/detect-plant")
async def detect_plant(
        image: UploadFile = File(...),
        latitude: Optional[float] = Form(None),
        longitude: Optional[float] = Form(None)
):
    """
    Receives an image file and optional GPS coordinates from the frontend,
    performs AI inference, and returns detection results.
    """
    if model is None:
        return JSONResponse(status_code=500, content={"error": "AI model not loaded or failed to load.",
                                                      "message": "Please train the model or check server startup logs."})

    try:
        # 1. Read and preprocess the image
        contents = await image.read()
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
        processed_image = inference_transform(pil_image)

        # Add batch dimension (model expects batches, even for a single image)
        image_tensor = processed_image.unsqueeze(0)

        # 2. Perform Inference
        # Move image_tensor to the same device as the model (e.g., CPU)
        device = next(model.parameters()).device  # Get model's device
        image_tensor = image_tensor.to(device)

        with torch.no_grad():  # Disable gradient calculation for faster inference
            output = model(image_tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)  # Get class probabilities

            # Get the top prediction (highest probability)
            confidence, predicted_idx = torch.max(probabilities, 0)

            predicted_class_name = CLASS_NAMES[predicted_idx.item()]
            predicted_confidence = confidence.item()

        # 3. Construct response
        response_data = {
            "status": "success",
            "detection_result": {
                "plant_id": predicted_class_name,
                "confidence": predicted_confidence,
                "latitude": latitude,
                "longitude": longitude,
                "image_filename": image.filename
            },
            "message": f"Detected {predicted_class_name} with {predicted_confidence:.2f} confidence."
        }
        return JSONResponse(content=response_data)

    except Exception as e:
        print(f"Error during plant detection: {e}")
        return JSONResponse(status_code=500, content={"error": "Failed to process image.", "details": str(e)})


# --- CORS Middleware ---
# Essential for frontend (Mamta's app) running on a different origin/port
from fastapi.middleware.cors import CORSMiddleware
origins = [
    "http://localhost",        # Common for frontend served directly from file system or basic http server
    "http://localhost:8080",   # Common for development servers (e.g., webpack-dev-server)
    "http://localhost:3000",   # Common for React/Vue dev servers
    "http://127.0.0.1:8000",   # If Mamta serves from same origin, or you access docsсв
    "http://127.0.0.1:8080",
    "https://*.ngrok-free.app", # Allow connections from ngrok URLs if needed for testing
    "http://localhost:8501"    # <--- ADD THIS LINE FOR MAMTA'S FRONTEND
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)