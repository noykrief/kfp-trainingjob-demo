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
│   ├── QUICKSTART.md               # 3-minute quick start guide
│   ├── README.md                   # Detailed documentation
│   └── requirements.txt            # Python dependencies
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
cd setup
./login.sh
```

### 2. Create PVC

```bash
oc apply -f create_pvc.yaml
```

### 3. Upload Pipeline to OpenShift AI

1. Go to OpenShift AI Dashboard
2. Navigate to project: `dog-classification-demo`
3. **Pipelines** → **Import pipeline**
4. Upload: `openshift-ai/dog_training_pipeline.yaml`

### 4. Create Run

- Set parameters:
  - `pvc_name`: `kfp-pvc-1`
  - `epochs`: `10`
  - `batch_size`: `32`
  - `learning_rate`: `0.001`
  - `use_pretrained`: `true`

- Click **Create**

Training runs for ~5-10 minutes and saves results to PVC.

## 📚 Documentation

- **[openshift-ai/QUICKSTART.md](openshift-ai/QUICKSTART.md)** - Fast 3-minute start
- **[openshift-ai/README.md](openshift-ai/README.md)** - Detailed guide with troubleshooting
- **[setup/deploy-to-openshift.md](setup/deploy-to-openshift.md)** - Deployment details

## 🔧 Configuration

**Cluster Details** (in `.env`):
- API: `https://api.ocp.v6jqb.sandbox5295.opentlc.com:6443`
- Project: `dog-classification-demo`
- PVC: `kfp-pvc-1`

## 🎓 What You'll Learn

1. ✅ Creating KFP pipelines for OpenShift AI
2. ✅ Using PVCs for model and data storage
3. ✅ Training PyTorch models in containers
4. ✅ Managing ML workflows with Data Science Pipelines

## 📊 Results

After training completes, the PVC contains:

```
/models/
├── best_model.pth      # Best performing model
├── final_model.pth     # Final model after all epochs
├── metrics.json        # Training history (loss, accuracy)
└── class_names.txt     # Dog breed labels
```

## 🔗 Resources

- [OpenShift AI Documentation](https://access.redhat.com/documentation/en-us/red_hat_openshift_ai)
- [Kubeflow Pipelines Documentation](https://www.kubeflow.org/docs/components/pipelines/)
- [PyTorch Documentation](https://pytorch.org/docs/)

---

**Built for:** OpenShift AI 3 • Kubeflow Pipelines • PyTorch
