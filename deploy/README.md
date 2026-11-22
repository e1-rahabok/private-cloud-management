# Install the PCM prototype on a lab Linux VM

The prototype runs on synthetic ACME data. It does not connect to vCenter or VCF Operations, and it changes nothing in your lab. Every action on its pages acts on the synthetic data only.

## What it needs

- Linux with systemd, Python 3.9 or later, PyYAML, git.
- One TCP port reachable from the browsers that will use it: 443 through nginx (section HTTPS with nginx), or 8080 for a quick trial without it.
- nginx, for HTTPS. PCM itself needs no database server and no internet access, unless you want Agent E2 through the AI gateway (section Agent E2).

## Security, before you open the port

- **There is no sign-in yet.** Anyone who reaches the port can use every workspace and press every button. Limit the port to the lab network with the VM's firewall.
- **Browsers reach PCM over HTTPS on 443, through nginx.** PCM speaks plain HTTP and has no TLS code. nginx ends TLS and forwards to PCM on `127.0.0.1:8080`. Port 8080 must not be reachable from the network (section HTTPS with nginx).
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
git clone https://github.com/e1-rahabok/private-cloud-management /opt/pcm
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
cd /opt/pcm && for t in executive noc l2 capacity store docs; do python3 -m unittest build.tests.test_$t 2>&1 | tail -1; done
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
- **Rule:** PCM listens on the loopback only. Port 8080 is never opened in the firewall.

Install nginx and put the certificate and key where nginx reads them (the lab's own CA, or a self-signed pair for a trial):

```bash
apt-get install -y nginx
```

```bash
install -d -m 750 /etc/nginx/pcm-tls   # then copy in pcm.crt and pcm.key; key mode 600, owned by root
```

Make PCM listen on the loopback only. In `/etc/pcm/pcm.env` set:

```
PCM_HOST=127.0.0.1
```

Create `/etc/nginx/sites-available/pcm`:

```nginx
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name _;

    ssl_certificate     /etc/nginx/pcm-tls/pcm.crt;
    ssl_certificate_key /etc/nginx/pcm-tls/pcm.key;
    ssl_protocols       TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
        proxy_read_timeout 120s;
    }
}
```

Enable it, test the file, reload:

```bash
ln -s /etc/nginx/sites-available/pcm /etc/nginx/sites-enabled/pcm && rm -f /etc/nginx/sites-enabled/default
```

```bash
nginx -t && systemctl reload nginx && systemctl restart pcm
```

Check it. The first must answer from PCM over HTTPS (`-k` skips trust of a self-signed certificate). The second must fail, because 8080 is loopback only:

```bash
curl -sk https://127.0.0.1/api/exec/summary | head -c 200
```

```bash
ss -ltn | grep 8080   # must show 127.0.0.1:8080, never 0.0.0.0:8080
```

This section describes the intended setup. If the lab VM's nginx file differs (server name, certificate paths, extra headers), the VM is the source of truth: copy its `/etc/nginx/sites-available/pcm` here so the two agree.

## Open the firewall to the lab network only

With ufw, replacing the network with your lab's. Open 443 and 80 (for the redirect), and nothing for 8080:

```bash
ufw allow from 192.168.10.0/24 to any port 443 proto tcp && ufw allow from 192.168.10.0/24 to any port 80 proto tcp
```

If an earlier install opened 8080, close it:

```bash
ufw delete allow from 192.168.10.0/24 to any port 8080 proto tcp
```

## Update

```bash
cd /opt/pcm && git pull && systemctl restart pcm
```

## Start clean

```bash
systemctl stop pcm && rm -f /var/lib/pcm/pcm.sqlite* && systemctl start pcm
```
