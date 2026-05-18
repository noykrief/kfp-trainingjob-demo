# OpenShift AI - Dog Breed Classification Demo

Simple training pipeline demo for OpenShift AI using Kubeflow Pipelines (KFP).

## 🎯 What This Demo Does

Demonstrates how to train a PyTorch CNN model on OpenShift AI to classify 5 dog breeds:
- Labrador
- Golden Retriever  
- German Shepherd
- Bulldog
- Poodle

## 📁 Project Structure

```
.
├── openshift-ai/                    # Main pipeline code
│   ├── dog_training_pipeline.py    # KFP pipeline definition
│   ├── dog_training_pipeline.yaml  # Compiled pipeline (ready to upload)
│   ├── upload_pipeline.py          # Script to upload pipeline via API
│   ├── create_run.py               # Script to create pipeline run via API
│   ├── QUICKSTART.md               # 3-minute quick start guide
│   ├── README.md                   # Detailed documentation
│   └── requirements.txt            # Python dependencies
├── openshift-objects/               # Kubernetes/OpenShift YAML files
│   ├── dspa.yaml                   # Data Science Pipelines Application
│   └── pvc.yaml                    # PersistentVolumeClaim
├── setup/
│   ├── create_pvc.yaml             # PVC configuration
│   ├── login.sh                    # OpenShift login helper
│   └── deploy-to-openshift.md      # Deployment guide
├── .env                            # Configuration (not in git)
└── .env.example                    # Configuration template
```

## 🚀 Quick Start

### 1. Login to OpenShift

```bash
oc login <your-cluster-api> -u <username>
```

### 2. Create Project and PVC

```bash
oc new-project <your-project-name>

# Update namespace in YAML files
sed -i 's/<your-namespace>/<your-project-name>/g' openshift-objects/*.yaml

# Create PVC
oc apply -f openshift-objects/pvc.yaml
```

### 3. Install Data Science Pipelines

```bash
oc apply -f openshift-objects/dspa.yaml
```

Wait for all pods to be ready:
```bash
oc get pods -w
```

### 4. Upload Pipeline

**Option A: Via CLI**
```bash
cd openshift-ai
export KFP_ENDPOINT=$(oc get route ds-pipeline-pipelines -o jsonpath='{.spec.host}')
export KFP_ENDPOINT="https://$KFP_ENDPOINT"
python3 upload_pipeline.py
```

**Option B: Via OpenShift AI Dashboard**
1. Navigate to your project in the dashboard
2. Go to **Pipelines** → **Import pipeline**
3. Upload: `openshift-ai/dog_training_pipeline.yaml`

### 5. Create Run

**Via CLI:**
```bash
python3 create_run.py
```

**Via Dashboard:**
- Set parameters:
  - `pvc_name`: `kfp-pvc-1`
  - `epochs`: `10`
  - `batch_size`: `32`
  - `learning_rate`: `0.001`
  - `use_pretrained`: `true`
- Click **Create**

Training runs for ~5-10 minutes and saves results to PVC.

## 🔧 Configuration

Copy `.env.example` to `.env` and update with your cluster details:

```bash
cp .env.example .env
# Edit .env with your cluster API, credentials, and project name
```

## 🎓 What You'll Learn

1. ✅ Creating KFP pipelines for OpenShift AI
2. ✅ Using PVCs for model and data storage
3. ✅ Training PyTorch models in containers
4. ✅ Managing ML workflows with Data Science Pipelines
5. ✅ Deploying Data Science Pipelines Application (DSPA)

## 📊 Results

After training completes, the PVC contains:

```
/pvc/models/
├── best_model.pth      # Best performing model
├── final_model.pth     # Final model after all epochs
├── metrics.json        # Training history (loss, accuracy)
└── class_names.txt     # Dog breed labels

/pvc/data/
├── train/              # Training images (500 synthetic images)
└── val/                # Validation images (100 synthetic images)
```

## 🐛 Troubleshooting

**Issue: Pipelines tab not showing in dashboard**
- Ensure DSPA name is short (e.g., `pipelines` not `default-datasciencepipelines`)
- Verify `aipipelines` is enabled in DataScienceCluster

**Issue: Training pod fails with shared memory error**
- The pipeline uses `num_workers=0` to avoid shared memory issues

**Issue: Permission denied when downloading pretrained weights**
- The pipeline sets cache directories to `/tmp` for write access

## 📚 Documentation

- **[openshift-ai/QUICKSTART.md](openshift-ai/QUICKSTART.md)** - Fast 3-minute start
- **[openshift-ai/README.md](openshift-ai/README.md)** - Detailed guide
- **[setup/deploy-to-openshift.md](setup/deploy-to-openshift.md)** - Deployment details

## 🔗 Resources

- [OpenShift AI Documentation](https://access.redhat.com/documentation/en-us/red_hat_openshift_ai)
- [Kubeflow Pipelines Documentation](https://www.kubeflow.org/docs/components/pipelines/)
- [PyTorch Documentation](https://pytorch.org/docs/)

---

**Built for:** OpenShift AI 3.2+ • Kubeflow Pipelines 2.5.0 • PyTorch 2.0
