#!/usr/bin/env bash

cd "$(dirname "$0")"
python dashboard/server.py "$@"