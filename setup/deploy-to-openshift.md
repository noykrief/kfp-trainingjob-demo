# Deploy to OpenShift AI

Instructions for deploying this demo to your OpenShift AI cluster.

## Cluster Information

- **API Server**: `https://api.ocp.v6jqb.sandbox5295.opentlc.com:6443`
- **Cluster**: `ocp.v6jqb.sandbox5295.opentlc.com`

## Prerequisites

1. **OpenShift CLI (oc)** installed
2. **Access credentials** for the cluster
3. **OpenShift AI** installed on the cluster
4. **Data Science Project** created

## Step 1: Login to OpenShift

```bash
# Login with username/password
oc login https://api.ocp.v6jqb.sandbox5295.opentlc.com:6443

# Or with token (recommended)
oc login --token=<your-token> --server=https://api.ocp.v6jqb.sandbox5295.opentlc.com:6443
```

**To get your token:**
1. Go to OpenShift Console
2. Click your username (top right)
3. Click "Copy login command"
4. Click "Display Token"
5. Copy the `oc login` command

## Step 2: Create or Select Data Science Project

```bash
# List existing projects
oc get projects | grep redhat-ods

# Create new project (if needed)
oc new-project my-ds-project

# Switch to project
oc project my-ds-project
```

## Step 3: Create PVC

```bash
# Apply PVC configuration
oc apply -f setup/create_pvc.yaml

# Verify PVC
oc get pvc training-data-pvc
```

## Step 4: Deploy KFP Pipeline

### Option A: Using OpenShift AI UI

1. **Open OpenShift AI Dashboard**
   - Find URL: `oc get route -n redhat-ods-applications | grep dashboard`
   - Or via OpenShift Console: Networking → Routes → search "dashboard"

2. **Navigate to Data Science Pipelines**
   - Click on your Data Science Project
   - Go to "Pipelines" tab
   - Click "Import pipeline"

3. **Upload Pipeline**
   - Compile first: `cd kfp && python training_pipeline.py`
   - Upload the generated `training_pipeline.yaml`

4. **Create Pipeline Run**
   - Click "Create run"
   - Set parameters:
     - `pvc_name`: training-data-pvc
     - `epochs`: 10
     - `batch_size`: 32
     - `learning_rate`: 0.001
   - Click "Create"

### Option B: Using KFP SDK

```python
from kfp import Client

# Get the KFP endpoint
# Run: oc get route -n <namespace> | grep ds-pipeline
KFP_ENDPOINT = "https://ds-pipeline-<your-project>.apps.ocp.v6jqb.sandbox5295.opentlc.com"

# Get token
# Run: oc whoami -t
TOKEN = "your-token-here"

# Create client
client = Client(
    host=KFP_ENDPOINT,
    existing_token=TOKEN,
)

# Upload pipeline
client.upload_pipeline_version(
    pipeline_package_path='kfp/training_pipeline.yaml',
    pipeline_version_name='v1',
)

# Create run
run = client.create_run_from_pipeline_package(
    pipeline_file='kfp/training_pipeline.yaml',
    arguments={
        'pvc_name': 'training-data-pvc',
        'epochs': 10,
    }
)

print(f"Run created: {run.run_id}")
```

## Step 5: Monitor Pipeline

### Using UI
1. Go to OpenShift AI Dashboard
2. Navigate to your project → Pipelines
3. Click on the run to see details
4. View logs, metrics, and artifacts

### Using CLI
```bash
# Get pipeline runs (requires tkn CLI)
tkn pipelinerun list

# Get logs
tkn pipelinerun logs <run-name> -f
```

## Step 6: Verify Results

```bash
# Create a pod to check PVC contents
oc run -it --rm debug --image=busybox --restart=Never -- sh

# Inside the pod, mount and check PVC:
# (you'll need to create a pod with PVC mounted)

# Better: Create a verification pod
cat <<EOF | oc apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: pvc-inspector
spec:
  containers:
  - name: inspector
    image: busybox
    command: ['sh', '-c', 'sleep 3600']
    volumeMounts:
    - name: data
      mountPath: /data
    - name: models
      mountPath: /models
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: training-data-pvc
  - name: models
    persistentVolumeClaim:
      claimName: training-data-pvc
EOF

# Exec into pod and check
oc exec -it pvc-inspector -- ls -la /models
oc exec -it pvc-inspector -- cat /models/metrics.json

# Cleanup
oc delete pod pvc-inspector
```

## Troubleshooting

### Issue: Cannot access OpenShift AI Dashboard

**Check route:**
```bash
oc get route -n redhat-ods-applications
```

### Issue: PVC not binding

**Check storage classes:**
```bash
oc get storageclass
```

**Update PVC with correct storage class:**
Edit `setup/create_pvc.yaml` and add:
```yaml
spec:
  storageClassName: <available-storage-class>
```

### Issue: Pipeline fails with permissions

**Check service account:**
```bash
oc get sa -n <your-project>
```

**Grant permissions:**
```bash
oc adm policy add-scc-to-user anyuid -z pipeline -n <your-project>
```

### Issue: Cannot find KFP endpoint

**Find Data Science Pipeline route:**
```bash
# List all routes in your project
oc get routes

# Or search specifically for pipeline
oc get route | grep pipeline
```

## Quick Reference Commands

```bash
# Login
oc login https://api.ocp.v6jqb.sandbox5295.opentlc.com:6443

# Get token
oc whoami -t

# Switch project
oc project my-ds-project

# Create PVC
oc apply -f setup/create_pvc.yaml

# View PVCs
oc get pvc

# View pipeline runs (if using Tekton)
tkn pipelinerun list

# View logs
oc logs -f <pod-name>

# Port-forward to access services locally
oc port-forward svc/<service-name> 8080:8080
```

## Next Steps

1. ✅ Deploy the demo pipeline
2. 📊 Monitor the training run
3. 🔍 Verify model saved to PVC
4. 🚀 Customize for your use case
5. 📚 Review metrics and logs

## Resources

- [OpenShift AI Documentation](https://access.redhat.com/documentation/en-us/red_hat_openshift_ai)
- [Data Science Pipelines Guide](https://access.redhat.com/documentation/en-us/red_hat_openshift_ai/1/html/working_on_data_science_projects/working-with-data-science-pipelines)
- [KFP SDK Documentation](https://kubeflow-pipelines.readthedocs.io/)
