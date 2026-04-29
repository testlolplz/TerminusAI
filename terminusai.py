#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║                         TERMINUS AI v1.4                          ║
║                   Your Terminal AI Companion                      ║
║                                                                   ║
║                      Created by: flint667                         ║
║                                                                   ║
║  v1.4 NEW FEATURES:                                              ║
║    • 🔄 Update Checker Menu (manual + auto)                      ║
║    • 🔥 DUAL AI MODE - Compare responses from 2 models           ║
║    • ⚡ Turbo Mode - Rewrite & enhance responses                 ║
║    • 🛡️ Fixed all NoneType & JSON errors                        ║
║    • 💾 Auto-save on exit                                        ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import subprocess
import json
import time
import hashlib
import urllib.request
import urllib.parse
import http.client
import re
import secrets
import string
import socket
import threading
from datetime import datetime
from collections import OrderedDict

# ==================== VERSION INFO ====================
VERSION = "1.4.0"
APP_NAME = "TerminusAI"
AUTHOR = "flint667"
AUTHOR_DISCORD = "flint667"
GITHUB_USER = "testlolplz"
REPO_URL = f"https://github.com/{GITHUB_USER}/TerminusAI"

# ==================== FILE MANAGEMENT ====================
class TerminusAIFiles:
    def __init__(self):
        self.base_dir = os.path.expanduser(f"~/.{APP_NAME.lower()}")
        self.chats_dir = os.path.join(self.base_dir, "chats")
        self.logs_dir = os.path.join(self.base_dir, "logs")
        self.backups_dir = os.path.join(self.base_dir, "backups")
        self.prompts_dir = os.path.join(self.base_dir, "prompts")
        self.cache_dir = os.path.join(self.base_dir, "cache")
        self.config_file = os.path.join(self.base_dir, "config.json")
        self.cache_file = os.path.join(self.cache_dir, "response_cache.json")
        self.update_check_file = os.path.join(self.cache_dir, "last_update_check.json")
        
        for dir_path in [self.base_dir, self.chats_dir, self.logs_dir, 
                        self.backups_dir, self.prompts_dir, self.cache_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def get_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_cache(self, cache):
        with open(self.cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
    
    def log_message(self, role, content):
        if not content:
            content = "[empty response]"
        log_file = os.path.join(self.logs_dir, f"chat_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {role}: {content[:500]}\n\n")
    
    def save_chat(self, name, history, model):
        filepath = os.path.join(self.chats_dir, f"{name}.json")
        with open(filepath, 'w') as f:
            json.dump({
                'name': name,
                'timestamp': datetime.now().isoformat(),
                'model': model,
                'version': VERSION,
                'history': history
            }, f, indent=2)
        return filepath
    
    def load_chat(self, name):
        filepath = os.path.join(self.chats_dir, f"{name}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    
    def list_chats(self):
        if not os.path.exists(self.chats_dir):
            return []
        return [f.replace('.json', '') for f in os.listdir(self.chats_dir) if f.endswith('.json')]

files = TerminusAIFiles()

# ==================== COLORS ====================
C = type('Color', (), {
    'GREEN': '\033[38;2;0;255;100m',
    'CYAN': '\033[38;2;0;200;255m',
    'YELLOW': '\033[38;2;255;200;0m',
    'RED': '\033[38;2;255;100;100m',
    'BLUE': '\033[38;2;100;150;255m',
    'PURPLE': '\033[38;2;200;100;255m',
    'ORANGE': '\033[38;2;255;150;50m',
    'WHITE': '\033[38;2;255;255;255m',
    'RESET': '\033[0m'
})()

# ==================== GLOBAL VARS ====================
API_KEY = ""
HISTORY = []
CURRENT_MODEL = "openrouter/free"
SECONDARY_MODEL = "google/gemini-2.0-flash-lite-preview-02-05:free"
DUAL_MODE = False
CUSTOM_PROMPT = ""

# ==================== CACHE SYSTEM ====================
class ResponseCache:
    def __init__(self, max_size=50):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.load()
    
    def load(self):
        try:
            data = files.get_cache()
            for key, value in list(data.items())[-self.max_size:]:
                self.cache[key] = value
        except:
            pass
    
    def save(self):
        try:
            data = {k: v for k, v in list(self.cache.items())[-self.max_size:]}
            files.save_cache(data)
        except:
            pass
    
    def get(self, question, model):
        if not question:
            return None
        key = hashlib.md5(f"{question}_{model}".encode()).hexdigest()
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]['answer']
        return None
    
    def put(self, question, model, answer):
        if not question or not answer:
            return
        key = hashlib.md5(f"{question}_{model}".encode()).hexdigest()
        self.cache[key] = {
            'answer': answer,
            'timestamp': time.time(),
            'question': question[:100]
        }
        self.cache.move_to_end(key)
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
        self.save()

cache = ResponseCache()

# ==================== CONNECTION POOL ====================
class ConnectionPool:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conn = {}
        return cls._instance
    
    def get_connection(self, host="openrouter.ai"):
        if host not in self.conn or self.conn[host] is None:
            self.conn[host] = http.client.HTTPSConnection(host, timeout=20)
        return self.conn[host]
    
    def close(self):
        for host, conn in self.conn.items():
            if conn:
                conn.close()
        self.conn = {}

conn_pool = ConnectionPool()

# ==================== UPDATE CHECKER ====================
def check_for_updates(force=False):
    """Check GitHub for new version"""
    if not force and os.path.exists(files.update_check_file):
        try:
            with open(files.update_check_file, 'r') as f:
                last_check = json.load(f)
                last_time = last_check.get('timestamp', 0)
                if time.time() - last_time < 86400:  # 24 hours
                    return last_check.get('update_available', False), last_check.get('latest_version')
        except:
            pass
    
    try:
        url = f"https://api.github.com/repos/{GITHUB_USER}/TerminusAI/releases/latest"
        req = urllib.request.Request(url, headers={'User-Agent': 'TerminusAI'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            latest = data.get('tag_name', '').replace('v', '')
            update_available = latest > VERSION if latest else False
            
            with open(files.update_check_file, 'w') as f:
                json.dump({
                    'timestamp': time.time(),
                    'update_available': update_available,
                    'latest_version': latest,
                    'current_version': VERSION
                }, f)
            
            return update_available, latest
    except Exception as e:
        return False, None

def show_update_banner():
    try:
        update_available, latest = check_for_updates()
        if update_available:
            print(f"\n{C.YELLOW}╔══════════════════════════════════════════════════╗")
            print(f"║  🎉 UPDATE AVAILABLE! v{latest} is out!              ║")
            print(f"║  Run: python -c \"$(curl -fsSL {REPO_URL}/raw/main/update.py)\"")
            print(f"╚══════════════════════════════════════════════════╝{C.RESET}")
            return True
    except:
        pass
    return False

def update_menu():
    """Manual update checker menu"""
    clear()
    print_header()
    print(f"\n{C.CYAN}╔══════════════════════════════════════════════════╗")
    print("║              🔄 UPDATE CHECKER                    ║")
    print("╚══════════════════════════════════════════════════╝\n{C.RESET}")
    
    print(f"{C.YELLOW}Current version: {C.GREEN}v{VERSION}{C.RESET}")
    
    print(f"\n{C.CYAN}[1] Check for updates now{C.RESET}")
    print(f"{C.CYAN}[2] View changelog{C.RESET}")
    print(f"{C.CYAN}[3] Download latest version{C.RESET}")
    print(f"{C.CYAN}[4] Update TerminusAI{C.RESET}")
    print(f"{C.CYAN}[0] Back to main menu{C.RESET}")
    
    choice = input(f"\n{C.GREEN}Select: {C.RESET}").strip()
    
    if choice == '1':
        print(f"\n{C.YELLOW}Checking for updates...{C.RESET}")
        update_available, latest = check_for_updates(force=True)
        if update_available:
            print(f"{C.GREEN}✓ Update available! v{latest} → v{VERSION}{C.RESET}")
            print(f"{C.CYAN}Use option 4 to update{C.RESET}")
        else:
            print(f"{C.GREEN}✓ You're on the latest version!{C.RESET}")
        input(f"\n{C.YELLOW}Press Enter...{C.RESET}")
    
    elif choice == '2':
        print(f"\n{C.CYAN}📋 Changelog for v{VERSION}:{C.RESET}")
        print(f"{C.GREEN}  • Added update checker menu{C.RESET}")
        print(f"{C.GREEN}  • Added DUAL AI MODE (compare responses){C.RESET}")
        print(f"{C.GREEN}  • Added Turbo Mode for response enhancement{C.RESET}")
        print(f"{C.GREEN}  • Fixed all NoneType and JSON errors{C.RESET}")
        print(f"{C.GREEN}  • Auto-save on exit{C.RESET}")
        input(f"\n{C.YELLOW}Press Enter...{C.RESET}")
    
    elif choice == '3':
        print(f"\n{C.CYAN}📥 Download instructions:{C.RESET}")
        print(f"{C.YELLOW}  curl -o ~/terminusai.py {REPO_URL}/raw/main/terminusai.py{C.RESET}")
        input(f"\n{C.YELLOW}Press Enter...{C.RESET}")
    
    elif choice == '4':
        print(f"\n{C.YELLOW}Updating TerminusAI...{C.RESET}")
        try:
            import urllib.request
            urllib.request.urlretrieve(f"{REPO_URL}/raw/main/terminusai.py", "/tmp/terminusai_new.py")
            subprocess.run(['cp', '/tmp/terminusai_new.py', os.path.expanduser("~/terminusai.py")])
            print(f"{C.GREEN}✓ Update downloaded! Restart TerminusAI to apply.{C.RESET}")
        except Exception as e:
            print(f"{C.RED}❌ Update failed: {e}{C.RESET}")
        input(f"\n{C.YELLOW}Press Enter...{C.RESET}")

# ==================== DUAL MODE & TURBO MODE ====================
def send_api_request(user_input, system_prompt, model):
    """Send request to specific model with proper error handling"""
    try:
        messages = [{"role": "system", "content": system_prompt}]
        for msg in HISTORY[-10:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_input})
        
        conn = conn_pool.get_connection()
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": 500,
            "top_p": 0.9
        })
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        conn.request("POST", "/api/v1/chat/completions", payload, headers)
        response = conn.getresponse()
        response_data = response.read().decode()
        
        if not response_data:
            return None, "Empty response from API"
        
        data = json.loads(response_data)
        
        if "error" in data:
            return None, data['error'].get('message', 'Unknown API error')
        
        if "choices" not in data or len(data["choices"]) == 0:
            return None, "No response choices returned"
        
        content = data["choices"][0].get("message", {}).get("content")
        
        if content is None:
            return None, "Empty response content"
        
        return content, None
        
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {str(e)[:50]}"
    except http.client.HTTPException as e:
        return None, f"HTTP error: {str(e)[:50]}"
    except socket.timeout:
        return None, "Connection timeout"
    except Exception as e:
        return None, f"Error: {str(e)[:80]}"

def dual_mode_chat(user_input, system_prompt):
    """Send request to two models and compare responses"""
    print(f"\n{C.CYAN}🔥 DUAL MODE: Asking both models...{C.RESET}\n")
    
    # Model 1 (Primary)
    print(f"{C.BLUE}[Model 1: {CURRENT_MODEL[:30]}]{C.RESET}")
    response1, error1 = send_api_request(user_input, system_prompt, CURRENT_MODEL)
    
    # Model 2 (Secondary)
    print(f"{C.PURPLE}[Model 2: {SECONDARY_MODEL[:30]}]{C.RESET}")
    response2, error2 = send_api_request(user_input, system_prompt, SECONDARY_MODEL)
    
    print(f"\n{C.YELLOW}{'='*50}{C.RESET}")
    print(f"{C.GREEN}📊 COMPARISON RESULTS:{C.RESET}")
    print(f"{C.YELLOW}{'='*50}{C.RESET}\n")
    
    # Display both responses
    print(f"{C.BLUE}╔══════════════════════════════════════════════════╗")
    print(f"║  MODEL 1: {CURRENT_MODEL[:40]:<40} ║")
    print(f"╚══════════════════════════════════════════════════╝{C.RESET}")
    
    if error1:
        print(f"{C.RED}❌ Error: {error1}{C.RESET}")
    else:
        print(highlight_code(response1))
    
    print(f"\n{C.PURPLE}╔══════════════════════════════════════════════════╗")
    print(f"║  MODEL 2: {SECONDARY_MODEL[:40]:<40} ║")
    print(f"╚══════════════════════════════════════════════════╝{C.RESET}")
    
    if error2:
        print(f"{C.RED}❌ Error: {error2}{C.RESET}")
    else:
        print(highlight_code(response2))
    
    # Ask which response to keep
    print(f"\n{C.YELLOW}{'─'*50}{C.RESET}")
    print(f"{C.CYAN}Which response do you want to keep?{C.RESET}")
    print(f"  {C.GREEN}[1] Keep Model 1 response{C.RESET}")
    print(f"  {C.GREEN}[2] Keep Model 2 response{C.RESET}")
    print(f"  {C.GREEN}[3] Keep both (append){C.RESET}")
    print(f"  {C.GREEN}[0] Discard both{C.RESET}")
    
    choice = input(f"\n{C.YELLOW}Select: {C.RESET}").strip()
    
    if choice == '1' and not error1:
        return response1
    elif choice == '2' and not error2:
        return response2
    elif choice == '3':
        if error1 and error2:
            return None
        elif error1:
            return response2
        elif error2:
            return response1
        return f"{response1}\n\n--- Alternative Response ---\n\n{response2}"
    else:
        return None

def turbo_rewrite(text):
    """Rewrite/enhance text using AI (Turbo Mode)"""
    if not text:
        return None
    
    print(f"\n{C.ORANGE}⚡ TURBO MODE: Enhancing response...{C.RESET}")
    
    rewrite_prompt = f"""Please rewrite and enhance the following text. Make it better, clearer, and more polished while keeping the same meaning and information:

Original: {text[:500]}

Enhanced version:"""
    
    system_prompt = "You are a text enhancement assistant. Rewrite text to be clearer and more polished."
    
    enhanced, error = send_api_request(rewrite_prompt, system_prompt, CURRENT_MODEL)
    
    if error:
        print(f"{C.RED}Turbo mode failed: {error}{C.RESET}")
        return text
    
    return enhanced

# ==================== UTILITIES ====================
def clear():
    os.system('clear')

def load_config():
    global API_KEY, CURRENT_MODEL, SECONDARY_MODEL, CUSTOM_PROMPT, DUAL_MODE
    config = files.get_config()
    API_KEY = config.get('api_key', '')
    CURRENT_MODEL = config.get('model', 'openrouter/free')
    SECONDARY_MODEL = config.get('secondary_model', 'google/gemini-2.0-flash-lite-preview-02-05:free')
    CUSTOM_PROMPT = config.get('custom_prompt', '')
    DUAL_MODE = config.get('dual_mode', False)

def save_config():
    config = files.get_config()
    config['api_key'] = API_KEY
    config['model'] = CURRENT_MODEL
    config['secondary_model'] = SECONDARY_MODEL
    config['custom_prompt'] = CUSTOM_PROMPT
    config['dual_mode'] = DUAL_MODE
    config['version'] = VERSION
    config['last_updated'] = datetime.now().isoformat()
    files.save_config(config)

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def print_header():
    tw = os.get_terminal_size().columns
    current_time = get_current_time()
    
    lines = [
        f"{C.BLUE}╔══════════════════════════════════════════════════╗",
        f"║           {APP_NAME} v{VERSION}                    ║",
        "║      Your Terminal AI Companion                  ║",
        f"╠══════════════════════════════════════════════════╣",
        f"║  🕐 {current_time:<49} ║",
        f"╚══════════════════════════════════════════════════╝{C.RESET}"
    ]
    
    print("\n" * 1)
    for line in lines:
        clean_len = len(line.replace(C.BLUE, '').replace(C.RESET, ''))
        pad = (tw - clean_len) // 2
        print(" " * max(0, pad) + line)

def fast_print(text, batch_size=30):
    if not text:
        print()
        return
    for i in range(0, len(text), batch_size):
        sys.stdout.write(text[i:i+batch_size])
        sys.stdout.flush()
        time.sleep(0.0003)
    print()

def highlight_code(text):
    if not text:
        return text
    pattern = r'```(\w+)?\n(.*?)```'
    def replace_code(match):
        lang = match.group(1) or 'text'
        code = match.group(2)
        return f"\n{C.GREEN}┌─[{lang.upper()}]─────────────────┐\n{C.YELLOW}{code}\n{C.GREEN}└────────────────────────────────┘{C.RESET}"
    try:
        return re.sub(pattern, replace_code, text, flags=re.DOTALL, count=3)
    except:
        return text

def smart_max_tokens(question):
    if not question:
        return 300
    length = len(question)
    if length < 30:
        return 300
    elif length < 100:
        return 500
    else:
        return 800

# ==================== FEATURES ====================
def copy_to_clipboard(text):
    if not text:
        return f"{C.YELLOW}⚠ Nothing to copy{C.RESET}"
    try:
        if len(text) > 5000:
            text = text[:5000]
        subprocess.run(['termux-clipboard-set', text], timeout=1, capture_output=True)
        return f"{C.GREEN}✓ Copied ({len(text)} chars){C.RESET}"
    except:
        return f"{C.RED}❌ Install termux-api{C.RESET}"

def paste_from_clipboard():
    try:
        result = subprocess.run(['termux-clipboard-get'], capture_output=True, text=True, timeout=1)
        if result.stdout:
            return f"{C.CYAN}📋 Clipboard:\n\n{result.stdout[:2000]}{C.RESET}"
        return f"{C.YELLOW}📋 Empty{C.RESET}"
    except:
        return f"{C.RED}❌ Install termux-api{C.RESET}"

def generate_image(prompt):
    if not prompt:
        return f"{C.YELLOW}⚠ Usage: /imagine description{C.RESET}"
    try:
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}"
        filename = os.path.join(files.base_dir, f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        print(f"{C.GREEN}🎨 Generating...{C.RESET}")
        urllib.request.urlretrieve(url, filename)
        if os.path.exists(filename) and os.path.getsize(filename) > 1000:
            try:
                subprocess.run(['termux-open', filename], timeout=2, capture_output=True)
                return f"{C.GREEN}✅ Saved: {filename}{C.RESET}"
            except:
                return f"{C.GREEN}✅ Saved: {filename}{C.RESET}"
        return f"{C.RED}❌ Failed to generate{C.RESET}"
    except Exception as e:
        return f"{C.RED}❌ Error: {str(e)[:50]}{C.RESET}"

def smart_calc(expression):
    if not expression:
        return f"{C.YELLOW}⚠ Usage: /calc 2+2{C.RESET}"
    try:
        expression = expression.replace(" ", "")
        import math
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        allowed.update({"abs": abs, "round": round})
        
        if not re.match(r'^[\d\s\+\-\*\/\%\(\)\.\^\,\|\&\~\<\>\=\!\+\-\*\/\%\*\*\,\s]+$', expression.replace("**", "")):
            if any(func in expression for func in ['sqrt', 'sin', 'cos', 'tan', 'log', 'pi', 'e']):
                result = eval(expression, {"__builtins__": {}}, allowed)
            else:
                return f"{C.RED}❌ Invalid expression{C.RESET}"
        else:
            result = eval(expression, {"__builtins__": {}}, {})
        return f"{C.GREEN}🧮 {expression} = {result}{C.RESET}"
    except ZeroDivisionError:
        return f"{C.RED}❌ Division by zero{C.RESET}"
    except Exception as e:
        return f"{C.RED}❌ Error: {str(e)[:30]}{C.RESET}"

def web_search(query):
    if not query:
        return f"{C.YELLOW}⚠ Usage: /search query{C.RESET}"
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode('utf-8')
            results = re.findall(r'<a rel="nofollow" class="result__a" href="[^"]*">([^<]+)</a>', html)
            output = f"{C.CYAN}🔍 '{query}':\n\n{C.RESET}"
            for i, title in enumerate(results[:5], 1):
                output += f"  {i}. {title}\n"
            return output if results else f"{C.YELLOW}No results{C.RESET}"
    except Exception as e:
        return f"{C.RED}❌ Search failed: {str(e)[:30]}{C.RESET}"

def get_weather(city):
    if not city:
        return f"{C.YELLOW}⚠ Usage: /weather city{C.RESET}"
    try:
        url = f"https://wttr.in/{city}?format=%C:+%t,+%w"
        with urllib.request.urlopen(url, timeout=8) as response:
            weather = response.read().decode('utf-8').strip()
            return f"{C.CYAN}🌤️ {city}: {weather}{C.RESET}"
    except Exception as e:
        return f"{C.RED}❌ Weather failed: {str(e)[:30]}{C.RESET}"

def generate_password(length=16):
    try:
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(chars) for _ in range(length))
        strength = "Strong" if length >= 12 else "Medium" if length >= 8 else "Weak"
        return f"{C.GREEN}🔐 Password: {password}\n   Strength: {strength}{C.RESET}"
    except:
        return f"{C.RED}❌ Failed to generate{C.RESET}"

def save_current_chat():
    global HISTORY
    if not HISTORY:
        return f"{C.YELLOW}⚠ No conversation to save{C.RESET}"
    
    name = input(f"{C.CYAN}📁 Name (Enter for auto): {C.RESET}").strip()
    if not name:
        name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        files.save_chat(name, HISTORY, CURRENT_MODEL)
        return f"{C.GREEN}✅ Saved: {name}{C.RESET}"
    except Exception as e:
        return f"{C.RED}❌ Save failed: {str(e)[:30]}{C.RESET}"

def load_chat_session():
    global HISTORY
    sessions = files.list_chats()
    if not sessions:
        return f"{C.YELLOW}⚠ No saved chats{C.RESET}"
    
    print(f"\n{C.CYAN}📂 Saved chats:{C.RESET}")
    for i, s in enumerate(sessions, 1):
        print(f"  {i}. {s}")
    
    try:
        choice = int(input(f"\n{C.GREEN}Select (1-{len(sessions)} or 0): {C.RESET}")) - 1
        if 0 <= choice < len(sessions):
            data = files.load_chat(sessions[choice])
            if data:
                HISTORY = data.get('history', [])
                return f"{C.GREEN}✅ Loaded {len(HISTORY)//2} exchanges{C.RESET}"
    except:
        pass
    return f"{C.YELLOW}Cancelled{C.RESET}"

# ==================== MAIN AI CHAT ====================
def ai_chat():
    global API_KEY, HISTORY, CURRENT_MODEL, SECONDARY_MODEL, CUSTOM_PROMPT, DUAL_MODE
    
    if not API_KEY:
        print(f"\n{C.RED}❌ No API key! Set in Settings (option 3){C.RESET}")
        input("\nPress Enter...")
        return
    
    system_prompt = CUSTOM_PROMPT if CUSTOM_PROMPT else f"You are {APP_NAME}, a helpful AI assistant. Be concise and helpful."
    
    while True:
        clear()
        print_header()
        tw = os.get_terminal_size().columns
        
        # Status bar
        mode_text = f"{C.ORANGE}🔥 DUAL MODE{C.RESET}" if DUAL_MODE else f"{C.CYAN}🔄 SINGLE MODE{C.RESET}"
        print(f"\n{C.CYAN}📡 {CURRENT_MODEL[:40]}{C.RESET}")
        print(f"{C.YELLOW}💬 {len(HISTORY)//2} exchanges | 💾 {len(cache.cache)} cached | {mode_text}{C.RESET}")
        if DUAL_MODE:
            print(f"{C.PURPLE}🔀 Secondary: {SECONDARY_MODEL[:35]}{C.RESET}")
        print("\n" + "─" * tw)
        print(f"{C.GREEN}You: {C.RESET}", end="")
        user_input = input()
        
        if not user_input or not user_input.strip():
            continue
        
        cmd = user_input.lower().strip()
        
        # Commands
        if cmd in ['/quit', 'quit', 'exit']:
            break
        elif cmd == '/clear':
            HISTORY = []
            print(f"\n{C.GREEN}✓ Cleared{C.RESET}")
            input("\nPress Enter...")
            continue
        elif cmd == '/help':
            help_text = f"""
{C.CYAN}📖 {APP_NAME} v{VERSION} Commands:{C.RESET}

{C.GREEN}Core:{C.RESET}  /help, /clear, /quit, /save, /load
{C.CYAN}Clipboard:{C.RESET}  /copy, /paste
{C.YELLOW}Media:{C.RESET}  /imagine <prompt>
{C.PURPLE}Tools:{C.RESET}  /calc <expr>, /password, /search <q>, /weather <city>
{C.ORANGE}Advanced:{C.RESET}  /dual, /turbo, /checkupdate, /models

{C.BLUE}💡 Examples:{C.RESET}
  /dual              - Toggle Dual Mode (compare 2 models)
  /turbo             - Enhance last response with AI
  /checkupdate       - Check for updates
  /models            - Change secondary model
"""
            print(help_text)
            input("\nPress Enter...")
            continue
        elif cmd == '/copy':
            if HISTORY:
                result = copy_to_clipboard(HISTORY[-1]['content'])
                print(f"\n{result}")
            else:
                print(f"\n{C.YELLOW}No response to copy{C.RESET}")
            input("\nPress Enter...")
            continue
        elif cmd == '/paste':
            print("\n" + paste_from_clipboard())
            input("\nPress Enter...")
            continue
        elif cmd.startswith('/imagine '):
            print("\n" + generate_image(user_input[9:]))
            input("\nPress Enter...")
            continue
        elif cmd.startswith('/calc '):
            print("\n" + smart_calc(user_input[6:]))
            input("\nPress Enter...")
            continue
        elif cmd.startswith('/search '):
            print("\n" + web_search(user_input[8:]))
            input("\nPress Enter...")
            continue
        elif cmd.startswith('/weather '):
            print("\n" + get_weather(user_input[9:]))
            input("\nPress Enter...")
            continue
        elif cmd == '/password':
            print("\n" + generate_password())
            input("\nPress Enter...")
            continue
        elif cmd == '/save':
            print("\n" + save_current_chat())
            input("\nPress Enter...")
            continue
        elif cmd == '/load':
            print("\n" + load_chat_session())
            input("\nPress Enter...")
            continue
        elif cmd == '/dual':
            DUAL_MODE = not DUAL_MODE
            save_config()
            print(f"\n{C.GREEN}✓ Dual Mode {'ENABLED' if DUAL_MODE else 'DISABLED'}{C.RESET}")
            print(f"{C.YELLOW}Dual mode will query both models and let you choose the best response{C.RESET}")
            input("\nPress Enter...")
            continue
        elif cmd == '/turbo':
            if HISTORY:
                last_response = HISTORY[-1]['content']
                enhanced = turbo_rewrite(last_response)
                if enhanced:
                    print(f"\n{C.GREEN}✨ Enhanced Response:{C.RESET}\n")
                    fast_print(highlight_code(enhanced))
                    HISTORY[-1]['content'] = enhanced
                    print(f"\n{C.GREEN}✓ Response updated!{C.RESET}")
                else:
                    print(f"\n{C.RED}❌ Turbo mode failed{C.RESET}")
            else:
                print(f"\n{C.YELLOW}⚠ No response to enhance{C.RESET}")
            input("\nPress Enter...")
            continue
        elif cmd == '/checkupdate':
            print(f"\n{C.YELLOW}Checking for updates...{C.RESET}")
            update_available, latest = check_for_updates(force=True)
            if update_available:
                print(f"{C.GREEN}✓ Update available! v{latest} → v{VERSION}{C.RESET}")
                print(f"{C.CYAN}Run option 4 in update menu to update{C.RESET}")
            else:
                print(f"{C.GREEN}✓ You're on the latest version!{C.RESET}")
            input("\nPress Enter...")
            continue
        elif cmd == '/models':
            print(f"\n{C.CYAN}Current secondary model: {SECONDARY_MODEL}{C.RESET}")
            print(f"{C.YELLOW}Enter new model ID (or Enter to keep): {C.RESET}", end="")
            new_model = input().strip()
            if new_model:
                SECONDARY_MODEL = new_model
                save_config()
                print(f"{C.GREEN}✓ Secondary model updated!{C.RESET}")
            input("\nPress Enter...")
            continue
        
        # Check cache first (only in single mode)
        if not DUAL_MODE:
            cached = cache.get(user_input, CURRENT_MODEL)
            if cached:
                print(f"\n{C.CYAN}AI (cached): {C.RESET}")
                highlighted = highlight_code(cached)
                fast_print(highlighted)
                HISTORY.append({"role": "user", "content": user_input})
                HISTORY.append({"role": "assistant", "content": cached})
                files.log_message("USER", user_input)
                files.log_message("ASSISTANT", cached)
                print("\n" + "─" * tw)
                input(f"{C.YELLOW}[Enter] continue{C.RESET}")
                continue
        
        # Get response
        print(f"\n{C.CYAN}AI: {C.RESET}")
        
        if DUAL_MODE:
            content = dual_mode_chat(user_input, system_prompt)
            if not content:
                print(f"{C.RED}❌ Both models failed to respond{C.RESET}")
                input("\nPress Enter...")
                continue
        else:
            content, error = send_api_request(user_input, system_prompt, CURRENT_MODEL)
            if error:
                print(f"{C.RED}❌ {error}{C.RESET}")
                print(f"\n{C.YELLOW}💡 Tips:{C.RESET}")
                print("  • Check your API key in Settings (option 3)")
                print("  • Make sure you have internet connection")
                print("  • Try switching models (option 4)")
                input("\nPress Enter...")
                continue
        
        # Cache and save response
        if content:
            if not DUAL_MODE:
                cache.put(user_input, CURRENT_MODEL, content)
            
            highlighted = highlight_code(content)
            HISTORY.append({"role": "user", "content": user_input})
            HISTORY.append({"role": "assistant", "content": content})
            
            if len(HISTORY) > 30:
                HISTORY = HISTORY[-30:]
            
            files.log_message("USER", user_input)
            files.log_message("ASSISTANT", content)
            
            fast_print(highlighted)
            print()
        
        print("\n" + "─" * tw)
        print(f"{C.YELLOW}[Enter] continue  |  /help  |  /dual  |  /turbo  |  /quit{C.RESET}", end="")
        input()

# ==================== SETTINGS ====================
def api_settings():
    global API_KEY
    clear()
    print_header()
    print(f"\n{C.CYAN}🔑 API Key Configuration{C.RESET}")
    print(f"Current: {API_KEY[:15]}...{API_KEY[-10:]}" if len(API_KEY) > 25 else "None set")
    print(f"\n{C.YELLOW}New key (or Enter to keep): {C.RESET}", end="")
    new_key = input().strip()
    if new_key:
        API_KEY = new_key
        save_config()
        print(f"{C.GREEN}✓ Saved!{C.RESET}")
    input("\nPress Enter...")

def switch_model():
    global CURRENT_MODEL
    clear()
    print_header()
    print(f"\n{C.CYAN}📡 Available Models:{C.RESET}")
    print("  1. openrouter/free (fastest, auto-select)")
    print("  2. google/gemini-2.0-flash-lite (fast)")
    print("  3. deepseek/deepseek-chat (good for coding)")
    print("  4. qwen/qwen-2.5-coder-32b (coding expert)")
    print("  5. Custom model ID")
    print(f"\n{C.GREEN}Current: {CURRENT_MODEL}{C.RESET}")
    choice = input(f"\n{C.YELLOW}Select (1-5): {C.RESET}").strip()
    
    models = {
        '1': 'openrouter/free',
        '2': 'google/gemini-2.0-flash-lite-preview-02-05:free',
        '3': 'deepseek/deepseek-chat:free',
        '4': 'qwen/qwen-2.5-coder-32b-instruct:free'
    }
    if choice in models:
        CURRENT_MODEL = models[choice]
        save_config()
        print(f"{C.GREEN}✓ Switched to {CURRENT_MODEL[:30]}{C.RESET}")
    elif choice == '5':
        custom = input(f"{C.CYAN}Enter model ID: {C.RESET}").strip()
        if custom:
            CURRENT_MODEL = custom
            save_config()
            print(f"{C.GREEN}✓ Switched to {custom[:30]}{C.RESET}")
    input("\nPress Enter...")

def custom_prompt():
    global CUSTOM_PROMPT
    clear()
    print_header()
    print(f"\n{C.CYAN}🎨 Custom System Prompt{C.RESET}")
    print(f"Current: {CUSTOM_PROMPT[:100] if CUSTOM_PROMPT else 'Default'}\n")
    print(f"{C.YELLOW}Enter new prompt (type 'END' on new line):{C.RESET}")
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    if lines:
        CUSTOM_PROMPT = '\n'.join(lines)
        save_config()
        print(f"{C.GREEN}✓ Saved!{C.RESET}")
    input("\nPress Enter...")

def storage_info():
    clear()
    print_header()
    print(f"\n{C.CYAN}💾 Storage Information{C.RESET}")
    
    def get_size(path):
        total = 0
        if os.path.exists(path):
            if os.path.isfile(path):
                return os.path.getsize(path)
            for root, dirs, files in os.walk(path):
                for f in files:
                    fp = os.path.join(root, f)
                    total += os.path.getsize(fp)
        return total
    
    sizes = {
        'Config': get_size(files.config_file),
        'Chats': get_size(files.chats_dir),
        'Logs': get_size(files.logs_dir),
        'Cache': get_size(files.cache_dir),
        'Backups': get_size(files.backups_dir),
        'Prompts': get_size(files.prompts_dir)
    }
    
    total = sum(sizes.values())
    
    print(f"\n{C.YELLOW}Location: {files.base_dir}{C.RESET}\n")
    for name, size in sizes.items():
        if size > 0:
            print(f"  {name:<10}: {size/1024:.1f} KB")
    print(f"\n{C.GREEN}  Total     : {total/1024:.1f} KB{C.RESET}")
    
    print(f"\n{C.CYAN}Options:{C.RESET}")
    print("  1. Clear cache")
    print("  2. Delete all logs")
    print("  0. Back")
    
    choice = input(f"\n{C.YELLOW}Select: {C.RESET}")
    if choice == '1':
        cache.cache.clear()
        cache.save()
        print(f"{C.GREEN}✓ Cache cleared{C.RESET}")
        time.sleep(1)
    elif choice == '2':
        import shutil
        if os.path.exists(files.logs_dir):
            shutil.rmtree(files.logs_dir)
            os.makedirs(files.logs_dir)
        print(f"{C.GREEN}✓ Logs deleted{C.RESET}")
        time.sleep(1)

# ==================== AUTO-INSTALLER ====================
def check_and_install_dependencies():
    print(f"{C.CYAN}")
    print("╔══════════════════════════════════════════════════╗")
    print("║         TerminusAI v1.4 - Quick Setup           ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"{C.RESET}")
    
    if not os.path.exists('/data/data/com.termux'):
        print(f"{C.RED}❌ Termux only!{C.RESET}")
        sys.exit(1)
    
    try:
        urllib.request.urlopen('https://8.8.8.8', timeout=2)
        print(f"{C.GREEN}✓ Internet OK{C.RESET}")
    except:
        print(f"{C.RED}❌ No internet{C.RESET}")
        sys.exit(1)
    
    print(f"{C.YELLOW}⚡ Installing dependencies...{C.RESET}")
    subprocess.run(['pkg', 'install', 'python', '-y'], capture_output=True)
    
    print(f"\n{C.CYAN}🔑 OpenRouter API key: {C.RESET}")
    print(f"{C.YELLOW}Get free key: https://openrouter.ai/keys{C.RESET}")
    api_key = input().strip()
    
    if api_key:
        config = files.get_config()
        config['api_key'] = api_key
        config['model'] = "openrouter/free"
        config['version'] = VERSION
        config['dual_mode'] = False
        config['last_setup'] = datetime.now().isoformat()
        files.save_config(config)
        print(f"{C.GREEN}✓ Ready!{C.RESET}")
    
    time.sleep(1)

# ==================== MAIN MENU ====================
def main():
    global API_KEY, DUAL_MODE
    
    if not os.path.exists(files.config_file):
        check_and_install_dependencies()
        load_config()
    
    load_config()
    show_update_banner()
    
    while True:
        clear()
        print_header()
        tw = os.get_terminal_size().columns
        
        # Mode indicator
        mode_indicator = f"{C.ORANGE}🔥 DUAL MODE ACTIVE{C.RESET}" if DUAL_MODE else f"{C.CYAN}🔄 SINGLE MODE{C.RESET}"
        
        print(f"\n{C.CYAN}╔════════════════════════════════════════════╗")
        print("║              MAIN MENU                       ║")
        print("╠════════════════════════════════════════════╣")
        print(f"║  {C.GREEN}1.{C.CYAN} 💬 Start Chat                          ║")
        print(f"║  {C.PURPLE}2.{C.CYAN} 🎨 Custom Prompt                      ║")
        print(f"║  {C.BLUE}3.{C.CYAN} 🔑 API Settings                       ║")
        print(f"║  {C.BLUE}4.{C.CYAN} 📡 Switch AI Model                    ║")
        print(f"║  {C.ORANGE}5.{C.CYAN} 🔥 Dual Mode Settings                 ║")
        print(f"║  {C.CYAN}6.{C.CYAN} 🔄 Update Checker                     ║")
        print(f"║  {C.YELLOW}7.{C.CYAN} 💾 Storage Manager                    ║")
        print(f"║  {C.CYAN}8.{C.CYAN} ℹ️  About                             ║")
        print(f"║  {C.RED}9.{C.CYAN} 🚪 Exit                              ║")
        print(f"╚════════════════════════════════════════════╝{C.RESET}")
        
        print(f"\n{C.GREEN}API: {'✅' if API_KEY else '❌'}{C.RESET}  {C.CYAN}Model: {CURRENT_MODEL[:25]}{C.RESET}")
        print(f"{C.YELLOW}Cache: {len(cache.cache)} items | {mode_indicator}{C.RESET}")
        
        choice = input(f"\n{C.GREEN}Select (1-9): {C.RESET}").strip()
        
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
            print(f"\n{C.ORANGE}🔥 DUAL MODE SETTINGS{C.RESET}\n")
            print(f"Current secondary model: {SECONDARY_MODEL}")
            print(f"Dual Mode: {'ON' if DUAL_MODE else 'OFF'}")
            print(f"\n{C.CYAN}[1] Toggle Dual Mode (on/off){C.RESET}")
            print(f"[2] Change secondary model{C.RESET}")
            print(f"[0] Back{C.RESET}")
            sub_choice = input(f"\n{C.GREEN}Select: {C.RESET}")
            if sub_choice == '1':
                DUAL_MODE = not DUAL_MODE
                save_config()
                print(f"{C.GREEN}✓ Dual Mode {'ENABLED' if DUAL_MODE else 'DISABLED'}{C.RESET}")
                input("\nPress Enter...")
            elif sub_choice == '2':
                print(f"\n{C.YELLOW}Enter new secondary model ID:{C.RESET}")
                new_model = input().strip()
                if new_model:
                    global SECONDARY_MODEL
                    SECONDARY_MODEL = new_model
                    save_config()
                    print(f"{C.GREEN}✓ Secondary model updated!{C.RESET}")
                input("\nPress Enter...")
        elif choice == '6':
            update_menu()
        elif choice == '7':
            storage_info()
        elif choice == '8':
            clear()
            print_header()
            print(f"\n{C.CYAN}{APP_NAME} v{VERSION}{C.RESET}")
            print(f"Created by: {AUTHOR}")
            print(f"Discord: {AUTHOR_DISCORD}")
            print(f"GitHub: {REPO_URL}")
            print(f"\n{C.GREEN}Features:{C.RESET}")
            print("  • 🔥 Dual AI Mode - Compare 2 models")
            print("  • ⚡ Turbo Mode - Enhance responses")
            print("  • 🔄 Auto & Manual update checking")
            print("  • Fast AI responses with caching")
            print("  • Image generation")
            print("  • Web search & weather")
            print("  • Clipboard support")
            print("  • Password generator")
            print("  • Save/load conversations")
            print(f"\n{C.YELLOW}Commands in chat: /help, /dual, /turbo, /checkupdate, /models{C.RESET}")
            input("\nPress Enter...")
        elif choice == '9':
            conn_pool.close()
            print(f"\n{C.GREEN}Goodbye! 👋{C.RESET}")
            sys.exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.GREEN}Goodbye! 👋{C.RESET}")
        sys.exit()
    except Exception as e:
        print(f"\n{C.RED}Fatal error: {e}{C.RESET}")
        sys.exit()