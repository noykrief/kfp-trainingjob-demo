"""
OpenShift AI - Dog Breed Classification Training Pipeline
Simple KFP pipeline for training a dog breed classifier
"""
from kfp import dsl
from kfp import kubernetes


@dsl.component(
    base_image="pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime",
    packages_to_install=["torchvision>=0.15.0", "Pillow>=9.0.0"]
)
def train_dog_classifier(
    data_dir: str = "/data",
    model_dir: str = "/models",
    epochs: int = 10,
    batch_size: int = 32,
    learning_rate: float = 0.001,
    use_pretrained: bool = True
):
    """
    Train dog breed classifier using PyTorch

    Args:
        data_dir: Directory containing training data
        model_dir: Directory to save trained models
        epochs: Number of training epochs
        batch_size: Batch size for training
        learning_rate: Learning rate for optimizer
        use_pretrained: Use pretrained ResNet18 weights
    """
    import os
    import json
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader
    from torchvision import datasets, transforms, models
    from datetime import datetime
    from PIL import Image
    import random

    # Create sample dataset function
    def create_sample_dataset(data_dir, num_samples_per_breed=100):
        """Generate synthetic dog images for demo purposes"""
        breeds = ['labrador', 'golden_retriever', 'german_shepherd', 'bulldog', 'poodle']

        train_dir = os.path.join(data_dir, 'train')
        val_dir = os.path.join(data_dir, 'val')

        print(f"📦 Creating dataset in: {data_dir}")

        for split_dir in [train_dir, val_dir]:
            for breed in breeds:
                breed_dir = os.path.join(split_dir, breed)
                os.makedirs(breed_dir, exist_ok=True)

                num_samples = num_samples_per_breed if split_dir == train_dir else num_samples_per_breed // 5

                for i in range(num_samples):
                    img_path = os.path.join(breed_dir, f'{breed}_{i:04d}.jpg')

                    if not os.path.exists(img_path):
                        # Create synthetic image (in production, use real images)
                        img = Image.new('RGB', (224, 224),
                                      color=(random.randint(50, 255),
                                            random.randint(50, 255),
                                            random.randint(50, 255)))
                        img.save(img_path, quality=85)

        print(f"✅ Dataset created: {len(breeds)} breeds")
        print(f"   Training: {num_samples_per_breed * len(breeds)} images")
        print(f"   Validation: {(num_samples_per_breed // 5) * len(breeds)} images")

        return breeds

    # Model definition
    class DogBreedClassifier(nn.Module):
        """ResNet18-based dog breed classifier"""
        def __init__(self, num_classes=5, pretrained=False):
            super(DogBreedClassifier, self).__init__()
            self.backbone = models.resnet18(pretrained=pretrained)
            num_features = self.backbone.fc.in_features
            self.backbone.fc = nn.Linear(num_features, num_classes)

        def forward(self, x):
            return self.backbone(x)

    # Main training logic
    print("=" * 70)
    print("🐕 DOG BREED CLASSIFICATION TRAINING")
    print("=" * 70)
    print(f"Started: {datetime.now()}")
    print(f"Data: {data_dir}")
    print(f"Models: {model_dir}")
    print(f"Epochs: {epochs} | Batch: {batch_size} | LR: {learning_rate}")
    print("=" * 70)

    # Create directories
    os.makedirs(model_dir, exist_ok=True)

    # Check/create dataset
    train_path = os.path.join(data_dir, 'train')
    if not os.path.exists(train_path) or len(os.listdir(train_path)) == 0:
        print("\n📦 Creating sample dataset...")
        breeds = create_sample_dataset(data_dir)
    else:
        print("\n📦 Using existing dataset")
        breeds = sorted([d for d in os.listdir(train_path)
                        if os.path.isdir(os.path.join(train_path, d))])

    num_classes = len(breeds)
    print(f"\n🎯 Training for {num_classes} breeds: {', '.join(breeds)}")

    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n💻 Device: {device}")
    if device.type == 'cuda':
        print(f"   GPU: {torch.cuda.get_device_name(0)}")

    # Data transforms
    train_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    val_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # Load datasets
    print("\n📊 Loading datasets...")
    train_dataset = datasets.ImageFolder(os.path.join(data_dir, 'train'),
                                        transform=train_transforms)
    val_dataset = datasets.ImageFolder(os.path.join(data_dir, 'val'),
                                      transform=val_transforms)

    train_loader = DataLoader(train_dataset, batch_size=batch_size,
                             shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=batch_size,
                           shuffle=False, num_workers=2)

    print(f"   Train batches: {len(train_loader)}")
    print(f"   Val batches: {len(val_loader)}")

    # Initialize model
    print("\n🏗️  Building model...")
    model = DogBreedClassifier(num_classes=num_classes, pretrained=use_pretrained)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Training loop
    print("\n🚀 Training started...\n")
    metrics = []
    best_val_acc = 0.0

    for epoch in range(epochs):
        print(f"Epoch {epoch+1}/{epochs}")
        print("-" * 50)

        # Training phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()

        train_loss = train_loss / train_total
        train_acc = 100.0 * train_correct / train_total

        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)

                outputs = model(inputs)
                loss = criterion(outputs, labels)

                val_loss += loss.item() * inputs.size(0)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()

        val_loss = val_loss / val_total
        val_acc = 100.0 * val_correct / val_total

        # Print metrics
        print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"  Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%")

        # Save metrics
        metrics.append({
            'epoch': epoch + 1,
            'train_loss': train_loss,
            'train_acc': train_acc,
            'val_loss': val_loss,
            'val_acc': val_acc
        })

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_path = os.path.join(model_dir, 'best_model.pth')
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'class_names': train_dataset.classes
            }, best_model_path)
            print(f"  ✓ Saved best model (Val Acc: {val_acc:.2f}%)")

        print()

    # Save final model
    final_model_path = os.path.join(model_dir, 'final_model.pth')
    torch.save({
        'epoch': epochs,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'class_names': train_dataset.classes
    }, final_model_path)

    # Save metrics
    metrics_path = os.path.join(model_dir, 'metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump({
            'metrics': metrics,
            'best_val_acc': best_val_acc,
            'num_classes': num_classes,
            'class_names': train_dataset.classes,
            'hyperparameters': {
                'epochs': epochs,
                'batch_size': batch_size,
                'learning_rate': learning_rate,
                'use_pretrained': use_pretrained
            }
        }, f, indent=2)

    # Save class names
    class_names_path = os.path.join(model_dir, 'class_names.txt')
    with open(class_names_path, 'w') as f:
        f.write('\n'.join(train_dataset.classes))

    print("=" * 70)
    print("✅ TRAINING COMPLETE!")
    print(f"   Best Validation Accuracy: {best_val_acc:.2f}%")
    print(f"   Models saved to: {model_dir}")
    print(f"   Completed: {datetime.now()}")
    print("=" * 70)


@dsl.pipeline(
    name="Dog Breed Classifier Training",
    description="Train a CNN model to classify dog breeds on OpenShift AI"
)
def dog_training_pipeline(
    pvc_name: str = "kfp-pvc-1",
    epochs: int = 10,
    batch_size: int = 32,
    learning_rate: float = 0.001,
    use_pretrained: bool = True
):
    """
    Dog breed classification training pipeline for OpenShift AI

    Args:
        pvc_name: Name of PVC for data and model storage
        epochs: Number of training epochs
        batch_size: Training batch size
        learning_rate: Optimizer learning rate
        use_pretrained: Use ImageNet pretrained weights
    """

    # Create training task
    train_task = train_dog_classifier(
        data_dir="/data",
        model_dir="/models",
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        use_pretrained=use_pretrained
    )

    # Mount PVC to task
    kubernetes.mount_pvc(
        train_task,
        pvc_name=pvc_name,
        mount_path="/data",
        sub_path="data"
    )

    kubernetes.mount_pvc(
        train_task,
        pvc_name=pvc_name,
        mount_path="/models",
        sub_path="models"
    )

    # Set resource requests and limits
    train_task.set_cpu_limit('4')
    train_task.set_memory_limit('8Gi')

    # Optional: Request GPU (uncomment if GPU available)
    # train_task.set_accelerator_type('nvidia.com/gpu')
    # train_task.set_accelerator_limit('1')


if __name__ == "__main__":
    """Compile the pipeline to YAML"""
    from kfp import compiler

    output_file = "dog_training_pipeline.yaml"

    compiler.Compiler().compile(
        pipeline_func=dog_training_pipeline,
        package_path=output_file
    )

    print("=" * 70)
    print("✅ Pipeline compiled successfully!")
    print("=" * 70)
    print(f"Output: {output_file}")
    print()
    print("📋 Next steps:")
    print("1. Upload to OpenShift AI Dashboard")
    print("   - Go to Data Science Pipelines")
    print("   - Click 'Import pipeline'")
    print(f"   - Upload {output_file}")
    print()
    print("2. Create a pipeline run:")
    print("   - pvc_name: kfp-pvc-1")
    print("   - epochs: 10")
    print("   - batch_size: 32")
    print("   - learning_rate: 0.001")
    print("   - use_pretrained: true")
    print()
    print("3. Monitor in OpenShift AI UI")
    print("=" * 70)
