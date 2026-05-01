#!/bin/bash
# Regenerate specs from the planner (which we already scrubbed), then rebuild queue
set -e
cd /home/ubuntu/autoimmune-reset
python3 scripts/plan-500-queue.py 2>&1 | tail -5
python3 scripts/build-five-hundred-queue.py 2>&1 | tail -15
