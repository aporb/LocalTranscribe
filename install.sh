#!/bin/bash
#
# LocalTranscribe Installation Script for macOS
#
# This script helps you install LocalTranscribe and all its dependencies.
# It will:
#   1. Check system requirements
#   2. Install Homebrew (if needed)
#   3. Install FFmpeg
#   4. Create Python virtual environment
#   5. Install Python dependencies
#   6. Set up configuration
#   7. Validate installation
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC}  $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC}  $1"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only."
    print_info "For other systems, please install dependencies manually."
    exit 1
fi

print_header "🎙️  LocalTranscribe Installation Script"

# Step 1: Check Python version
print_header "Step 1: Checking Python Version"

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed."
    print_info "Install Python 3.9+ from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    print_success "Python $PYTHON_VERSION (meets requirement: $REQUIRED_VERSION+)"
else
    print_error "Python $PYTHON_VERSION is too old (requires $REQUIRED_VERSION+)"
    print_info "Install Python 3.9+ from https://www.python.org/downloads/"
    exit 1
fi

# Step 2: Check/Install Homebrew
print_header "Step 2: Checking Homebrew"

if ! command -v brew &> /dev/null; then
    print_warning "Homebrew is not installed."
    read -p "Install Homebrew now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        print_success "Homebrew installed"
    else
        print_warning "Skipping Homebrew installation"
        print_info "You'll need to install FFmpeg manually"
    fi
else
    print_success "Homebrew is installed"
fi

# Step 3: Check/Install FFmpeg
print_header "Step 3: Checking FFmpeg"

if ! command -v ffmpeg &> /dev/null; then
    if command -v brew &> /dev/null; then
        print_info "Installing FFmpeg via Homebrew..."
        brew install ffmpeg
        print_success "FFmpeg installed"
    else
        print_error "FFmpeg is not installed and Homebrew is not available"
        print_info "Install FFmpeg from https://ffmpeg.org/download.html"
        exit 1
    fi
else
    print_success "FFmpeg is installed"
fi

# Step 4: Create Virtual Environment
print_header "Step 4: Setting Up Virtual Environment"

VENV_DIR="venv"

if [ -d "$VENV_DIR" ]; then
    print_warning "Virtual environment already exists at ./$VENV_DIR"
    read -p "Recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
        print_info "Creating new virtual environment..."
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    else
        print_info "Using existing virtual environment"
    fi
else
    print_info "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"
print_success "Virtual environment activated"

# Step 5: Upgrade pip
print_header "Step 5: Upgrading pip"

pip install --upgrade pip
print_success "pip upgraded"

# Step 6: Install LocalTranscribe
print_header "Step 6: Installing LocalTranscribe"

if [ -f "pyproject.toml" ]; then
    print_info "Installing LocalTranscribe in development mode..."
    pip install -e ".[dev]"
    print_success "LocalTranscribe installed (development mode)"
elif [ -f "requirements.txt" ]; then
    print_info "Installing from requirements.txt..."
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_error "No pyproject.toml or requirements.txt found"
    exit 1
fi

# Step 7: Install Optional Dependencies
print_header "Step 7: Installing Optional Dependencies"

print_info "Checking system architecture..."
ARCH=$(uname -m)

if [[ "$ARCH" == "arm64" ]]; then
    print_success "Apple Silicon (M1/M2/M3/M4) detected"
    print_info "Installing MLX-Whisper for optimal performance..."

    if pip install mlx-whisper mlx; then
        print_success "MLX-Whisper installed"
    else
        print_warning "Failed to install MLX-Whisper, but continuing..."
    fi
else
    print_info "Intel Mac detected"
    print_info "MLX-Whisper is not available for Intel Macs"
fi

# Offer to install additional Whisper implementations
read -p "Install faster-whisper? (recommended for CPU) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install faster-whisper
    print_success "faster-whisper installed"
fi

read -p "Install openai-whisper? (reference implementation) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install openai-whisper
    print_success "openai-whisper installed"
fi

# Step 8: Configure HuggingFace Token
print_header "Step 8: Configuring HuggingFace Token"

if [ -f ".env" ]; then
    print_info ".env file already exists"
    if grep -q "HUGGINGFACE_TOKEN" .env; then
        print_success "HuggingFace token is configured"
    else
        print_warning "HuggingFace token not found in .env"
    fi
else
    print_info "Creating .env file..."
    touch .env
fi

print_info "\nTo use speaker diarization, you need a HuggingFace token:"
print_info "1. Visit: https://huggingface.co/settings/tokens"
print_info "2. Create a token with 'read' access"
print_info "3. Accept the model license: https://huggingface.co/pyannote/speaker-diarization-3.1"
echo

read -p "Enter your HuggingFace token (or press Enter to skip): " HF_TOKEN

if [ -n "$HF_TOKEN" ]; then
    # Remove existing token if present
    sed -i.bak '/HUGGINGFACE_TOKEN/d' .env
    echo "HUGGINGFACE_TOKEN=$HF_TOKEN" >> .env
    print_success "HuggingFace token saved to .env"
else
    print_warning "Skipping HuggingFace token configuration"
    print_info "You can add it later to .env file: HUGGINGFACE_TOKEN=your_token"
    print_info "Or use --skip-diarization for transcription only"
fi

# Step 9: Create Directories
print_header "Step 9: Creating Directories"

mkdir -p input
mkdir -p output

print_success "Created ./input directory for audio files"
print_success "Created ./output directory for results"

# Step 10: Copy Example Config
print_header "Step 10: Setting Up Configuration"

if [ -f "config.yaml.example" ] && [ ! -f "localtranscribe.yaml" ]; then
    print_info "Copying example configuration..."
    cp config.yaml.example localtranscribe.yaml
    print_success "Created localtranscribe.yaml"
    print_info "You can edit this file to customize settings"
else
    print_info "Configuration file already exists or example not found"
fi

# Step 11: Validate Installation
print_header "Step 11: Validating Installation"

print_info "Running health check..."
echo

if localtranscribe doctor --verbose; then
    print_success "Health check passed!"
else
    print_warning "Health check found some issues"
    print_info "Review the output above for details"
fi

# Final Summary
print_header "🎉 Installation Complete!"

echo -e "${GREEN}LocalTranscribe has been installed successfully!${NC}\n"

echo "Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Place audio files in ./input directory"
echo "  3. Run: localtranscribe process input/your_audio.mp3"
echo ""
echo "For help:"
echo "  localtranscribe --help"
echo "  localtranscribe doctor          # Check system health"
echo "  localtranscribe config-show     # View configuration"
echo ""
echo "Documentation: https://github.com/yourusername/localtranscribe"
echo ""

print_info "The virtual environment is currently activated in this shell."
print_info "To deactivate, run: deactivate"
print_info "To activate later, run: source venv/bin/activate"

echo ""
