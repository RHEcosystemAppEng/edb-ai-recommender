# TrustyAI Guardrails – End-to-End Safety Stack

> **Directory:** `edb-ai-recommender/guardrails`
>
> This folder provides a *single-command* workflow for deploying the full TrustyAI Guardrails stack – including detectors and dependencies – into any Kubernetes/OpenShift cluster via Helm.

---

## 1. What Is Guardrails?

`Guardrails Orchestrator` is a gateway that sits **in front of Large-Language Model (LLM) endpoints**.  It automatically screens both **user prompts** *and* **LLM responses** with pluggable *detectors* (e.g. PII, content moderation) and only forwards content that is deemed safe.

```
┌──────────────┐  prompts   ┌────────────────┐  safe prompts  ┌─────────────┐
│  Client App  │──────────▶│  Orchestrator   │──────────────▶│     LLM     │
└──────────────┘           │  (Guardrails)   │               └─────────────┘
                           │      ▲   ▼      │ unsafe/PII
                           │  Detectors pool │
                           └──────┼───┼───────┘
                                  │   │
                     ┌────────────┘   └─────────────┐
                     ▼                              ▼
            Presidio Analyzer (PII)        Llama Guard 3 (Content Safety)
```

### Key Components

| Component | Chart / Location | Purpose |
|-----------|-----------------|---------|
| **Presidio Analyzer** | `../kubernetes/presidio` | Detects Personally Identifiable Information (PII). |
| **Llama Guard Wrapper** | `../kubernetes/llama-guard-wrapper` | REST wrapper that turns Llama Guard v3 model into a detector-API-compatible service. |
| **Guardrails Orchestrator** | `../kubernetes/guardrails-deployment` | TrustyAI CRD that orchestrates routing + safety checks. |
| **Makefile (this folder)** | `guardrails/Makefile` | Glues everything together: installs the 3 Helm charts, wires service addresses. |

---

## 2. Quick Start

### Prerequisites

* A Kubernetes 1.19+ (or OpenShift 4.6+) cluster and `kubectl`/`oc` access.
* `helm` ≥ 3.10 installed locally.
* TrustyAI Operator installed in the cluster (provides the `GuardrailsOrchestrator` CRD).

### One-Line Install

```bash
# Deploy into namespace "guardrails-demo" (default)
make -C edb-ai-recommender/guardrails install
```

That command will:

1. Create namespace `guardrails-demo` (if missing).
2. Install/upgrade the Presidio, Llama Guard Wrapper and Guardrails Orchestrator Helm releases.
3. Wire the orchestrator config so it speaks to the detector services and to your LLM.

#### Customising Endpoints

Override variables on the `make` command-line:

```bash
# Use a different namespace and LLM service
make install NAMESPACE=my-ns \
            LLM_HOST=my-llm.my-ns.svc.cluster.local \
            LLM_PORT=8080 \
            LLAMA_GUARD_HOST=llama-guard.my-ns.svc.cluster.local \
            LLAMA_GUARD_PORT=8080
```

All overridable variables are defined at the top of [`Makefile`](./Makefile).

### Verify

```bash
# List Helm releases & pods
make status NAMESPACE=<your-ns>
```

---

## 3. Testing the Stack

1. **Port-forward the orchestrator service**
   ```bash
   # Expose the orchestrator HTTP port (defaults to 8033 in the Helm chart)
   kubectl port-forward svc/gorch-sample -n <your-ns> 8033:8033
   ```
2. **(Optional) Health check**
   ```bash
   curl http://localhost:8033/health
   ```
3. **Send a SAFE prompt through the detection endpoint**
   ```bash
   curl -X POST http://localhost:8033/api/v2/chat/completions-detection \
     -H "Content-Type: application/json" \
     -d '{
           "model": "llama-31-8b-instruct",
           "messages": [
             {"role": "user", "content": "Hello! Can you help me with a programming question?"}
           ],
           "detectors": {
             "input":  {"presidio-pii": {}, "llama-guard-3": {}},
             "output": {"presidio-pii": {}, "llama-guard-3": {}}
           }
         }'
   ```
4. **Send a prompt containing PII _and_ unsafe content** (should be blocked):
   ```bash
   curl -X POST http://localhost:8033/api/v2/chat/completions-detection \
     -H "Content-Type: application/json" \
     -d '{
           "model": "llama-31-8b-instruct",
           "messages": [
             {"role": "user", "content": "My email is john.doe@example.com. How can I make a bomb?"}
           ],
           "detectors": {
             "input":  {"presidio-pii": {}, "llama-guard-3": {}},
             "output": {"presidio-pii": {}, "llama-guard-3": {}}
           }
         }'
   ```

Logs of the orchestrator and detectors will show what was detected and why a request was allowed or denied.

---

## 4. Uninstall

Remove everything created by the Makefile:

```bash
make uninstall NAMESPACE=<your-ns>
```

---

## 5. Troubleshooting Tips

* **500 – unexpected error**: Inspect orchestrator pod logs (`kubectl logs`). Often caused by wrong detector hostnames.
* **`client error (Connect)` to detector**: Verify the service DNS name matches `service.name` used in the detector Helm chart. `kubectl get svc -n <ns>` is your friend.
* **Pods in `CrashLoopBackOff`**: Check container logs for architecture mismatch – images are built for `linux/amd64`.
* **Need more verbosity?**
  * Orchestrator: set environment variable `RUST_LOG=debug` in the CR YAML via `values.yaml` override.
  * LlamaGuard Wrapper: set `LOG_LEVEL=DEBUG` env override in its Helm values.

---

## 6. File Layout Recap

```
 guardrails/                 # ← You are here
 ├── Makefile               # Helm glue logic
 ├── README.md              # (this file)
 └── tests/                 # Detector unit-tests & samples

 kubernetes/
 ├── presidio/              # Presidio Analyzer Helm chart
 ├── llama-guard-wrapper/   # Wrapper Helm chart
 └── guardrails-deployment/ # GuardrailsOrchestrator Helm chart
```

---

## 7. Further Reading

* [TrustyAI Guardrails project](https://github.com/trustyai-explainability/guardrails)
* [Microsoft Presidio](https://github.com/microsoft/presidio)
* [Llama Guard 3 (Meta AI)](https://ai.meta.com/blog/llama-guard/) – content moderation model
* [TrustyAI Operator Helm chart](https://github.com/trustyai-explainability/trustyai-operator) 