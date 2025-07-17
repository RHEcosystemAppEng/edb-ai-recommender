# Presidio Analyzer for FMS Guardrails Orchestrator

This is an adapted version of the Presidio Analyzer that supports the FMS Guardrails Orchestrator's `/api/v1/text/contents` endpoint format while maintaining backward compatibility with the original Presidio API.

## Overview

The Presidio Analyzer has been extended to support the FMS Guardrails Orchestrator's standardized detector API format. This allows Presidio to be used as a detector service within the FMS Guardrails Orchestrator ecosystem.

## New Endpoint: `/api/v1/text/contents`

### Request Format

The new endpoint accepts requests in the FMS Guardrails Orchestrator format:

```json
{
  "contents": [
    "Text to analyze for PII",
    "Another text to analyze",
    "Third text to analyze"
  ],
  "detector_params": {
    "language": "en",
    "threshold": 0.5,
    "entities": ["EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN"],
    "correlation_id": "optional-correlation-id",
    "return_decision_process": false,
    "context": "optional-context",
    "allow_list": ["allowed@email.com"],
    "allow_list_match": "exact"
  }
}
```

### Response Format

The response follows the FMS Guardrails Orchestrator's `ContentAnalysisResponse` format:

```json
[
  [
    {
      "start": 14,
      "end": 26,
      "text": "john@example.com",
      "detection": "EMAIL_ADDRESS",
      "detection_type": "pii",
      "score": 0.95,
      "detector_id": "EmailRecognizer",
      "evidence": [],
      "metadata": {}
    }
  ],
  [
    {
      "start": 8,
      "end": 19,
      "text": "555-123-4567",
      "detection": "PHONE_NUMBER",
      "detection_type": "pii",
      "score": 0.92,
      "detector_id": "PhoneRecognizer",
      "evidence": [],
      "metadata": {}
    }
  ],
  []
]
```

## Configuration for FMS Guardrails Orchestrator

To use this adapted Presidio Analyzer with FMS Guardrails Orchestrator, add the following configuration to your orchestrator's `config.yaml`:

```yaml
detectors:
  presidio-pii:
    type: text_contents
    service:
      hostname: presidio-analyzer.your-namespace.svc.cluster.local
      port: 3000
    chunker_id: whole_doc_chunker
    default_threshold: 0.5
    language: en
    headers:
      content-type: application/json
```

## Deployment

### Docker

Build and run the container:

```bash
# Build the image
docker build -t presidio-analyzer-fms .

# Run the container
docker run -p 3000:3000 presidio-analyzer-fms
```

### Kubernetes/OpenShift

Deploy using the provided Dockerfile:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: presidio-analyzer
  namespace: your-namespace
spec:
  replicas: 1
  selector:
    matchLabels:
      app: presidio-analyzer
  template:
    metadata:
      labels:
        app: presidio-analyzer
    spec:
      containers:
      - name: presidio-analyzer
        image: presidio-analyzer-fms:latest
        ports:
        - containerPort: 3000
        env:
        - name: PORT
          value: "3000"
        - name: LOG_LEVEL
          value: "INFO"
---
apiVersion: v1
kind: Service
metadata:
  name: presidio-analyzer
  namespace: your-namespace
spec:
  selector:
    app: presidio-analyzer
  ports:
  - port: 3000
    targetPort: 3000
  type: ClusterIP
```

## Testing

Use the provided test script to verify the endpoint works correctly:

```bash
# Test the new endpoint
python test_contents_endpoint.py

# Test with a custom URL
python test_contents_endpoint.py http://your-service-url:3000
```

## Environment Variables

- `PORT`: Port to run the service on (default: 3000)
- `LOG_LEVEL`: Logging level (default: INFO)
- `ANALYZER_CONF_FILE`: Path to analyzer configuration file
- `NLP_CONF_FILE`: Path to NLP engine configuration file
- `RECOGNIZER_REGISTRY_CONF_FILE`: Path to recognizer registry configuration file

## Supported Parameters

The `detector_params` object supports the following Presidio parameters:

- `language`: Language code (default: "en")
- `threshold`: Minimum score threshold (default: 0.5)
- `entities`: List of entity types to detect (if not specified, all entities are detected)
- `correlation_id`: Optional correlation ID for tracking
- `return_decision_process`: Whether to return decision process (default: false)
- `context`: Optional context for analysis
- `allow_list`: List of allowed values
- `allow_list_match`: Match type for allow list (default: "exact")
- `regex_flags`: Regular expression flags

## Backward Compatibility

The original `/analyze` endpoint is still available and works exactly as before. This ensures that existing Presidio Analyzer integrations continue to work without modification.

## Differences from Original Presidio API

1. **Batch Processing**: The new endpoint supports processing multiple text contents in a single request
2. **Standardized Format**: Uses the FMS Guardrails Orchestrator's standardized request/response format
3. **Parameter Mapping**: Presidio parameters are mapped from `detector_params` instead of being at the top level
4. **Response Structure**: Returns a list of detection lists, one per input content

## Troubleshooting

### Common Issues

1. **No detections found**: Check that the `threshold` is not too high or that the text contains the expected PII patterns
2. **Language not supported**: Ensure the specified language is supported by your Presidio installation
3. **Service not reachable**: Verify the service is running and the hostname/port are correct in your orchestrator configuration

### Logs

Check the application logs for detailed error information:

```bash
# If running in Docker
docker logs <container-id>

# If running in Kubernetes
kubectl logs -f deployment/presidio-analyzer
```

## Contributing

This adaptation maintains the core Presidio Analyzer functionality while adding FMS Guardrails Orchestrator compatibility. Any improvements should maintain backward compatibility with the original Presidio API. 