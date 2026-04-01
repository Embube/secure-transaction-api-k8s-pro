#!/usr/bin/env bash
set -euo pipefail

helm repo add gatekeeper https://open-policy-agent.github.io/gatekeeper/charts --force-update
helm repo update

kubectl create namespace gatekeeper-system --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install gatekeeper gatekeeper/gatekeeper \
  --namespace gatekeeper-system \
  --wait
