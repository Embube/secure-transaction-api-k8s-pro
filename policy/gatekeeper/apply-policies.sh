#!/usr/bin/env bash
set -euo pipefail

kubectl apply -f policy/gatekeeper/constrainttemplates/
kubectl apply -f policy/gatekeeper/constraints/
