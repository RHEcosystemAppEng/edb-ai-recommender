# TrustyAI Guardrails Helm Chart

This Helm chart deploys TrustyAI Guardrails with Presidio PII detection capabilities on Kubernetes.

## Overview

TrustyAI Guardrails provides a framework for implementing AI safety and compliance measures. This chart deploys:

- **TrustyAI Guardrails Orchestrator**: The main orchestrator service that coordinates between LLM services and detectors
- **Presidio Analyzer**: Microsoft's Presidio for PII (Personally Identifiable Information) detection
- **Optional LLM Service**: Can deploy a local LLM service or connect to external ones

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- TrustyAI Operator installed in the cluster
- Access to container registries (Quay.io, etc.)

## Installation

### Quick Start

```bash
# Add the Helm repository (if using a repository)
helm repo add trustyai https://trustyai.github.io/charts

# Install the chart
helm install trustyai-guardrails ./guardrails-deployment \
  --namespace trustyai-guardrails \
  --create-namespace
```

### Custom Configuration

```bash
# Install with custom values
helm install trustyai-guardrails ./guardrails-deployment \
  --namespace trustyai-guardrails \
  --create-namespace \
  --values custom-values.yaml
```

## Configuration

### Values File

The following table lists the configurable parameters and their default values:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `orchestrator.enabled` | Enable TrustyAI Orchestrator | `true` |
| `orchestrator.replicas` | Number of orchestrator replicas | `1` |
| `orchestrator.image.repository` | Orchestrator image repository | `quay.io/trustyai/trustyai-guardrails-orchestrator` |
| `orchestrator.image.tag` | Orchestrator image tag | `latest` |
| `presidio.enabled` | Enable Presidio Analyzer | `true` |
| `presidio.replicas` | Number of Presidio replicas | `1` |
| `presidio.image.repository` | Presidio image repository | `quay.io/rh-ee-vli/trustyai-guardrails-presidio-pii` |
| `presidio.image.tag` | Presidio image tag | `latest` |
| `llm.enabled` | Enable local LLM service | `false` |
| `llm.image.repository` | LLM image repository | `quay.io/trustyai/llama-3-1-8b-instruct` |

### LLM Configuration

The chart can connect to external LLM services or deploy a local one:

```yaml
orchestrator:
  config:
    llm:
      enabled: true
      service:
        hostname: "llama-3-1-8b-instruct-predictor.rag-demo-16.svc.cluster.local"
        port: 8080
        timeout: 30s
```

### Presidio Configuration

Presidio can be configured for different PII detection scenarios:

```yaml
orchestrator:
  config:
    detectors:
      presidio-pii:
        enabled: true
        type: "text_contents"
        service:
          hostname: "presidio-analyzer.trustyai-guardrails.svc.cluster.local"
          port: 3000
        chunker_id: "whole_doc_chunker"
        default_threshold: 0.5
        language: "en"
```

## Usage

### Testing the Deployment

1. **Port Forward to the Orchestrator**:
   ```bash
   kubectl port-forward svc/trustyai-guardrails-orchestrator 8080:8080 -n trustyai-guardrails
   ```

2. **Test PII Detection**:
   ```bash
   curl -X POST http://localhost:8080/chat \
     -H "Content-Type: application/json" \
     -d '{
       "messages": [
         {
           "role": "user", 
           "content": "My name is John Doe and my email is john@example.com"
         }
       ]
     }'
   ```

3. **Expected Response**:
   ```json
   {
     "response": "I cannot provide personal information about individuals.",
     "detections": [
       {
         "type": "presidio-pii",
         "entities": [
           {
             "entity_type": "PERSON",
             "start": 11,
             "end": 19,
             "score": 0.95
           },
           {
             "entity_type": "EMAIL_ADDRESS",
             "start": 35,
             "end": 52,
             "score": 0.98
           }
         ]
       }
     ]
   }
   ```

### Monitoring

Check the status of your deployment:

```bash
# Check pods
kubectl get pods -n trustyai-guardrails

# Check services
kubectl get svc -n trustyai-guardrails

# Check logs
kubectl logs -f deployment/trustyai-guardrails-orchestrator -n trustyai-guardrails
kubectl logs -f deployment/trustyai-guardrails-presidio -n trustyai-guardrails
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client App    │───▶│   Orchestrator   │───▶│  LLM Service    │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Presidio Analyzer│
                       │   (PII Detection)│
                       └──────────────────┘
```

## Troubleshooting

### Common Issues

1. **Image Pull Errors**:
   - Ensure you have access to the container registries
   - Check image pull secrets if using private registries

2. **Service Connection Issues**:
   - Verify LLM service is accessible from the cluster
   - Check network policies and service mesh configurations

3. **Presidio Model Loading**:
   - Presidio may take time to download NLP models on first startup
   - Check logs for model download progress

### Debug Commands

```bash
# Check pod status
kubectl describe pod -l app.kubernetes.io/name=trustyai-guardrails -n trustyai-guardrails

# Check service endpoints
kubectl get endpoints -n trustyai-guardrails

# Check ConfigMap
kubectl get configmap trustyai-guardrails-orchestrator-config -n trustyai-guardrails -o yaml
```

## Uninstallation

```bash
helm uninstall trustyai-guardrails -n trustyai-guardrails
```

## Contributing

To contribute to this Helm chart:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the chart locally
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0. 