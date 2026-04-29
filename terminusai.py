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
║  NEW in v1.1:                                                    ║
║    • 📋 Clipboard support (/copy, /paste)                        ║
║    • 🎨 AI image generation (/imagine)                           ║
║    • 🧮 Smart calculator (/calc)                                 ║
║    • 🔄 Auto-update checker                                      ║
║    • 🔍 Search chat history (/findchat)                          ║
║    • 📝 Context summarization (/summarize)                       ║
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
from datetime import datetime

# ==================== AUTO-INSTALLER ====================
def check_and_install_dependencies():
    """Automatically check and install required packages on first run"""
    
    print("\033[36m")
    print("╔══════════════════════════════════════════════════╗")
    print("║         TerminusAI v1.1 - First Time Setup      ║")
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
    for pkg in ['python', 'git']:
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
    
    print("\n\033[92m✅ Setup complete! Launching TerminusAI v1.1...\033[0m")
    time.sleep(2)

# ==================== MAIN TERMINUSAI v1.1 CODE ====================
import urllib.request
import urllib.parse
import http.client
import threading
import re
import secrets
import string
import tempfile
import hashlib
from collections import Counter

VERSION = "1.1.0"
APP_NAME = "TerminusAI"
AUTHOR = "flint667"
AUTHOR_DISCORD = "flint667"
GITHUB_USER = "testlolplz"
REPO_URL = f"https://github.com/{GITHUB_USER}/TerminusAI"

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

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d %A")

def print_header():
    tw = os.get_terminal_size().columns
    current_time = get_current_time()
    current_date = get_current_date()
    
    logo = [
        "╔══════════════════════════════════════════════════╗",
        f"║           {APP_NAME} v{VERSION}                    ║",
        "║      Your Terminal AI Companion                  ║",
        "╠══════════════════════════════════════════════════╣",
        f"║  📅 {current_date:<48} ║",
        f"║  🕐 {current_time:<49} ║",
        "╚══════════════════════════════════════════════════╝"
    ]
    
    print("\n" * 1)
    for line in logo:
        pad = (tw - len(line)) // 2
        print(" " * max(0, pad) + get_rgb(100, 150, 255) + line + '\033[0m')

def show_loading_animation():
    chars = "⣾⣽⣻⢿⡿⣟⣯⣷"
    for i in range(15):
        sys.stdout.write(f"\r{get_rgb(0, 255, 100)} [{APP_NAME}] Thinking {chars[i % len(chars)]}\033[0m")
        sys.stdout.flush()
        time.sleep(0.05)
    sys.stdout.write("\r" + " " * 30 + "\r")

def log_message(role, content):
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = f"{LOGS_DIR}/chat_log_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(log_file, 'a') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {role}: {content}\n\n")

def highlight_code(text):
    pattern = r'```(\w+)?\n(.*?)```'
    def replace_code(match):
        lang = match.group(1) or 'text'
        code = match.group(2)
        return f"\n{get_rgb(100, 255, 100)}┌─[{lang.upper()}]─────────────────┐\n{get_rgb(200, 200, 0)}{code}\n{get_rgb(100, 255, 100)}└────────────────────────────────┘\033[0m"
    return re.sub(pattern, replace_code, text, flags=re.DOTALL)

# ==================== v1.1 NEW FEATURES ====================

def copy_to_clipboard(text):
    try:
        if len(text) > 5000:
            text = text[:5000] + "\n... (truncated)"
        subprocess.run(['termux-clipboard-set', text], timeout=2, capture_output=True)
        return f"📋 Copied to clipboard ({len(text)} characters)"
    except FileNotFoundError:
        return "⚠️ Clipboard not available. Install: pkg install termux-api"
    except:
        return "❌ Copy failed"

def paste_from_clipboard():
    try:
        result = subprocess.run(['termux-clipboard-get'], capture_output=True, text=True, timeout=2)
        if result.stdout:
            return f"📋 Clipboard content:\n\n{result.stdout[:2000]}"
        return "📋 Clipboard is empty"
    except FileNotFoundError:
        return "⚠️ Clipboard not available. Install: pkg install termux-api"
    except:
        return "❌ Paste failed"

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
                return f"✅ Image saved: {filename}\n🖼️ Opening in gallery..."
            except:
                return f"✅ Image saved: {os.path.abspath(filename)}"
        return "❌ Failed to generate image. Try a different prompt."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def smart_calc(expression):
    try:
        expression = expression.replace(" ", "")
        import math
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        allowed.update({"abs": abs, "round": round, "min": min, "max": max})
        
        # Safety check
        if not re.match(r'^[\d\s\+\-\*\/\%\(\)\.\^\,\|\&\~\<\>\=\!\+\-\*\/\%\*\*\,\s]+$', expression.replace("**", "")):
            if any(func in expression for func in ['sqrt', 'sin', 'cos', 'tan', 'log', 'pi', 'e']):
                result = eval(expression, {"__builtins__": {}}, allowed)
            else:
                return "❌ Invalid expression"
        else:
            result = eval(expression, {"__builtins__": {}}, {})
        
        return f"🧮 {expression} = {result}"
    except ZeroDivisionError:
        return "❌ Division by zero"
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
            links = re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)"', html)
            
            output = f"{get_rgb(0, 255, 200)}🔍 Search results for '{query}':\n\n{get_rgb(200, 200, 200)}"
            for i, (title, link) in enumerate(zip(results[:5], links[:5]), 1):
                output += f"{i}. {title}\n   {get_rgb(100, 200, 255)}{link}\n{get_rgb(200, 200, 200)}"
            return output if results else f"No results found for '{query}'"
    except:
        return "❌ Search failed"

def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=%C:+%t,+%w,+%h"
        with urllib.request.urlopen(url, timeout=10) as response:
            weather = response.read().decode('utf-8').strip()
            return f"🌤️ Weather in {city}: {weather}"
    except:
        return "❌ Weather fetch failed"

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(chars) for _ in range(length))
    
    strength = "Weak"
    if length >= 12 and any(c in "!@#$%^&*" for c in password):
        strength = "Strong"
    elif length >= 8:
        strength = "Medium"
    
    return f"🔐 Generated Password:\n{password}\nStrength: {strength}"

def search_chat_history(keyword):
    if not os.path.exists(LOGS_DIR):
        return "📂 No chat logs found yet"
    
    results = []
    keyword_lower = keyword.lower()
    
    for log_file in os.listdir(LOGS_DIR):
        if log_file.endswith('.txt'):
            filepath = os.path.join(LOGS_DIR, log_file)
            with open(filepath, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if keyword_lower in line.lower():
                        context_start = max(0, i-1)
                        context_end = min(len(lines), i+2)
                        context = ''.join(lines[context_start:context_end])
                        results.append({
                            'file': log_file,
                            'line': i+1,
                            'context': context.strip()
                        })
                        if len(results) >= 10:
                            break
            if len(results) >= 10:
                break
    
    if not results:
        return f"🔍 No results found for '{keyword}'"
    
    output = f"🔍 Search results for '{keyword}':\n\n"
    for r in results[:10]:
        output += f"📄 {r['file']} (line {r['line']}):\n   {r['context'][:100]}\n\n"
    return output

def summarize_context():
    global HISTORY
    
    if len(HISTORY) < 6:
        return "📝 Conversation is too short to summarize (need at least 3 exchanges)"
    
    summary_parts = []
    user_messages = []
    ai_messages = []
    
    for i, msg in enumerate(HISTORY):
        if msg['role'] == 'user':
            user_messages.append(msg['content'][:100])
        else:
            ai_messages.append(msg['content'][:100])
    
    summary_parts.append(f"📊 Conversation Summary:")
    summary_parts.append(f"   • Total exchanges: {len(HISTORY)//2}")
    summary_parts.append(f"   • User messages: {len(user_messages)}")
    summary_parts.append(f"   • AI responses: {len(ai_messages)}")
    
    all_text = ' '.join(user_messages + ai_messages).lower()
    common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with']
    words = [w for w in all_text.split() if w not in common_words and len(w) > 3]
    
    if words:
        top_words = Counter(words).most_common(5)
        summary_parts.append(f"\n   💡 Main topics: {', '.join([w[0] for w in top_words])}")
    
    if len(HISTORY) >= 4:
        last_user = HISTORY[-2]['content'][:150] if len(HISTORY) >= 2 else ""
        summary_parts.append(f"\n   🎯 Recent focus:\n   {last_user[:100]}...")
    
    return '\n'.join(summary_parts)

def check_for_updates():
    try:
        url = f"https://api.github.com/repos/{GITHUB_USER}/TerminusAI/releases/latest"
        req = urllib.request.Request(url, headers={'User-Agent': 'TerminusAI'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get('tag_name', '').replace('v', '')
            if latest_version and latest_version > VERSION:
                return {'update_available': True, 'latest': latest_version, 'current': VERSION}
        return {'update_available': False}
    except:
        return {'update_available': False}

def save_chat_session():
    global HISTORY
    if not HISTORY:
        return "⚠️ No conversation to save"
    
    name = input("📁 Session name (Enter for auto): ").strip()
    if not name:
        name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    os.makedirs(CHATS_DIR, exist_ok=True)
    filename = f"{CHATS_DIR}/{name}.json"
    
    save_data = {
        'app': APP_NAME,
        'version': VERSION,
        'timestamp': datetime.now().isoformat(),
        'model': CURRENT_MODEL,
        'history': HISTORY
    }
    
    with open(filename, 'w') as f:
        json.dump(save_data, f, indent=2)
    
    return f"✅ Saved to {filename}"

def load_chat_session():
    global HISTORY
    if not os.path.exists(CHATS_DIR):
        return "⚠️ No saved sessions found"
    
    sessions = [f.replace('.json', '') for f in os.listdir(CHATS_DIR) if f.endswith('.json')]
    if not sessions:
        return "⚠️ No saved sessions found"
    
    print(f"\n📂 Available sessions:")
    for i, session in enumerate(sessions, 1):
        stat = os.stat(f"{CHATS_DIR}/{session}.json")
        modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f"  {i}. {session} - {modified}")
    
    try:
        choice = int(input("\nSelect (1-{} or 0 to cancel): ".format(len(sessions)))) - 1
        if 0 <= choice < len(sessions):
            with open(f"{CHATS_DIR}/{sessions[choice]}.json", 'r') as f:
                load_data = json.load(f)
                HISTORY = load_data.get('history', [])
            return f"✅ Loaded {len(HISTORY)//2} exchanges"
    except:
        pass
    return "Cancelled"

# ==================== AI CHAT FUNCTION ====================

def ai_chat():
    global API_KEY, HISTORY, CURRENT_MODEL, CUSTOM_PROMPT
    
    if not API_KEY:
        print("\n\033[91m❌ ERROR: No API key configured!\033[0m")
        print("Please set your API key in Settings (option 3)")
        input("\nPress Enter...")
        return
    
    default_prompt = f"""You are {APP_NAME}, a helpful, harmless, and honest AI assistant for Termux.
You provide accurate information, refuse harmful requests, and follow ethical guidelines.
You cannot assist with illegal activities, hacking, malware, or any malicious actions.
You respond concisely and helpfully. You are friendly but professional.
When providing code, use proper markdown code blocks with language specification."""
    
    system_prompt = CUSTOM_PROMPT if CUSTOM_PROMPT else default_prompt
    
    while True:
        clear()
        print_header()
        tw = os.get_terminal_size().columns
        
        print("\n" + get_rgb(100, 200, 255) + "┌" + "─" * (tw - 2) + "┐")
        status = f"│ 📡 Model: {CURRENT_MODEL[:35]:<35} │ 💬 History: {len(HISTORY)//2} exchanges │"
        info = f"│ 🎨 Prompt: {'Custom' if CUSTOM_PROMPT else 'Default':<15} │ 🕐 {get_current_time()} │"
        print(status)
        print(info)
        print("└" + "─" * (tw - 2) + "┘\033[0m")
        
        print("\n" + get_rgb(255, 150, 100) + "┌─[ YOU ]────────────────────────────────────────────┐")
        print("│ Type /help for commands, /quit to exit                │")
        print("└─────────────────────────────────────────────────────────┘\033[0m")
        print(get_rgb(200, 200, 100) + " >> \033[0m", end="")
        user_input = input()
        
        if not user_input.strip():
            continue
        
        log_message("USER", user_input)
        
        # Handle commands
        if user_input.startswith('/'):
            cmd = user_input.lower().split()[0] if ' ' in user_input else user_input.lower()
            args = user_input.split(' ', 1)[1] if ' ' in user_input else ''
            
            if cmd == '/quit':
                break
            elif cmd == '/help':
                help_text = f"""
\033[96m📖 {APP_NAME} v{VERSION} Commands:\033[0m

\033[93mCore Commands:\033[0m
  /help          - Show this help
  /clear         - Clear conversation history
  /quit          - Exit to menu

\033[93mChat Management:\033[0m
  /save          - Save current session
  /load          - Load a saved session
  /summarize     - Summarize current conversation
  /findchat      - Search chat history

\033[93mProductivity:\033[0m
  /copy          - Copy last response to clipboard
  /paste         - Paste from clipboard
  /calc <expr>   - Calculate math expression
  /password      - Generate secure password

\033[93mInternet Features:\033[0m
  /search <query> - Search the web
  /weather <city> - Get weather information
  /imagine <text> - Generate AI image

\033[93mSystem:\033[0m
  /checkupdate   - Check for updates
  /model         - Switch AI model
  /voice         - Speak last response (requires Termux API)

\033[90mExamples:\033[0m
  /calc 2+2*10
  /search python tutorial
  /weather London
  /imagine a cat in space
  /findchat python
"""
                print(help_text)
                input("\nPress Enter to continue...")
                continue
            
            elif cmd == '/clear':
                HISTORY = []
                print("\n\033[92m✓ Conversation history cleared\033[0m")
                input("\nPress Enter...")
                continue
            
            elif cmd == '/save':
                print("\n" + save_chat_session())
                input("\nPress Enter...")
                continue
            
            elif cmd == '/load':
                print("\n" + load_chat_session())
                input("\nPress Enter...")
                continue
            
            elif cmd == '/copy':
                if HISTORY and len(HISTORY) >= 2:
                    result = copy_to_clipboard(HISTORY[-1]['content'])
                    print(f"\n\033[92m{result}\033[0m")
                else:
                    print("\n\033[93mNo response to copy\033[0m")
                input("\nPress Enter...")
                continue
            
            elif cmd == '/paste':
                print("\n" + paste_from_clipboard())
                input("\nPress Enter...")
                continue
            
            elif cmd == '/imagine':
                if not args:
                    print("\n\033[93mUsage: /imagine description of image\033[0m")
                    print("Example: /imagine a beautiful sunset over mountains")
                else:
                    print("\n" + generate_image(args))
                input("\nPress Enter...")
                continue
            
            elif cmd == '/calc':
                if not args:
                    print("\n\033[93mUsage: /calc 2+2*3\033[0m")
                    print("Examples: /calc (100-25)/3, /calc sqrt(16), /calc 2**10")
                else:
                    print("\n" + smart_calc(args))
                input("\nPress Enter...")
                continue
            
            elif cmd == '/search':
                if not args:
                    print("\n\033[93mUsage: /search your query here\033[0m")
                else:
                    print("\n" + web_search(args))
                input("\nPress Enter...")
                continue
            
            elif cmd == '/weather':
                if not args:
                    print("\n\033[93mUsage: /weather city_name\033[0m")
                    print("Example: /weather London")
                else:
                    print("\n" + get_weather(args))
                input("\nPress Enter...")
                continue
            
            elif cmd == '/password':
                length = int(args) if args and args.isdigit() else 16
                print("\n" + generate_password(length))
                input("\nPress Enter...")
                continue
            
            elif cmd == '/findchat':
                if not args:
                    print("\n\033[93mUsage: /findchat keyword\033[0m")
                    print("Searches through all your past conversations")
                else:
                    print("\n" + search_chat_history(args))
                input("\nPress Enter...")
                continue
            
            elif cmd == '/summarize':
                print("\n" + summarize_context())
                input("\nPress Enter...")
                continue
            
            elif cmd == '/checkupdate':
                update = check_for_updates()
                if update.get('update_available'):
                    print(f"\n\033[93m🔄 Update available!\033[0m")
                    print(f"   Current: v{update['current']}")
                    print(f"   Latest: v{update['latest']}")
                    print(f"\n   Run: curl -sSL {REPO_URL}/raw/main/terminusai.py -o ~/terminusai.py")
                else:
                    print(f"\n\033[92m✅ TerminusAI v{VERSION} is up to date!\033[0m")
                input("\nPress Enter...")
                continue
            
            elif cmd == '/model':
                print("\n\033[93mSwitch model from Settings menu (option 4)\033[0m")
                input("\nPress Enter...")
                continue
            
            elif cmd == '/voice':
                if HISTORY and len(HISTORY) >= 2:
                    try:
                        subprocess.run(['termux-tts-speak', HISTORY[-1]['content'][:500]], timeout=5)
                        print("\n\033[92m🔊 Speaking...\033[0m")
                    except:
                        print("\n\033[93m⚠️ TTS not available. Install termux-api\033[0m")
                else:
                    print("\n\033[93mNo response to speak\033[0m")
                input("\nPress Enter...")
                continue
            
            else:
                print(f"\n\033[93mUnknown command: {cmd}\033[0m")
                print("Type /help for available commands")
                input("\nPress Enter...")
                continue
        
        # AI Response
        show_loading_animation()
        
        print("\n" + get_rgb(0, 200, 255) + f"┌─[ {APP_NAME} ]───────────────────────────────────┐")
        print("│ Response:                                                │")
        print("└─────────────────────────────────────────────────────────┘\033[0m\n")
        
        try:
            messages = [{"role": "system", "content": system_prompt}]
            recent_history = HISTORY[-20:] if len(HISTORY) > 20 else HISTORY
            for msg in recent_history:
                messages.append(msg)
            messages.append({"role": "user", "content": user_input})
            
            conn = http.client.HTTPSConnection("openrouter.ai")
            payload = json.dumps({
                "model": CURRENT_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1500,
                "top_p": 0.9
            })
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "X-Title": f"{APP_NAME} v{VERSION}"
            }
            
            conn.request("POST", "/api/v1/chat/completions", payload, headers)
            res = conn.getresponse()
            data = json.loads(res.read().decode())
            
            if "error" in data:
                error_msg = data['error'].get('message', 'Unknown error')
                print(f"\n\033[91m❌ API ERROR: {error_msg}\033[0m")
                if "no api key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                    print("\n\033[93m💡 Your API key is invalid. Please reconfigure it.\033[0m")
            else:
                content = data['choices'][0]['message']['content']
                content = highlight_code(content)
                
                HISTORY.append({"role": "user", "content": user_input})
                HISTORY.append({"role": "assistant", "content": content})
                
                if len(HISTORY) > 40:
                    HISTORY = HISTORY[-40:]
                
                log_message(APP_NAME, content)
                
                # Typewriter effect
                for char in content:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(0.002)
                print("\n")
                
        except Exception as e:
            error_str = str(e)
            print(f"\n\033[91m❌ CONNECTION ERROR\033[0m")
            print(f"   • Check your internet connection")
            print(f"   • Verify your API key is correct")
            print(f"   • Error: {error_str[:100]}")
        
        print("\n" + get_rgb(100, 100, 100) + "─" * tw)
        print(get_rgb(150, 150, 100) + "  [Enter] Continue  |  /help for commands  |  /voice to speak  |  /quit to exit\033[0m", end="")
        input()

# ==================== SETTINGS FUNCTIONS ====================

def api_settings():
    global API_KEY
    clear()
    print_header()
    tw = os.get_terminal_size().columns
    c = (tw - 45) // 2
    
    print("\n" + " " * c + get_rgb(255, 200, 0) + "╔══════════════════════════════════════════════╗")
    print(" " * c + "║           🔑 API KEY CONFIGURATION           ║")
    print(" " * c + "╚══════════════════════════════════════════════╝\033[0m")
    
    print("\n" + " " * c + get_rgb(200, 200, 200) + "Get your free API key from: https://openrouter.ai/keys")
    print(" " * c + "Use the free tier - no credit card required!\n")
    
    if API_KEY:
        print(" " * c + get_rgb(0, 255, 0) + f"Current key: {API_KEY[:15]}...{API_KEY[-10:]}")
    
    print("\n" + " " * c + get_rgb(255, 100, 100) + "┌────────────────────────────────────────────┐")
    print(" " * c + "│  Paste your OpenRouter API key below:        │")
    print(" " * c + "│  (leave empty to keep current)               │")
    print(" " * c + "└────────────────────────────────────────────┘\033[0m")
    
    print("\n" + " " * c, end="")
    temp = input(get_rgb(0, 255, 200) + "⚡ API Key > " + get_rgb(255, 255, 255))
    
    if temp.strip():
        API_KEY = temp.strip()
        save_config()
        print("\n" + " " * c + get_rgb(0, 255, 0) + "✓ API key saved successfully!")
    else:
        print("\n" + " " * c + get_rgb(255, 100, 0) + "⚠ Keeping existing API key")
    
    print("\n" + " " * c + get_rgb(200, 200, 200) + "Press Enter to continue...", end="")
    input()

def switch_model():
    global CURRENT_MODEL
    clear()
    print_header()
    
    print("\n" + get_rgb(100, 255, 100) + "📡 Available free models:\n" + get_rgb(200, 200, 200))
    print("  1. openrouter/free (Auto-select best)")
    print("  2. Google Gemini 2.0 Flash Lite")
    print("  3. Qwen Coder 32B")
    print("  4. DeepSeek Chat")
    print("  5. Microsoft Phi-3 Mini")
    print("  6. Custom model ID")
    
    print(f"\n{get_rgb(100, 255, 100)}Current: {get_rgb(0, 255, 200)}{CURRENT_MODEL}")
    print(f"{get_rgb(100, 255, 100)}Select model (1-6): \033[0m", end="")
    choice = input().strip()
    
    models = {
        '1': 'openrouter/free',
        '2': 'google/gemini-2.0-flash-lite-preview-02-05:free',
        '3': 'qwen/qwen-2.5-coder-32b-instruct:free',
        '4': 'deepseek/deepseek-chat:free',
        '5': 'microsoft/phi-3-mini-128k-instruct:free'
    }
    
    if choice in models:
        CURRENT_MODEL = models[choice]
        save_config()
        print(f"\n{get_rgb(0, 255, 0)}✓ Switched to: {CURRENT_MODEL}\033[0m")
    elif choice == '6':
        custom = input(f"\n{get_rgb(100, 255, 100)}Enter custom model ID: \033[0m").strip()
        if custom:
            CURRENT_MODEL = custom
            save_config()
            print(f"\n{get_rgb(0, 255, 0)}✓ Switched to: {CURRENT_MODEL}\033[0m")
    
    input("\nPress Enter to continue...")

def custom_prompt_manager():
    global CUSTOM_PROMPT
    clear()
    print_header()
    
    print("\n" + get_rgb(255, 200, 0) + "╔══════════════════════════════════════════════╗")
    print("║           🎨 CUSTOM PROMPT MANAGER          ║")
    print("╚══════════════════════════════════════════════╝\033[0m")
    
    print(f"\n{get_rgb(100, 255, 100)}Current custom prompt:{get_rgb(200, 200, 200)}")
    print("═" * 50)
    if CUSTOM_PROMPT:
        print(CUSTOM_PROMPT[:500])
        if len(CUSTOM_PROMPT) > 500:
            print("...(truncated)")
    else:
        print("(No custom prompt set - using default)")
    print("═" * 50)
    
    print(f"\n{get_rgb(255, 200, 0)}Options:")
    print("  1. Set new custom prompt")
    print("  2. Reset to default prompt")
    print("  0. Back")
    
    choice = input(f"\n{get_rgb(0, 255, 200)}Select: \033[0m")
    
    if choice == '1':
        print(f"{get_rgb(100, 255, 100)}\n📝 Enter your custom prompt (type 'END' on new line to finish):\n{get_rgb(200, 200, 200)}")
        lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
        CUSTOM_PROMPT = '\n'.join(lines)
        save_config()
        print(f"{get_rgb(0, 255, 0)}✓ Custom prompt saved!\033[0m")
    elif choice == '2':
        CUSTOM_PROMPT = ""
        save_config()
        print(f"{get_rgb(0, 255, 0)}✓ Reset to default prompt\033[0m")
    
    input(f"\n{get_rgb(200, 200, 200)}Press Enter to continue...")

# ==================== MAIN MENU ====================

def main():
    global API_KEY
    
    # First run check
    if not os.path.exists(CONFIG_FILE):
        check_and_install_dependencies()
        load_config()
    
    load_config()
    
    # Check for updates silently
    update_available = check_for_updates().get('update_available', False)
    
    while True:
        clear()
        print_header()
        tw = os.get_terminal_size().columns
        UI_W = 54
        b_pad = (tw - UI_W) // 2
        
        if update_available:
            print("\n" + " " * b_pad + get_rgb(255, 200, 0) + "🎉 UPDATE AVAILABLE! Run /checkupdate in chat\033[0m")
        
        print("\n" + " " * b_pad + get_rgb(200, 200, 255) + "╔" + "═" * (UI_W - 2) + "╗")
        
        menu_items = [
            f"  🤖 1. Start Chat with {APP_NAME}",
            "  🎨 2. Custom Prompt Manager",
            "  🔑 3. Configure API Key", 
            "  📡 4. Switch AI Model",
            "  ℹ️  5. About & Info",
            "  🚪 6. Exit"
        ]
        
        colors = [
            get_rgb(0, 255, 100), get_rgb(255, 100, 255),
            get_rgb(255, 200, 0), get_rgb(100, 200, 255),
            get_rgb(200, 200, 200), get_rgb(255, 100, 100)
        ]
        
        for idx, item in enumerate(menu_items):
            display = item.ljust(UI_W - 2)
            print(" " * b_pad + "║" + colors[idx] + display + get_rgb(200, 200, 255) + "║")
        
        print(" " * b_pad + "╚" + "═" * (UI_W - 2) + "╝\033[0m")
        
        key_status = f"✓ API: {'Configured' if API_KEY else 'Missing'}"
        model_status = f"📡 Model: {CURRENT_MODEL[:25]}"
        prompt_status = f"🎨 Prompt: {'Custom' if CUSTOM_PROMPT else 'Default'}"
        
        print("\n" + " " * ((tw - len(key_status)) // 2) + get_rgb(100, 200, 100) + key_status)
        print(" " * ((tw - len(model_status)) // 2) + get_rgb(100, 200, 255) + model_status)
        print(" " * ((tw - len(prompt_status)) // 2) + get_rgb(255, 200, 100) + prompt_status + "\033[0m")
        
        print(f"\n" + " " * ((tw - 50) // 2) + get_rgb(100, 100, 100) + f"Created by {AUTHOR} (Discord: {AUTHOR_DISCORD})")
        print(" " * ((tw - 40) // 2) + get_rgb(100, 100, 100) + REPO_URL)
        
        print("\n" + " " * ((tw - 35) // 2), end="")
        choice = input(get_rgb(255, 255, 100) + "┌─[SELECT]─► " + get_rgb(0, 255, 200))
        
        if choice == '1':
            ai_chat()
        elif choice == '2':
            custom_prompt_manager()
        elif choice == '3':
            api_settings()
            save_config()
        elif choice == '4':
            switch_model()
        elif choice == '5':
            clear()
            print_header()
            print("\n" + get_rgb(100, 255, 100) + f"╔════════════════════════════════════════════╗")
            print(f"║     {APP_NAME} v{VERSION} - Terminal AI Companion   ║")
            print("║  ═══════════════════════════════════════════   ║")
            print("║  • Complete AI assistant for Termux            ║")
            print("║  • Powered by OpenRouter API (free tier)       ║")
            print("║  • No cost, no credit card required            ║")
            print("║                                                ║")
            print("║  ✨ FEATURES in v1.1:                          ║")
            print("║  • 📋 Clipboard support (/copy, /paste)       ║")
            print("║  • 🎨 AI image generation (/imagine)          ║")
            print("║  • 🧮 Smart calculator (/calc)                ║")
            print("║  • 🔍 Search chat history (/findchat)         ║")
            print("║  • 📝 Context summarization (/summarize)      ║")
            print("║  • 🔄 Auto-update checker                     ║")
            print("║  • 🔔 Notifications for long responses        ║")
            print("║  • 💾 Save/load conversations                 ║")
            print("║  • 🎨 Custom system prompts                   ║")
            print("║  • 🌐 Web search & weather                    ║")
            print("║  • 🎤 Text-to-speech output                   ║")
            print("║                                                ║")
            print(f"║  👨‍💻 Created by: {AUTHOR}                       ║")
            print(f"║  💬 Discord: {AUTHOR_DISCORD}                   ║")
            print(f"║  📦 GitHub: {REPO_URL}                         ║")
            print("║                                                ║")
            print("║  📝 Type /help in chat for all commands        ║")
            print("╚════════════════════════════════════════════════╝\033[0m")
            input("\nPress Enter to continue...")
        elif choice == '6':
            print("\n" + get_rgb(0, 255, 0) + f"Goodbye from {APP_NAME}! 👋\033[0m")
            sys.exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + get_rgb(0, 255, 0) + f"\nExited. Goodbye from {APP_NAME}!\033[0m")
        sys.exit()
    except Exception as e:
        print(f"\n\033[91mFatal error: {e}\033[0m")
        sys.exit()