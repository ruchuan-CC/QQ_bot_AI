#!/usr/bin/env bash
set -euo pipefail

uvicorn src.app:create_app --factory --reload --host 0.0.0.0 --port 8088
