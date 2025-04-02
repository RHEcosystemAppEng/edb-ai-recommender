#! /usr/bin/env bash
set -e

podman build -t ai-recommender .
podman tag localhost/ai-recommender:latest docker.io/psamouelian/ai-recommender:latest
podman push docker.io/psamouelian/ai-recommender:latest

helm uninstall ai-recommender --ignore-not-found
helm install ai-recommender ./kubernetes/ai-recommender