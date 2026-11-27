# lab-vm-ssh.ps1 - key-based SSH to the lab VM, the host moltbot29.
#
# No passwords are stored or read here. Login uses the SSH key configured in
# ~/.ssh/config under the host alias below. BatchMode is on, so ssh never
# prompts: if key login is refused, the call fails at once with the reason.
#
# Usage (dot-source, then call):
#   . .\tools\lab-vm-ssh\lab-vm-ssh.ps1
#   Test-Moltbot                      # is key login working?
#   Invoke-Moltbot 'uptime'           # run one command on the host
#   Get-MoltbotSshdLog                # read the sshd log (needs passwordless sudo, see below)

$script:MoltbotAlias = 'moltbot29-iwan-claw'

function Invoke-Moltbot {
    param([Parameter(Mandatory)][string]$Command)
    # BatchMode and ConnectTimeout stop ssh from waiting on a prompt or a dead host.
    $lines = & ssh -o BatchMode=yes -o ConnectTimeout=10 $script:MoltbotAlias $Command 2>&1
    $code = $LASTEXITCODE
    $text = ($lines | Out-String).TrimEnd()
    if ($text -match 'Permission denied \(publickey') {
        throw "moltbot: key login refused by the host. Server-side fix needed (see Get-MoltbotSshdLog)."
    }
    [pscustomobject]@{ ExitCode = $code; Output = $text }
}

function Test-Moltbot {
    try {
        $r = Invoke-Moltbot 'echo moltbot-key-login-ok; hostname'
        if ($r.Output -match 'moltbot-key-login-ok') {
            "OK: key login works. Host: " + (($r.Output -split "`n")[-1].Trim())
            return $true
        }
        "FAILED: unexpected output: $($r.Output)"
        return $false
    } catch {
        "FAILED: $($_.Exception.Message)"
        return $false
    }
}

function Get-MoltbotSshdLog {
    # Needs the sudoers rule for this exact command on the host (see README in this folder).
    # sudo -n fails at once instead of prompting, so this never hangs.
    $cmd = 'sudo -n /usr/bin/journalctl -u ssh -u sshd -n 40 --no-pager'
    Invoke-Moltbot $cmd
}
