#!/usr/bin/env bash
# Simple entrypoint: runs uvicorn using environment defaults if not provided
exec uvicorn "${APP_MODULE:-main:app}" --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}" --reload
