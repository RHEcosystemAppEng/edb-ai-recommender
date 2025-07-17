#!/usr/bin/env bash
#
# test_orchestrator.sh
#
# Usage:
#   ORCHESTRATOR_URL="https://your-orch-url" ./test_orchestrator.sh

ORCHESTRATOR_URL=${ORCHESTRATOR_URL:-"http://localhost:8080"}

curl -sSf -X POST "${ORCHESTRATOR_URL}/api/v2/chat/completions-detection" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-31-8b-instruct",
    "messages": [
      {
        "role": "user",
        "content": "My email is test@example.com and phone is 555-123-4567. Can you help me with something?"
      }
    ],
    "detectors": {
      "input": {
        "presidio-pii": {},
        "llama-guard-3": {}
      },
      "output": {
        "presidio-pii": {},
        "llama-guard-3": {}
      }
    }
  }'
