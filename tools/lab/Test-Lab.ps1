# Test-Lab.ps1 - checks every lab access path used from this laptop.
# Reads each password from Windows Credential Manager and never prints it.
#
#   pwsh -NoProfile -File tools\lab\Test-Lab.ps1
#
# The lab's addresses come from $HOME\.secrets\lab.json (tools\lab\Lab-Config.ps1, DESIGN-9).
#
# Checks: the lab VM's key login and sudo log, VCF Operations login, vCenter login,
# the PCM pages on the VM over https 443, and the VM's hardening (T-LIVE-037a): 8080 and 8090 refused from the
# network and bound to 127.0.0.1 only, and unattended upgrades enabled.

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
. (Join-Path $root 'lab\Lab-Config.ps1')
. (Join-Path $root 'lab-vm-ssh\lab-vm-ssh.ps1')
$lab = Get-LabConfig

Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices;
public class LabCred {
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct CREDENTIAL {
        public int Flags; public int Type; public string TargetName; public string Comment;
        public long LastWritten; public int CredentialBlobSize; public IntPtr CredentialBlob;
        public int Persist; public int AttributeCount; public IntPtr Attributes;
        public string TargetAlias; public string UserName;
    }
    [DllImport("advapi32.dll", EntryPoint = "CredReadW", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern bool CredRead(string target, int type, int flags, out IntPtr cred);
    [DllImport("advapi32.dll")] public static extern void CredFree(IntPtr cred);
    public static string[] Read(string target) {
        IntPtr p;
        if (!CredRead(target, 1, 0, out p)) return null;
        CREDENTIAL c = (CREDENTIAL)Marshal.PtrToStructure(p, typeof(CREDENTIAL));
        string pw = Marshal.PtrToStringUni(c.CredentialBlob, c.CredentialBlobSize / 2);
        string user = c.UserName;
        CredFree(p);
        return new string[] { user, pw };
    }
}
"@

$results = [System.Collections.Generic.List[object]]::new()
function Add-Result($name, $ok, $detail) {
    $results.Add([pscustomobject]@{ Check = $name; Result = $(if ($ok) { 'PASS' } else { 'FAIL' }); Detail = $detail })
}

# 1. The lab VM: key login, then the sudo log
try {
    $r = Invoke-Moltbot 'echo moltbot-ok; hostname'
    $ok = $r.Output -match 'moltbot-ok'
    Add-Result 'Lab VM key login' $ok ($(if ($ok) { 'key-only login works' } else { $r.Output }))
    $log = Get-MoltbotSshdLog
    Add-Result 'Lab VM sshd log (sudo)' ($log.ExitCode -eq 0) ("exit " + $log.ExitCode)
} catch {
    Add-Result 'Lab VM key login' $false $_.Exception.Message
}

# 2. VCF Operations: token from the suite API (credential target https://<its host>/)
$vcfHost = $lab.vcf_operations_host
$cred = [LabCred]::Read("https://$vcfHost/")
if ($null -eq $cred) {
    Add-Result 'VCF Operations login' $false 'no credential in Credential Manager'
} else {
    try {
        $body = @{ username = $cred[0]; password = $cred[1] } | ConvertTo-Json -Compress
        $cred = $null
        $resp = Invoke-RestMethod -Method Post -Uri "https://$vcfHost/suite-api/api/auth/token/acquire" `
            -Body $body -ContentType 'application/json' -Headers @{ Accept = 'application/json' } `
            -SkipCertificateCheck -TimeoutSec 30
        $body = $null
        Add-Result 'VCF Operations login' ([bool]$resp.token) ("token issued, expires " + $resp.expiresAt)
    } catch {
        $cred = $null
        Add-Result 'VCF Operations login' $false ("HTTP " + $_.Exception.Response.StatusCode.value__)
    }
}

# 3. vCenter: session from the REST API. The stored target carries the helper's suffix.
$vcHost = $lab.vcenter_host
$cred = [LabCred]::Read("administrator@vsphere.local@$vcHost.dbh-insights-helper")
if ($null -eq $cred) {
    Add-Result 'vCenter login' $false 'no credential in Credential Manager'
} else {
    try {
        # The helper stores the user as user@host; vCenter needs just user@domain.
        $user = $cred[0] -replace "@$([regex]::Escape($vcHost))$", ''
        $basic = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($user + ':' + $cred[1])))
        $cred = $null
        $session = Invoke-RestMethod -Method Post -Uri "https://$vcHost/api/session" `
            -Headers @{ Authorization = "Basic $basic" } -SkipCertificateCheck -TimeoutSec 30
        $basic = $null
        Add-Result 'vCenter login' ([bool]$session) 'session created'
    } catch {
        $cred = $null
        Add-Result 'vCenter login' $false ("HTTP " + $_.Exception.Response.StatusCode.value__)
    }
}

# 4. PCM on the VM: pages over https 443
$pages = '/exec', '/noc/wall', '/noc', '/l2', '/capacity', '/docs'
$clock = '?now=2026-10-19T10:05:00%2B08:00'
$base = "https://$($lab.vm_host)"
$codes = foreach ($p in $pages) {
    curl.exe -sk -o NUL -w "%{http_code}" --max-time 10 ($base + $p + $clock)
}
$ok = (@($codes | Where-Object { $_ -eq '200' }).Count -eq $pages.Count)
Add-Result 'PCM pages over https 443' $ok ("codes: " + ($codes -join ' '))

# 5. The VM's hardening (R-LIVE-037, T-LIVE-037a): PCM and Agent E2 answer only inside the VM; security updates on
foreach ($port in 8080, 8090) {
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 5 ("http://$($lab.vm_host):$port/")
    Add-Result "Port $port refused from the network" ($code -eq '000') ("http code: " + $code)
}
try {
    $r = Invoke-Moltbot "ss -ltnH | awk '{print `$4}' | grep -E ':(8080|8090)$'"
    $open = @(($r.Output -split "`n") | Where-Object { $_ -and $_ -notmatch '^127\.0\.0\.1:' })
    Add-Result 'PCM and Agent E2 listen on 127.0.0.1 only' ($open.Count -eq 0 -and $r.Output) ("listening: " + (($r.Output -split "`n") -join ' '))
    $u = Invoke-Moltbot 'systemctl is-enabled unattended-upgrades 2>&1'
    Add-Result 'Unattended upgrades enabled' ($u.Output.Trim() -eq 'enabled') $u.Output.Trim()
} catch {
    Add-Result 'VM hardening read over SSH' $false $_.Exception.Message
}

$results | Format-Table -AutoSize -Wrap | Out-String -Width 200
$failed = @($results | Where-Object { $_.Result -eq 'FAIL' }).Count
"$($results.Count - $failed) of $($results.Count) checks passed"
if ($failed -gt 0) { exit 1 }
