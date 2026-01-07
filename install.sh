#!/bin/bash
#
# Rory Installation Script
# Your CMO in the terminal
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/robynnai/robynn-claude-cmo/main/install.sh | bash
#
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

INSTALL_DIR="$HOME/.claude/skills/rory"
REPO_URL="https://github.com/robynnai/robynn-claude-cmo.git"

echo ""
echo -e "${BLUE}┌─────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│                                             │${NC}"
echo -e "${BLUE}│   ${GREEN}Installing Rory${BLUE}                          │${NC}"
echo -e "${BLUE}│   ${NC}Your CMO in the terminal${BLUE}                 │${NC}"
echo -e "${BLUE}│                                             │${NC}"
echo -e "${BLUE}└─────────────────────────────────────────────┘${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check for git
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed. Please install git first.${NC}"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} git"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed. Please install Python 3.9+ first.${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION"

# Check for Claude Code skills directory
CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
if [ ! -d "$CLAUDE_SKILLS_DIR" ]; then
    echo -e "${YELLOW}Creating Claude Code skills directory...${NC}"
    mkdir -p "$CLAUDE_SKILLS_DIR"
fi
echo -e "  ${GREEN}✓${NC} Claude Code skills directory"

# Install or update
echo ""
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Updating existing installation...${NC}"
    cd "$INSTALL_DIR"

    # Stash any local changes
    git stash --quiet 2>/dev/null || true

    # Pull latest
    git pull --quiet origin main 2>/dev/null || git pull --quiet origin master 2>/dev/null || {
        echo -e "${RED}Error: Failed to update. Try removing $INSTALL_DIR and reinstalling.${NC}"
        exit 1
    }

    echo -e "  ${GREEN}✓${NC} Updated to latest version"
else
    echo -e "${YELLOW}Cloning repository...${NC}"
    git clone --quiet "$REPO_URL" "$INSTALL_DIR" || {
        echo -e "${RED}Error: Failed to clone repository.${NC}"
        exit 1
    }
    echo -e "  ${GREEN}✓${NC} Repository cloned"
fi

# Install Python dependencies
echo ""
echo -e "${YELLOW}Installing Python dependencies...${NC}"
cd "$INSTALL_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Install requirements
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt

echo -e "  ${GREEN}✓${NC} Dependencies installed"

# Create .env from example if it doesn't exist
if [ ! -f "$INSTALL_DIR/.env" ]; then
    if [ -f "$INSTALL_DIR/.env.example" ]; then
        cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
        echo -e "  ${GREEN}✓${NC} Created .env file (needs configuration)"
    fi
fi

# Success message
echo ""
echo -e "${GREEN}┌─────────────────────────────────────────────┐${NC}"
echo -e "${GREEN}│                                             │${NC}"
echo -e "${GREEN}│   Installation complete!                    │${NC}"
echo -e "${GREEN}│                                             │${NC}"
echo -e "${GREEN}└─────────────────────────────────────────────┘${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo -e "  1. ${YELLOW}Get your API key:${NC}"
echo -e "     https://robynn.ai/settings/api-keys"
echo ""
echo -e "  2. ${YELLOW}Configure Rory:${NC}"
echo -e "     cd $INSTALL_DIR"
echo -e "     Edit .env and add your ROBYNN_API_KEY"
echo ""
echo -e "  3. ${YELLOW}Try it out in Claude Code:${NC}"
echo -e "     /rory write a linkedin post about our product"
echo ""
echo -e "${BLUE}Documentation:${NC} https://github.com/robynnai/robynn-claude-cmo"
echo ""
