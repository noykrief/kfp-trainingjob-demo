# Quick Start - 3 Minutes to Training

Get your dog breed classifier training in 3 minutes on OpenShift AI.

## ✅ What You Already Have

- ✅ OpenShift cluster access
- ✅ Logged in as admin
- ✅ Project: `dog-classification-demo`
- ✅ PVC: `kfp-pvc-1`
- ✅ Compiled pipeline: `dog_training_pipeline.yaml`

## 🚀 3 Steps to Start Training

### Step 1: Access OpenShift AI Dashboard (30 seconds)

```bash
# Find the dashboard URL
export PATH="$HOME/bin:$PATH"
oc get route -n redhat-ods-applications | grep dashboard
```

Or go directly to:
```
https://rhods-dashboard-redhat-ods-applications.apps.ocp.v6jqb.sandbox5295.opentlc.com
```

Login with:
- Username: `admin`
- Password: `<your-password>`

### Step 2: Import Pipeline (1 minute)

1. In OpenShift AI Dashboard, go to **Data Science Projects**
2. Click on project: `dog-classification-demo`
3. Go to **Pipelines** tab
4. Click **Import pipeline**
5. Upload file: `dog_training_pipeline.yaml`
6. Name: `Dog Breed Classifier`
7. Click **Import**

### Step 3: Create Run (1 minute)

1. Click **Create run**
2. Select pipeline: `Dog Breed Classifier`
3. Use default parameters:
   ```
   pvc_name: kfp-pvc-1
   epochs: 10
   batch_size: 32
   learning_rate: 0.001
   use_pretrained: true
   ```
4. Click **Create**

## 🎯 Expected Output

Training will:
1. ✅ Create synthetic dog images (500 train + 100 validation)
2. ✅ Train ResNet18 model for 10 epochs
3. ✅ Save best model to PVC
4. ✅ Generate metrics.json

**Duration:** ~5-10 minutes (depending on resources)

## 📊 Monitor Progress

In the OpenShift AI UI:
- **Graph view**: See pipeline steps
- **Logs**: View training output in real-time
- **Metrics**: See loss and accuracy per epoch

Example training log output:
```
🐕 DOG BREED CLASSIFICATION TRAINING
======================================
Epoch 1/10
--------------------------------------------------
  Train Loss: 1.2345 | Train Acc: 65.32%
  Val Loss:   1.1234 | Val Acc:   68.50%
  ✓ Saved best model (Val Acc: 68.50%)

Epoch 2/10
--------------------------------------------------
  Train Loss: 0.9876 | Train Acc: 72.15%
  Val Loss:   0.8765 | Val Acc:   75.25%
  ✓ Saved best model (Val Acc: 75.25%)
...
```

## ✅ Verify Results

### Option 1: Via OpenShift AI UI
- Pipeline run status: ✅ Succeeded
- Duration: ~5-10 minutes
- Artifacts: Model files saved

### Option 2: Via CLI

```bash
export PATH="$HOME/bin:$PATH"

# Check pods
oc get pods -n dog-classification-demo

# Create inspector pod to check PVC
oc run inspector --rm -it --image=busybox \
  --overrides='{"spec":{"volumes":[{"name":"storage","persistentVolumeClaim":{"claimName":"kfp-pvc-1"}}],"containers":[{"name":"inspector","image":"busybox","stdin":true,"tty":true,"command":["sh"],"volumeMounts":[{"name":"storage","mountPath":"/mnt"}]}]}}'

# Inside inspector pod:
ls -lh /mnt/models/
cat /mnt/models/metrics.json
exit
```

Expected files in PVC:
```
/mnt/models/
├── best_model.pth       (~45 MB)
├── final_model.pth      (~45 MB)
├── metrics.json         (training history)
└── class_names.txt      (dog breeds list)
```

## 🎓 What's Next?

1. ✅ **Run completed successfully?** Try with more epochs!
2. 📸 **Add real dog images** - Replace synthetic data
3. 🔧 **Tune hyperparameters** - Adjust learning rate, batch size
4. 📊 **Add evaluation step** - Create multi-step pipeline
5. 🚀 **Deploy for inference** - Serve the trained model

## 🐛 Troubleshooting

### Can't find Data Science Pipelines?

Check if DSPA (Data Science Pipelines Application) is installed:
```bash
oc get dspa -n dog-classification-demo
```

If not found, you need to create a DSPA instance in OpenShift AI UI.

### Pipeline fails immediately?

Check PVC:
```bash
oc get pvc kfp-pvc-1
oc describe pvc kfp-pvc-1
```

### Want to see pod logs directly?

```bash
# Find the training pod
oc get pods -n dog-classification-demo | grep train

# View logs
oc logs -f <pod-name>
```

## 📞 Need Help?

Check the main [README.md](README.md) for detailed documentation.
