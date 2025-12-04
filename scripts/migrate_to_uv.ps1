# Migration Script for Sik Sort - Switch from pip to UV
# This script helps existing users migrate from pip to UV

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Sik Sort - Migration to UV" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if UV is installed
Write-Host "Checking for UV installation..." -ForegroundColor Yellow
$uvInstalled = Get-Command uv -ErrorAction SilentlyContinue

if (-not $uvInstalled) {
    Write-Host "UV is not installed. Installing UV..." -ForegroundColor Yellow
    try {
        Invoke-Expression "& { $(Invoke-RestMethod https://astral.sh/uv/install.ps1) }"
        Write-Host "UV installed successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to install UV. Please install manually:" -ForegroundColor Red
        Write-Host "powershell -c `"irm https://astral.sh/uv/install.ps1 | iex`"" -ForegroundColor White
        exit 1
    }
}
else {
    Write-Host "UV is already installed." -ForegroundColor Green
}

Write-Host ""

# Check if in virtual environment
if ($env:VIRTUAL_ENV) {
    Write-Host "You are currently in a virtual environment." -ForegroundColor Yellow
    Write-Host "Deactivating..." -ForegroundColor Yellow
    deactivate
}

# Check if .venv exists
if (Test-Path ".venv") {
    Write-Host "Found existing .venv directory." -ForegroundColor Yellow
    $response = Read-Host "Do you want to remove it and create a new one with UV? (y/n)"
    
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "Removing old .venv..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force .venv
        Write-Host "Old .venv removed." -ForegroundColor Green
    }
    else {
        Write-Host "Keeping existing .venv. You can manually remove it later." -ForegroundColor Yellow
        Write-Host "Migration cancelled." -ForegroundColor Red
        exit 0
    }
}

Write-Host ""
Write-Host "Creating new virtual environment with UV..." -ForegroundColor Yellow
uv venv

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to create virtual environment." -ForegroundColor Red
    exit 1
}

Write-Host "Virtual environment created successfully!" -ForegroundColor Green
Write-Host ""

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

Write-Host "Installing Sik Sort with development dependencies..." -ForegroundColor Yellow
uv pip install -e ".[dev]"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install dependencies." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host "Migration Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run tests to verify: uv run pytest" -ForegroundColor White
Write-Host "2. Try the application: sik --help" -ForegroundColor White
Write-Host "3. Check out UV_QUICK_REFERENCE.md for UV commands" -ForegroundColor White
Write-Host ""
Write-Host "Your virtual environment is now active!" -ForegroundColor Green
