# SSH to the lab VM

`lab-vm-ssh.ps1` logs in to the lab VM, the host `moltbot29-iwan-claw` (10.114.1.29), with an SSH key, runs commands there and reads its sshd log. It holds no passwords.

## One-time host setup (needs the sudo password, run once)

This lets the `apollos` user read the sshd log without a password, and nothing else. Run it in a terminal and type the password when asked:

```powershell
ssh -t apollos@moltbot29-iwan-claw "echo 'apollos ALL=(root) NOPASSWD: /usr/bin/journalctl -u ssh -u sshd -n 40 --no-pager' | sudo tee /etc/sudoers.d/apollos-moltbot-log >/dev/null && sudo chmod 440 /etc/sudoers.d/apollos-moltbot-log && sudo visudo -cf /etc/sudoers.d/apollos-moltbot-log && sudo -n /usr/bin/journalctl -u ssh -u sshd -n 40 --no-pager | tail -n 5"
```

`visudo -cf` checks the rule before it takes effect. The last step runs the exact command without a password, so a success shows its last lines.

To remove the rule later:

```powershell
ssh -t apollos@moltbot29-iwan-claw "sudo rm /etc/sudoers.d/apollos-moltbot-log"
```

## Use

```powershell
. .\tools\lab-vm-ssh\lab-vm-ssh.ps1
Test-Moltbot              # key login
Get-MoltbotSshdLog        # sshd log, needs the host setup above
```
