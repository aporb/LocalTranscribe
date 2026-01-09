# LocalTranscribe Windows Installer
# PowerShell installation script for Windows
# Usage: .\install.ps1
#
# Based on Microsoft PowerShell best practices:
# https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell-on-windows

#Requires -Version 5.1

# Set strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Color functions for better UX
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green $args }
function Write-Info { Write-ColorOutput Cyan $args }
function Write-Warning { Write-ColorOutput Yellow $args }
function Write-Failure { Write-ColorOutput Red $args }

# Banner
Write-Info ""
Write-Info "╔════════════════════════════════════════════════════════╗"
Write-Info "║   LocalTranscribe Installer for Windows               ║"
Write-Info "║   Privacy-first audio transcription & diarization     ║"
Write-Info "╚════════════════════════════════════════════════════════╝"
Write-Info ""

# Step 1: Check Python version
Write-Info "→ Step 1/5: Checking Python installation..."
try {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        Write-Failure "✗ Python not found in PATH"
        Write-Info ""
        Write-Info "Please install Python 3.9 or higher:"
        Write-Info "  Option 1: Download from https://www.python.org/downloads/"
        Write-Info "  Option 2: Install via Microsoft Store"
        Write-Info "  Option 3: Use winget: winget install Python.Python.3.11"
        Write-Info ""
        Write-Info "Make sure to check 'Add Python to PATH' during installation!"
        exit 1
    }

    $pythonVersion = python --version 2>&1 | Out-String
    if ($pythonVersion -match "Python 3\.(\d+)") {
        $minorVersion = [int]$Matches[1]
        if ($minorVersion -lt 9) {
            Write-Failure "✗ Python 3.9+ required. Current: $pythonVersion"
            Write-Info "Please upgrade Python from https://www.python.org/downloads/"
            exit 1
        }
        Write-Success "✓ Python $pythonVersion detected"
    } else {
        Write-Failure "✗ Unable to determine Python version"
        exit 1
    }
} catch {
    Write-Failure "✗ Error checking Python: $_"
    exit 1
}

# Step 2: Check FFmpeg
Write-Info ""
Write-Info "→ Step 2/5: Checking FFmpeg installation..."
$ffmpegExists = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpegExists) {
    Write-Warning "⚠ FFmpeg not found in PATH"
    Write-Info ""
    Write-Info "FFmpeg is required for audio format conversion."
    Write-Info "Installation options:"
    Write-Info "  Option 1 (Recommended): choco install ffmpeg"
    Write-Info "  Option 2: scoop install ffmpeg"
    Write-Info "  Option 3: Download from https://ffmpeg.org/download.html"
    Write-Info "           and add to PATH manually"
    Write-Info ""

    $continue = Read-Host "Continue installation without FFmpeg? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Info "Installation cancelled. Please install FFmpeg and try again."
        exit 0
    }
    Write-Warning "⚠ Continuing without FFmpeg (some features may not work)"
} else {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-String -Pattern "ffmpeg version" | Select-Object -First 1
    Write-Success "✓ FFmpeg detected: $ffmpegVersion"
}

# Step 3: Create virtual environment
Write-Info ""
Write-Info "→ Step 3/5: Creating virtual environment..."
try {
    if (Test-Path ".venv") {
        Write-Warning "⚠ Virtual environment already exists"
        $recreate = Read-Host "Recreate virtual environment? (y/N)"
        if ($recreate -eq "y" -or $recreate -eq "Y") {
            Remove-Item -Recurse -Force .venv
            python -m venv .venv
            Write-Success "✓ Virtual environment recreated"
        } else {
            Write-Info "→ Using existing virtual environment"
        }
    } else {
        python -m venv .venv
        Write-Success "✓ Virtual environment created"
    }
} catch {
    Write-Failure "✗ Failed to create virtual environment: $_"
    exit 1
}

# Activate virtual environment
Write-Info "→ Activating virtual environment..."
$activateScript = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
    Write-Success "✓ Virtual environment activated"
} else {
    Write-Failure "✗ Activation script not found"
    exit 1
}

# Step 4: Install LocalTranscribe
Write-Info ""
Write-Info "→ Step 4/5: Installing LocalTranscribe..."
Write-Info "  This may take several minutes (downloading PyTorch, etc.)"
Write-Info ""

try {
    # Upgrade pip first
    python -m pip install --upgrade pip --quiet

    # Check for CUDA availability
    Write-Info "→ Detecting hardware acceleration..."
    $hasCuda = $false
    try {
        $nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
        if ($nvidiaSmi) {
            Write-Success "✓ NVIDIA GPU detected - installing with CUDA support"
            $hasCuda = $true
        } else {
            Write-Info "→ No NVIDIA GPU detected - installing CPU version"
        }
    } catch {
        Write-Info "→ Installing CPU version"
    }

    # Install with faster-whisper for better CPU performance
    Write-Info "→ Installing package (this will take 5-10 minutes)..."
    pip install -e ".[faster]" 2>&1 | ForEach-Object {
        if ($_ -match "Successfully installed") {
            Write-Success "✓ $_"
        } elseif ($_ -match "ERROR|error") {
            Write-Failure "✗ $_"
        }
    }

    Write-Success "✓ LocalTranscribe installed successfully"
} catch {
    Write-Failure "✗ Installation failed: $_"
    Write-Info ""
    Write-Info "Troubleshooting:"
    Write-Info "  1. Ensure you have a stable internet connection"
    Write-Info "  2. Try running PowerShell as Administrator"
    Write-Info "  3. Manually install: pip install -e .[faster]"
    exit 1
}

# Step 5: Configure HuggingFace token
Write-Info ""
Write-Info "→ Step 5/5: HuggingFace Configuration"
Write-Info ""
Write-Info "For speaker diarization, you need a free HuggingFace account token."
Write-Info ""
Write-Info "Setup instructions:"
Write-Info "  1. Visit: https://huggingface.co/settings/tokens"
Write-Info "  2. Click 'New token' and select 'Read' permissions"
Write-Info "  3. Accept required model licenses:"
Write-Info "     • https://huggingface.co/pyannote/speaker-diarization-3.1"
Write-Info "     • https://huggingface.co/pyannote/segmentation-3.0"
Write-Info ""

$skipToken = Read-Host "Do you have a HuggingFace token ready? (Y/n)"
if ($skipToken -eq "" -or $skipToken -eq "y" -or $skipToken -eq "Y") {
    $token = Read-Host "Enter your HuggingFace token (hidden)" -AsSecureString
    $tokenPlainText = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($token)
    )

    if ($tokenPlainText -and $tokenPlainText.Length -gt 0) {
        try {
            $envContent = "HUGGINGFACE_TOKEN=`"$tokenPlainText`"`n"
            $envContent | Out-File -FilePath ".env" -Encoding utf8 -NoNewline
            Write-Success "✓ Token saved to .env"

            # Validate token format
            if ($tokenPlainText -match "^hf_[a-zA-Z0-9]{20,}$") {
                Write-Success "✓ Token format looks valid"
            } else {
                Write-Warning "⚠ Token format may be invalid (should start with 'hf_')"
            }
        } catch {
            Write-Failure "✗ Failed to save token: $_"
        }
    } else {
        Write-Warning "⚠ No token entered - you can set it later"
    }
} else {
    Write-Info "→ Skipping token setup"
    Write-Info "  You can configure it later by running: localtranscribe init"
    Write-Info "  Or create a .env file with: HUGGINGFACE_TOKEN=your_token"
}

# Final steps
Write-Info ""
Write-Info "╔════════════════════════════════════════════════════════╗"
Write-Success "║              Installation Complete! 🎉                 ║"
Write-Info "╚════════════════════════════════════════════════════════╝"
Write-Info ""
Write-Info "Quick Start:"
Write-Info "  1. Make sure virtual environment is active:"
Write-Info "     .\.venv\Scripts\Activate.ps1"
Write-Info ""
Write-Info "  2. Run system health check:"
Write-Info "     localtranscribe doctor"
Write-Info ""
Write-Info "  3. Try transcribing an audio file:"
Write-Info "     localtranscribe audio.mp3"
Write-Info ""
Write-Info "  4. See example commands:"
Write-Info "     localtranscribe --help-examples"
Write-Info ""
Write-Info "Documentation: https://github.com/aporb/LocalTranscribe"
Write-Info ""

# Run health check if user wants
$runDoctor = Read-Host "Run system health check now? (Y/n)"
if ($runDoctor -eq "" -or $runDoctor -eq "y" -or $runDoctor -eq "Y") {
    Write-Info ""
    Write-Info "Running health check..."
    Write-Info ""
    localtranscribe doctor --verbose
}

Write-Info ""
Write-Success "Happy transcribing! 🎙️"
Write-Info ""
