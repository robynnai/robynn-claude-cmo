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
    else
        touch ".env"
    fi
fi

# Ensure bin/rory is executable
if [ -f "bin/rory" ]; then
    chmod +x bin/rory
fi

echo -e "  ${GREEN}✓${NC} Plugin files ready"

# ============================================================================
# API Key Configuration (shared by both Claude Code and Claude Desktop)
# ============================================================================

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Get your API key at: ${YELLOW}https://robynn.ai/settings/api-keys${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "Enter your Robynn API key (or press Enter to skip for now):"
read -r API_KEY

if [ -z "$API_KEY" ]; then
    API_KEY=""
    echo -e "  ${YELLOW}⚠${NC} Skipped - run 'rory init' later to configure"
else
    # Validate the API key
    echo -e "  ${YELLOW}Validating API key...${NC}"
    HTTP_STATUS=$(.venv/bin/python3 -c "
import httpx
try:
    r = httpx.get('https://robynn.ai/api/cli/context', headers={'Authorization': 'Bearer $API_KEY'}, timeout=10)
    print(r.status_code)
except:
    print('error')
" 2>/dev/null)
    
    if [ "$HTTP_STATUS" = "200" ]; then
        echo -e "  ${GREEN}✓${NC} API key validated"
    else
        echo -e "  ${YELLOW}⚠${NC} Could not validate key (will save anyway)"
    fi
fi

# ============================================================================
# Save API Key to Plugin .env (for Claude Code / rory CLI)
# ============================================================================

if [ -n "$API_KEY" ]; then
    # Update or add ROBYNN_API_KEY in .env
    if grep -q "^ROBYNN_API_KEY=" .env 2>/dev/null; then
        # Replace existing key
        sed -i.bak "s/^ROBYNN_API_KEY=.*/ROBYNN_API_KEY=$API_KEY/" .env && rm -f .env.bak
    else
        # Add new key
        echo "ROBYNN_API_KEY=$API_KEY" >> .env
    fi
    echo -e "  ${GREEN}✓${NC} Saved to plugin .env (for Claude Code)"
fi

# ============================================================================
# Claude Desktop Auto-Configuration
# ============================================================================

echo ""
echo -e "${YELLOW}Configuring Claude Desktop...${NC}"

# Detect Claude Desktop config location
if [[ "$OSTYPE" == "darwin"* ]]; then
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
    CLAUDE_CONFIG="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
    CLAUDE_CONFIG="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    CLAUDE_CONFIG_DIR="$APPDATA/Claude"
    CLAUDE_CONFIG="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
else
    echo -e "  ${YELLOW}⚠${NC} Could not detect Claude Desktop config location"
    CLAUDE_CONFIG=""
fi

# Function to configure Claude Desktop using Python
configure_claude_desktop() {
    local api_key="$1"
    
    .venv/bin/python3 << PYTHON_SCRIPT
import json
import os
import sys

config_path = "$CLAUDE_CONFIG"
install_dir = "$INSTALL_DIR"
api_key = "$api_key"

# Read existing config or create new one
config = {}
if os.path.exists(config_path):
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        config = {}

# Ensure mcpServers exists
if 'mcpServers' not in config:
    config['mcpServers'] = {}

# Add/update rory server
env_config = {}
if api_key and api_key != "":
    env_config['ROBYNN_API_KEY'] = api_key

config['mcpServers']['rory'] = {
    'command': os.path.join(install_dir, '.venv', 'bin', 'python'),
    'args': [os.path.join(install_dir, 'mcp_server.py')],
    'env': env_config
}

# Write config
os.makedirs(os.path.dirname(config_path), exist_ok=True)
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print('OK')
PYTHON_SCRIPT
}

if [ -n "$CLAUDE_CONFIG" ]; then
    # Check if Claude Desktop is installed
    if [ -d "$CLAUDE_CONFIG_DIR" ] || [ -f "$CLAUDE_CONFIG" ]; then
        echo -e "  ${GREEN}✓${NC} Found Claude Desktop config"
        
        # Configure Claude Desktop with the API key
        RESULT=$(configure_claude_desktop "$API_KEY")
        if [ "$RESULT" = "OK" ]; then
            echo -e "  ${GREEN}✓${NC} Claude Desktop configured"
        else
            echo -e "  ${RED}✗${NC} Failed to configure Claude Desktop"
        fi
    else
        echo -e "  ${YELLOW}⚠${NC} Claude Desktop not found - skipping"
        echo -e "      Install from: ${YELLOW}https://claude.ai/download${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} Skipping (unsupported OS)"
fi

# ============================================================================
# Success Message
# ============================================================================

echo ""
echo -e "${GREEN}┌─────────────────────────────────────────────────────────────────┐${NC}"
echo -e "${GREEN}│                    Installation complete!                       │${NC}"
echo -e "${GREEN}└─────────────────────────────────────────────────────────────────┘${NC}"
echo ""

if [ -n "$API_KEY" ]; then
    # API key was provided and saved
    echo -e "${GREEN}✓ Configured for:${NC}"
    echo -e "  • Claude Code (plugin .env)"
    if [ -n "$CLAUDE_CONFIG" ] && [ -d "$CLAUDE_CONFIG_DIR" ]; then
        echo -e "  • Claude Desktop (MCP server)"
        echo ""
        echo -e "${BLUE}Final step:${NC}"
        echo -e "  ${YELLOW}Restart Claude Desktop${NC} to load Rory"
    fi
    echo ""
    echo -e "${BLUE}Try these:${NC}"
    echo -e "  rory status                    ${GREEN}# Check connection${NC}"
    echo -e "  rory help                      ${GREEN}# See all commands${NC}"
    echo -e "  rory write linkedin-post       ${GREEN}# Create content${NC}"
else
    # API key was skipped
    echo -e "${YELLOW}Setup incomplete - no API key provided${NC}"
    echo ""
    echo -e "${BLUE}To finish setup, run:${NC}"
    echo -e "  ${YELLOW}rory init${NC}"
    echo ""
    echo -e "This will:"
    echo -e "  1. Open your browser to get an API key"
    echo -e "  2. Validate and save the key"
    echo -e "  3. Connect you to your Brand Hub"
fi

echo ""
echo -e "${BLUE}Documentation:${NC} ${YELLOW}https://robynn.ai/docs/rory${NC}"
echo -e "${BLUE}Get API key:${NC}   ${YELLOW}https://robynn.ai/settings/api-keys${NC}"
