#!/bin/bash
set -e

echo "================================"
echo "Building LocalTranscribe GUI"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from project root
if [ ! -d "localtranscribe-gui" ]; then
  echo "Error: Must run from project root directory"
  exit 1
fi

# Step 1: Install dependencies
echo -e "${BLUE}Step 1/3: Installing dependencies...${NC}"
cd localtranscribe-gui
pnpm install
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 2: Build frontend
echo -e "${BLUE}Step 2/3: Building frontend...${NC}"
pnpm build
echo -e "${GREEN}✓ Frontend built${NC}"
echo ""

# Step 3: Build Tauri application
echo -e "${BLUE}Step 3/3: Building Tauri application...${NC}"
echo -e "${YELLOW}Note: This may take several minutes...${NC}"
pnpm tauri build --no-signing
echo -e "${GREEN}✓ Tauri application built${NC}"
echo ""

# Show output location
echo "================================"
echo -e "${GREEN}✅ Build complete!${NC}"
echo "================================"
echo ""
echo "Output files:"
if [ "$(uname)" == "Darwin" ]; then
  echo "  macOS: src-tauri/target/release/bundle/dmg/"
  echo "  App:   src-tauri/target/release/bundle/macos/"
elif [ "$(uname)" == "Linux" ]; then
  echo "  AppImage: src-tauri/target/release/bundle/appimage/"
  echo "  deb:      src-tauri/target/release/bundle/deb/"
fi
echo ""
echo "To run the app:"
echo "  ./src-tauri/target/release/LocalTranscribe"
echo ""
