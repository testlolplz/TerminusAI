
#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║                         TERMINUS AI v1.0                          ║
║                   Your Terminal AI Companion                      ║
║                                                                   ║
║                      Created by: flint                        ║
║                         Discord: flint667                         ║
║                         GitHub: testlolplz                        ║
║                                                                   ║
║           ⚡ Free & Open Source AI Assistant for Termux          ║
╚═══════════════════════════════════════════════════════════════════╝

TerminusAI - A powerful, feature-rich AI assistant for Termux
that brings the power of LLMs directly to your Android terminal.

Repository: https://github.com/testlolplz/TerminusAI
License: MIT
"""

import os
import sys
import time
import json
import re
import subprocess
import tempfile
import urllib.request
import urllib.parse
import http.client
import threading
import socket
import random
import hashlib
import secrets
import string
from datetime import datetime

# ==================== VERSION INFO ====================
VERSION = "1.0.0"
APP_NAME = "TerminusAI"
AUTHOR = "flint667"
AUTHOR_DISCORD = "flint667"
GITHUB_USER = "testlolplz"
REPO_URL = f"https://github.com/{GITHUB_USER}/TerminusAI"

# ==================== CONFIGURATION ====================
API_KEY = ""
HISTORY = []
CURRENT_MODEL = "openrouter/free"
CUSTOM_PROMPT = ""
CONFIG_FILE = os.path.expanduser(f"~/{APP_NAME.lower()}_config.json")
CHATS_DIR = f"{APP_NAME.lower()}_chats"
LOGS_DIR = f"{APP_NAME.lower()}_logs"
BACKUP_DIR = f"{APP_NAME.lower()}_backups"
PROMPTS_DIR = f"{APP_NAME.lower()}_prompts"

# ==================== UTILITY FUNCTIONS ====================
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
    """Log conversations for history"""
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = f"{LOGS_DIR}/chat_log_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(log_file, 'a') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {role}: {content}\n\n")

# ==================== FEATURE FUNCTIONS ====================
def highlight_code(text):
    """Syntax highlighting for code blocks"""
    pattern = r'```(\w+)?\n(.*?)```'
    
    def replace_code(match):
        lang = match.group(1) or 'text'
        code = match.group(2)
        return f"\n{get_rgb(100, 255, 100)}┌─[{lang.upper()}]─────────────────┐\n{get_rgb(200, 200, 0)}{code}\n{get_rgb(100, 255, 100)}└────────────────────────────────┘\033[0m"
    
    return re.sub(pattern, replace_code, text, flags=re.DOTALL)

def manage_custom_prompt():
    """Manage custom system prompts"""
    global CUSTOM_PROMPT
    
    clear()
    print_header()
    tw = os.get_terminal_size().columns
    c = (tw - 45) // 2
    
    print("\n" + " " * c + get_rgb(255, 200, 0) + "╔══════════════════════════════════════════════╗")
    print(" " * c + "║           🎨 CUSTOM PROMPT MANAGER          ║")
    print(" " * c + "╚══════════════════════════════════════════════╝\033[0m")
    
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
    print("  2. Load prompt from file")
    print("  3. Save current prompt to file")
    print("  4. Use default prompt (reset)")
    print("  0. Back to menu")
    
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
        if not os.path.exists(PROMPTS_DIR):
            os.makedirs(PROMPTS_DIR)
        prompts = [f for f in os.listdir(PROMPTS_DIR) if f.endswith('.txt')]
        if prompts:
            print(f"{get_rgb(100, 255, 100)}\nAvailable prompts:")
            for i, p in enumerate(prompts, 1):
                print(f"  {i}. {p}")
            idx = input(f"\nSelect prompt number: ")
            try:
                with open(f"{PROMPTS_DIR}/{prompts[int(idx)-1]}", 'r') as f:
                    CUSTOM_PROMPT = f.read()
                save_config()
                print(f"{get_rgb(0, 255, 0)}✓ Prompt loaded!\033[0m")
            except:
                print(f"{get_rgb(255, 0, 0)}❌ Failed to load\033[0m")
        else:
            print(f"{get_rgb(255, 100, 0)}⚠ No saved prompts found\033[0m")
    
    elif choice == '3':
        if CUSTOM_PROMPT:
            os.makedirs(PROMPTS_DIR, exist_ok=True)
            name = input("Filename (without .txt): ").strip()
            with open(f"{PROMPTS_DIR}/{name}.txt", 'w') as f:
                f.write(CUSTOM_PROMPT)
            print(f"{get_rgb(0, 255, 0)}✓ Prompt saved to {PROMPTS_DIR}/{name}.txt\033[0m")
        else:
            print(f"{get_rgb(255, 100, 0)}⚠ No custom prompt to save\033[0m")
    
    elif choice == '4':
        CUSTOM_PROMPT = ""
        save_config()
        print(f"{get_rgb(0, 255, 0)}✓ Using default prompt\033[0m")
    
    input(f"\n{get_rgb(200, 200, 200)}Press Enter to continue...")

def save_chat_session():
    """Save current conversation to a named file"""
    global HISTORY
    if not HISTORY:
        print(f"{get_rgb(255, 100, 0)}⚠ No conversation to save\033[0m")
        return False
    
    print(f"{get_rgb(100, 255, 100)}📁 Session name (Enter for auto): \033[0m", end="")
    name = input().strip()
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
    
    print(f"{get_rgb(0, 255, 0)}✓ Saved to {filename}\033[0m")
    return True

def load_chat_session():
    """Load a previous conversation"""
    global HISTORY
    if not os.path.exists(CHATS_DIR):
        print(f"{get_rgb(255, 100, 0)}⚠ No saved sessions found\033[0m")
        return False
    
    sessions = [f.replace('.json', '') for f in os.listdir(CHATS_DIR) if f.endswith('.json')]
    if not sessions:
        print(f"{get_rgb(255, 100, 0)}⚠ No saved sessions found\033[0m")
        return False
    
    print(f"{get_rgb(100, 255, 100)}📂 Available sessions:\033[0m")
    for i, session in enumerate(sessions, 1):
        stat = os.stat(f"{CHATS_DIR}/{session}.json")
        size = stat.st_size
        modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f"  {i}. {session} ({size} bytes) - {modified}")
    
    print(f"\n{get_rgb(100, 255, 100)}Select (1-{len(sessions)} or 0 to cancel): \033[0m", end="")
    choice = input().strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(sessions):
            with open(f"{CHATS_DIR}/{sessions[idx]}.json", 'r') as f:
                load_data = json.load(f)
                HISTORY = load_data.get('history', [])
            print(f"{get_rgb(0, 255, 0)}✓ Loaded {len(HISTORY)//2} exchanges\033[0m")
            return True
        else:
            return False
    except:
        return False

def execute_python(code):
    """Safely execute Python code from chat"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        result = subprocess.run(['python', temp_file], 
                              capture_output=True, text=True, timeout=10)
        output = result.stdout or result.stderr
        return output if output.strip() else "✓ Code executed successfully (no output)"
    except subprocess.TimeoutExpired:
        return "⚠️ Code execution timed out (10s limit)"
    except Exception as e:
        return f"❌ Error: {str(e)}"
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass

def web_search(query):
    """Search the web using DuckDuckGo"""
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
    except Exception as e:
        return f"Search error: {str(e)}"

def read_file(filename):
    """Read and display file contents"""
    try:
        with open(filename, 'r') as f:
            content = f.read()
            return f"📄 Contents of {filename}:\n\n```\n{content[:2000]}\n```\n{'(truncated)' if len(content) > 2000 else ''}"
    except FileNotFoundError:
        return f"❌ File not found: {filename}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def write_file(filename, content):
    """Write content to file"""
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return f"✓ Saved to {filename}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_system_info():
    """Get Termux system information"""
    info = []
    info.append(f"{get_rgb(0, 255, 200)}🤖 System Information:\n{get_rgb(200, 200, 200)}")
    info.append(f"═" * 35)
    info.append(f"• {APP_NAME} Version: {VERSION}")
    info.append(f"• Python: {sys.version.split()[0]}")
    info.append(f"• Platform: {sys.platform}")
    
    try:
        storage = subprocess.run(['df', '-h', '/data/data/com.termux/files/home'], 
                                capture_output=True, text=True, timeout=5).stdout
        if '\n' in storage:
            lines = storage.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 4:
                    info.append(f"• Storage: {parts[3]} free / {parts[1]} total")
    except:
        pass
    
    try:
        mem = subprocess.run(['free', '-h'], capture_output=True, text=True, timeout=5).stdout
        if '\n' in mem:
            lines = mem.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 3:
                    info.append(f"• Memory: {parts[2]} free / {parts[1]} total")
    except:
        pass
    
    return '\n'.join(info)

def export_to_markdown():
    """Export conversation to markdown"""
    global HISTORY
    if not HISTORY:
        print(f"{get_rgb(255, 100, 0)}⚠ No conversation to export\033[0m")
        return False
    
    filename = f"{APP_NAME.lower()}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(filename, 'w') as f:
        f.write(f"# {APP_NAME} Chat Export\n\n")
        f.write(f"**App:** {APP_NAME} v{VERSION}\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Model:** {CURRENT_MODEL}\n")
        f.write(f"**Author:** {AUTHOR}\n")
        f.write(f"**GitHub:** {REPO_URL}\n\n")
        f.write("---\n\n")
        
        for msg in HISTORY:
            role = "**User**" if msg['role'] == 'user' else f"**{APP_NAME}**"
            f.write(f"### {role}\n\n")
            f.write(f"{msg['content']}\n\n")
            f.write("---\n\n")
    
    print(f"{get_rgb(0, 255, 0)}✓ Exported to {filename}\033[0m")
    return True

def switch_model():
    """Switch between available AI models"""
    global CURRENT_MODEL
    
    models = {
        '1': 'openrouter/free',
        '2': 'google/gemini-2.0-flash-lite-preview-02-05:free',
        '3': 'qwen/qwen-2.5-coder-32b-instruct:free',
        '4': 'deepseek/deepseek-chat:free',
        '5': 'microsoft/phi-3-mini-128k-instruct:free',
        '6': 'mistralai/mistral-7b-instruct:free',
        '7': 'meta-llama/llama-3.2-3b-instruct:free',
        '8': 'custom'
    }
    
    print(f"{get_rgb(100, 255, 100)}📡 Available free models:\n{get_rgb(200, 200, 200)}")
    print("  1. openrouter/free (Auto-select best)")
    print("  2. Google Gemini 2.0 Flash Lite")
    print("  3. Qwen Coder 32B")
    print("  4. DeepSeek Chat")
    print("  5. Microsoft Phi-3 Mini")
    print("  6. Mistral 7B")
    print("  7. Meta Llama 3.2")
    print("  8. Custom model ID")
    
    print(f"\n{get_rgb(100, 255, 100)}Current: {get_rgb(0, 255, 200)}{CURRENT_MODEL}")
    print(f"{get_rgb(100, 255, 100)}Select model (1-8): \033[0m", end="")
    choice = input().strip()
    
    if choice in models:
        if choice == '8':
            print(f"{get_rgb(100, 255, 100)}Enter custom model ID: \033[0m", end="")
            custom = input().strip()
            if custom:
                CURRENT_MODEL = custom
        else:
            CURRENT_MODEL = models[choice]
        save_config()
        print(f"{get_rgb(0, 255, 0)}✓ Switched to: {CURRENT_MODEL}\033[0m")
        return True
    
    return False

def execute_terminal(command):
    """Execute terminal command safely"""
    try:
        result = subprocess.run(command, shell=True, 
                              capture_output=True, text=True, timeout=10)
        output = result.stdout or result.stderr
        return output if output.strip() else "✓ Command executed (no output)"
    except subprocess.TimeoutExpired:
        return "⚠️ Command timed out (10s limit)"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def text_to_speech(text):
    """Convert AI responses to speech"""
    try:
        if len(text) > 500:
            text = text[:500] + "..."
        subprocess.run(['termux-tts-speak', text], timeout=5, capture_output=True)
        return "🔊 Speaking response..."
    except FileNotFoundError:
        return "⚠️ TTS not available. Install: pkg install termux-api"
    except:
        return "⚠️ TTS failed"

def download_file(url, filename=None):
    """Download files from the internet"""
    try:
        if not filename:
            filename = url.split('/')[-1] or 'downloaded_file'
        
        urllib.request.urlretrieve(url, filename)
        size = os.path.getsize(filename)
        return f"✓ Downloaded: {filename} ({size} bytes)"
    except Exception as e:
        return f"❌ Download failed: {str(e)}"

def get_weather(city):
    """Get weather information"""
    try:
        url = f"https://wttr.in/{city}?format=%C:+%t,+%w,+%h"
        with urllib.request.urlopen(url, timeout=10) as response:
            weather = response.read().decode('utf-8').strip()
            return f"🌤️ Weather in {city}: {weather}"
    except:
        return "❌ Weather fetch failed"

def get_news():
    """Get latest news headlines"""
    try:
        url = "https://feeds.bbci.co.uk/news/rss.xml"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            import xml.etree.ElementTree as ET
            data = response.read()
            root = ET.fromstring(data)
            headlines = []
            for item in root.findall('.//item')[:5]:
                title = item.find('title').text
                headlines.append(f"• {title}")
            return "📰 Latest News:\n" + "\n".join(headlines)
    except:
        return "❌ News fetch failed"

def create_backup():
    """Backup all chats and config"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{APP_NAME.lower()}_backup_{timestamp}"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    os.makedirs(backup_path, exist_ok=True)
    
    # Backup config
    if os.path.exists(CONFIG_FILE):
        subprocess.run(['cp', CONFIG_FILE, backup_path])
    
    # Backup chats
    if os.path.exists(CHATS_DIR):
        subprocess.run(['cp', '-r', CHATS_DIR, backup_path])
    
    # Backup logs
    if os.path.exists(LOGS_DIR):
        subprocess.run(['cp', '-r', LOGS_DIR, backup_path])
    
    # Backup prompts
    if os.path.exists(PROMPTS_DIR):
        subprocess.run(['cp', '-r', PROMPTS_DIR, backup_path])
    
    # Create archive
    os.makedirs(BACKUP_DIR, exist_ok=True)
    archive_name = f"{BACKUP_DIR}/{backup_name}.tar.gz"
    subprocess.run(['tar', '-czf', archive_name, backup_path])
    subprocess.run(['rm', '-rf', backup_path])
    
    return f"✓ Backup created: {archive_name}"

def show_storage_stats():
    """Show storage usage statistics"""
    stats = []
    stats.append(f"{get_rgb(0, 255, 200)}📊 Storage Statistics:\n{get_rgb(200, 200, 200)}")
    
    if os.path.exists(CONFIG_FILE):
        size = os.path.getsize(CONFIG_FILE)
        stats.append(f"• Config: {size} bytes")
    
    if os.path.exists(CHATS_DIR):
        total_size = 0
        num_files = 0
        for file in os.listdir(CHATS_DIR):
            filepath = os.path.join(CHATS_DIR, file)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
                num_files += 1
        stats.append(f"• Chat sessions: {num_files} files, {total_size} bytes")
    
    if os.path.exists(LOGS_DIR):
        total_size = 0
        for file in os.listdir(LOGS_DIR):
            filepath = os.path.join(LOGS_DIR, file)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
        stats.append(f"• Logs: {total_size} bytes")
    
    if os.path.exists(PROMPTS_DIR):
        total_size = 0
        for file in os.listdir(PROMPTS_DIR):
            total_size += os.path.getsize(os.path.join(PROMPTS_DIR, file))
        stats.append(f"• Custom prompts: {total_size} bytes")
    
    return '\n'.join(stats)

def generate_qr(text):
    """Generate QR code from text"""
    try:
        filename = f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(text)}"
        urllib.request.urlretrieve(url, filename)
        return f"✓ QR code saved as: {filename}"
    except Exception as e:
        return f"❌ Failed: {str(e)}"

def generate_password(length=16):
    """Generate secure password"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(chars) for _ in range(length))
    
    strength = "Weak"
    if length >= 12 and any(c in "!@#$%^&*" for c in password):
        strength = "Strong"
    elif length >= 8:
        strength = "Medium"
    
    return f"🔐 Generated Password:\n{password}\nStrength: {strength}"

def todo_list():
    """Simple todo list manager"""
    todo_file = f"{CHATS_DIR}/todo.json"
    
    if os.path.exists(todo_file):
        with open(todo_file, 'r') as f:
            todos = json.load(f)
    else:
        todos = []
    
    print(f"{get_rgb(100, 255, 100)}📝 TODO LIST MANAGER:\n{get_rgb(200, 200, 200)}")
    if todos:
        for i, todo in enumerate(todos, 1):
            status = "✓" if todo.get('done', False) else "□"
            print(f"  {status} {i}. {todo['task']}")
    else:
        print("  No todos yet")
    
    print(f"\n{get_rgb(255, 200, 0)}Commands: add <task> | done <number> | delete <number> | list | clear")
    cmd = input(f"{get_rgb(0, 255, 200)}> \033[0m").strip().lower()
    
    if cmd.startswith('add '):
        task = cmd[4:]
        todos.append({'task': task, 'done': False, 'created': datetime.now().isoformat()})
        result = f"✓ Added: {task}"
    elif cmd.startswith('done '):
        try:
            idx = int(cmd[5:]) - 1
            if 0 <= idx < len(todos):
                todos[idx]['done'] = True
                result = f"✓ Completed: {todos[idx]['task']}"
            else:
                result = "❌ Invalid number"
        except:
            result = "❌ Invalid command"
    elif cmd.startswith('delete '):
        try:
            idx = int(cmd[7:]) - 1
            if 0 <= idx < len(todos):
                removed = todos.pop(idx)
                result = f"✓ Deleted: {removed['task']}"
            else:
                result = "❌ Invalid number"
        except:
            result = "❌ Invalid command"
    elif cmd == 'list':
        pending = [t['task'] for t in todos if not t.get('done', False)]
        result = "Pending: " + ", ".join(pending) if pending else "No pending tasks"
    elif cmd == 'clear':
        todos = []
        result = "✓ Todo list cleared"
    else:
        result = "Unknown command"
    
    with open(todo_file, 'w') as f:
        json.dump(todos, f, indent=2)
    
    return result

# ==================== API SETTINGS ====================
def api_setting():
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

# ==================== COMMAND HANDLER ====================
COMMANDS = {
    '/help': 'Show all commands',
    '/clear': 'Clear conversation history',
    '/save': 'Save current chat session',
    '/load': 'Load a previous session',
    '/run': 'Execute Python code',
    '/search': 'Search the web (usage: /search query)',
    '/read': 'Read a file (usage: /read filename)',
    '/write': 'Write to a file (usage: /write filename)',
    '/exec': 'Execute terminal command (usage: /exec command)',
    '/sysinfo': 'Show system information',
    '/model': 'Switch AI model',
    '/export': 'Export chat to markdown',
    '/voice': 'Speak the last response',
    '/download': 'Download a file (usage: /download URL)',
    '/weather': 'Get weather (usage: /weather city)',
    '/news': 'Get latest news headlines',
    '/backup': 'Create backup of all data',
    '/stats': 'Show storage statistics',
    '/qr': 'Generate QR code (usage: /qr text)',
    '/password': 'Generate secure password (usage: /password 16)',
    '/todo': 'Open todo list manager',
    '/quit': 'Exit to menu'
}

def handle_command(cmd, args):
    """Handle slash commands"""
    if cmd == '/help':
        help_text = f"📖 {APP_NAME} Commands:\n"
        for k, v in COMMANDS.items():
            help_text += f"  {k:<12} - {v}\n"
        help_text += f"\n💡 Need help? Visit {REPO_URL}\n"
        help_text += f"👨‍💻 Created by: {AUTHOR} (Discord: {AUTHOR_DISCORD})"
        return help_text
    
    elif cmd == '/clear':
        global HISTORY
        HISTORY = []
        log_message("SYSTEM", "Conversation cleared")
        return "✓ Conversation history cleared"
    
    elif cmd == '/save':
        save_chat_session()
        return ""
    
    elif cmd == '/load':
        load_chat_session()
        return ""
    
    elif cmd == '/run':
        print(f"{get_rgb(100, 255, 100)}📝 Paste Python code (type 'END' on a new line to finish):\n{get_rgb(200, 200, 200)}")
        lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
        code = '\n'.join(lines)
        return execute_python(code)
    
    elif cmd == '/search':
        if not args:
            return "Usage: /search your query here"
        return web_search(args)
    
    elif cmd == '/read':
        if not args:
            return "Usage: /read filename.txt"
        return read_file(args.strip())
    
    elif cmd == '/write':
        if not args:
            return "Usage: /write filename.txt\nThen paste content and type END on new line"
        filename = args.strip()
        print(f"{get_rgb(100, 255, 100)}📝 Paste content (type 'END' on a new line to finish):\n{get_rgb(200, 200, 200)}")
        lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
        content = '\n'.join(lines)
        return write_file(filename, content)
    
    elif cmd == '/exec':
        if not args:
            return "Usage: /exec command"
        return execute_terminal(args)
    
    elif cmd == '/sysinfo':
        return get_system_info()
    
    elif cmd == '/model':
        switch_model()
        return ""
    
    elif cmd == '/export':
        export_to_markdown()
        return ""
    
    elif cmd == '/voice':
        if HISTORY and len(HISTORY) >= 2:
            last_response = HISTORY[-1]['content']
            return text_to_speech(last_response)
        return "No response to speak"
    
    elif cmd == '/download':
        if not args:
            return "Usage: /download URL"
        parts = args.split()
        url = parts[0]
        filename = parts[1] if len(parts) > 1 else None
        return download_file(url, filename)
    
    elif cmd == '/weather':
        if not args:
            return "Usage: /weather city_name"
        return get_weather(args)
    
    elif cmd == '/news':
        return get_news()
    
    elif cmd == '/backup':
        return create_backup()
    
    elif cmd == '/stats':
        return show_storage_stats()
    
    elif cmd == '/qr':
        if not args:
            return "Usage: /qr text to encode"
        return generate_qr(args)
    
    elif cmd == '/password':
        length = int(args) if args and args.isdigit() else 16
        return generate_password(length)
    
    elif cmd == '/todo':
        return todo_list()
    
    elif cmd == '/quit':
        return "QUIT"
    
    else:
        return f"Unknown command: {cmd}. Type /help for available commands."

# ==================== MAIN CHAT FUNCTION ====================
def ai_chat():
    global API_KEY, HISTORY, CURRENT_MODEL, CUSTOM_PROMPT
    
    if not API_KEY:
        clear()
        print_header()
        print("\n" + get_rgb(255, 100, 100) + "╔════════════════════════════════════════════╗")
        print("║  ❌ ERROR: No API key configured!          ║")
        print("║  Please set your API key in settings first ║")
        print("╚════════════════════════════════════════════╝\033[0m")
        time.sleep(2)
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
        
        if user_input.startswith('/'):
            parts = user_input.split(' ', 1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ''
            response = handle_command(cmd, args)
            if response == "QUIT":
                break
            if response:
                print(f"\n{get_rgb(0, 200, 255)}┌─[ SYSTEM ]────────────────────────────────────────┐")
                print(f"{response}")
                print("└─────────────────────────────────────────────────────────┘\033[0m")
                input("\nPress Enter to continue...")
            continue
        
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
                print(f"\n{get_rgb(255, 80, 80)}╔══════════════════════════════════════════════════╗")
                print(f"║  ❌ API ERROR: {error_msg[:45]:<45} ║")
                print(f"╚══════════════════════════════════════════════════╝\033[0m")
                
                if "no api key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                    print(f"\n{get_rgb(255, 200, 0)}💡 Your API key is invalid. Please reconfigure it.\033[0m")
            else:
                content = data['choices'][0]['message']['content']
                content = highlight_code(content)
                
                HISTORY.append({"role": "user", "content": user_input})
                HISTORY.append({"role": "assistant", "content": content})
                
                if len(HISTORY) > 40:
                    HISTORY = HISTORY[-40:]
                
                log_message(APP_NAME, content)
                
                for char in content:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(0.002)
                print("\n")
            
        except Exception as e:
            error_str = str(e)
            print(f"\n{get_rgb(255, 80, 80)}╔══════════════════════════════════════════════════╗")
            print(f"║  ❌ CONNECTION ERROR                             ║")
            print(f"║  • Check your internet connection               ║")
            print(f"║  • Verify your API key is correct               ║")
            print(f"║  • Error: {error_str[:35]:<35} ║")
            print(f"╚══════════════════════════════════════════════════╝\033[0m")
        
        print("\n" + get_rgb(100, 100, 100) + "─" * tw)
        print(get_rgb(150, 150, 100) + f"  [Enter] Continue  |  /help for commands  |  /voice to speak  |  /quit to menu\033[0m", end="")
        input()

# ==================== MAIN MENU ====================
def main():
    load_config()
    
    for dir_name in [CHATS_DIR, LOGS_DIR, BACKUP_DIR, PROMPTS_DIR]:
        os.makedirs(dir_name, exist_ok=True)
    
    while True:
        clear()
        print_header()
        tw = os.get_terminal_size().columns
        UI_W = 54
        b_pad = (tw - UI_W) // 2
        
        print("\n" + " " * b_pad + get_rgb(200, 200, 255) + "╔" + "═" * (UI_W - 2) + "╗")
        
        menu_items = [
            f"  🤖 1. Start Chat with {APP_NAME}",
            "  🎨 2. Custom Prompt Manager",
            "  🔑 3. Configure API Key", 
            "  📡 4. Switch AI Model",
            "  💾 5. Backup & Storage",
            "  ℹ️  6. About & Info",
            "  🚪 7. Exit"
        ]
        
        colors = [
            get_rgb(0, 255, 100), get_rgb(255, 100, 255),
            get_rgb(255, 200, 0), get_rgb(100, 200, 255),
            get_rgb(255, 150, 100), get_rgb(200, 200, 200),
            get_rgb(255, 100, 100)
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
            manage_custom_prompt()
        elif choice == '3':
            api_setting()
            save_config()
        elif choice == '4':
            switch_model()
            time.sleep(1)
        elif choice == '5':
            clear()
            print_header()
            print("\n" + get_rgb(100, 255, 100) + "╔════════════════════════════════════════════╗")
            print("║           💾 BACKUP & STORAGE              ║")
            print("╚════════════════════════════════════════════╝\033[0m")
            print("\n" + show_storage_stats())
            print(f"\n{get_rgb(255, 200, 0)}Options:")
            print("  1. Create backup")
            print("  2. View backup directory")
            print("  0. Back")
            backup_choice = input(f"\n{get_rgb(0, 255, 200)}Select: \033[0m")
            if backup_choice == '1':
                print("\n" + create_backup())
                input("\nPress Enter...")
            elif backup_choice == '2':
                if os.path.exists(BACKUP_DIR):
                    subprocess.run(['ls', '-lh', BACKUP_DIR])
                else:
                    print("No backups yet")
                input("\nPress Enter...")
        elif choice == '6':
            clear()
            print_header()
            print("\n" + get_rgb(100, 255, 100) + f"╔════════════════════════════════════════════╗")
            print(f"║     {APP_NAME} v{VERSION} - Terminal AI Companion   ║")
            print("║  ═══════════════════════════════════════════   ║")
            print("║  • Complete AI assistant for Termux            ║")
            print("║  • Powered by OpenRouter API (free tier)       ║")
            print("║  • No cost, no credit card required            ║")
            print("║                                                ║")
            print("║  ✨ FEATURES:                                  ║")
            print("║  • Custom system prompts                       ║")
            print("║  • Code execution & highlighting              ║")
            print("║  • Web search & news                           ║")
            print("║  • File operations & downloads                ║")
            print("║  • Chat save/load/export                      ║")
            print("║  • Voice output (TTS)                         ║")
            print("║  • Todo lists & QR codes                      ║")
            print("║  • Password generator                         ║")
            print("║  • Backup & restore                           ║")
            print("║  • 25+ slash commands                         ║")
            print("║                                                ║")
            print(f"║  👨‍💻 Created by: {AUTHOR}                       ║")
            print(f"║  💬 Discord: {AUTHOR_DISCORD}                   ║")
            print(f"║  📦 GitHub: {REPO_URL}                         ║")
            print("║                                                ║")
            print("║  📝 Type /help in chat for all commands        ║")
            print("╚════════════════════════════════════════════════╝\033[0m")
            input("\nPress Enter to continue...")
        elif choice == '7':
            print("\n" + get_rgb(0, 255, 0) + f"Goodbye from {APP_NAME}! 👋\033[0m")
            sys.exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + get_rgb(0, 255, 0) + f"\nExited. Goodbye from {APP_NAME}!\033[0m")
        sys.exit()
    except Exception as e:
        print(f"\n{get_rgb(255, 0, 0)}Fatal error: {e}\033[0m")
        sys.exit()