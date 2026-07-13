#!/usr/bin/env bash
set -euo pipefail

APP_NAME="${APP_NAME:-devmon}"
NAMESPACE="${NAMESPACE:-devmon}"
DOCKERHUB_NAMESPACE="${DOCKERHUB_NAMESPACE:-mahamah}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
USE_REMOTE_IMAGES="${USE_REMOTE_IMAGES:-1}"

echo "Checking shared Minikube infrastructure..."
kubectl get ns >/dev/null
kubectl get ns ingress-nginx >/dev/null
kubectl get deployment ingress-nginx-controller -n ingress-nginx >/dev/null

if [ "${USE_REMOTE_IMAGES}" = "1" ]; then
  IMAGE="${DOCKERHUB_NAMESPACE}/${APP_NAME}:${IMAGE_TAG}"
else
  IMAGE="${APP_NAME}:local"
fi

echo "Applying Kubernetes manifest..."
kubectl apply -f k8s/devmon.yaml
kubectl set image deployment/devmon devmon="${IMAGE}" -n "${NAMESPACE}"
kubectl rollout status deployment/devmon -n "${NAMESPACE}" --timeout=120s

echo "Current state:"
kubectl get pods -n "${NAMESPACE}" -o wide
kubectl get svc -n "${NAMESPACE}"
kubectl get ingress -n "${NAMESPACE}"
kubectl get pvc -n "${NAMESPACE}" || true

echo "URLs:"
echo "https://devmon.mah.com/"
echo "https://devmon.192.168.239.141.sslip.io/"
