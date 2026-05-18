#!/usr/bin/env python3
"""
Create a pipeline run from the YAML package
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

print(f"Connecting to KFP at: {KFP_ENDPOINT}")

# Create KFP client
client = kfp.Client(
    host=KFP_ENDPOINT,
    existing_token=token,
    ssl_ca_cert=None  # Skip TLS verification for demo
)

pipeline_file = "dog_training_pipeline.yaml"

print(f"\nCreating run from {pipeline_file}...")

# Create run from pipeline package
run = client.create_run_from_pipeline_package(
    pipeline_file=pipeline_file,
    arguments={
        'pvc_name': 'kfp-pvc-1',
        'epochs': 10,
        'batch_size': 32,
        'learning_rate': 0.001,
        'use_pretrained': True
    },
    run_name="dog-training-demo-run"
)

print(f"Run created successfully!")
print(f"   Run ID: {run.run_id}")
print(f"\nMonitor at: {KFP_ENDPOINT}/#/runs/details/{run.run_id}")
