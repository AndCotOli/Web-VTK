#!/usr/bin/env bash
CURRENT_DIR=$(dirname "$0")

cd "$CURRENT_DIR/.." || exit
DEPLOY_DIR="$PWD"
cd "../.." || exit
ROOT_DIR="$PWD"

docker run --rm \
    -v "$DEPLOY_DIR:/deploy" \
    -v "$ROOT_DIR:/local-app" \
    kitware/trame build
