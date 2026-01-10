# LocalTranscribe GUI Build Script for Windows
# Run this from the project root directory

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Building LocalTranscribe GUI" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if running from project root
if (-Not (Test-Path "localtranscribe-gui")) {
    Write-Host "Error: Must run from project root directory" -ForegroundColor Red
    exit 1
}

# Step 1: Install dependencies
Write-Host "Step 1/3: Installing dependencies..." -ForegroundColor Blue
Set-Location localtranscribe-gui
pnpm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 2: Build frontend
Write-Host "Step 2/3: Building frontend..." -ForegroundColor Blue
pnpm build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build frontend" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Frontend built" -ForegroundColor Green
Write-Host ""

# Step 3: Build Tauri application
Write-Host "Step 3/3: Building Tauri application..." -ForegroundColor Blue
Write-Host "Note: This may take several minutes..." -ForegroundColor Yellow
pnpm tauri build --no-signing
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build Tauri application" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Tauri application built" -ForegroundColor Green
Write-Host ""

# Show output location
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ Build complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output files:"
Write-Host "  MSI:   src-tauri\target\release\bundle\msi\"
Write-Host "  NSIS:  src-tauri\target\release\bundle\nsis\"
Write-Host ""
Write-Host "To run the app:"
Write-Host "  .\src-tauri\target\release\LocalTranscribe.exe"
Write-Host ""
