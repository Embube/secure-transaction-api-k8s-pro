#!/usr/bin/env bash
set -euo pipefail

helm repo add jetstack https://charts.jetstack.io --force-update
helm repo update

kubectl create namespace cert-manager --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --set crds.enabled=true \
  --wait
