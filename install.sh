#!/bin/bash

# TerminusAI Installer Script v1.0
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
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║         TerminusAI v1.0 Installer               ║"
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
    echo -e "${YELLOW}Please connect to the internet and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Internet connection OK${NC}"

# Function to download with fallback methods
download_file() {
    local url=$1
    local output=$2
    
    # Try curl
    if command -v curl > /dev/null 2>&1; then
        if curl -s -o "$output" "$url"; then
            return 0
        fi
    fi
    
    # Try wget
    if command -v wget > /dev/null 2>&1; then
        if wget -q -O "$output" "$url"; then
            return 0
        fi
    fi
    
    # Try python urllib
    if command -v python > /dev/null 2>&1; then
        if python -c "import urllib.request; urllib.request.urlretrieve('$url', '$output')" 2>/dev/null; then
            return 0
        fi
    fi
    
    return 1
}

echo -e "${YELLOW}[1/7] Updating packages...${NC}"
pkg update -y && pkg upgrade -y

echo -e "${YELLOW}[2/7] Installing Python...${NC}"
pkg install python -y

echo -e "${YELLOW}[3/7] Installing git...${NC}"
pkg install git -y

echo -e "${YELLOW}[4/7] Creating directories...${NC}"
mkdir -p ~/terminusai_chats
mkdir -p ~/terminusai_logs
mkdir -p ~/terminusai_backups
mkdir -p ~/terminusai_prompts

echo -e "${YELLOW}[5/7] Downloading TerminusAI...${NC}"

# Backup existing installation
if [ -f ~/terminusai.py ]; then
    echo -e "${YELLOW}⚠ Backing up existing installation...${NC}"
    mv ~/terminusai.py ~/terminusai.py.bak.$(date +%Y%m%d_%H%M%S)
fi

# Try multiple raw URLs (GitHub raw, alternative CDN)
DOWNLOAD_SUCCESS=false

# Primary URL
if download_file "https://raw.githubusercontent.com/testlolplz/TerminusAI/main/terminusai.py" ~/terminusai.py; then
    DOWNLOAD_SUCCESS=true
    echo -e "${GREEN}✓ Downloaded from primary source${NC}"
fi

# If primary fails, try alternative
if [ "$DOWNLOAD_SUCCESS" = false ]; then
    echo -e "${YELLOW}⚠ Primary download failed, trying alternative...${NC}"
    if download_file "https://raw.githubusercontent.com/testlolplz/TerminusAI/main/terminusai.py" ~/terminusai.py; then
        DOWNLOAD_SUCCESS=true
        echo -e "${GREEN}✓ Downloaded from alternative source${NC}"
    fi
fi

if [ "$DOWNLOAD_SUCCESS" = false ]; then
    echo -e "${RED}❌ Failed to download TerminusAI!${NC}"
    echo -e "${YELLOW}Please check your internet connection or try again later.${NC}"
    echo -e "${CYAN}You can also manually download from:${NC}"
    echo -e "${CYAN}https://github.com/testlolplz/TerminusAI/blob/main/terminusai.py${NC}"
    exit 1
fi

echo -e "${YELLOW}[6/7] Setting permissions...${NC}"
chmod +x ~/terminusai.py

# Verify the file downloaded correctly
if [ ! -s ~/terminusai.py ]; then
    echo -e "${RED}❌ Downloaded file is empty!${NC}"
    exit 1
fi

# Optional: Install Termux API for voice features
echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}🎤 Do you want to install Termux API for voice features?${NC}"
echo -e "${YELLOW}This enables text-to-speech functionality.${NC}"
echo -e "${CYAN}(y/N): ${NC}"
read -r install_api

if [[ $install_api == "y" || $install_api == "Y" ]]; then
    echo -e "${YELLOW}Installing Termux API...${NC}"
    pkg install termux-api -y
    echo -e "${GREEN}✓ Termux API installed!${NC}"
    echo -e "${YELLOW}Note: You may need to grant microphone permissions in Android settings.${NC}"
fi

# Get API key
echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}🔑 Do you want to configure your OpenRouter API key now?${NC}"
echo -e "${YELLOW}Get a free key from: https://openrouter.ai/keys${NC}"
echo -e "${CYAN}(y/N): ${NC}"
read -r configure_key

if [[ $configure_key == "y" || $configure_key == "Y" ]]; then
    echo -e "${YELLOW}Enter your OpenRouter API key:${NC}"
    read -r api_key
    if [[ -n "$api_key" ]]; then
        # Create config file
        cat > ~/terminusai_config.json << EOF
{
    "api_key": "$api_key",
    "model": "openrouter/free",
    "custom_prompt": "",
    "version": "1.0.0",
    "last_updated": "$(date -Iseconds)"
}
EOF
        echo -e "${GREEN}✓ API key saved to ~/terminusai_config.json${NC}"
    else
        echo -e "${YELLOW}⚠ No API key entered. You can configure it later in the app.${NC}"
    fi
fi

# Create alias
echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}⚡ Do you want to create a 'terminusai' command alias?${NC}"
echo -e "${YELLOW}This lets you run TerminusAI by typing 'terminusai'${NC}"
echo -e "${CYAN}(y/N): ${NC}"
read -r create_alias

if [[ $create_alias == "y" || $create_alias == "Y" ]]; then
    # Check if alias already exists
    if ! grep -q "alias terminusai=" ~/.bashrc; then
        echo "" >> ~/.bashrc
        echo "# TerminusAI Alias" >> ~/.bashrc
        echo "alias terminusai='python ~/terminusai.py'" >> ~/.bashrc
        echo -e "${GREEN}✓ Alias created!${NC}"
        echo -e "${YELLOW}Run 'source ~/.bashrc' to use it now, or restart Termux.${NC}"
    else
        echo -e "${GREEN}✓ Alias already exists.${NC}"
    fi
fi

# Final message
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗"
echo -e "║     ✅ TerminusAI installed successfully!         ║"
echo -e "║                                                  ║"
echo -e "║  🚀 To start TerminusAI, run:                    ║"
echo -e "║     ${WHITE}python ~/terminusai.py${GREEN}                       ║"
echo -e "║                                                  ║"
if grep -q "alias terminusai=" ~/.bashrc 2>/dev/null; then
    echo -e "║  Or just type: ${WHITE}terminusai${GREEN}                       ║"
    echo -e "║                                                  ║"
fi
echo -e "║  📝 Get your free API key at:                    ║"
echo -e "║     ${CYAN}https://openrouter.ai/keys${GREEN}                   ║"
echo -e "║                                                  ║"
echo -e "║  📖 Type ${WHITE}/help${GREEN} in chat for all commands       ║"
echo -e "║                                                  ║"
echo -e "║  💬 Need help? Discord: ${WHITE}flint667${GREEN}                ║"
echo -e "║  📦 GitHub: ${WHITE}https://github.com/testlolplz/TerminusAI${GREEN}"
echo -e "╚══════════════════════════════════════════════════╝${NC}"
echo ""

# Offer to run
echo -e "${CYAN}🚀 Do you want to start TerminusAI now? (y/N): ${NC}"
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