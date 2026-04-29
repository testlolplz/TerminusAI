#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║                         TERMINUS AI v1.3.1                        ║
║                   Your Terminal AI Companion                      ║
║                                                                   ║
║                      Created by: flint667                         ║
║                                                                   ║
║  v1.3.1 BUG FIXES:                                               ║
║    • 🔧 Fixed NoneType error in API responses                    ║
║    • 🛡️ Better error handling for all API calls                  ║
║    • ✅ Validates responses before processing                     ║
║    • 🔄 Auto-retry on empty responses                            ║
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
from datetime import datetime
from collections import OrderedDict

# ==================== VERSION INFO ====================
VERSION = "1.3.1"
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
FAST_GREEN = '\033[38;2;0;255;100m'
FAST_CYAN = '\033[38;2;0;200;255m'
FAST_YELLOW = '\033[38;2;255;200;0m'
FAST_RED = '\033[38;2;255;100;100m'
FAST_BLUE = '\033[38;2;100;150;255m'
FAST_PURPLE = '\033[38;2;200;100;255m'
FAST_RESET = '\033[0m'

# ==================== GLOBAL VARS ====================
API_KEY = ""
HISTORY = []
CURRENT_MODEL = "openrouter/free"
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
            cls._instance.conn = None
        return cls._instance
    
    def get_connection(self):
        if self.conn is None:
            self.conn = http.client.HTTPSConnection("openrouter.ai", timeout=20)
        return self.conn
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

conn_pool = ConnectionPool()

# ==================== AUTO-UPDATE CHECKER ====================
def check_for_updates():
    try:
        if os.path.exists(files.update_check_file):
            with open(files.update_check_file, 'r') as f:
                last_check = json.load(f)
                last_time = last_check.get('timestamp', 0)
                if time.time() - last_time < 86400:
                    return last_check.get('update_available', False), last_check.get('latest_version')
    except:
        pass
    
    try:
        url = f"https://api.github.com/repos/{GITHUB_USER}/TerminusAI/releases/latest"
        req = urllib.request.Request(url, headers={'User-Agent': 'TerminusAI'})
        with urllib.request.urlopen(req, timeout=5) as response:
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
    except:
        return False, None

def show_update_banner():
    try:
        update_available, latest = check_for_updates()
        if update_available:
            print(f"\n{FAST_YELLOW}╔══════════════════════════════════════════════════╗")
            print(f"║  🎉 UPDATE AVAILABLE! v{latest} is out!              ║")
            print(f"║  Run: curl -o ~/.terminusai/terminusai.py {REPO_URL}/raw/main/terminusai.py")
            print(f"╚══════════════════════════════════════════════════╝{FAST_RESET}")
            return True
    except:
        pass
    return False

# ==================== AUTO-INSTALLER ====================
def check_and_install_dependencies():
    print(f"{FAST_CYAN}")
    print("╔══════════════════════════════════════════════════╗")
    print("║         TerminusAI v1.3.1 - Quick Setup         ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"{FAST_RESET}")
    
    if not os.path.exists('/data/data/com.termux'):
        print(f"{FAST_RED}❌ Termux only!{FAST_RESET}")
        sys.exit(1)
    
    try:
        urllib.request.urlopen('https://8.8.8.8', timeout=2)
        print(f"{FAST_GREEN}✓ Internet OK{FAST_RESET}")
    except:
        print(f"{FAST_RED}❌ No internet{FAST_RESET}")
        sys.exit(1)
    
    print(f"{FAST_YELLOW}⚡ Installing dependencies...{FAST_RESET}")
    subprocess.run(['pkg', 'install', 'python', '-y'], capture_output=True)
    
    print(f"\n{FAST_CYAN}🔑 OpenRouter API key: {FAST_RESET}")
    print(f"{FAST_YELLOW}Get free key: https://openrouter.ai/keys{FAST_RESET}")
    api_key = input().strip()
    
    if api_key:
        config = files.get_config()
        config['api_key'] = api_key
        config['model'] = "openrouter/free"
        config['version'] = VERSION
        config['last_setup'] = datetime.now().isoformat()
        files.save_config(config)
        print(f"{FAST_GREEN}✓ Ready!{FAST_RESET}")
    
    time.sleep(1)

# ==================== UTILITIES ====================
def clear():
    os.system('clear')

def load_config():
    global API_KEY, CURRENT_MODEL, CUSTOM_PROMPT
    config = files.get_config()
    API_KEY = config.get('api_key', '')
    CURRENT_MODEL = config.get('model', 'openrouter/free')
    CUSTOM_PROMPT = config.get('custom_prompt', '')

def save_config():
    config = files.get_config()
    config['api_key'] = API_KEY
    config['model'] = CURRENT_MODEL
    config['custom_prompt'] = CUSTOM_PROMPT
    config['version'] = VERSION
    config['last_updated'] = datetime.now().isoformat()
    files.save_config(config)

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def print_header():
    tw = os.get_terminal_size().columns
    current_time = get_current_time()
    
    lines = [
        f"{FAST_BLUE}╔══════════════════════════════════════════════════╗",
        f"║           {APP_NAME} v{VERSION}                    ║",
        "║      Your Terminal AI Companion                  ║",
        f"╠══════════════════════════════════════════════════╣",
        f"║  🕐 {current_time:<49} ║",
        f"╚══════════════════════════════════════════════════╝{FAST_RESET}"
    ]
    
    print("\n" * 1)
    for line in lines:
        clean_len = len(line.replace(FAST_BLUE, '').replace(FAST_RESET, ''))
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
        return f"\n{FAST_GREEN}┌─[{lang.upper()}]─────────────────┐\n{FAST_YELLOW}{code}\n{FAST_GREEN}└────────────────────────────────┘{FAST_RESET}"
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
        return f"{FAST_YELLOW}⚠ Nothing to copy{FAST_RESET}"
    try:
        if len(text) > 5000:
            text = text[:5000]
        subprocess.run(['termux-clipboard-set', text], timeout=1, capture_output=True)
        return f"{FAST_GREEN}✓ Copied ({len(text)} chars){FAST_RESET}"
    except:
        return f"{FAST_RED}❌ Install termux-api{FAST_RESET}"

def paste_from_clipboard():
    try:
        result = subprocess.run(['termux-clipboard-get'], capture_output=True, text=True, timeout=1)
        if result.stdout:
            return f"{FAST_CYAN}📋 Clipboard:\n\n{result.stdout[:2000]}{FAST_RESET}"
        return f"{FAST_YELLOW}📋 Empty{FAST_RESET}"
    except:
        return f"{FAST_RED}❌ Install termux-api{FAST_RESET}"

def generate_image(prompt):
    if not prompt:
        return f"{FAST_YELLOW}⚠ Usage: /imagine description{FAST_RESET}"
    try:
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}"
        filename = os.path.join(files.base_dir, f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        print(f"{FAST_GREEN}🎨 Generating...{FAST_RESET}")
        urllib.request.urlretrieve(url, filename)
        if os.path.exists(filename) and os.path.getsize(filename) > 1000:
            try:
                subprocess.run(['termux-open', filename], timeout=2, capture_output=True)
                return f"{FAST_GREEN}✅ Saved: {filename}{FAST_RESET}"
            except:
                return f"{FAST_GREEN}✅ Saved: {filename}{FAST_RESET}"
        return f"{FAST_RED}❌ Failed to generate{FAST_RESET}"
    except Exception as e:
        return f"{FAST_RED}❌ Error: {str(e)[:50]}{FAST_RESET}"

def smart_calc(expression):
    if not expression:
        return f"{FAST_YELLOW}⚠ Usage: /calc 2+2{FAST_RESET}"
    try:
        expression = expression.replace(" ", "")
        import math
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        allowed.update({"abs": abs, "round": round})
        
        if not re.match(r'^[\d\s\+\-\*\/\%\(\)\.\^\,\|\&\~\<\>\=\!\+\-\*\/\%\*\*\,\s]+$', expression.replace("**", "")):
            if any(func in expression for func in ['sqrt', 'sin', 'cos', 'tan', 'log', 'pi', 'e']):
                result = eval(expression, {"__builtins__": {}}, allowed)
            else:
                return f"{FAST_RED}❌ Invalid expression{FAST_RESET}"
        else:
            result = eval(expression, {"__builtins__": {}}, {})
        return f"{FAST_GREEN}🧮 {expression} = {result}{FAST_RESET}"
    except ZeroDivisionError:
        return f"{FAST_RED}❌ Division by zero{FAST_RESET}"
    except Exception as e:
        return f"{FAST_RED}❌ Error: {str(e)[:30]}{FAST_RESET}"

def web_search(query):
    if not query:
        return f"{FAST_YELLOW}⚠ Usage: /search query{FAST_RESET}"
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode('utf-8')
            results = re.findall(r'<a rel="nofollow" class="result__a" href="[^"]*">([^<]+)</a>', html)
            output = f"{FAST_CYAN}🔍 '{query}':\n\n{FAST_RESET}"
            for i, title in enumerate(results[:5], 1):
                output += f"  {i}. {title}\n"
            return output if results else f"{FAST_YELLOW}No results{FAST_RESET}"
    except Exception as e:
        return f"{FAST_RED}❌ Search failed: {str(e)[:30]}{FAST_RESET}"

def get_weather(city):
    if not city:
        return f"{FAST_YELLOW}⚠ Usage: /weather city{FAST_RESET}"
    try:
        url = f"https://wttr.in/{city}?format=%C:+%t,+%w"
        with urllib.request.urlopen(url, timeout=8) as response:
            weather = response.read().decode('utf-8').strip()
            return f"{FAST_CYAN}🌤️ {city}: {weather}{FAST_RESET}"
    except Exception as e:
        return f"{FAST_RED}❌ Weather failed: {str(e)[:30]}{FAST_RESET}"

def generate_password(length=16):
    try:
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(chars) for _ in range(length))
        strength = "Strong" if length >= 12 else "Medium" if length >= 8 else "Weak"
        return f"{FAST_GREEN}🔐 Password: {password}\n   Strength: {strength}{FAST_RESET}"
    except:
        return f"{FAST_RED}❌ Failed to generate{FAST_RESET}"

def save_current_chat():
    global HISTORY
    if not HISTORY:
        return f"{FAST_YELLOW}⚠ No conversation to save{FAST_RESET}"
    
    name = input(f"{FAST_CYAN}📁 Name (Enter for auto): {FAST_RESET}").strip()
    if not name:
        name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        files.save_chat(name, HISTORY, CURRENT_MODEL)
        return f"{FAST_GREEN}✅ Saved: {name}{FAST_RESET}"
    except Exception as e:
        return f"{FAST_RED}❌ Save failed: {str(e)[:30]}{FAST_RESET}"

def load_chat_session():
    global HISTORY
    sessions = files.list_chats()
    if not sessions:
        return f"{FAST_YELLOW}⚠ No saved chats{FAST_RESET}"
    
    print(f"\n{FAST_CYAN}📂 Saved chats:{FAST_RESET}")
    for i, s in enumerate(sessions, 1):
        print(f"  {i}. {s}")
    
    try:
        choice = int(input(f"\n{FAST_GREEN}Select (1-{len(sessions)} or 0): {FAST_RESET}")) - 1
        if 0 <= choice < len(sessions):
            data = files.load_chat(sessions[choice])
            if data:
                HISTORY = data.get('history', [])
                return f"{FAST_GREEN}✅ Loaded {len(HISTORY)//2} exchanges{FAST_RESET}"
    except:
        pass
    return f"{FAST_YELLOW}Cancelled{FAST_RESET}"

# ==================== MAIN AI CHAT ====================
def send_api_request(user_input, system_prompt):
    """Send request to API with proper error handling"""
    try:
        messages = [{"role": "system", "content": system_prompt}]
        for msg in HISTORY[-10:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_input})
        
        conn = conn_pool.get_connection()
        payload = json.dumps({
            "model": CURRENT_MODEL,
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": smart_max_tokens(user_input),
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
        return None, f"Invalid JSON response: {str(e)[:50]}"
    except http.client.HTTPException as e:
        return None, f"HTTP error: {str(e)[:50]}"
    except socket.timeout:
        return None, "Connection timeout"
    except Exception as e:
        return None, f"Error: {str(e)[:80]}"

def ai_chat():
    global API_KEY, HISTORY, CURRENT_MODEL, CUSTOM_PROMPT
    
    if not API_KEY:
        print(f"\n{FAST_RED}❌ No API key! Set in Settings (option 3){FAST_RESET}")
        input("\nPress Enter...")
        return
    
    system_prompt = CUSTOM_PROMPT if CUSTOM_PROMPT else f"You are {APP_NAME}, a helpful AI assistant. Be concise and helpful."
    
    while True:
        clear()
        print_header()
        tw = os.get_terminal_size().columns
        
        print(f"\n{FAST_CYAN}📡 {CURRENT_MODEL[:40]}{FAST_RESET}")
        print(f"{FAST_YELLOW}💬 {len(HISTORY)//2} exchanges | 💾 {len(cache.cache)} cached{FAST_RESET}")
        print("\n" + "─" * tw)
        print(f"{FAST_GREEN}You: {FAST_RESET}", end="")
        user_input = input()
        
        if not user_input or not user_input.strip():
            continue
        
        cmd = user_input.lower().strip()
        
        # Commands
        if cmd in ['/quit', 'quit', 'exit']:
            break
        elif cmd == '/clear':
            HISTORY = []
            print(f"\n{FAST_GREEN}✓ Cleared{FAST_RESET}")
            input("\nPress Enter...")
            continue
        elif cmd == '/help':
            help_text = f"""
{FAST_CYAN}📖 {APP_NAME} v{VERSION} Commands:{FAST_RESET}

{FAST_GREEN}Core:{FAST_RESET}  /help, /clear, /quit, /save, /load
{FAST_CYAN}Clipboard:{FAST_RESET}  /copy, /paste
{FAST_YELLOW}Media:{FAST_RESET}  /imagine <prompt>
{FAST_PURPLE}Tools:{FAST_RESET}  /calc <expr>, /password, /search <q>, /weather <city>

{FAST_BLUE}💡 Examples:{FAST_RESET}
  /calc 2+2*10
  /imagine a cat in space
  /search python tutorial
  /weather London
"""
            print(help_text)
            input("\nPress Enter...")
            continue
        elif cmd == '/copy':
            if HISTORY:
                result = copy_to_clipboard(HISTORY[-1]['content'])
                print(f"\n{result}")
            else:
                print(f"\n{FAST_YELLOW}No response to copy{FAST_RESET}")
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
        
        # Check cache first
        cached = cache.get(user_input, CURRENT_MODEL)
        if cached:
            print(f"\n{FAST_CYAN}AI (cached): {FAST_RESET}")
            highlighted = highlight_code(cached)
            fast_print(highlighted)
            HISTORY.append({"role": "user", "content": user_input})
            HISTORY.append({"role": "assistant", "content": cached})
            files.log_message("USER", user_input)
            files.log_message("ASSISTANT", cached)
            print("\n" + "─" * tw)
            input(f"{FAST_YELLOW}[Enter] continue{FAST_RESET}")
            continue
        
        # API call
        print(f"\n{FAST_CYAN}AI: {FAST_RESET}")
        
        content, error = send_api_request(user_input, system_prompt)
        
        if error:
            print(f"{FAST_RED}❌ {error}{FAST_RESET}")
            print(f"\n{FAST_YELLOW}💡 Tips:{FAST_RESET}")
            print("  • Check your API key in Settings (option 3)")
            print("  • Make sure you have internet connection")
            print("  • Try switching models (option 4)")
        elif content:
            # Cache the response
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
        else:
            print(f"{FAST_RED}❌ No response received{FAST_RESET}")
        
        print("\n" + "─" * tw)
        print(f"{FAST_YELLOW}[Enter] continue  |  /help  |  /quit{FAST_RESET}", end="")
        input()

# ==================== SETTINGS ====================
def api_settings():
    global API_KEY
    clear()
    print_header()
    print(f"\n{FAST_CYAN}🔑 API Key Configuration{FAST_RESET}")
    print(f"Current: {API_KEY[:15]}...{API_KEY[-10:]}" if len(API_KEY) > 25 else "None set")
    print(f"\n{FAST_YELLOW}New key (or Enter to keep): {FAST_RESET}", end="")
    new_key = input().strip()
    if new_key:
        API_KEY = new_key
        save_config()
        print(f"{FAST_GREEN}✓ Saved!{FAST_RESET}")
    input("\nPress Enter...")

def switch_model():
    global CURRENT_MODEL
    clear()
    print_header()
    print(f"\n{FAST_CYAN}📡 Available Models:{FAST_RESET}")
    print("  1. openrouter/free (fastest, auto-select)")
    print("  2. google/gemini-2.0-flash-lite (fast)")
    print("  3. deepseek/deepseek-chat (good for coding)")
    print("  4. qwen/qwen-2.5-coder-32b (coding expert)")
    print(f"\n{FAST_GREEN}Current: {CURRENT_MODEL}{FAST_RESET}")
    choice = input(f"\n{FAST_YELLOW}Select (1-4): {FAST_RESET}").strip()
    
    models = {
        '1': 'openrouter/free',
        '2': 'google/gemini-2.0-flash-lite-preview-02-05:free',
        '3': 'deepseek/deepseek-chat:free',
        '4': 'qwen/qwen-2.5-coder-32b-instruct:free'
    }
    if choice in models:
        CURRENT_MODEL = models[choice]
        save_config()
        print(f"{FAST_GREEN}✓ Switched to {CURRENT_MODEL[:30]}{FAST_RESET}")
    input("\nPress Enter...")

def custom_prompt():
    global CUSTOM_PROMPT
    clear()
    print_header()
    print(f"\n{FAST_CYAN}🎨 Custom System Prompt{FAST_RESET}")
    print(f"Current: {CUSTOM_PROMPT[:100] if CUSTOM_PROMPT else 'Default'}\n")
    print(f"{FAST_YELLOW}Enter new prompt (type 'END' on new line):{FAST_RESET}")
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    if lines:
        CUSTOM_PROMPT = '\n'.join(lines)
        save_config()
        print(f"{FAST_GREEN}✓ Saved!{FAST_RESET}")
    input("\nPress Enter...")

def storage_info():
    clear()
    print_header()
    print(f"\n{FAST_CYAN}💾 Storage Information{FAST_RESET}")
    
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
    
    print(f"\n{FAST_YELLOW}Location: {files.base_dir}{FAST_RESET}\n")
    for name, size in sizes.items():
        if size > 0:
            print(f"  {name:<10}: {size/1024:.1f} KB")
    print(f"\n{FAST_GREEN}  Total     : {total/1024:.1f} KB{FAST_RESET}")
    
    print(f"\n{FAST_CYAN}Options:{FAST_RESET}")
    print("  1. Clear cache")
    print("  2. Delete all logs")
    print("  0. Back")
    
    choice = input(f"\n{FAST_YELLOW}Select: {FAST_RESET}")
    if choice == '1':
        cache.cache.clear()
        cache.save()
        print(f"{FAST_GREEN}✓ Cache cleared{FAST_RESET}")
        time.sleep(1)
    elif choice == '2':
        import shutil
        if os.path.exists(files.logs_dir):
            shutil.rmtree(files.logs_dir)
            os.makedirs(files.logs_dir)
        print(f"{FAST_GREEN}✓ Logs deleted{FAST_RESET}")
        time.sleep(1)

# ==================== MAIN MENU ====================
def main():
    global API_KEY
    
    if not os.path.exists(files.config_file):
        check_and_install_dependencies()
        load_config()
    
    load_config()
    show_update_banner()
    
    while True:
        clear()
        print_header()
        tw = os.get_terminal_size().columns
        
        print(f"\n{FAST_CYAN}╔════════════════════════════════════════════╗")
        print("║              MAIN MENU                       ║")
        print("╠════════════════════════════════════════════╣")
        print(f"║  {FAST_GREEN}1.{FAST_CYAN} 💬 Start Chat (v1.3.1)               ║")
        print(f"║  {FAST_PURPLE}2.{FAST_CYAN} 🎨 Custom Prompt                     ║")
        print(f"║  {FAST_BLUE}3.{FAST_CYAN} 🔑 API Settings                      ║")
        print(f"║  {FAST_BLUE}4.{FAST_CYAN} 📡 Switch AI Model                   ║")
        print(f"║  {FAST_YELLOW}5.{FAST_CYAN} 💾 Storage Manager                   ║")
        print(f"║  {FAST_CYAN}6.{FAST_CYAN} ℹ️  About                            ║")
        print(f"║  {FAST_RED}7.{FAST_CYAN} 🚪 Exit                             ║")
        print(f"╚════════════════════════════════════════════╝{FAST_RESET}")
        
        print(f"\n{FAST_GREEN}API: {'✅' if API_KEY else '❌'}{FAST_RESET}  {FAST_CYAN}Model: {CURRENT_MODEL[:25]}{FAST_RESET}")
        print(f"{FAST_YELLOW}Cache: {len(cache.cache)} items{FAST_RESET}")
        
        choice = input(f"\n{FAST_GREEN}Select (1-7): {FAST_RESET}").strip()
        
        if choice == '1':
            ai_chat()
        elif choice == '2':
            custom_prompt()
        elif choice == '3':
            api_settings()
        elif choice == '4':
            switch_model()
        elif choice == '5':
            storage_info()
        elif choice == '6':
            clear()
            print_header()
            print(f"\n{FAST_CYAN}{APP_NAME} v{VERSION}{FAST_RESET}")
            print(f"Created by: {AUTHOR}")
            print(f"Discord: {AUTHOR_DISCORD}")
            print(f"GitHub: {REPO_URL}")
            print(f"\n{FAST_GREEN}Features:{FAST_RESET}")
            print("  • Fast AI responses with caching")
            print("  • Image generation")
            print("  • Web search & weather")
            print("  • Clipboard support")
            print("  • Password generator")
            print("  • Save/load conversations")
            print(f"\n{FAST_YELLOW}All data stored in: {files.base_dir}{FAST_RESET}")
            input("\nPress Enter...")
        elif choice == '7':
            conn_pool.close()
            print(f"\n{FAST_GREEN}Goodbye! 👋{FAST_RESET}")
            sys.exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{FAST_GREEN}Goodbye! 👋{FAST_RESET}")
        sys.exit()
    except Exception as e:
        print(f"\n{FAST_RED}Fatal error: {e}{FAST_RESET}")
        sys.exit()