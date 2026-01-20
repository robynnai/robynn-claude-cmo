#!/bin/bash
#
# Rory Installation Script
# Your CMO in the terminal
#
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect if we are running inside the repository or installing fresh
if [ -f "rory.py" ] && [ -d ".claude-plugin" ]; then
    # We are already in the plugin directory
    INSTALL_DIR=$(pwd)
    echo -e "${BLUE}Detected local installation in $INSTALL_DIR${NC}"
else
    # Fresh installation
    INSTALL_DIR="$HOME/.claude/skills/rory"
    REPO_URL="https://github.com/robynnai/robynn-claude-cmo.git"
    
    echo -e "${YELLOW}Cloning repository to $INSTALL_DIR...${NC}"
    if [ -d "$INSTALL_DIR" ]; then
        cd "$INSTALL_DIR"
        git pull --quiet origin main 2>/dev/null || true
    else
        mkdir -p "$(dirname "$INSTALL_DIR")"
        git clone --quiet "$REPO_URL" "$INSTALL_DIR"
    fi
    cd "$INSTALL_DIR"
fi

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed. Please install Python 3.9+ first.${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION"

# Install Python dependencies
echo -e "${YELLOW}Setting up virtual environment and dependencies...${NC}"

# Use uv if available for speed, otherwise standard venv
if command -v uv &> /dev/null; then
    echo -e "  Using ${BLUE}uv${NC} for faster installation"
    uv venv .venv --quiet
    uv pip install -r requirements.txt --quiet
else
    python3 -m venv .venv
    .venv/bin/pip install --quiet --upgrade pip
    .venv/bin/pip install --quiet -r requirements.txt
fi

echo -e "  ${GREEN}✓${NC} Dependencies installed"

# Create .env from example if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp ".env.example" ".env"
        echo -e "  ${GREEN}✓${NC} Created .env file (needs configuration)"
    fi
fi

# Ensure bin/rory is executable
if [ -f "bin/rory" ]; then
    chmod +x bin/rory
fi

echo ""
echo -e "${GREEN}┌─────────────────────────────────────────────┐${NC}"
echo -e "${GREEN}│   Installation complete!                    │${NC}"
echo -e "${GREEN}└─────────────────────────────────────────────┘${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Get your API key: ${YELLOW}https://robynn.ai/settings/api-keys${NC}"
echo -e "  2. Configure Rory:   ${YELLOW}rory config <your_api_key>${NC}"
echo ""
