# Presidio Analyzer Helm Chart

This Helm chart deploys **Presidio Analyzer**, an open-source service for detecting personally identifiable information (PII) in text.  The chart is designed for Kubernetes and OpenShift clusters and can be installed with a single Helm command.

---

## Overview

The chart creates the following resources:

| Resource | Purpose |
|----------|---------|
| **Deployment / Pod** | Runs the Presidio Analyzer container |
| **Service** | Exposes the analyzer internally in the cluster |
| **(Optional) Route / Ingress** | Exposes the analyzer outside the cluster (OpenShift / Kubernetes Ingress) |
| **ConfigMap** | Provides runtime configuration such as model and recognizer settings |

Presidio exposes two compatible REST APIs:

1. **Legacy /analyze endpoint** – original Presidio request format.
2. **FMS Guardrails “contents” endpoint** – wrapper that adapts Presidio output to the TrustyAI Guardrails conventions.

---

## Prerequisites

* Kubernetes **1.19+** or OpenShift **4.6+**
* **Helm 3**
* A container registry (e.g. Quay.io, Docker Hub) containing a compatible Presidio Analyzer image.  The default tag is `quay.io/<your-repo>/presidio-analyzer:latest`.
* (Optional – OpenShift) Expose a Route if external access is required.

---

## Installation

### Quick Start

```bash
# Create (or switch to) the target namespace
kubectl create namespace presidio-demo   # or: oc new-project presidio-demo

# Install with default settings
helm install presidio-analyzer ./presidio \
  --namespace presidio-demo \
  --create-namespace
```

### Custom Configuration

All tunables are exposed in `values.yaml`.  Provide a custom file or pass `--set` flags:

```bash
helm install presidio-analyzer ./presidio \
  --namespace presidio-demo \
  --values my-values.yaml
```

Example `my-values.yaml` – change the container image and number of replicas:

```yaml
image:
  repository: quay.io/rh-ee-vli/trustyai-guardrails-presidio-pii
  tag: latest
replicaCount: 2
service:
  type: ClusterIP  # or NodePort / LoadBalancer / Route
  port: 3000
```

---

## Configuration Reference

| Key | Description | Default |
|-----|-------------|---------|
| `replicaCount` | Number of analyzer pods | `1` |
| `image.repository` | Container image repository | `quay.io/presidio/presidio-analyzer` |
| `image.tag` | Image tag | `latest` |
| `service.port` | Service port exposed by the container | `3000` |
| `service.type` | Service type (`ClusterIP`, `NodePort`, `LoadBalancer`) | `ClusterIP` |
| `resources` | Pod CPU/Memory requests & limits | `{}` |
| `nodeSelector`, `tolerations`, `affinity` | Scheduling options | _empty_ |

Consult `values.yaml` for the full list.

---

## Testing the Deployment

Once the pod is **Running**, verify the endpoints.

### 1. Health Check

```bash
curl http://presidio-analyzer.presidio-demo.svc.cluster.local:3000/health
```
Expected response:
```text
Presidio Analyzer service is up
```

### 2. Legacy `/analyze` Endpoint

```bash
curl -X POST http://presidio-analyzer.presidio-demo.svc.cluster.local:3000/analyze \
  -H "Content-Type: application/json" \
  -d '{
        "text": "My email is test@example.com and phone is 555-123-4567",
        "language": "en",
        "score_threshold": 0.5,
        "entities": ["EMAIL_ADDRESS", "PHONE_NUMBER"]
      }'
```

### 3. Guardrails-Compatible `contents` Endpoint

```bash
curl -X POST http://presidio-analyzer.presidio-demo.svc.cluster.local:3000/api/v1/text/contents \
  -H "Content-Type: application/json" \
  -d '{
        "contents": ["My email is test@example.com and phone is 555-123-4567"],
        "detector_params": {
          "language": "en",
          "threshold": 0.5,
          "entities": ["EMAIL_ADDRESS", "PHONE_NUMBER"]
        }
      }'
```

Both endpoints should return JSON containing the detected entities.

---

## Troubleshooting

| Symptom | Possible Cause | Resolution |
|---------|----------------|------------|
| `Connection refused` or timeout | Service not running / wrong URL | Verify pod status and service DNS name.  Use `kubectl get pods` and `kubectl get svc`. |
| `401 / 403` errors | Authentication enforced by ingress | Check ingress / route configuration. |
| `500 Internal Server Error` | Mis-configuration in recognizer settings | Inspect pod logs: `kubectl logs deployment/presidio-analyzer -n presidio-demo`. |
| `exec format error` on container start | Image built for wrong CPU architecture | Rebuild with the correct `--platform` (e.g. `linux/amd64`). |

Useful commands:

```bash
# Pod and service status
kubectl get pods -n presidio-demo
kubectl describe pod <pod-name> -n presidio-demo
kubectl get svc presidio-analyzer -n presidio-demo

# View container logs
kubectl logs deployment/presidio-analyzer -n presidio-demo

# Exec into the container (if allowed)
kubectl exec -it deployment/presidio-analyzer -n presidio-demo -- /bin/sh
```

---

## Uninstallation

```bash
helm uninstall presidio-analyzer -n presidio-demo
kubectl delete namespace presidio-demo   # optional – remove the whole project
```

---

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make your changes and test locally.
4. Submit a pull request.

---

## License

This project is licensed under the **Apache License 2.0**. 