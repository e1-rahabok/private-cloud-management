#!/usr/bin/env bash
# Install the Agent E2 service next to PCM on a lab Linux VM, in one go (deploy/README.md, Agent E2).
# Run as root after PCM is installed:  sudo bash /opt/pcm/deploy/install-agent-e2.sh
# It asks for the AI gateway key without showing it, stores it in /etc/pcm/pcm.env (root and group pcm only),
# starts the service, and checks a real question through PCM. Safe to run again: it updates and restarts.
set -euo pipefail

ENV_FILE=/etc/pcm/pcm.env
E2_DIR=/opt/agent-e2
E2_REPO=https://github.com/e1-rahabok/agent-e2
UNIT_SRC=/opt/pcm/deploy/agent-e2.service

say() { printf '\n== %s\n' "$*"; }
fail() { printf '\nSTOPPED: %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || fail "run it as root: sudo bash $0"
[ -d /opt/pcm ] && id pcm >/dev/null 2>&1 || fail "PCM is not installed here. Install it first (deploy/README.md, Install)."
[ -f "$UNIT_SRC" ] || fail "$UNIT_SRC is missing. Update PCM first: cd /opt/pcm && git pull"
[ -f "$ENV_FILE" ] || fail "$ENV_FILE is missing. Install PCM first (deploy/README.md, Install)."

# Set or replace one KEY=value line in the env file. The value never goes through sed or the command line.
set_env() {
  local tmp; tmp=$(mktemp)
  KEY="$1" VAL="$2" awk 'BEGIN { k = ENVIRON["KEY"]; v = ENVIRON["VAL"]; done = 0 }
    index($0, k "=") == 1 { print k "=" v; done = 1; next } { print }
    END { if (!done) print k "=" v }' "$ENV_FILE" > "$tmp"
  cat "$tmp" > "$ENV_FILE"; rm -f "$tmp"
}

say "1/6 Python package"
if command -v apt-get >/dev/null; then apt-get install -y -q python3-requests >/dev/null
elif command -v dnf >/dev/null; then dnf install -y -q python3-requests >/dev/null
else fail "install python3-requests with your package manager, then run this again"; fi
python3 -c 'import requests, yaml' || fail "python3 cannot import requests and yaml"

say "2/6 Agent E2 code in $E2_DIR"
if [ -d "$E2_DIR/.git" ]; then git -C "$E2_DIR" pull -q --ff-only
else git clone -q "$E2_REPO" "$E2_DIR"; fi
install -d -o pcm -g pcm -m 750 "$E2_DIR/harness/.cache"

say "3/6 The AI gateway key"
current=$(grep -E '^AI_GATEWAY_API_KEY=.+' "$ENV_FILE" || true)
if [ -n "$current" ]; then
  read -r -p "A key is already set. Replace it? [y/N] " again
else
  again=y
fi
if [ "${again,,}" = y ]; then
  read -r -s -p "Paste the Vercel AI Gateway key (it is not shown), then Enter: " key; echo
  [ -n "$key" ] || fail "no key given"
  set_env AI_GATEWAY_API_KEY "$key"; unset key
fi
set_env PCM_AGENT_E2_URL "http://127.0.0.1:8090"
chown root:pcm "$ENV_FILE"; chmod 640 "$ENV_FILE"

say "4/6 Start the service"
cp "$UNIT_SRC" /etc/systemd/system/agent-e2.service
systemctl daemon-reload
systemctl enable -q agent-e2
systemctl restart agent-e2
systemctl restart pcm

say "5/6 Wait for it (the first start reads the knowledge base: up to 3 minutes)"
ok=""
for _ in $(seq 1 90); do
  if curl -fsS --max-time 2 http://127.0.0.1:8090/v1/health >/dev/null 2>&1; then ok=1; break; fi
  systemctl is-active -q agent-e2 || fail "the service stopped. See: journalctl -u agent-e2 -n 30 --no-pager"
  sleep 2
done
[ -n "$ok" ] || fail "no answer on port 8090 after 3 minutes. See: journalctl -u agent-e2 -n 30 --no-pager"
echo "Agent E2 answers its health check."

say "6/6 One real question through PCM (a local model or the gateway: 10 to 60 seconds)"
port=$(grep -E '^PCM_PORT=' "$ENV_FILE" | cut -d= -f2); port=${port:-8080}
for _ in $(seq 1 15); do curl -fsS --max-time 2 "http://127.0.0.1:$port/api/l2/agent/health" >/dev/null 2>&1 && break; sleep 2; done
src=$(curl -sS --max-time 180 -X POST "http://127.0.0.1:$port/api/l2/agent/ask" -H 'Content-Type: application/json' \
  -d '{"question":"What does a Guest OS run queue of 0.38 per vCPU mean?","context":{"kind":"page","object":"estate","pillar":"summary","window":"24h"}}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin).get("source","error"))' 2>/dev/null || echo error)
case "$src" in
  service) printf '\nDONE. Agent E2 answered. Reload PCM in the browser: the E2 mark is dark with a green dot.\n' ;;
  model_unavailable) fail "the service runs, but its model cannot be reached: check the key, and that this VM can reach ai-gateway.vercel.sh on HTTPS. Then run this script again." ;;
  *) fail "PCM did not get an answer ($src). See: journalctl -u agent-e2 -n 30 --no-pager" ;;
esac
