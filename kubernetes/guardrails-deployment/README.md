# TrustyAI Guardrails Helm Chart

This Helm chart deploys a TrustyAI GuardrailsOrchestrator custom resource that integrates with existing AI safety and compliance services.

## Overview

This chart creates:

- **GuardrailsOrchestrator Custom Resource**: A TrustyAI CRD that orchestrates between LLM services and safety detectors
- **ConfigMap**: Configuration for connecting to external services (LLM, Presidio, Llama Guard, etc.)

**Note**: This chart does NOT deploy the actual detector services (Presidio, Llama Guard) or LLM services. These must be deployed separately and made accessible to the orchestrator.

## Prerequisites

- Kubernetes 1.19+ or OpenShift 4.6+
- Helm 3.0+
- **TrustyAI Operator installed** (provides the GuardrailsOrchestrator CRD)
  - For OpenShift: Install from OperatorHub in the OpenShift Console
  - For Kubernetes: Follow the [TrustyAI Operator installation guide](https://github.com/trustyai-explainability/trustyai-operator)
- Pre-deployed services:
  - LLM service (e.g., Llama 3.1)
  - Presidio Analyzer service (optional, for PII detection)
  - Llama Guard service (optional, for content moderation)

### Installing TrustyAI Operator on OpenShift

1. **Via OpenShift Console**:
   - Navigate to Operators → OperatorHub
   - Search for "TrustyAI"
   - Click Install and follow the prompts

2. **Via CLI**:
   ```bash
   # Create the operator namespace
   oc create namespace trustyai-operator-system
   
   # Apply the operator subscription
   cat <<EOF | oc apply -f -
   apiVersion: operators.coreos.com/v1alpha1
   kind: Subscription
   metadata:
     name: trustyai-operator
     namespace: openshift-operators
   spec:
     channel: stable
     name: trustyai-operator
     source: redhat-operators
     sourceNamespace: openshift-marketplace
   EOF
   
   # Verify operator is running
   oc get pods -n trustyai-operator-system
   ```

## Installation

### Quick Start

```bash
# For Kubernetes
helm install trustyai-guardrails ./guardrails-deployment \
  --namespace guardrails-demo \
  --create-namespace

# For OpenShift
oc new-project guardrails-demo
helm install trustyai-guardrails ./guardrails-deployment \
  --namespace guardrails-demo
```

### Custom Configuration

```bash
# For Kubernetes
helm install trustyai-guardrails ./guardrails-deployment \
  --namespace my-namespace \
  --create-namespace \
  --values custom-values.yaml

# For OpenShift
oc new-project my-namespace
helm install trustyai-guardrails ./guardrails-deployment \
  --namespace my-namespace \
  --values custom-values.yaml
```

## Configuration

### Default Values

The following table lists the configurable parameters and their default values from `values.yaml`:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `namespace` | Kubernetes namespace for deployment | `guardrails-demo` |
| **Orchestrator** | | |
| `orchestrator.name` | Name of the GuardrailsOrchestrator resource | `gorch-sample` |
| `orchestrator.replicas` | Number of orchestrator pod replicas | `1` |
| `orchestrator.configMapName` | Name of the ConfigMap for orchestrator config | `fms-orchestr8-config-nlp` |
| **Chat Generation Service** | | |
| `chatGeneration.service.hostname` | LLM service hostname | `llama-31-8b-instruct-predictor.llama-models.svc.cluster.local` |
| `chatGeneration.service.port` | LLM service port | `8080` |
| **Detectors** | | |
| `detectors.presidioPii.enabled` | Enable Presidio PII detector | `true` |
| `detectors.presidioPii.type` | Detector type | `text_contents` |
| `detectors.presidioPii.service.hostname` | Presidio service hostname | `presidio-analyzer.guardrails-demo.svc.cluster.local` |
| `detectors.presidioPii.service.port` | Presidio service port | `3000` |
| `detectors.presidioPii.chunker_id` | Text chunking strategy | `whole_doc_chunker` |
| `detectors.presidioPii.defaultThreshold` | Detection confidence threshold | `0.5` |
| `detectors.presidioPii.language` | Language for detection | `en` |
| `detectors.llamaGuard3.enabled` | Enable Llama Guard 3 detector | `true` |
| `detectors.llamaGuard3.service.hostname` | Llama Guard service hostname | `llama-guard-wrapper.guardrails-demo.svc.cluster.local` |
| `detectors.llamaGuard3.service.port` | Llama Guard service port | `3001` |
| **Passthrough Headers** | | |
| `passthroughHeaders` | Headers to pass through to services | `["content-type"]` |

### Example Custom Values

Create a `custom-values.yaml` file:

```yaml
namespace: my-guardrails

orchestrator:
  name: production-orchestrator
  replicas: 3
  configMapName: prod-orchestrator-config

chatGeneration:
  service:
    hostname: my-llm-service.production.svc.cluster.local
    port: 8080

detectors:
  presidioPii:
    enabled: true
    defaultThreshold: 0.7  # More strict threshold
    service:
      hostname: presidio.production.svc.cluster.local
      port: 3000
  
  llamaGuard3:
    enabled: false  # Disable Llama Guard

passthroughHeaders:
  - content-type
  - authorization
  - x-request-id
```

## Architecture

```
                        ┌───────────────────────────────────┐
                        │   TrustyAI Operator               │
                        │   (manages GuardrailsOrchestrator)│
                        └────────────┬──────────────────────┘
                                     │ creates/manages
                                     ▼
┌──────────────┐      ┌──────────────────────────────────┐
│  Client App  │─────▶│  GuardrailsOrchestrator Pods     │
│              │      │  (created by this chart)         │
└──────────────┘      └────────────┬─────────────────────┘
                                   │ routes requests to
                    ┌──────────────┴───────────────────────┐
                    ▼                                      ▼
        ┌─────────────────────┐              ┌──────────────────────┐
        │  External Services  │              │   Safety Detectors   │
        ├─────────────────────┤              ├──────────────────────┤
        │ • LLM Service       │              │ • Presidio Analyzer  │
        │   (Llama 3.1, etc.) │              │ • Llama Guard 3      │
        └─────────────────────┘              └──────────────────────┘
```

### Request Flow

1. Client sends request to GuardrailsOrchestrator
2. Orchestrator checks content with configured detectors (Presidio, Llama Guard)
3. If content passes safety checks, request is forwarded to LLM service
4. Response from LLM is checked again by detectors
5. Safe response is returned to client

## Usage

### Verify Deployment

1. **Check Custom Resource**:
   ```bash
   # Kubernetes
   kubectl get guardrailsorchestrator -n guardrails-demo
   
   # OpenShift
   oc get guardrailsorchestrator -n guardrails-demo
   ```

2. **Check Generated Pods** (created by the operator):
   ```bash
   # Kubernetes
   kubectl get pods -n guardrails-demo -l app.kubernetes.io/name=guardrails-demo
   
   # OpenShift
   oc get pods -n guardrails-demo -l app.kubernetes.io/name=guardrails-demo
   ```

3. **View Configuration**:
   ```bash
   # Kubernetes
   kubectl get configmap fms-orchestr8-config-nlp -n guardrails-demo -o yaml
   
   # OpenShift
   oc get configmap fms-orchestr8-config-nlp -n guardrails-demo -o yaml
   ```

### Testing the Deployment

1. **Port Forward to the Orchestrator**:
   ```bash
   # Kubernetes
   kubectl port-forward svc/gorch-sample -n guardrails-demo 8080:8080
   
   # OpenShift
   oc port-forward svc/gorch-sample -n guardrails-demo 8080:8080
   ```

   **For OpenShift Route** (alternative to port-forward):
   ```bash
   # Create a route to expose the service
   oc expose svc/gorch-sample -n guardrails-demo
   
   # Get the route URL
   oc get route gorch-sample -n guardrails-demo -o jsonpath='{.spec.host}'
   ```

2. **Test Request with PII**:
   ```bash
   # Using port-forward (both Kubernetes and OpenShift)
   curl -X POST http://localhost:8080/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "messages": [
         {
           "role": "user", 
           "content": "My name is John Doe and my SSN is 123-45-6789"
         }
       ]
     }'
   
   # Using OpenShift route
   ROUTE_URL=$(oc get route gorch-sample -n guardrails-demo -o jsonpath='{.spec.host}')
   curl -X POST http://${ROUTE_URL}/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "messages": [
         {
           "role": "user", 
           "content": "My name is John Doe and my SSN is 123-45-6789"
         }
       ]
     }'
   ```

3. **Expected Behavior**:
   - Presidio will detect PII (name and SSN)
   - Llama Guard may flag content safety issues
   - Request may be blocked or sanitized based on detector thresholds

## Troubleshooting

### Common Issues

1. **GuardrailsOrchestrator Not Created**:
   ```bash
   # Ensure TrustyAI Operator is installed
   # Kubernetes
   kubectl get crd guardrailsorchestrators.trustyai.opendatahub.io
   
   # OpenShift
   oc get crd guardrailsorchestrators.trustyai.opendatahub.io
   ```
   - Check operator logs if CRD exists but resource isn't created

2. **Service Connection Errors**:
   - Verify external services are running and accessible
   - Check service DNS names resolve correctly
   - Ensure network policies allow communication
   - **OpenShift**: Check Security Context Constraints (SCCs) if pods fail to start

3. **Detector Not Working**:
   - Check detector service logs
   - Verify detector is enabled in values
   - Confirm detector service endpoint is correct

### Debug Commands

```bash
# Check GuardrailsOrchestrator status
# Kubernetes
kubectl describe guardrailsorchestrator gorch-sample -n guardrails-demo

# OpenShift
oc describe guardrailsorchestrator gorch-sample -n guardrails-demo

# Check orchestrator pods logs
# Kubernetes
kubectl logs -l app.kubernetes.io/name=guardrails-demo -n guardrails-demo

# OpenShift
oc logs -l app.kubernetes.io/name=guardrails-demo -n guardrails-demo

# Test service connectivity
# Kubernetes
kubectl run test-pod --image=busybox -n guardrails-demo --rm -it -- wget -O- presidio-analyzer.guardrails-demo.svc.cluster.local:3000/health

# OpenShift
oc run test-pod --image=busybox -n guardrails-demo --rm -it -- wget -O- presidio-analyzer.guardrails-demo.svc.cluster.local:3000/health

# OpenShift-specific: Check project status
oc status -n guardrails-demo

# OpenShift-specific: View in web console
oc console
```

### OpenShift-Specific Considerations

1. **Security Context Constraints (SCCs)**:
   ```bash
   # Check if pods need specific SCCs
   oc get pod -n guardrails-demo -o yaml | grep scc
   
   # If needed, grant SCC to service account
   oc adm policy add-scc-to-user anyuid -z default -n guardrails-demo
   ```

2. **Network Policies**:
   ```bash
   # List network policies
   oc get networkpolicy -n guardrails-demo
   ```

3. **Resource Quotas**:
   ```bash
   # Check project quotas
   oc describe quota -n guardrails-demo
   oc describe limits -n guardrails-demo
   ```

## Chart Structure

```
guardrails-deployment/
├── Chart.yaml                 # Chart metadata
├── values.yaml               # Default configuration values
├── README.md                 # This file
├── .helmignore              # Files to ignore
├── templates/
│   ├── guardrails_orchestrator.yaml  # GuardrailsOrchestrator CR
│   ├── orchestrator_config.yaml      # ConfigMap with orchestrator config
│   └── _helpers.tpl                  # Template helpers
└── charts/                   # Dependency charts (if any)
```

## Uninstallation

```bash
# Kubernetes
helm uninstall trustyai-guardrails -n guardrails-demo

# OpenShift
helm uninstall trustyai-guardrails -n guardrails-demo
oc delete project guardrails-demo  # Optional: remove the entire project

# Or if installed in a custom namespace
helm uninstall trustyai-guardrails -n my-namespace
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