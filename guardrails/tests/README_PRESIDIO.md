# Testing Presidio Analyzer on OpenShift

This guide provides multiple ways to test the presidio-analyzer endpoint deployed on your OpenShift cluster.

## Quick Start

### Option 1: Simple curl-based test (Recommended for quick checks)

```bash
# Test with default URL
./quick-curl-test.sh

# Test with custom URL
./quick-curl-test.sh http://your-presidio-service.example.com
```

### Option 2: Comprehensive Python-based test

```bash
# Test with default URL
./test-openshift.sh

# Test with custom URL
./test-openshift.sh http://your-presidio-service.example.com

# Run with verbose output
./test-openshift.sh -v

# Run performance test
./test-openshift.sh -p
```

### Option 3: Direct Python script

```bash
# Test with default URL
python3 test-openshift-endpoint.py

# Test with custom URL
python3 test-openshift-endpoint.py http://your-presidio-service.example.com
```

## Test Scripts Overview

### 1. `quick-curl-test.sh` - Simple curl-based test
- **Dependencies**: Only `curl` (no Python required)
- **Features**: 
  - Health endpoint test
  - Legacy `/analyze` endpoint test
  - FMS Guardrails Orchestrator endpoint test
  - Multiple contents test
  - Basic performance test
- **Best for**: Quick verification, CI/CD pipelines, environments without Python

### 2. `test-openshift.sh` - Comprehensive test wrapper
- **Dependencies**: Python3, requests library
- **Features**:
  - All features from Python script
  - Colored output
  - Logging to file
  - Command-line options
  - Automatic dependency installation
- **Best for**: Full testing, debugging, development

### 3. `test-openshift-endpoint.py` - Python test script
- **Dependencies**: Python3, requests library
- **Features**:
  - Comprehensive test cases
  - Performance testing
  - Detailed result analysis
  - Multiple test scenarios
- **Best for**: Detailed testing, custom test scenarios

## Manual Testing Commands

If you prefer to test manually, here are the key commands:

### Health Check
```bash
curl -s http://presidio-analyzer-guardrails-presidio.apps.ai-dev02.kni.syseng.devcluster.openshift.com/health
```

### Legacy Endpoint Test
```bash
curl -X POST http://presidio-analyzer-guardrails-presidio.apps.ai-dev02.kni.syseng.devcluster.openshift.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "My email is test@example.com and phone is 555-123-4567",
    "language": "en",
    "score_threshold": 0.5,
    "entities": ["EMAIL_ADDRESS", "PHONE_NUMBER"]
  }'
```

### FMS Guardrails Orchestrator Endpoint Test
```bash
curl -X POST http://presidio-analyzer-guardrails-presidio.apps.ai-dev02.kni.syseng.devcluster.openshift.com/api/v1/text/contents \
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

## Expected Responses

### Health Endpoint
```json
"Presidio Analyzer service is up"
```

### Legacy Endpoint
```json
[
  {
    "analysis_explanation": null,
    "end": 28,
    "entity_type": "EMAIL_ADDRESS",
    "recognition_metadata": {
      "recognizer_identifier": "EmailRecognizer_123456",
      "recognizer_name": "EmailRecognizer"
    },
    "score": 1.0,
    "start": 12
  },
  {
    "analysis_explanation": null,
    "end": 54,
    "entity_type": "PHONE_NUMBER",
    "recognition_metadata": {
      "recognizer_identifier": "PhoneRecognizer_123456",
      "recognizer_name": "PhoneRecognizer"
    },
    "score": 0.75,
    "start": 42
  }
]
```

### FMS Guardrails Orchestrator Endpoint
```json
[
  [
    {
      "start": 12,
      "end": 28,
      "text": "test@example.com",
      "detection": "EMAIL_ADDRESS",
      "detection_type": "pii",
      "score": 1.0,
      "evidence": [],
      "metadata": {},
      "detector_id": "EmailRecognizer"
    },
    {
      "start": 42,
      "end": 54,
      "text": "555-123-4567",
      "detection": "PHONE_NUMBER",
      "detection_type": "pii",
      "score": 0.75,
      "evidence": [],
      "metadata": {},
      "detector_id": "PhoneRecognizer"
    }
  ]
]
```

## Troubleshooting

### Common Issues

1. **Connection refused or timeout**
   - Check if the service is running on OpenShift
   - Verify the URL is correct
   - Check network connectivity

2. **401/403 Unauthorized/Forbidden**
   - Check if authentication is required
   - Verify service account permissions

3. **500 Internal Server Error**
   - Check service logs on OpenShift
   - Verify the service is properly configured

4. **Python requests library not found**
   ```bash
   pip3 install requests
   ```

### Debugging Commands

```bash
# Check if endpoint is reachable
curl -v http://presidio-analyzer-guardrails-presidio.apps.ai-dev02.kni.syseng.devcluster.openshift.com/health

# Test with verbose curl output
curl -v -X POST http://presidio-analyzer-guardrails-presidio.apps.ai-dev02.kni.syseng.devcluster.openshift.com/api/v1/text/contents \
  -H "Content-Type: application/json" \
  -d '{"contents": ["test"], "detector_params": {"language": "en", "threshold": 0.5}}'

# Check OpenShift service status
oc get pods -n your-namespace
oc logs deployment/presidio-analyzer -n your-namespace
```

## Integration with FMS Guardrails Orchestrator

Once you've verified the presidio-analyzer is working, you can integrate it with the FMS Guardrails Orchestrator by updating your configuration:

```yaml
detectors:
  presidio-pii:
    type: text_contents
    service:
      hostname: presidio-analyzer-guardrails-presidio.apps.ai-dev02.kni.syseng.devcluster.openshift.com # change this to your deployment route
      port: 3000
    chunker_id: whole_doc_chunker
    default_threshold: 0.5
    language: en
    headers:
      content-type: application/json
```

## Performance Testing

For load testing, you can use the performance test feature:

```bash
# Run performance test with more requests
./test-openshift.sh -p

# Or modify the Python script to increase request count
python3 test-openshift-endpoint.py http://your-url
```

## Logging and Output

- **Verbose mode**: Use `-v` flag for detailed output
- **Log files**: Results are saved to `test_results.log` when not in verbose mode
- **Exit codes**: Scripts exit with 0 for success, 1 for failure

## Custom Test Scenarios

You can modify the Python test script to add custom test scenarios:

```python
# Add custom test case
custom_test = {
    "description": "Custom PII detection",
    "payload": {
        "contents": ["Your custom text here"],
        "detector_params": {
            "language": "en",
            "threshold": 0.5,
            "entities": ["EMAIL_ADDRESS", "PHONE_NUMBER"]
        }
    }
}
```

This guide should help you thoroughly test your presidio-analyzer deployment on OpenShift! 