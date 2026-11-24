#!/usr/bin/env bash
# Update PCM and Agent E2 on the VM to the latest main, restart both services, check Agent E2 answers.
# Run on the VM:  sudo bash update-services.sh
# Overrides: E2_DIR, PCM_DIR, E2_UNIT, PCM_UNIT, E2_PORT.
set -euo pipefail

E2_DIR=${E2_DIR:-/opt/agent-e2}
PCM_DIR=${PCM_DIR:-/opt/pcm}
E2_UNIT=${E2_UNIT:-agent-e2}
PCM_UNIT=${PCM_UNIT:-pcm}
E2_PORT=${E2_PORT:-8090}

[ "$(id -u)" -eq 0 ] || { echo "Run as root: sudo bash $0" >&2; exit 1; }

for d in "$E2_DIR" "$PCM_DIR"; do
  git -C "$d" fetch -q origin main
  echo "== $d: $(git -C "$d" rev-parse --short HEAD) -> $(git -C "$d" rev-parse --short origin/main)"
  git -C "$d" pull --ff-only origin main
done

systemctl restart "$E2_UNIT" "$PCM_UNIT"

echo "Waiting for Agent E2 on port $E2_PORT (startup takes about 50 s)..."
body='{"facts":{"object":{"kind":"cluster"},"pillar":"Performance","window":"Last 24 hours","kpis":[]}}'
for _ in $(seq 1 30); do
  if out=$(curl -sf -X POST "localhost:$E2_PORT/v1/suggest" -H 'Content-Type: application/json' -d "$body"); then
    echo "OK: /v1/suggest answers: $out"
    systemctl is-active "$E2_UNIT" "$PCM_UNIT"
    echo "Now hard-refresh the browser (Ctrl+Shift+R)."
    exit 0
  fi
  sleep 5
done
echo "FAIL: /v1/suggest did not answer in 150 s. Check: journalctl -u $E2_UNIT -n 50 --no-pager" >&2
exit 1
