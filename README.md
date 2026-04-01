# Secure Transaction API on Kubernetes

A portfolio-grade DevSecOps project that demonstrates how to containerize and deploy a secure Flask API on Kubernetes with GitHub Actions, Trivy scanning, Helm, Amazon EKS deployment validation, HTTPS via cert-manager, Prometheus/Grafana monitoring, and Gatekeeper policy enforcement.

## Features

- Dockerized Flask API with health, readiness, and metrics endpoints
- Kubernetes manifests and a production-style Helm chart
- GitHub Actions pipeline with Docker Hub push and Trivy scans
- Real EKS validation and Helm-based deployment
- HTTPS-ready ingress with cert-manager ClusterIssuer examples
- Prometheus `ServiceMonitor` and preconfigured Grafana dashboard
- OPA Gatekeeper sample policies for security enforcement

## Project Structure

```text
secure-transaction-api-k8s-pro/
├── .github/workflows/ci-cd-trivy-dockerhub-eks.yml
├── app/
├── helm/secure-transaction-api/
├── k8s/
├── monitoring/
├── platform/cert-manager/
├── policy/gatekeeper/
├── .gitignore
├── .trivyignore
└── README.md
```

## App Endpoints

- `/` application info
- `/health` liveness probe
- `/ready` readiness probe
- `/metrics` Prometheus metrics
- `/transactions` secured endpoint
- `/transactions/<id>` secured endpoint

## Local Development

```bash
cd app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Test locally:

```bash
curl http://localhost:5000/health
curl -H "X-API-KEY: not-set" http://localhost:5000/transactions
curl http://localhost:5000/metrics
```

## Build the Container

```bash
docker build -t secure-transaction-api:1.0 ./app
```

## Deploy Locally with Minikube

```bash
minikube start
minikube image load secure-transaction-api:1.0
kubectl apply -f k8s/
kubectl port-forward svc/transaction-api-service 8080:80 -n secure-bank
```

Then test:

```bash
curl http://localhost:8080/health
curl -H "X-API-KEY: change-me" http://localhost:8080/transactions
```

## Helm Install

```bash
helm lint ./helm/secure-transaction-api

helm upgrade --install secure-transaction-api ./helm/secure-transaction-api \
  --namespace secure-bank \
  --create-namespace \
  --set image.repository=YOUR_DOCKERHUB_USERNAME/secure-transaction-api \
  --set image.tag=latest \
  --set secret.apiKey=change-me
```

## GitHub Secrets Required

Add these in GitHub > Settings > Secrets and variables > Actions:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `EKS_CLUSTER_NAME`
- `APP_API_KEY`

## EKS Deployment Validation

The workflow updates kubeconfig, checks cluster access, lints and templates the Helm chart, deploys it, waits for rollout, and runs `helm test`.

## Install cert-manager

```bash
chmod +x platform/cert-manager/install-cert-manager.sh
./platform/cert-manager/install-cert-manager.sh
kubectl apply -f platform/cert-manager/clusterissuer-staging.yaml
```

When your DNS is ready, switch the ingress annotation to `letsencrypt-prod` and apply `clusterissuer-prod.yaml`.

## Install Monitoring

```bash
chmod +x monitoring/install-monitoring.sh
./monitoring/install-monitoring.sh
```

Port-forward Grafana:

```bash
kubectl port-forward svc/kube-prom-stack-grafana 3000:80 -n monitoring
```

Open `http://localhost:3000`

## Install Gatekeeper and Policies

```bash
chmod +x policy/gatekeeper/install-gatekeeper.sh
chmod +x policy/gatekeeper/apply-policies.sh

./policy/gatekeeper/install-gatekeeper.sh
./policy/gatekeeper/apply-policies.sh
```

Included sample policies:
- require `runAsNonRoot=true`
- require `readOnlyRootFilesystem=true`
- require `allowPrivilegeEscalation=false`
- block images using the `:latest` tag

## Notes

- Replace placeholder domains, email addresses, and secrets before deploying.
- The ingress assumes an NGINX ingress controller is installed.
- `ServiceMonitor` requires Prometheus Operator / kube-prometheus-stack.

## Update
- Triggering GitHub Actions pipeline
