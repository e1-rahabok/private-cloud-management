# PCM prototype installation on a lab Linux VM

The prototype runs on synthetic ACME data. It does not connect to vCenter or VCF Operations, and it changes nothing in your lab. Every action on its pages acts on the synthetic data only.

## Prerequisites

- Linux with systemd, Python 3.9 or later, PyYAML, git.
- One TCP port reachable from the browsers that will use it: 443 through nginx (section HTTPS with nginx), or 8080 for a quick trial without it (set `PCM_HOST=0.0.0.0` in `/etc/pcm/pcm.env` for the trial only).
- nginx, for HTTPS. PCM itself needs no database server and no internet access, unless you want Agent E2 through the AI gateway (section Agent E2).

## Security, before you open the port

- **There is no sign-in yet.** Anyone who reaches the port can use every workspace and press every button. Limit the port to the lab network with the VM's firewall.
- **Browsers reach PCM over HTTPS on 443, through nginx.** PCM speaks plain HTTP and has no TLS code. nginx ends TLS and forwards to PCM on `127.0.0.1:8080`. On the lab VM, PCM also still listens on `0.0.0.0:8080`: plain HTTP from the network, without TLS. Close it once nothing needs it (section HTTPS with nginx, Close port 8080).
- `pcm.env.example` sets `PCM_HOST=127.0.0.1`, so a new install listens only inside the VM, behind nginx (R-LIVE-037).
- Turn on security updates: `apt install -y unattended-upgrades && dpkg-reconfigure -f noninteractive unattended-upgrades` (R-LIVE-037).
- The service runs as its own user, `pcm`, with write access only to `/var/lib/pcm`.
- The Agent E2 key, if used, lives in `/etc/pcm/pcm.env`, readable by root and the `pcm` group only.

## Install

Run as root, or with sudo. Debian and Ubuntu shown; on RHEL-family use `dnf install -y python3 python3-pyyaml git`.

```bash
apt-get update && apt-get install -y python3 python3-yaml git
```

```bash
useradd --system --home /opt/pcm --shell /usr/sbin/nologin pcm
```

```bash
git clone https://github.com/e1-rahabok/private-cloud-manager /opt/pcm
```

```bash
install -d -o pcm -g pcm -m 750 /var/lib/pcm && install -d -m 750 -g pcm /etc/pcm
```

```bash
install -m 640 -g pcm /opt/pcm/deploy/pcm.env.example /etc/pcm/pcm.env
```

```bash
cp /opt/pcm/deploy/pcm.service /etc/systemd/system/pcm.service && systemctl daemon-reload && systemctl enable --now pcm
```

## Check it

```bash
systemctl status pcm --no-pager
```

```bash
curl -s "http://127.0.0.1:8080/api/exec/summary?now=2026-10-19T10:05:00%2B08:00" | head -c 300
```

```bash
cd /opt/pcm && for t in core.tests.test_store executive.tests.test_executive noc.tests.test_noc l2.tests.test_l2 l2.tests.test_kpi_from_parts capacity.tests.test_capacity docs_workspace.tests.test_docs_workspace; do python3 -m unittest pcm.$t 2>&1 | tail -1; done
```

Each test line must say `OK`. Then open `https://<vm-address>/exec` from a lab browser (after section HTTPS with nginx; for a trial without nginx, `http://<vm-address>:8080/exec`). The demo URLs are in [`../demo/README.md`](../demo/README.md).

## Agent E2

Without this section, the E2 mark is grey and the Agent E2 panel says "The Agent E2 service is not available." PCM itself works.

- **What it is:** a second service on the same VM, from the Agent E2 repository. It holds the knowledge base and calls the model. PCM calls it on `127.0.0.1:8090`; it listens on the loopback only.
- **What it needs:** `python3-requests`, and in the lab a key for the AI gateway in `/etc/pcm/pcm.env`, as one line `AI_GATEWAY_API_KEY=vck_...` (Vercel: AI Gateway, API Keys; PCM and Agent E2 both read this name), with outbound HTTPS to `ai-gateway.vercel.sh`. A customer site points it at its local model server instead.

**One command** does all of the steps below and checks a real question. It asks for the key without showing it:

```bash
sudo bash /opt/pcm/deploy/install-agent-e2.sh   # or a saved copy: sudo bash install-agent-e2.sh
```

The same steps, by hand:

```bash
apt-get install -y python3-requests
```

```bash
git clone https://github.com/e1-rahabok/agent-e2 /opt/agent-e2
```

```bash
install -d -o pcm -g pcm -m 750 /opt/agent-e2/harness/.cache
```

Set `AI_GATEWAY_API_KEY=` in `/etc/pcm/pcm.env`, then:

```bash
cp /opt/pcm/deploy/agent-e2.service /etc/systemd/system/agent-e2.service && systemctl daemon-reload && systemctl enable --now agent-e2
```

```bash
systemctl restart pcm
```

The first start embeds the knowledge base, about 50 s. Then check the service, and PCM's view of it:

```bash
curl -s http://127.0.0.1:8090/v1/health
```

```bash
curl -s http://127.0.0.1:8080/api/l2/agent/health
```

Both must say the service is up (`"ok": true`, `"available": true`). In the browser the E2 mark turns dark with a green dot.

| The panel says | What is down | Fix |
|---|---|---|
| The Agent E2 service is not available. | The service: not installed, not started, or still starting | `systemctl status agent-e2 --no-pager`; wait 50 s after a start |
| Agent E2 is running, but its model cannot be reached. | The model: no key, a wrong key, or no route to the gateway | Check `AI_GATEWAY_API_KEY` in `/etc/pcm/pcm.env`, then `systemctl restart agent-e2`; `journalctl -u agent-e2 -n 20` |

Update it with PCM:

```bash
cd /opt/agent-e2 && git pull && systemctl restart agent-e2
```

## HTTPS with nginx

- **Design:** TLS ends at nginx, not in PCM. Browser to nginx on port 443 is encrypted. nginx to PCM on `127.0.0.1:8080` is plain HTTP inside the VM.
- **Why:** one place holds the certificate and its renewal. PCM stays free of key handling.
- **The lab VM, checked with `nginx -T` and `ss -ltn` on 2026-11-23:** nginx listens on 443 with TLS, certificate `/etc/ssl/certs/pcm.crt`, key `/etc/ssl/private/pcm.key`, and forwards to `http://127.0.0.1:8080`. Nothing listens on port 80. PCM listens on `0.0.0.0:8080`, so 8080 is still reachable over plain HTTP; `tools/lab/Test-Lab.ps1` checks both 443 and 8080.

Install nginx and put the certificate and key where the lab VM has them (the lab's own CA, or a self-signed pair for a trial). The key is mode 600, owned by root:

```bash
apt-get install -y nginx
```

Create `/etc/nginx/sites-available/pcm`. The `listen`, `ssl_certificate*` and `proxy_pass` lines are the lab VM's. The headers and the timeout are recommended; they are not confirmed on the VM. The timeout must exceed the 180 s PCM waits for Agent E2; a shorter one cuts the wait and the panel shows a gateway error:

```nginx
server {
    listen 443 ssl;
    server_name _;

    ssl_certificate     /etc/ssl/certs/pcm.crt;
    ssl_certificate_key /etc/ssl/private/pcm.key;
    ssl_protocols       TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
        proxy_read_timeout 200s;
    }
}
```

Enable it, test the file, reload:

```bash
ln -s /etc/nginx/sites-available/pcm /etc/nginx/sites-enabled/pcm && rm -f /etc/nginx/sites-enabled/default
```

```bash
nginx -t && systemctl reload nginx
```

Check it. It must answer from PCM over HTTPS (`-k` skips trust of a self-signed certificate):

```bash
curl -sk https://127.0.0.1/api/exec/summary | head -c 200
```

### Close port 8080 (recommended, not done on the lab VM yet)

Port 8080 serves the same pages without TLS. To close it, make PCM listen on the loopback only. In `/etc/pcm/pcm.env` set:

```
PCM_HOST=127.0.0.1
```

```bash
systemctl restart pcm
```

```bash
ss -ltn | grep 8080   # now 127.0.0.1:8080, no longer 0.0.0.0:8080
```

- Then drop the 8080 check from `tools/lab/Test-Lab.ps1`, which expects 8080 to answer.

This section follows the lab VM. If the VM's nginx file changes, the VM is the source of truth: copy its `/etc/nginx/sites-available/pcm` here so the two agree.

## Open the firewall to the lab network only

With ufw, replacing the network with your lab's. Open 443:

```bash
ufw allow from 10.20.0.0/24 to any port 443 proto tcp
```

While PCM still listens on `0.0.0.0:8080`, limit 8080 to the lab network too. Once it is closed (section Close port 8080), remove the rule:

```bash
ufw delete allow from 10.20.0.0/24 to any port 8080 proto tcp
```

## Update

```bash
cd /opt/pcm && git pull && cp deploy/pcm.service /etc/systemd/system/pcm.service && systemctl daemon-reload && systemctl restart pcm
```

The copy keeps the installed unit file the same as the repository's, whose `ExecStart` names the server module.

## Start clean

```bash
systemctl stop pcm && rm -f /var/lib/pcm/pcm.sqlite* && systemctl start pcm
```

## To do

Not urgent: the whole lab is behind a firewall (author, 2026-11-23).

- [ ] **Close port 8080 on the lab VM.** PCM still listens on `0.0.0.0:8080`, plain HTTP that bypasses TLS. Steps: section HTTPS with nginx, Close port 8080.
- [ ] **Drop the 8080 check from `tools/lab/Test-Lab.ps1`,** in the same change: it expects 8080 to answer, so it fails once 8080 is closed.
- [ ] **Remove the ufw rule for 8080,** if one exists (section Open the firewall to the lab network only).
- [ ] **Copy the lab VM's `/etc/nginx/sites-available/pcm` into section HTTPS with nginx.** The proxy headers and the timeout there are recommended, not yet confirmed on the VM.
