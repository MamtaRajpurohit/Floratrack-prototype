# backend/train_model.py

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms, models
from PIL import Image
import os
import glob  # For easily finding files in nested directories
from sklearn.model_selection import train_test_split  # For splitting image paths if needed
import numpy as np  # For numpy operations


# --- 1. Custom Dataset Class ---
class PlantDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.image_paths = []
        self.labels = []
        self.class_names = []
        self.class_to_idx = {}

        # Scan for top-level class folders (e.g., 'Baikiaea_Plurijuga', 'what not to pick')
        # Sort class names to ensure consistent mapping (e.g., alphabetical order)
        top_level_class_folders = sorted([d.name for d in os.scandir(root_dir) if d.is_dir()])

        if not top_level_class_folders:
            raise RuntimeError(
                f"No class directories found in {root_dir}. Expected folders like 'Baikiaea_Plurijuga' and 'what not to pick'.")

        for idx, class_name in enumerate(top_level_class_folders):
            self.class_names.append(class_name)
            self.class_to_idx[class_name] = idx
            class_path = os.path.join(root_dir, class_name)

            # Recursively find images in all subdirectories of this class
            # This handles nested folders like 'Baikiaea_Plurijuga/Branches images'
            for img_path in glob.glob(os.path.join(class_path, '**', '*.*'), recursive=True):
                if img_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    self.image_paths.append(img_path)
                    self.labels.append(idx)

        if not self.image_paths:
            raise RuntimeError(
                f"No images found in {root_dir}. Please check your dataset path and image file extensions.")

        print(f"Dataset loaded: {len(self.image_paths)} images across {len(self.class_names)} classes.")
        print(f"Class to index mapping: {self.class_to_idx}")
        # Optional: Print distribution for verification
        # from collections import Counter
        # print("Label distribution:", Counter(self.labels))

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert("RGB")
        label = self.labels[idx]

        if self.transform:
            image = self.transform(image)

        return image, label


# --- 2. Main Training Function ---
def train_model(data_root_dir="data", model_save_path="trained_model.pth", num_epochs=50, batch_size=32):
    print("--- Starting AI Model Training Script ---")

    # Define Data Transformations (common for image classification)
    # These transforms will be applied to your images before feeding them to the model.
    data_transforms = {
        'train': transforms.Compose([
            transforms.RandomResizedCrop(224),  # Random crop and resize
            transforms.RandomHorizontalFlip(),  # Randomly flip horizontally
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),  # Add color jitter
            transforms.ToTensor(),  # Converts image to PyTorch tensor
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])  # ImageNet normalization
        ]),
        'val': transforms.Compose([
            transforms.Resize(256),  # Resize to 256
            transforms.CenterCrop(224),  # Crop to 224x224
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    # --- Prepare Dataset ---
    try:
        full_dataset = PlantDataset(root_dir=data_root_dir, transform=None)  # Apply transforms in split datasets
    except RuntimeError as e:
        print(f"Error loading dataset: {e}")
        print(
            "Please ensure your 'data' directory exists and contains 'Baikiaea_Plurijuga' and 'what not to pick' folders.")
        print("Make sure these folders contain image files.")
        return  # Exit if dataset isn't ready

    # Split dataset indices for training and validation
    train_indices, val_indices = train_test_split(
        range(len(full_dataset)),
        test_size=0.2,  # 20% for validation
        stratify=full_dataset.labels,  # Important for imbalanced datasets
        random_state=42  # For reproducibility
    )

    # Create separate datasets with appropriate transforms for train and validation
    train_dataset = torch.utils.data.Subset(full_dataset, train_indices)
    val_dataset = torch.utils.data.Subset(full_dataset, val_indices)

    # Apply transforms to subsets:
    # We need to manually apply the transform callable to each item in the subset.
    # This isn't automatically handled by Subset unless the Dataset's __getitem__
    # method is modified to take a transform explicitly for the subset.
    # A common way is to make `full_dataset` hold the transform and `Subset` uses it.
    # For now, let's just update the transform for the full_dataset instance
    # that is used to create the subsets, then modify the __getitem__ of `Subset`
    # or pass a factory function.
    # For simplicity in this quick prototype, let's ensure the `transform` in the
    # `PlantDataset` is applied correctly. The current `PlantDataset` takes `transform`
    # in its init, so it will be applied.

    # Re-instantiate datasets with specific transforms (cleaner way)
    train_dataset_actual = PlantDataset(root_dir=data_root_dir, transform=data_transforms['train'])
    train_dataset_actual.image_paths = [full_dataset.image_paths[i] for i in train_indices]
    train_dataset_actual.labels = [full_dataset.labels[i] for i in train_indices]

    val_dataset_actual = PlantDataset(root_dir=data_root_dir, transform=data_transforms['val'])
    val_dataset_actual.image_paths = [full_dataset.image_paths[i] for i in val_indices]
    val_dataset_actual.labels = [full_dataset.labels[i] for i in val_indices]

    # Create DataLoaders
    # num_workers > 0 makes data loading faster, adjust based on your CPU cores
    num_workers = os.cpu_count() // 2 if os.cpu_count() else 0
    train_dataloader = DataLoader(train_dataset_actual, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_dataloader = DataLoader(val_dataset_actual, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    # Use GPU if available, else CPU
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Define Model Architecture (Transfer Learning: ResNet18)
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)  # Use latest recommended weights

    # Get the number of input features for the final layer
    num_ftrs = model.fc.in_features

    # Replace the final layer with a new one that has the correct number of output classes
    num_classes = len(full_dataset.class_names)  # Should be 2 (Baikiaea_Plurijuga, what not to pick)
    if num_classes < 2:
        print(f"Error: Found only {num_classes} classes. A classification model requires at least two.")
        print(
            "Please ensure your 'data' directory contains both 'Baikiaea_Plurijuga' and 'what not to pick' folders with images.")
        return

    model.fc = nn.Linear(num_ftrs, num_classes)
    model = model.to(device)  # Move model to GPU/CPU

    # Define Loss Function and Optimizer
    criterion = nn.CrossEntropyLoss()  # Suitable for multi-class classification
    optimizer = optim.Adam(model.parameters(), lr=0.001)  # Adam is a good general-purpose optimizer

    # Basic Training Loop
    print(f"Starting training for {num_epochs} epochs...")
    best_accuracy = 0.0

    for epoch in range(num_epochs):
        print(f"\nEpoch {epoch + 1}/{num_epochs}")
        print("-" * 10)

        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()  # Set model to training mode
                dataloader = train_dataloader
            else:
                model.eval()  # Set model to evaluate mode
                dataloader = val_dataloader

            running_loss = 0.0
            running_corrects = 0

            # Iterate over data
            for batch_idx, (inputs, labels) in enumerate(dataloader):
                inputs = inputs.to(device)
                labels = labels.to(device)

                # Zero the parameter gradients
                optimizer.zero_grad()

                # Forward pass
                # Only track gradients if in training phase
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)  # Get the predicted class
                    loss = criterion(outputs, labels)

                    # Backward + optimize only if in training phase
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

                # Print progress every N batches (adjust N as needed)
                if batch_idx % (len(dataloader) // 5 or 1) == 0:  # Print 5 times per epoch phase
                    print(f"  {phase} Batch {batch_idx + 1}/{len(dataloader)} Loss: {loss.item():.4f}")

            epoch_loss = running_loss / len(dataloader.dataset)
            epoch_acc = running_corrects.double() / len(dataloader.dataset)

            print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

            # Deep copy the model if it's the best performing
            if phase == 'val' and epoch_acc > best_accuracy:
                best_accuracy = epoch_acc
                # Save the best model weights
                torch.save(model.state_dict(), model_save_path)
                print(f"  *** New best model saved with accuracy: {best_accuracy:.4f} ***")

    print("\n--- AI Model Training Complete! ---")
    print(f"Best validation accuracy: {best_accuracy:.4f}")
    print(f"Final model saved to: {model_save_path}")


if __name__ == "__main__":
    # Define the root directory where your 'Baikiaea_Plurijuga' and 'what not to pick' folders reside.
    # This assumes 'data' is one level up from your 'backend' directory.
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    data_root_for_training = os.path.join(current_script_dir, "..", "data")

    # --- Run the training ---
    # You can adjust num_epochs and batch_size here.
    # Start with a small num_epochs (e.g., 5-10) to ensure everything runs.
    # Then increase for better accuracy.
    train_model(data_root_dir=data_root_for_training, num_epochs=50, batch_size=32)