#!/bin/sh
set -eu
cd "/Users/mirlim/sidejob/mybroker/mybroker"
mkdir -p reports/runtime
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance run \
  --topics config/topics.json \
  --profile examples/profiles/beginner-conservative.json \
  ${MYBROKER_EVIDENCE_SOURCES:-} \
  --today-url "${MYBROKER_TODAY_URL:-http://localhost:8787/reports/product/today.html}" \
  --notification-provider "${MYBROKER_NOTIFICATION_PROVIDER:-telegram}" \
  --dry-run
