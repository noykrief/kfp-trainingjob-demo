# OpenShift AI - Dog Breed Classification Training

Simple training pipeline for OpenShift AI using Kubeflow Pipelines.

## 🎯 What This Does

Trains a PyTorch CNN model to classify 5 dog breeds:
- Labrador
- Golden Retriever
- German Shepherd
- Bulldog
- Poodle

## 📋 Prerequisites

- OpenShift AI 3 with Data Science Pipelines installed
- PVC created: `kfp-pvc-1` (already done ✅)
- Python 3.8+ for local compilation

## 🚀 Quick Start

### Step 1: Compile Pipeline

```bash
cd openshift-ai
pip install kfp
python dog_training_pipeline.py
```

This creates: `dog_training_pipeline.yaml`

### Step 2: Upload to OpenShift AI

**Option A: Using UI**

1. Find and access OpenShift AI Dashboard:
   ```bash
   # Get dashboard URL
   oc get route -n redhat-ods-applications | grep dashboard
   ```
   Or access via OpenShift Console → Networking → Routes

2. Navigate to your Data Science Project: `dog-classification-demo`

3. Go to **Pipelines** tab

4. Click **Import pipeline**

5. Upload `dog_training_pipeline.yaml`

6. Name it: `Dog Breed Classifier Training`

**Option B: Using CLI** (if DSPA configured)

```bash
# Get KFP endpoint
export KFP_ENDPOINT=$(oc get route ds-pipeline-dspa -n dog-classification-demo -o jsonpath='{.spec.host}')

# Upload pipeline (requires kfp SDK)
python << EOF
from kfp import Client

client = Client(host=f"https://{os.environ['KFP_ENDPOINT']}")
client.upload_pipeline(
    pipeline_package_path='dog_training_pipeline.yaml',
    pipeline_name='Dog Breed Classifier Training'
)
EOF
```

### Step 3: Create a Run

**In OpenShift AI UI:**

1. Go to **Pipelines** → **Runs**

2. Click **Create run**

3. Select pipeline: `Dog Breed Classifier Training`

4. Set parameters:
   - `pvc_name`: `kfp-pvc-1`
   - `epochs`: `10`
   - `batch_size`: `32`
   - `learning_rate`: `0.001`
   - `use_pretrained`: `true`

5. Click **Create**

### Step 4: Monitor Training

- Watch logs in real-time in OpenShift AI UI
- See training progress: loss, accuracy per epoch
- Check run status and duration

## 📊 What Happens During Training

1. **Dataset Preparation**
   - Checks if images exist in PVC
   - Creates synthetic images if needed (for demo)
   - Organizes in train/val folders

2. **Model Training**
   - Loads ResNet18 architecture
   - Trains for specified epochs
   - Validates after each epoch
   - Saves best model based on validation accuracy

3. **Results Saved to PVC**
   ```
   /models/
   ├── best_model.pth       # Best performing model
   ├── final_model.pth      # Model after last epoch
   ├── metrics.json         # Training metrics
   └── class_names.txt      # List of dog breeds
   ```

## 🔧 Customization

### Change Training Parameters

Edit pipeline parameters when creating a run:

```yaml
epochs: 20              # More training
batch_size: 64          # Larger batches (needs more memory)
learning_rate: 0.0001   # Slower learning
use_pretrained: false   # Train from scratch
```

### Use Your Own Dog Images

1. Prepare images in this structure:
   ```
   data/
   ├── train/
   │   ├── labrador/*.jpg
   │   ├── golden_retriever/*.jpg
   │   ├── german_shepherd/*.jpg
   │   ├── bulldog/*.jpg
   │   └── poodle/*.jpg
   └── val/
       └── (same structure)
   ```

2. Upload to PVC:
   ```bash
   # Create upload pod
   oc run uploader --image=busybox --command sleep 3600 \
     --overrides='{"spec":{"volumes":[{"name":"data","persistentVolumeClaim":{"claimName":"kfp-pvc-1"}}],"containers":[{"name":"uploader","image":"busybox","command":["sleep","3600"],"volumeMounts":[{"name":"data","mountPath":"/data","subPath":"data"}]}]}}'
   
   # Copy data
   oc cp ./data uploader:/data/
   
   # Cleanup
   oc delete pod uploader
   ```

3. Run pipeline - it will use your images!

## 📈 View Results

### Check Metrics

```bash
# Create inspector pod
oc run inspector --rm -it --image=busybox \
  --overrides='{"spec":{"volumes":[{"name":"storage","persistentVolumeClaim":{"claimName":"kfp-pvc-1"}}],"containers":[{"name":"inspector","image":"busybox","stdin":true,"tty":true,"command":["sh"],"volumeMounts":[{"name":"storage","mountPath":"/mnt"}]}]}}'

# Inside pod:
cat /mnt/models/metrics.json
ls -lh /mnt/models/
exit
```

### Sample Metrics Output

```json
{
  "metrics": [
    {
      "epoch": 1,
      "train_loss": 1.2345,
      "train_acc": 65.32,
      "val_loss": 1.1234,
      "val_acc": 68.50
    },
    ...
  ],
  "best_val_acc": 85.75,
  "num_classes": 5,
  "class_names": ["bulldog", "german_shepherd", "golden_retriever", "labrador", "poodle"]
}
```

## 🐛 Troubleshooting

### Pipeline fails to start

```bash
# Check Data Science Pipeline Application (DSPA)
oc get dspa -n dog-classification-demo

# Check pipeline pods
oc get pods -n dog-classification-demo | grep pipeline
```

### PVC not accessible

```bash
# Check PVC status
oc get pvc kfp-pvc-1

# Describe for events
oc describe pvc kfp-pvc-1
```

### Out of memory

Reduce batch size in pipeline parameters:
- `batch_size`: `16` (instead of 32)

Or increase memory request in code:
```python
kubernetes.set_memory_request(train_task, '8Gi')
kubernetes.set_memory_limit(train_task, '16Gi')
```

## 📚 Next Steps

1. ✅ Run basic training
2. 📸 Add real dog images
3. 🎯 Improve model accuracy
4. 🔄 Add data preprocessing step
5. 📊 Add evaluation metrics
6. 🚀 Deploy for inference

## 🔗 Resources

- [OpenShift AI Docs](https://access.redhat.com/documentation/en-us/red_hat_openshift_ai)
- [KFP Documentation](https://www.kubeflow.org/docs/components/pipelines/)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
