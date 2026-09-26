$ErrorActionPreference = "Stop"

# 1. Retrieve Infisical credentials
Import-Module "C:\scripts\deepseek4vibetools\shared\credential-manager\src\CredentialManager.psm1" -Force
$id = Get-Credential -Name "InfisicalAinovationID"
$sec = Get-Credential -Name "InfisicalAinovationSecret"

# 2. Login to Infisical
$body = @{ clientId = $id; clientSecret = $sec } | ConvertTo-Json
$res = Invoke-RestMethod -Uri "http://localhost:18181/api/v1/auth/universal-auth/login" -Method Post -Body $body -ContentType "application/json"
$vaultToken = $res.accessToken
$headers = @{ Authorization = "Bearer $vaultToken" }

# 3. Retrieve CF_PAGES_TOKEN
$secUrl = "http://localhost:18181/api/v3/secrets/raw/CF_PAGES_TOKEN?workspaceId=09f30673-98b3-4bb0-a341-e0bafaec9d2f&environment=prod"
$pagesToken = (Invoke-RestMethod -Uri $secUrl -Headers $headers).secret.secretValue
$cfHeaders = @{ Authorization = "Bearer $pagesToken"; "Content-Type" = "application/json" }
$accountId = "9042b346338fe50948c893402422a851"

# 4. Create Pages project 'promptforge' via REST API
Write-Host "[+] Creating Pages project 'promptforge' via REST API..." -ForegroundColor Yellow
$createUrl = "https://api.cloudflare.com/client/v4/accounts/$accountId/pages/projects"
$projectBody = @{
    name = "promptforge"
    production_branch = "main"
} | ConvertTo-Json

try {
    $createRes = Invoke-RestMethod -Uri $createUrl -Headers $cfHeaders -Method Post -Body $projectBody
    Write-Host "[✓] Pages project 'promptforge' created successfully!" -ForegroundColor Green
} catch {
    $err = $_.Exception.Response
    Write-Host "Project creation returned: $($_.Exception.Message)"
}

# 5. Deploy static bundle
Write-Host "[+] Deploying static bundle to 'promptforge'..." -ForegroundColor Yellow
$env:CLOUDFLARE_API_TOKEN = $pagesToken
$env:CLOUDFLARE_ACCOUNT_ID = $accountId
$distDir = "H:\03-services-and-infra\prompt-engineer\site\dist"
& npx -y wrangler pages deploy "$distDir" --project-name="promptforge" --branch="main" --commit-dirty=true

# 6. Bind custom domain 'promptforge.ainovation.top'
Write-Host "[+] Binding custom domain 'promptforge.ainovation.top'..." -ForegroundColor Yellow
$domainUrl = "https://api.cloudflare.com/client/v4/accounts/$accountId/pages/projects/promptforge/domains"
$domainBody = @{
    name = "promptforge.ainovation.top"
} | ConvertTo-Json
try {
    $domRes = Invoke-RestMethod -Uri $domainUrl -Headers $cfHeaders -Method Post -Body $domainBody
    Write-Host "[✓] Custom domain 'promptforge.ainovation.top' bound successfully!" -ForegroundColor Green
} catch {
    Write-Host "Domain binding note: $($_.Exception.Message)"
}
