#!/bin/sh
exec python3 "$(dirname "$0")/.drydock/bin/verify.py" "$@"
