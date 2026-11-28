# Lab-Config.ps1 - the lab's addresses and host names, read from $HOME\.secrets\lab.json (DESIGN-9).
#
# No repository holds them (R-WS-010 in the workspace). Copy tools\lab\lab.example.json to
# $HOME\.secrets\lab.json and put the lab's values in it. Dot-source this file, then call Get-LabConfig.

function Get-LabConfig {
    $path = Join-Path $HOME '.secrets\lab.json'
    if (-not (Test-Path $path)) {
        throw "No $path. Copy tools\lab\lab.example.json there and fill in the lab's addresses (DESIGN-9)."
    }
    $config = Get-Content -Raw $path | ConvertFrom-Json
    foreach ($key in 'vm_ssh_alias', 'vm_user', 'vm_host', 'vcf_operations_host', 'vcenter_host') {
        if (-not $config.$key) { throw "$path has no '$key'. See tools\lab\lab.example.json." }
    }
    $config
}
