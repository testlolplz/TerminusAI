#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║                         TERMINUS AI v1.1                          ║
║                   Your Terminal AI Companion                      ║
║                                                                   ║
║                      Created by: flint667                         ║
║                         Discord: flint667                         ║
║                                                                   ║
║           ⚡ Free & Open Source AI Assistant for Termux          ║
║                                                                   ║
║  This is a SELF-CONTAINED file - just run it!                    ║
║  It will automatically install dependencies on first run.        ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import subprocess
import json
import time

# ==================== AUTO-INSTALLER ====================
def check_and_install_dependencies():
    """Automatically check and install required packages on first run"""
    
    required_packages = ['python', 'git']
    optional_packages = ['termux-api']
    missing = []
    
    print("\033[36m")
    print("╔══════════════════════════════════════════════════╗")
    print("║         TerminusAI - First Time Setup           ║")
    print("║      Checking and installing dependencies       ║")
    print("╚══════════════════════════════════════════════════╝")
    print("\033[0m")
    
    # Check if running in Termux
    if not os.path.exists('/data/data/com.termux'):
        print("\033[91m❌ This script is designed for Termux only!\033[0m")
        print("Please install Termux from F-Droid first.")
        sys.exit(1)
    
    # Check internet
    print("\033[93m📡 Checking internet connection...\033[0m")
    try:
        import urllib.request
        urllib.request.urlopen('https://google.com', timeout=5)
        print("\033[92m✓ Internet connected\033[0m")
    except:
        print("\033[91m❌ No internet connection!\033[0m")
        sys.exit(1)
    
    # Update packages
    print("\n\033[93m[1/4] Updating packages...\033[0m")
    subprocess.run(['pkg', 'update', '-y'], capture_output=True)
    subprocess.run(['pkg', 'upgrade', '-y'], capture_output=True)
    print("\033[92m✓ Packages updated\033[0m")
    
    # Install Python and git if needed
    print("\n\033[93m[2/4] Installing required packages...\033[0m")
    for pkg in required_packages:
        result = subprocess.run(['pkg', 'install', pkg, '-y'], capture_output=True)
        if result.returncode == 0:
            print(f"\033[92m✓ {pkg} installed\033[0m")
        else:
            print(f"\033[93m⚠ {pkg} may already be installed\033[0m")
    
    # Ask about optional Termux API
    print("\n\033[95m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
    print("\033[96m📋 OPTIONAL FEATURES:\033[0m")
    print("\033[93m🎤 Install Termux API for clipboard, notifications & TTS? (y/N): \033[0m")
    install_api = input().strip().lower()
    
    if install_api == 'y':
        print("\n\033[93m[3/4] Installing Termux API...\033[0m")
        subprocess.run(['pkg', 'install', 'termux-api', '-y'], capture_output=True)
        print("\033[92m✓ Termux API installed\033[0m")
        print("\033[93m⚠ You also need to install Termux:API app from F-Droid!\033[0m")
    
    # Create directories
    print("\n\033[93m[4/4] Creating directories...\033[0m")
    for dir_name in ['terminusai_chats', 'terminusai_logs', 'terminusai_backups', 'terminusai_prompts']:
        os.makedirs(os.path.expanduser(f"~/{dir_name}"), exist_ok=True)
    print("\033[92m✓ Directories created\033[0m")
    
    # Ask for API key
    print("\n\033[95m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
    print("\033[96m🔑 OpenRouter API Key Configuration:\033[0m")
    print("\033[93mGet your free key from: https://openrouter.ai/keys\033[0m")
    print("\033[96mEnter your API key (or press Enter to skip for now): \033[0m")
    api_key = input().strip()
    
    if api_key:
        config = {
            "api_key": api_key,
            "model": "openrouter/free",
            "custom_prompt": "",
            "version": "1.1.0",
            "last_updated": datetime.now().isoformat()
        }
        with open(os.path.expanduser("~/terminusai_config.json"), 'w') as f:
            json.dump(config, f, indent=2)
        print("\033[92m✓ API key saved!\033[0m")
    
    # Create alias
    print("\n\033[95m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
    print("\033[96m⚡ Create 'terminusai' command alias? (y/N): \033[0m")
    create_alias = input().strip().lower()
    
    if create_alias == 'y':
        bashrc = os.path.expanduser("~/.bashrc")
        with open(bashrc, 'a') as f:
            f.write("\n# TerminusAI Alias\n")
            f.write("alias terminusai='python ~/terminusai.py'\n")
        print("\033[92m✓ Alias created! Run 'source ~/.bashrc' to use it.\033[0m")
    
    print("\n\033[92m✅ Setup complete! Launching TerminusAI...\033[0m")
    time.sleep(2)

# ==================== ACTUAL TERMINUSAI CODE ====================
import urllib.request
import urllib.parse
import http.client
import threading
import re
import secrets
import string
import tempfile
from datetime import datetime

VERSION = "1.1.0"
APP_NAME = "TerminusAI"
AUTHOR = "flint667"
REPO_URL = "https://github.com/testlolplz/TerminusAI"

# Global variables
API_KEY = ""
HISTORY = []
CURRENT_MODEL = "openrouter/free"
CUSTOM_PROMPT = ""
CONFIG_FILE = os.path.expanduser(f"~/{APP_NAME.lower()}_config.json")
CHATS_DIR = f"{APP_NAME.lower()}_chats"
LOGS_DIR = f"{APP_NAME.lower()}_logs"
BACKUP_DIR = f"{APP_NAME.lower()}_backups"
PROMPTS_DIR = f"{APP_NAME.lower()}_prompts"

def clear():
    os.system('clear')

def load_config():
    global API_KEY, CURRENT_MODEL, CUSTOM_PROMPT
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                API_KEY = config.get('api_key', '')
                CURRENT_MODEL = config.get('model', 'openrouter/free')
                CUSTOM_PROMPT = config.get('custom_prompt', '')
        except:
            pass

def save_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump({
            'api_key': API_KEY,
            'model': CURRENT_MODEL,
            'custom_prompt': CUSTOM_PROMPT,
            'version': VERSION,
            'last_updated': datetime.now().isoformat()
        }, f, indent=2)

def get_rgb(r, g, b):
    return f'\033[38;2;{r};{g};{b}m'

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def print_header():
    tw = os.get_terminal_size().columns
    lines = [
        "╔══════════════════════════════════════════════════╗",
        f"║           {APP_NAME} v{VERSION}                    ║",
        "║      Your Terminal AI Companion                  ║",
        "╚══════════════════════════════════════════════════╝"
    ]
    print("\n")
    for line in lines:
        pad = (tw - len(line)) // 2
        print(" " * max(0, pad) + get_rgb(100, 150, 255) + line + '\033[0m')

def highlight_code(text):
    pattern = r'```(\w+)?\n(.*?)```'
    def replace_code(match):
        lang = match.group(1) or 'text'
        code = match.group(2)
        return f"\n{get_rgb(100, 255, 100)}┌─[{lang.upper()}]─────────────────┐\n{get_rgb(200, 200, 0)}{code}\n{get_rgb(100, 255, 100)}└────────────────────────────────┘\033[0m"
    return re.sub(pattern, replace_code, text, flags=re.DOTALL)

def copy_to_clipboard(text):
    try:
        if len(text) > 5000:
            text = text[:5000] + "\n... (truncated)"
        subprocess.run(['termux-clipboard-set', text], timeout=2, capture_output=True)
        return f"📋 Copied ({len(text)} chars)"
    except:
        return "❌ Clipboard failed (install Termux:API)"

def paste_from_clipboard():
    try:
        result = subprocess.run(['termux-clipboard-get'], capture_output=True, text=True, timeout=2)
        if result.stdout:
            return f"📋 Clipboard:\n\n{result.stdout[:2000]}"
        return "📋 Clipboard empty"
    except:
        return "❌ Paste failed (install Termux:API)"

def generate_image(prompt):
    try:
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}"
        filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        print(f"\033[92m🎨 Generating image...\033[0m")
        urllib.request.urlretrieve(url, filename)
        if os.path.exists(filename) and os.path.getsize(filename) > 1000:
            try:
                subprocess.run(['termux-open', filename], timeout=2, capture_output=True)
                return f"✅ Image saved: {filename}"
            except:
                return f"✅ Image saved: {os.path.abspath(filename)}"
        return "❌ Failed to generate image"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def smart_calc(expression):
    try:
        expression = expression.replace(" ", "")
        import math
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        allowed.update({"abs": abs, "round": round})
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"🧮 {expression} = {result}"
    except:
        return "❌ Invalid expression"

def web_search(query):
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            results = re.findall(r'<a rel="nofollow" class="result__a" href="[^"]*">([^<]+)</a>', html)
            output = f"🔍 Results for '{query}':\n\n"
            for i, title in enumerate(results[:5], 1):
                output += f"{i}. {title}\n"
            return output if results else "No results"
    except:
        return "❌ Search failed"

def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=%C:+%t,+%w"
        with urllib.request.urlopen(url, timeout=10) as response:
            weather = response.read().decode('utf-8').strip()
            return f"🌤️ {city}: {weather}"
    except:
        return "❌ Weather failed"

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(chars) for _ in range(length))
    strength = "Strong" if length >= 12 else "Medium" if length >= 8 else "Weak"
    return f"🔐 Password: {password}\nStrength: {strength}"

def save_chat():
    if not HISTORY:
        return "No conversation to save"
    name = input("Session name (Enter for auto): ").strip()
    if not name:
        name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(CHATS_DIR, exist_ok=True)
    with open(f"{CHATS_DIR}/{name}.json", 'w') as f:
        json.dump({'history': HISTORY, 'timestamp': datetime.now().isoformat()}, f, indent=2)
    return f"✓ Saved: {name}"

def load_chat():
    global HISTORY
    if not os.path.exists(CHATS_DIR):
        return "No saved chats"
    sessions = [f.replace('.json', '') for f in os.listdir(CHATS_DIR) if f.endswith('.json')]
    if not sessions:
        return "No saved chats"
    print("\n📂 Available sessions:")
    for i, s in enumerate(sessions, 1):
        print(f"  {i}. {s}")
    try:
        choice = int(input("\nSelect: ")) - 1
        if 0 <= choice < len(sessions):
            with open(f"{CHATS_DIR}/{sessions[choice]}.json", 'r') as f:
                data = json.load(f)
                HISTORY = data.get('history', [])
            return f"✓ Loaded {len(HISTORY)//2} exchanges"
    except:
        pass
    return "Cancelled"

def ai_chat():
    global API_KEY, HISTORY, CURRENT_MODEL, CUSTOM_PROMPT
    
    if not API_KEY:
        print("\n\033[91m❌ No API key! Configure it in Settings (option 3)\033[0m")
        input("\nPress Enter...")
        return
    
    default_prompt = "You are a helpful AI assistant for Termux. Be concise and helpful."
    system_prompt = CUSTOM_PROMPT if CUSTOM_PROMPT else default_prompt
    
    while True:
        clear()
        print_header()
        tw = os.get_terminal_size().columns
        
        print(f"\n\033[96mModel: {CURRENT_MODEL[:40]}\033[0m")
        print(f"\033[93mHistory: {len(HISTORY)//2} exchanges\033[0m")
        print("\n" + "─" * tw)
        print("\033[92mYou: \033[0m", end="")
        user_input = input()
        
        if not user_input.strip():
            continue
        
        # Commands
        if user_input == '/quit' or user_input == 'quit':
            break
        elif user_input == '/clear':
            HISTORY = []
            print("\n\033[92m✓ History cleared\033[0m")
            input("\nPress Enter...")
            continue
        elif user_input == '/help':
            print("\n\033[96m📖 Commands:\033[0m")
            print("  /help      - This help")
            print("  /clear     - Clear history")
            print("  /save      - Save session")
            print("  /load      - Load session")
            print("  /copy      - Copy last response")
            print("  /paste     - Paste from clipboard")
            print("  /imagine   - Generate image")
            print("  /calc      - Calculate")
            print("  /search    - Web search")
            print("  /weather   - Get weather")
            print("  /password  - Generate password")
            print("  /quit      - Exit")
            input("\nPress Enter...")
            continue
        elif user_input == '/copy':
            if HISTORY:
                result = copy_to_clipboard(HISTORY[-1]['content'])
                print(f"\n\033[92m{result}\033[0m")
            else:
                print("\n\033[93mNo response to copy\033[0m")
            input("\nPress Enter...")
            continue
        elif user_input == '/paste':
            result = paste_from_clipboard()
            print(f"\n\033[92m{result}\033[0m")
            input("\nPress Enter...")
            continue
        elif user_input.startswith('/imagine '):
            prompt = user_input[9:]
            print("\n" + generate_image(prompt))
            input("\nPress Enter...")
            continue
        elif user_input.startswith('/calc '):
            expr = user_input[6:]
            print("\n" + smart_calc(expr))
            input("\nPress Enter...")
            continue
        elif user_input.startswith('/search '):
            query = user_input[8:]
            print("\n" + web_search(query))
            input("\nPress Enter...")
            continue
        elif user_input.startswith('/weather '):
            city = user_input[9:]
            print("\n" + get_weather(city))
            input("\nPress Enter...")
            continue
        elif user_input == '/password':
            print("\n" + generate_password())
            input("\nPress Enter...")
            continue
        elif user_input == '/save':
            print("\n" + save_chat())
            input("\nPress Enter...")
            continue
        elif user_input == '/load':
            print("\n" + load_chat())
            input("\nPress Enter...")
            continue
        
        # AI Response
        print("\n\033[96mAI: \033[0m")
        
        try:
            messages = [{"role": "system", "content": system_prompt}]
            for msg in HISTORY[-20:]:
                messages.append(msg)
            messages.append({"role": "user", "content": user_input})
            
            conn = http.client.HTTPSConnection("openrouter.ai")
            payload = json.dumps({
                "model": CURRENT_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            })
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            
            conn.request("POST", "/api/v1/chat/completions", payload, headers)
            res = conn.getresponse()
            data = json.loads(res.read().decode())
            
            if "error" in data:
                print(f"\n\033[91mError: {data['error'].get('message', 'Unknown')}\033[0m")
            else:
                content = data['choices'][0]['message']['content']
                content = highlight_code(content)
                
                HISTORY.append({"role": "user", "content": user_input})
                HISTORY.append({"role": "assistant", "content": content})
                
                for char in content:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(0.002)
                print("\n")
                
        except Exception as e:
            print(f"\n\033[91mError: {str(e)}\033[0m")
        
        print("\n" + "─" * tw)
        input("\033[90mPress Enter to continue...\033[0m")

def api_settings():
    global API_KEY
    clear()
    print_header()
    print("\n\033[93m🔑 API Key Configuration\033[0m")
    print("Get your free key: https://openrouter.ai/keys\n")
    print(f"Current key: {API_KEY[:20]}..." if API_KEY else "No API key set")
    print("\nEnter new API key (or Enter to keep current):")
    new_key = input().strip()
    if new_key:
        API_KEY = new_key
        save_config()
        print("\n\033[92m✓ API key saved!\033[0m")
    input("\nPress Enter...")

def switch_model():
    global CURRENT_MODEL
    clear()
    print_header()
    print("\n\033[93m📡 Available Models:\033[0m")
    print("  1. openrouter/free (auto-select best)")
    print("  2. google/gemini-2.0-flash-lite:free")
    print("  3. qwen/qwen-2.5-coder-32b:free")
    print("  4. deepseek/deepseek-chat:free")
    print("  5. Custom model ID")
    print(f"\n\033[96mCurrent: {CURRENT_MODEL}\033[0m")
    
    choice = input("\nSelect (1-5): ").strip()
    models = {
        '1': 'openrouter/free',
        '2': 'google/gemini-2.0-flash-lite-preview-02-05:free',
        '3': 'qwen/qwen-2.5-coder-32b-instruct:free',
        '4': 'deepseek/deepseek-chat:free'
    }
    if choice in models:
        CURRENT_MODEL = models[choice]
        save_config()
        print(f"\n\033[92m✓ Switched to {CURRENT_MODEL}\033[0m")
    elif choice == '5':
        custom = input("Enter model ID: ").strip()
        if custom:
            CURRENT_MODEL = custom
            save_config()
            print(f"\n\033[92m✓ Switched to {CURRENT_MODEL}\033[0m")
    input("\nPress Enter...")

def custom_prompt():
    global CUSTOM_PROMPT
    clear()
    print_header()
    print("\n\033[93m🎨 Custom System Prompt\033[0m")
    print(f"\nCurrent: {CUSTOM_PROMPT[:100] if CUSTOM_PROMPT else 'Default prompt'}")
    print("\nEnter your custom prompt (type 'END' on new line to finish):")
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    if lines:
        CUSTOM_PROMPT = '\n'.join(lines)
        save_config()
        print("\n\033[92m✓ Custom prompt saved!\033[0m")
    input("\nPress Enter...")

def main():
    global API_KEY
    
    # First run check - if no config, run setup
    if not os.path.exists(CONFIG_FILE):
        from datetime import datetime
        check_and_install_dependencies()
        load_config()
    
    load_config()
    
    while True:
        clear()
        print_header()
        
        print("\n\033[96m╔════════════════════════════════════════════╗")
        print("║              MAIN MENU                       ║")
        print("╠════════════════════════════════════════════╣")
        print("║  \033[92m1.\033[0m 🤖 Start Chat                         ║")
        print("║  \033[93m2.\033[0m 🎨 Custom Prompt                     ║")
        print("║  \033[94m3.\033[0m 🔑 API Settings                      ║")
        print("║  \033[95m4.\033[0m 📡 Switch AI Model                  ║")
        print("║  \033[96m5.\033[0m ℹ️  About                           ║")
        print("║  \033[91m6.\033[0m 🚪 Exit                            ║")
        print("╚════════════════════════════════════════════╝\033[0m")
        
        print(f"\n\033[90mAPI: {'✅ Configured' if API_KEY else '❌ Missing'}\033[0m")
        print(f"\033[90mModel: {CURRENT_MODEL[:30]}\033[0m")
        
        choice = input("\n\033[92mSelect (1-6): \033[0m").strip()
        
        if choice == '1':
            ai_chat()
        elif choice == '2':
            custom_prompt()
        elif choice == '3':
            api_settings()
        elif choice == '4':
            switch_model()
        elif choice == '5':
            clear()
            print_header()
            print(f"\n\033[96m{APP_NAME} v{VERSION}\033[0m")
            print(f"Created by: {AUTHOR}")
            print(f"GitHub: {REPO_URL}")
            print("\nFeatures:")
            print("  • AI Chat (OpenRouter free tier)")
            print("  • Image generation")
            print("  • Web search & weather")
            print("  • Clipboard support")
            print("  • Code execution")
            print("  • Password generator")
            print("  • Save/load chats")
            input("\nPress Enter...")
        elif choice == '6':
            print("\n\033[92mGoodbye! 👋\033[0m")
            sys.exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[92m\nGoodbye! 👋\033[0m")
        sys.exit()
    except Exception as e:
        print(f"\n\033[91mFatal error: {e}\033[0m")
        sys.exit()