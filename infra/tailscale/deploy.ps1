$ErrorActionPreference = 'Stop'

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Docker is not installed or not on PATH.'
}
if (-not (Get-Command tailscale -ErrorAction SilentlyContinue)) {
    throw 'Tailscale is not installed or not on PATH.'
}
if (-not (Test-Path '.env')) {
    throw 'Create .env from .env.example before deployment.'
}

$required = @('N8N_ENCRYPTION_KEY', 'WEBHOOK_URL', 'N8N_EDITOR_BASE_URL')
$values = @{}
Get-Content '.env' | ForEach-Object {
    if ($_ -match '^([^#=]+)=(.*)$') {
        $values[$matches[1].Trim()] = $matches[2].Trim()
    }
}
foreach ($name in $required) {
    if (-not $values.ContainsKey($name) -or [string]::IsNullOrWhiteSpace($values[$name])) {
        throw "Missing required .env value: $name"
    }
}
if ($values['WEBHOOK_URL'] -notmatch '^https://[a-z0-9.-]+\.ts\.net/$') {
    throw 'WEBHOOK_URL must be the HTTPS Tailscale Funnel URL ending in a slash.'
}

docker compose -f docker-compose.local.yml up -d --build postgres n8n
$localHealth = Invoke-WebRequest 'http://127.0.0.1:5678/healthz' -UseBasicParsing -TimeoutSec 10
if ($localHealth.StatusCode -ne 200) {
    throw 'Local n8n health check failed.'
}

tailscale funnel --bg 5678
tailscale funnel status

$publicHealth = Invoke-WebRequest ($values['WEBHOOK_URL'] + 'healthz') -UseBasicParsing -TimeoutSec 20
if ($publicHealth.StatusCode -ne 200) {
    throw 'Public Funnel health check failed.'
}

Write-Host 'n8n is healthy locally and through Tailscale Funnel.'

