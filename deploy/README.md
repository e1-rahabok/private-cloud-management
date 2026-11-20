# Install the PCM prototype on a lab Linux VM

The prototype runs on synthetic ACME data. It does not connect to vCenter or VCF Operations, and it changes nothing in your lab. Every action on its pages acts on the synthetic data only.

## What it needs

- Linux with systemd, Python 3.9 or later, PyYAML, git.
- One TCP port reachable from the browsers that will use it (8080 by default).
- Nothing else. No database server, no web server, no internet access, unless you want live Agent E2 drafts through the AI gateway.

## Security, before you open the port

- **There is no sign-in yet.** Anyone who reaches the port can use every workspace and press every button. Limit the port to the lab network with the VM's firewall.
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

Each test line must say `OK`. Then open `http://<vm-address>:8080/exec` from a lab browser. The demo URLs are in [`../demo/README.md`](../demo/README.md).

## Open the firewall to the lab network only

With ufw, replacing the network with your lab's:

```bash
ufw allow from 192.168.10.0/24 to any port 8080 proto tcp
```

## Update

```bash
cd /opt/pcm && git pull && systemctl restart pcm
```

## Start clean

```bash
systemctl stop pcm && rm -f /var/lib/pcm/pcm.sqlite* && systemctl start pcm
```
