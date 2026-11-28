# SSH to the lab VM

`lab-vm-ssh.ps1` logs in to the lab VM with an SSH key, under the host alias that `$HOME\.secrets\lab.json` names (`vm_ssh_alias`; the file's shape is [lab.example.json](../lab/lab.example.json); DESIGN-9 in the workspace's [system design](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/design/system.md) keeps the lab's addresses and credentials out of every repository), runs commands there and reads its sshd log. It holds no passwords.

## One-time host setup (needs the sudo password, run once)

This lets the VM's user (`vm_user` in `lab.json`) read the sshd log without a password, and nothing else. Run it in a terminal and type the password when asked:

```powershell
. .\tools\lab\Lab-Config.ps1; $lab = Get-LabConfig; $u = $lab.vm_user
ssh -t "$u@$($lab.vm_ssh_alias)" "echo '$u ALL=(root) NOPASSWD: /usr/bin/journalctl -u ssh -u sshd -n 40 --no-pager' | sudo tee /etc/sudoers.d/$u-moltbot-log >/dev/null && sudo chmod 440 /etc/sudoers.d/$u-moltbot-log && sudo visudo -cf /etc/sudoers.d/$u-moltbot-log && sudo -n /usr/bin/journalctl -u ssh -u sshd -n 40 --no-pager | tail -n 5"
```

`visudo -cf` checks the rule before it takes effect. The last step runs the exact command without a password, so a success shows its last lines.

To remove the rule later:

```powershell
. .\tools\lab\Lab-Config.ps1; $lab = Get-LabConfig; $u = $lab.vm_user
ssh -t "$u@$($lab.vm_ssh_alias)" "sudo rm /etc/sudoers.d/$u-moltbot-log"
```

## Use

```powershell
. .\tools\lab-vm-ssh\lab-vm-ssh.ps1
Test-Moltbot              # key login
Get-MoltbotSshdLog        # sshd log, needs the host setup above
```
