#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${NAMESPACE:-devmon}"

kubectl get ns
kubectl get pods -n "${NAMESPACE}" -o wide
kubectl get svc -n "${NAMESPACE}"
kubectl get ingress -n "${NAMESPACE}"
kubectl get deployment -n "${NAMESPACE}"
curl -kI https://devmon.mah.com/
curl -kI https://devmon.192.168.239.141.sslip.io/
