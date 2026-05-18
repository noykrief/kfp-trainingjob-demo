#!/usr/bin/env python3
"""
Upload KFP pipeline to OpenShift AI Data Science Pipelines
"""
import kfp
import os
import sys

# KFP endpoint - update this with your cluster's route
# Get it with: oc get route -n <namespace> | grep ds-pipeline
KFP_ENDPOINT = os.getenv("KFP_ENDPOINT")
if not KFP_ENDPOINT:
    print("Error: KFP_ENDPOINT environment variable not set")
    print("Example: export KFP_ENDPOINT=https://ds-pipeline-pipelines-<namespace>.apps.<cluster>.com")
    sys.exit(1)

# Get OpenShift token
token = os.popen("oc whoami -t").read().strip()

print(f"🔗 Connecting to KFP at: {KFP_ENDPOINT}")
print(f"🔑 Using token: {token[:20]}...")

# Create KFP client
client = kfp.Client(
    host=KFP_ENDPOINT,
    existing_token=token,
    ssl_ca_cert=None  # Skip TLS verification for demo
)

print("\n📤 Uploading pipeline...")

# Upload pipeline
pipeline_file = "dog_training_pipeline_clean.yaml"
pipeline = client.upload_pipeline(
    pipeline_package_path=pipeline_file,
    pipeline_name="Dog Breed Classifier Training",
    description="Train a CNN model to classify dog breeds using PyTorch and PVC storage"
)

print(f"   Pipeline uploaded successfully!")
print(f"   Pipeline ID: {pipeline.pipeline_id}")
print(f"   Pipeline Name: {pipeline.display_name}")

print("    Creating pipeline run...")

# Create run
run = client.create_run_from_pipeline_package(
    pipeline_file=pipeline_file,
    arguments={
        'pvc_name': 'kfp-pvc-1',
        'epochs': 10,
        'batch_size': 32,
        'learning_rate': 0.001,
        'use_pretrained': True
    },
    run_name="dog-training-run-1"
)

print(f"   Run created successfully!")
print(f"   Run ID: {run.run_id}")
print(f"   Run Name: {run.name}")
print(f"   Monitor at: {KFP_ENDPOINT}/#/runs/details/{run.run_id}")

