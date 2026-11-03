#!/usr/bin/env bash

BASE_URL="https://devops-midterm-59foyr6t0-me-c309.vercel.app"
LOG_FILE="health.log"
FAILED=0

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOG_FILE"; }

for path in / /about; do
  read -r code time < <(curl -s -o /dev/null -m 10 -w '%{http_code} %{time_total}' "$BASE_URL$path")
  if [ "$code" = "200" ]; then
    log "UP   $BASE_URL$path -> HTTP $code in ${time}s"
  else
    log "DOWN $BASE_URL$path -> HTTP ${code:-000}"
    FAILED=1
  fi
done

if [ "$FAILED" -eq 0 ]; then log "SUMMARY healthy ($BASE_URL)"; else log "SUMMARY UNHEALTHY ($BASE_URL)"; fi
exit $FAILED
