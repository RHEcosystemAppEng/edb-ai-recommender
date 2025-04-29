#! /usr/bin/env bash
set -e

podman build -t psamouelian/custom-elyra-image:latest .
podman tag localhost/psamouelian/custom-elyra-image:latest quay.io/rh-ee-psamouel/edb/custom-elyra-image:latest
podman push quay.io/rh-ee-psamouel/edb/custom-elyra-image:latest
