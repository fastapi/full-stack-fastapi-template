# PowerShell version of SQLModel generation script

# Simple SQLModel generation script
# Read database configuration from .env file

# Stop on error
$ErrorActionPreference = "Stop"

Write-Host "Reading configuration from .env file..." -ForegroundColor Blue

# Read .env file
$envFile = "../../.env"
if (-not (Test-Path $envFile)) {
    Write-Error ".env file not found at $envFile"
    exit 1
}

# Parse .env file
$envVars = @{}
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^([^#][^=]*?)=(.*)$') {
        $envVars[$matches[1]] = $matches[2]
    }
}

if (-not $envVars.ContainsKey('DATABASE_SOURCE_DSN')) {
    Write-Error "DATABASE_SOURCE_DSN not found in .env file"
    exit 1
}

$databaseDsn = $envVars['DATABASE_SOURCE_DSN']

Write-Host "Executing sqlacodegen..." -ForegroundColor Blue
Write-Host "Command: uv run sqlacodegen --generator sqlmodels `"$databaseDsn`" --outfile ../app/generated_sqlmodels.py" -ForegroundColor Gray

# Execute sqlacodegen
uv run sqlacodegen --generator sqlmodels "$databaseDsn" --outfile ../app/generated_sqlmodels.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "SQLModel code generated successfully: ../app/generated_sqlmodels.py" -ForegroundColor Green
} else {
    Write-Error "Failed to generate SQLModel code"
    exit 1
}
