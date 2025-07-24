# Makefile for deploying TrustyAI Guardrails stack
# Includes Presidio Analyzer, Llama Guard Wrapper, and Guardrails Orchestrator

# ----- Configuration -------------------------------------------------------
# Override any variable on the command line, e.g.
#   make install NAMESPACE=my-namespace LLM_HOST=my-llm.default.svc LLM_PORT=8080

HELM           ?= helm
NAMESPACE      ?= guardrails-demo

# LLM endpoint (chat generation service)
LLM_HOST       ?= llama-31-8b-instruct-predictor.llama-models.svc.cluster.local
LLM_PORT       ?= 8080

# Default dev02 Llama Guard model service used by the wrapper
LLAMA_GUARD_HOST ?= llama-guard-3-8b-predictor.llama-models.svc.cluster.local
LLAMA_GUARD_PORT ?= 8080
LLAMA_GUARD_MODEL       ?= llama-guard-3-8b
LLAMA_GUARD_BASE_URL    := http://$(LLAMA_GUARD_HOST):$(LLAMA_GUARD_PORT)

# Chart locations (relative to this Makefile)
CHART_ROOT       := ../kubernetes
PRESIDIO_CHART   := $(CHART_ROOT)/presidio
LLAMA_CHART      := $(CHART_ROOT)/llama-guard-wrapper
GUARDRAILS_CHART := $(CHART_ROOT)/guardrails-deployment

# Helm release names
PRESIDIO_RELEASE   ?= presidio
LLAMA_RELEASE      ?= llama-guard-wrapper
GUARDRAILS_RELEASE ?= guardrails

# Derived service names (must match chart templates)
PRESIDIO_SERVICE := presidio-analyzer.$(NAMESPACE).svc.cluster.local
LLAMA_SERVICE    := llama-wrapper-$(LLAMA_RELEASE).$(NAMESPACE).svc.cluster.local

# ----- Targets -------------------------------------------------------------
.PHONY: all install presidio llama-guard-wrapper guardrails uninstall \
        uninstall-presidio uninstall-llama-guard-wrapper uninstall-guardrails status

all: install

install: presidio llama-guard-wrapper guardrails

# --- Individual components -------------------------------------------------

presidio:
	@echo "Installing/Upgrading Presidio Analyzer …"
	$(HELM) upgrade --install $(PRESIDIO_RELEASE) $(PRESIDIO_CHART) \
	  --namespace $(NAMESPACE) --create-namespace \
	  --set service.name=presidio-analyzer

llama-guard-wrapper:
	@echo "Installing/Upgrading Llama Guard Wrapper …"
	$(HELM) upgrade --install $(LLAMA_RELEASE) $(LLAMA_CHART) \
	  --namespace $(NAMESPACE) \
	  --set env.baseUrl=$(LLAMA_GUARD_BASE_URL) \
	  --set env.model=$(LLAMA_GUARD_MODEL)

# Guardrails orchestrator configured to talk to the services above
# chatGeneration -> LLM endpoint (user-supplied)
# detectors.presidioPii -> Presidio service deployed by this Makefile
# detectors.llamaGuard3 -> Wrapper service deployed above

guardrails:
	@echo "Installing/Upgrading TrustyAI Guardrails …"
	$(HELM) upgrade --install $(GUARDRAILS_RELEASE) $(GUARDRAILS_CHART) \
	  --namespace $(NAMESPACE) \
	  --set namespace=$(NAMESPACE) \
	  --set chatGeneration.service.hostname=$(LLM_HOST) \
	  --set chatGeneration.service.port=$(LLM_PORT) \
	  --set detectors.presidioPii.service.hostname=$(PRESIDIO_SERVICE) \
	  --set detectors.presidioPii.service.port=3000 \
	  --set detectors.llamaGuard3.service.hostname=$(LLAMA_SERVICE) \
	  --set detectors.llamaGuard3.service.port=3001

# --- Uninstall -------------------------------------------------------------

uninstall: uninstall-guardrails uninstall-llama-guard-wrapper uninstall-presidio

uninstall-%:
	@echo "Uninstalling $* … (ignoring errors if not installed)"
	-$(HELM) uninstall $* --namespace $(NAMESPACE)

uninstall-presidio:
	@echo "Uninstalling $(PRESIDIO_RELEASE) … (ignoring errors if not installed)"
	-$(HELM) uninstall $(PRESIDIO_RELEASE) --namespace $(NAMESPACE)

uninstall-llama-guard-wrapper:
	@echo "Uninstalling $(LLAMA_RELEASE) … (ignoring errors if not installed)"
	-$(HELM) uninstall $(LLAMA_RELEASE) --namespace $(NAMESPACE)

uninstall-guardrails:
	@echo "Uninstalling $(GUARDRAILS_RELEASE) … (ignoring errors if not installed)"
	-$(HELM) uninstall $(GUARDRAILS_RELEASE) --namespace $(NAMESPACE)

# --- Status ----------------------------------------------------------------

status:
	@echo "\n--- Helm Releases in $(NAMESPACE) ---"
	$(HELM) list -n $(NAMESPACE)
	@echo "\n--- Pods in $(NAMESPACE) ---"
	kubectl get pods -n $(NAMESPACE) 