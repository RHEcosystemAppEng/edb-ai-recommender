# Llama Guard Wrapper Helm Chart

This Helm chart deploys the **Llama Guard Wrapper**, a lightweight HTTP service that forwards content-moderation requests to an upstream Llama Guard model (e.g. *llama-guard-3-8b*).  The wrapper presents a simple REST API, adds minor parameter validation, and standardises responses for use by TrustyAI Guardrails or other safety pipelines.

---

## Overview

The chart installs the following Kubernetes resources:

| Resource                | Purpose                                            |
|-------------------------|----------------------------------------------------|
| **Deployment / Pod**    | Runs the wrapper container                          |
| **Service**             | Exposes the wrapper inside the cluster             |
| *(Optional) Ingress / Route* | Exposes the service externally (OpenShift / Kubernetes Ingress) |

Default runtime ports:

| Port | Description |
|------|-------------|
| `3001` | HTTP API & health checks |

---

## Prerequisites

* **Kubernetes 1.19+** or **OpenShift 4.6+**
* **Helm 3**
* Container registry access to `quay.io/rh-ee-vli/trustyai-guardrails-llama-guard-wrapper` (or your own rebuilt image)
* The upstream Llama Guard model service must already be running and reachable via the URL configured in `values.yaml` (`env.baseUrl`).

---

## Installation

### Quick Start

```bash
# Create (or switch to) the target namespace
kubectl create namespace guardrails-demo   # or: oc new-project guardrails-demo

# Install with default values
helm install llama-wrapper ./llama-wrapper \
  --namespace guardrails-demo \
  --create-namespace
```

### Custom Configuration

All parameters are defined in `values.yaml`.  You can either pass `--set` flags or supply a custom file:

```bash
helm install llama-wrapper ./llama-wrapper \
  --namespace guardrails-demo \
  --values my-values.yaml
```

Example `my-values.yaml`:

```yaml
replicaCount: 2

image:
  repository: quay.io/myrepo/llama-guard-wrapper
  tag: v1.0.0
  pullPolicy: IfNotPresent

env:
  baseUrl: http://my-llama-guard-svc.llama.svc.cluster.local:8080
  model: llama-guard-3-8b

service:
  type: ClusterIP
  port: 3001
```

---

## Configuration Reference

| Key | Description | Default |
|-----|-------------|---------|
| `replicaCount` | Number of wrapper pods | `1` |
| `image.repository` | Container image repository | `quay.io/rh-ee-vli/trustyai-guardrails-llama-guard-wrapper` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Kubernetes image pull policy | `IfNotPresent` |
| `env.baseUrl` | URL of the upstream Llama Guard model | `http://llama-guard-3-8b-predictor.llama-models.svc.cluster.local:8080` |
| `env.model` | Model identifier sent to Llama Guard | `llama-guard-3-8b` |
| `service.type` | Service type (`ClusterIP`, `NodePort`, `LoadBalancer`) | `ClusterIP` |
| `service.port` | Port exposed by the container & service | `3001` |
| `resources` | CPU / Memory requests & limits | See `values.yaml` |

---

## Verifying the Deployment

After the pod reaches **Running**, confirm the service is healthy.

### 1. Health Check

```bash
curl http://llama-wrapper.guardrails-demo.svc.cluster.local:3001/health
```
Expected response:
```text
OK
```

### 2. Moderation Request Example

```bash
curl -X POST http://llama-wrapper.guardrails-demo.svc.cluster.local:3001/moderate \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test message."}'
```
The exact path/format may differ depending on your wrapper implementation, but the above illustrates a typical usage.

---

## Troubleshooting

| Symptom | Possible Cause | Resolution |
|---------|----------------|------------|
| `Connection refused` | Service not running / incorrect DNS | Verify pod status and service address (`kubectl get pods,svc`). |
| `502 / 503` errors | Upstream Llama Guard model unreachable | Check `env.baseUrl`, network policies, or model service health. |
| `500 Internal Server Error` | Wrapper exception | Inspect pod logs: `kubectl logs deployment/llama-wrapper -n guardrails-demo`. |
| Pod restart loop | Missing image or bad command | Verify image repository/tag and container entrypoint. |

Useful commands:

```bash
kubectl get pods -n guardrails-demo
kubectl describe pod <pod-name> -n guardrails-demo
kubectl logs deployment/llama-wrapper -n guardrails-demo
```

---

## Uninstallation

```bash
helm uninstall llama-wrapper -n guardrails-demo
kubectl delete namespace guardrails-demo   # optional – remove the entire project
```

