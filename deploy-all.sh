#! /usr/bin/env bash
set -e

helm install --debug --namespace=test-edb-project edb-workbench ./workbench