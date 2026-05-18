#!/bin/bash
#
# Login script for OpenShift
# Make sure to copy .env.example to .env and fill in your credentials
#

set -e

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load environment variables from project root
ENV_FILE="${PROJECT_ROOT}/.env"
if [ -f "$ENV_FILE" ]; then
    export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
else
    echo "❌ Error: .env file not found at $ENV_FILE"
    echo "Please copy .env.example to .env and fill in your credentials:"
    echo "  cd $PROJECT_ROOT"
    echo "  cp .env.example .env"
    echo "  # Then edit .env with your credentials"
    exit 1
fi

# Validate required variables
if [ -z "$OPENSHIFT_API" ] || [ -z "$OPENSHIFT_USERNAME" ] || [ -z "$OPENSHIFT_PASSWORD" ]; then
    echo "❌ Error: Missing required environment variables"
    echo "Please check your .env file has:"
    echo "  - OPENSHIFT_API"
    echo "  - OPENSHIFT_USERNAME"
    echo "  - OPENSHIFT_PASSWORD"
    exit 1
fi

echo "=========================================="
echo "🔐 Logging in to OpenShift"
echo "=========================================="
echo "API: ${OPENSHIFT_API}"
echo "User: ${OPENSHIFT_USERNAME}"
echo "=========================================="
echo

# Login to OpenShift
oc login "${OPENSHIFT_API}" \
    -u "${OPENSHIFT_USERNAME}" \
    -p "${OPENSHIFT_PASSWORD}" \
    --insecure-skip-tls-verify

echo
echo "✅ Login successful!"
echo

# Switch to project if specified
if [ -n "$OPENSHIFT_PROJECT" ]; then
    echo "Switching to project: ${OPENSHIFT_PROJECT}"
    oc project "${OPENSHIFT_PROJECT}" 2>/dev/null || {
        echo "Project not found. Creating..."
        oc new-project "${OPENSHIFT_PROJECT}"
    }
fi

echo
echo "📊 Current context:"
oc whoami
oc project
echo
