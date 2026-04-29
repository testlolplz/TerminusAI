#!/bin/bash

# TerminusAI Installer Script v1.1
# Created by: flint667 (Discord: flint667)
# GitHub: https://github.com/testlolplz/TerminusAI

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║         TerminusAI v1.1 Installer               ║"
echo "║      Your Terminal AI Companion                  ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running in Termux
if [[ ! -d /data/data/com.termux ]]; then
    echo -e "${RED}❌ This script is designed for Termux only!${NC}"
    echo -e "${YELLOW}Please install Termux from F-Droid first:${NC}"
    echo -e "${CYAN}https://f-droid.org/en/packages/com.termux/${NC}"
    exit 1
fi

# Check internet connection
echo -e "${YELLOW}📡 Checking internet connection...${NC}"
if ! ping -c 1 google.com > /dev/null 2>&1; then
    echo -e "${RED}❌ No internet connection detected!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Internet connection OK${NC}"

# Function to download with fallback
download_file() {
    local url=$1
    local output=$2
    
    if command -v curl > /dev/null 2>&1; then
        curl -s -o "$output" "$url" && return 0
    fi
    if command -v wget > /dev/null 2>&1; then
        wget -q -O "$output" "$url" && return 0
    fi
    if command -v python > /dev/null 2>&1; then
        python -c "import urllib.request; urllib.request.urlretrieve('$url', '$output')" 2>/dev/null && return 0
    fi
    return 1
}

echo -e "${YELLOW}[1/8] Updating packages...${NC}"
pkg update -y && pkg upgrade -y

echo -e "${YELLOW}[2/8] Installing Python...${NC}"
pkg install python -y

echo -e "${YELLOW}[3/8] Installing git...${NC}"
pkg install git -y

echo -e "${YELLOW}[4/8] Creating directories...${NC}"
mkdir -p ~/terminusai_chats
mkdir -p ~/terminusai_logs
mkdir -p ~/terminusai_backups
mkdir -p ~/terminusai_prompts

echo -e "${YELLOW}[5/8] Downloading TerminusAI v1.1...${NC}"

if [ -f ~/terminusai.py ]; then
    echo -e "${YELLOW}⚠ Backing up existing installation...${NC}"
    mv ~/terminusai.py ~/terminusai.py.bak.$(date +%Y%m%d_%H%M%S)
fi

if download_file "https://raw.githubusercontent.com/testlolplz/TerminusAI/main/terminusai.py" ~/terminusai.py; then
    echo -e "${GREEN}✓ TerminusAI v1.1 downloaded${NC}"
else
    echo -e "${RED}❌ Failed to download TerminusAI${NC}"
    echo -e "${YELLOW}You can manually download from:${NC}"
    echo -e "${CYAN}https://github.com/testlolplz/TerminusAI/blob/main/terminusai.py${NC}"
    exit 1
fi

echo -e "${YELLOW}[6/8] Setting permissions...${NC}"
chmod +x ~/terminusai.py

# Install Termux API for clipboard, notifications, TTS
echo -e "${YELLOW}[7/8] Installing Termux API...${NC}"
pkg install termux-api -y
echo -e "${GREEN}✓ Termux API installed${NC}"

# Ask about features
echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}📋 OPTIONAL FEATURES:${NC}"

# TTS
echo -e "${YELLOW}🎤 Enable Text-to-Speech? (y/N): ${NC}"
read -r install_tts
if [[ $install_tts == "y" || $install_tts == "Y" ]]; then
    echo -e "${GREEN}✓ TTS will be available (use /voice in chat)${NC}"
fi

# Notifications
echo -e "${YELLOW}🔔 Enable desktop notifications? (y/N): ${NC}"
read -r install_notify
if [[ $install_notify == "y" || $install_notify == "Y" ]]; then
    echo -e "${GREEN}✓ Notifications enabled (auto for long responses)${NC}"
fi

# API Key
echo -e "${YELLOW}🔑 Configure OpenRouter API key? (y/N): ${NC}"
read -r configure_key

if [[ $configure_key == "y" || $configure_key == "Y" ]]; then
    echo -e "${CYAN}Get your free key from: https://openrouter.ai/keys${NC}"
    echo -e "${YELLOW}Enter API key: ${NC}"
    read -r api_key
    if [[ -n "$api_key" ]]; then
        cat > ~/terminusai_config.json << JSONEOF
{
    "api_key": "$api_key",
    "model": "openrouter/free",
    "custom_prompt": "",
    "version": "1.1.0",
    "last_updated": "$(date -Iseconds)"
}
JSONEOF
        echo -e "${GREEN}✓ API key saved to ~/terminusai_config.json${NC}"
    fi
fi

# Create alias
echo -e "${YELLOW}⚡ Create 'terminusai' command alias? (y/N): ${NC}"
read -r create_alias

if [[ $create_alias == "y" || $create_alias == "Y" ]]; then
    if ! grep -q "alias terminusai=" ~/.bashrc 2>/dev/null; then
        echo "" >> ~/.bashrc
        echo "# TerminusAI Alias" >> ~/.bashrc
        echo "alias terminusai='python ~/terminusai.py'" >> ~/.bashrc
        echo -e "${GREEN}✓ Alias created!${NC}"
        echo -e "${YELLOW}Run 'source ~/.bashrc' to use it now, or restart Termux.${NC}"
    else
        echo -e "${GREEN}✓ Alias already exists.${NC}"
    fi
fi

echo -e "${YELLOW}[8/8] Installation complete!${NC}"

# Final message
echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║     ✅ TerminusAI v1.1 installed successfully!    ║"
echo "║                                                  ║"
echo "║  🚀 NEW FEATURES in v1.1:                        ║"
echo "║     📋 /copy, /paste - Clipboard support         ║"
echo "║     🎨 /imagine     - AI image generation        ║"
echo "║     🧮 /calc        - Smart calculator           ║"
echo "║     🔍 /findchat    - Search chat history        ║"
echo "║     📝 /summarize   - Context summarization      ║"
echo "║     🔄 Auto-update checker                      ║"
echo "║                                                  ║"
echo "║  🚀 To start: python ~/terminusai.py            ║"
if grep -q "alias terminusai=" ~/.bashrc 2>/dev/null; then
    echo "║  Or just type: terminusai                       ║"
fi
echo "║  📖 Type /help in chat for all commands         ║"
echo "║                                                  ║"
echo "║  📦 GitHub: https://github.com/testlolplz/TerminusAI"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# Offer to run
echo ""
echo -e "${CYAN}🚀 Start TerminusAI now? (y/N): ${NC}"
read -r run_now
if [[ $run_now == "y" || $run_now == "Y" ]]; then
    echo -e "${GREEN}Starting TerminusAI...${NC}"
    sleep 1
    python ~/terminusai.py
else
    echo -e "${YELLOW}You can start TerminusAI anytime by running:${NC}"
    echo -e "${CYAN}python ~/terminusai.py${NC}"
    if grep -q "alias terminusai=" ~/.bashrc 2>/dev/null; then
        echo -e "${CYAN}terminusai${NC}"
    fi
fi