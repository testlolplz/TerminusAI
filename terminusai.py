#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║                    TERMINUS AI v1.5.1 FINAL                       ║
║                   Your Terminal AI Companion                      ║
║                                                                   ║
║                      Created by: flint667                         ║
║                                                                   ║
║  v1.5.1 NEW FEATURES:                                            ║
║    • 🔑 Professional API Key Manager                             ║
║    • 📡 Model-Key pairing system                                 ║
║    • ✅ Test API keys before saving                              ║
║    • 📋 Multiple key storage                                     ║
║    • 🎯 Auto-select best key for model                           ║
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
VERSION = "1.5.1"
APP_NAME = "TerminusAI"
AUTHOR = "flint667"
AUTHOR_DISCORD = "flint667"
GITHUB_USER = "testlolplz"
REPO_URL = f"https://github.com/{GITHUB_USER}/TerminusAI"

# ==================== COLORS ====================
class Colors:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

C = Colors()

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
        try:
            with open(log_file, 'a') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {role}: {content[:500]}\n\n")
        except:
            pass

files = TerminusAIFiles()

# ==================== API KEY MANAGER ====================
class APIKeyManager:
    def __init__(self):
        self.keys = {}
        self.model_keys = {}
        self.load()
    
    def load(self):
        config = files.get_config()
        self.keys = config.get('api_keys', {})
        self.model_keys = config.get('model_keys', {})
    
    def save(self):
        config = files.get_config()
        config['api_keys'] = self.keys
        config['model_keys'] = self.model_keys
        files.save_config(config)
    
    def add_key(self, name, key):
        if name in self.keys:
            return False, "Key name already exists"
        self.keys[name] = {
            'key': key,
            'created': datetime.now().isoformat(),
            'last_used': None
        }
        self.save()
        return True, f"Key '{name}' added successfully"
    
    def remove_key(self, name):
        if name not in self.keys:
            return False, "Key not found"
        del self.keys[name]
        # Remove from model assignments
        to_remove = [m for m, k in self.model_keys.items() if k == name]
        for m in to_remove:
            del self.model_keys[m]
        self.save()
        return True, f"Key '{name}' removed"
    
    def assign_key_to_model(self, model_name, key_name):
        if key_name not in self.keys:
            return False, f"Key '{key_name}' not found"
        self.model_keys[model_name] = key_name
        self.save()
        return True, f"Key '{key_name}' assigned to model '{model_name}'"
    
    def get_key_for_model(self, model_name):
        # Check if model has specific key assigned
        if model_name in self.model_keys:
            key_name = self.model_keys[model_name]
            if key_name in self.keys:
                # Update last used
                self.keys[key_name]['last_used'] = datetime.now().isoformat()
                self.save()
                return self.keys[key_name]['key']
        
        # Return first available key
        for key_name, key_data in self.keys.items():
            key_data['last_used'] = datetime.now().isoformat()
            self.save()
            return key_data['key']
        
        return None
    
    def list_keys(self):
        return list(self.keys.keys())
    
    def get_key_info(self, name):
        if name in self.keys:
            info = self.keys[name]
            return {
                'name': name,
                'created': info.get('created', 'Unknown'),
                'last_used': info.get('last_used', 'Never'),
                'assigned_to': [m for m, k in self.model_keys.items() if k == name]
            }
        return None
    
    def test_key(self, key):
        """Test if API key works"""
        try:
            conn = http.client.HTTPSConnection("openrouter.ai", timeout=10)
            payload = json.dumps({
                "model": "openrouter/free",
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 5
            })
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
            conn.request("POST", "/api/v1/chat/completions", payload, headers)
            response = conn.getresponse()
            data = json.loads(response.read().decode())
            
            if "error" in data:
                return False, data['error'].get('message', 'Invalid key')
            return True, "Key works!"
        except Exception as e:
            return False, str(e)[:50]

api_manager = APIKeyManager()

# ==================== GLOBAL VARS ====================
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
        if not question or not model:
            return None
        key = hashlib.md5(f"{question}_{model}".encode()).hexdigest()
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key].get('answer')
        return None
    
    def put(self, question, model, answer):
        if not question or not model or not answer:
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

# ==================== UTILITIES ====================
def clear():
    os.system('clear')

def load_config():
    global CURRENT_MODEL, SECONDARY_MODEL, CUSTOM_PROMPT, DUAL_MODE
    config = files.get_config()
    CURRENT_MODEL = config.get('model', 'openrouter/free')
    SECONDARY_MODEL = config.get('secondary_model', 'google/gemini-2.0-flash-lite-preview-02-05:free')
    CUSTOM_PROMPT = config.get('custom_prompt', '')
    DUAL_MODE = config.get('dual_mode', False)
    api_manager.load()

def save_config():
    config = files.get_config()
    config['model'] = CURRENT_MODEL
    config['secondary_model'] = SECONDARY_MODEL
    config['custom_prompt'] = CUSTOM_PROMPT
    config['dual_mode'] = DUAL_MODE
    config['version'] = VERSION
    config['last_updated'] = datetime.now().isoformat()
    files.save_config(config)
    api_manager.save()

def get_current_time():
    return datetime.now().strftime("%I:%M %p")

def get_current_date():
    return datetime.now().strftime("%A, %B %d, %Y")

def print_banner():
    clear()
    tw = os.get_terminal_size().columns
    date_str = get_current_date()
    time_str = get_current_time()
    
    banner_lines = [
        f"{C.BRIGHT_CYAN}╔{'═' * 58}╗{C.RESET}",
        f"{C.BRIGHT_CYAN}║{C.BRIGHT_WHITE} {APP_NAME} v{VERSION}{' ' * (40 - len(VERSION))} {C.BRIGHT_CYAN}║{C.RESET}",
        f"{C.BRIGHT_CYAN}║{C.BRIGHT_GREEN}      Your Terminal AI Companion          {C.BRIGHT_CYAN}║{C.RESET}",
        f"{C.BRIGHT_CYAN}╠{'═' * 58}╣{C.RESET}",
        f"{C.BRIGHT_CYAN}║{C.BRIGHT_YELLOW}  📅 {date_str:<48} {C.BRIGHT_CYAN}║{C.RESET}",
        f"{C.BRIGHT_CYAN}║{C.BRIGHT_YELLOW}  🕐 {time_str:<49} {C.BRIGHT_CYAN}║{C.RESET}",
        f"{C.BRIGHT_CYAN}╚{'═' * 58}╝{C.RESET}"
    ]
    
    for line in banner_lines:
        pad = (tw - 60) // 2
        print(" " * max(0, pad) + line)

def fast_print(text, delay=0.0005):
    if not text:
        print()
        return
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def highlight_code(text):
    if not text:
        return text
    pattern = r'```(\w+)?\n(.*?)```'
    def replace_code(match):
        lang = match.group(1) or 'text'
        code = match.group(2)
        return f"\n{C.BRIGHT_GREEN}┌─[{lang.upper()}]─{C.RESET}\n{C.BRIGHT_YELLOW}{code}{C.RESET}\n{C.BRIGHT_GREEN}└────────────{C.RESET}"
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

# ==================== API REQUEST ====================
def send_api_request(user_input, system_prompt, model):
    if not user_input or not model:
        return None, "Invalid parameters"
    
    # Get API key for this model
    api_key = api_manager.get_key_for_model(model)
    if not api_key:
        return None, "No API key configured for this model. Please add an API key in Settings."
    
    try:
        messages = [{"role": "system", "content": str(system_prompt)}]
        for msg in HISTORY[-10:]:
            if msg and isinstance(msg, dict):
                messages.append(msg)
        messages.append({"role": "user", "content": str(user_input)})
        
        conn = http.client.HTTPSConnection("openrouter.ai", timeout=20)
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": smart_max_tokens(user_input),
            "top_p": 0.9
        })
        headers = {
            "Authorization": f"Bearer {api_key}",
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
        
        return str(content), None
        
    except json.JSONDecodeError:
        return None, "Invalid JSON response"
    except http.client.HTTPException:
        return None, "HTTP connection error"
    except socket.timeout:
        return None, "Connection timeout"
    except Exception as e:
        return None, f"Error: {str(e)[:50]}"

# ==================== API KEY MANAGEMENT UI ====================
def api_key_manager_menu():
    while True:
        print_banner()
        print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
        print(f"║{C.BRIGHT_WHITE}              🔑 API KEY MANAGER                {C.BRIGHT_CYAN}║")
        print(f"╚{'═' * 58}╝{C.RESET}")
        
        keys = api_manager.list_keys()
        
        if keys:
            print(f"\n{C.BRIGHT_GREEN}📋 Saved API Keys:{C.RESET}\n")
            for i, name in enumerate(keys, 1):
                info = api_manager.get_key_info(name)
                assigned = ", ".join(info['assigned_to']) if info['assigned_to'] else "None"
                print(f"  {C.BRIGHT_CYAN}{i}.{C.RESET} {C.BRIGHT_WHITE}{name}{C.RESET}")
                print(f"      {C.DIM}Assigned to: {assigned}{C.RESET}")
                print(f"      Created: {info['created'][:10] if info['created'] else 'Unknown'}{C.RESET}")
        else:
            print(f"\n{C.BRIGHT_YELLOW}⚠ No API keys configured{C.RESET}")
            print(f"{C.DIM}Add your first API key to get started!{C.RESET}")
        
        print(f"\n{C.BRIGHT_CYAN}┌────────────────────────────────────────────────┐{C.RESET}")
        print(f"│  {C.BRIGHT_GREEN}[1]{C.RESET} Add new API key                         │")
        print(f"│  {C.BRIGHT_GREEN}[2]{C.RESET} Remove API key                         │")
        print(f"│  {C.BRIGHT_GREEN}[3]{C.RESET} Assign key to model                    │")
        print(f"│  {C.BRIGHT_GREEN}[4]{C.RESET} Test API key                           │")
        print(f"│  {C.BRIGHT_GREEN}[5]{C.RESET} View key details                       │")
        print(f"│  {C.BRIGHT_GREEN}[0]{C.RESET} Back to main menu                      │")
        print(f"{C.BRIGHT_CYAN}└────────────────────────────────────────────────┘{C.RESET}")
        
        choice = input(f"\n{C.BRIGHT_GREEN}Select: {C.RESET}").strip()
        
        if choice == '1':
            add_api_key()
        elif choice == '2':
            remove_api_key()
        elif choice == '3':
            assign_key_to_model()
        elif choice == '4':
            test_api_key()
        elif choice == '5':
            view_key_details()
        elif choice == '0':
            break

def add_api_key():
    print_banner()
    print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
    print(f"║{C.BRIGHT_WHITE}              ➕ ADD API KEY                     {C.BRIGHT_CYAN}║")
    print(f"╚{'═' * 58}╝{C.RESET}")
    
    print(f"\n{C.CYAN}Get your free API key from:{C.RESET}")
    print(f"{C.BRIGHT_YELLOW}https://openrouter.ai/keys{C.RESET}\n")
    
    print(f"{C.BRIGHT_WHITE}Enter a name for this key (e.g., 'main', 'backup'):{C.RESET}")
    name = input(f"{C.BRIGHT_GREEN}> {C.RESET}").strip()
    
    if not name:
        print(f"\n{C.BRIGHT_RED}❌ Key name required{C.RESET}")
        input(f"\n{C.DIM}Press Enter...{C.RESET}")
        return
    
    print(f"\n{C.BRIGHT_WHITE}Enter your OpenRouter API key:{C.RESET}")
    key = input(f"{C.BRIGHT_GREEN}> {C.RESET}").strip()
    
    if not key:
        print(f"\n{C.BRIGHT_RED}❌ API key required{C.RESET}")
        input(f"\n{C.DIM}Press Enter...{C.RESET}")
        return
    
    print(f"\n{C.YELLOW}Testing key...{C.RESET}")
    success, message = api_manager.test_key(key)
    
    if success:
        result, msg = api_manager.add_key(name, key)
        if result:
            print(f"\n{C.BRIGHT_GREEN}✅ Key added successfully!{C.RESET}")
        else:
            print(f"\n{C.BRIGHT_RED}❌ {msg}{C.RESET}")
    else:
        print(f"\n{C.BRIGHT_RED}❌ Key test failed: {message}{C.RESET}")
        print(f"{C.YELLOW}Do you want to add it anyway? (y/N):{C.RESET}")
        confirm = input().strip().lower()
        if confirm == 'y':
            result, msg = api_manager.add_key(name, key)
            if result:
                print(f"\n{C.BRIGHT_GREEN}✅ Key added (untested){C.RESET}")
            else:
                print(f"\n{C.BRIGHT_RED}❌ {msg}{C.RESET}")
    
    input(f"\n{C.DIM}Press Enter...{C.RESET}")

def remove_api_key():
    print_banner()
    print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
    print(f"║{C.BRIGHT_WHITE}              ➖ REMOVE API KEY                  {C.BRIGHT_CYAN}║")
    print(f"╚{'═' * 58}╝{C.RESET}")
    
    keys = api_manager.list_keys()
    if not keys:
        print(f"\n{C.BRIGHT_YELLOW}⚠ No API keys to remove{C.RESET}")
        input(f"\n{C.DIM}Press Enter...{C.RESET}")
        return
    
    print(f"\n{C.BRIGHT_GREEN}Select key to remove:{C.RESET}\n")
    for i, name in enumerate(keys, 1):
        print(f"  {C.BRIGHT_CYAN}{i}.{C.RESET} {name}")
    
    print(f"  {C.BRIGHT_CYAN}0.{C.RESET} Cancel")
    
    choice = input(f"\n{C.BRIGHT_GREEN}Select: {C.RESET}").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(keys):
        name = keys[int(choice)-1]
        print(f"\n{C.YELLOW}Remove key '{name}'? (y/N):{C.RESET}")
        confirm = input().strip().lower()
        if confirm == 'y':
            result, msg = api_manager.remove_key(name)
            if result:
                print(f"\n{C.BRIGHT_GREEN}✅ {msg}{C.RESET}")
            else:
                print(f"\n{C.BRIGHT_RED}❌ {msg}{C.RESET}")
    input(f"\n{C.DIM}Press Enter...{C.RESET}")

def assign_key_to_model():
    print_banner()
    print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
    print(f"║{C.BRIGHT_WHITE}              🔗 ASSIGN KEY TO MODEL             {C.BRIGHT_CYAN}║")
    print(f"╚{'═' * 58}╝{C.RESET}")
    
    keys = api_manager.list_keys()
    if not keys:
        print(f"\n{C.BRIGHT_YELLOW}⚠ No API keys available. Add a key first.{C.RESET}")
        input(f"\n{C.DIM}Press Enter...{C.RESET}")
        return
    
    models = [
        "openrouter/free",
        "google/gemini-2.0-flash-lite-preview-02-05:free",
        "deepseek/deepseek-chat:free",
        "qwen/qwen-2.5-coder-32b-instruct:free"
    ]
    
    print(f"\n{C.BRIGHT_GREEN}Select model:{C.RESET}\n")
    for i, model in enumerate(models, 1):
        assigned = api_manager.model_keys.get(model, "None")
        print(f"  {C.BRIGHT_CYAN}{i}.{C.RESET} {model[:40]}")
        print(f"      {C.DIM}Current key: {assigned}{C.RESET}")
    
    print(f"  {C.BRIGHT_CYAN}5.{C.RESET} Custom model ID")
    print(f"  {C.BRIGHT_CYAN}0.{C.RESET} Cancel")
    
    choice = input(f"\n{C.BRIGHT_GREEN}Select: {C.RESET}").strip()
    
    if choice == '0':
        return
    elif choice == '5':
        model = input(f"{C.CYAN}Enter model ID: {C.RESET}").strip()
        if not model:
            return
    elif choice.isdigit() and 1 <= int(choice) <= 4:
        model = models[int(choice)-1]
    else:
        return
    
    print(f"\n{C.BRIGHT_GREEN}Select API key to assign:{C.RESET}\n")
    for i, name in enumerate(keys, 1):
        print(f"  {C.BRIGHT_CYAN}{i}.{C.RESET} {name}")
    
    key_choice = input(f"\n{C.BRIGHT_GREEN}Select: {C.RESET}").strip()
    
    if key_choice.isdigit() and 1 <= int(key_choice) <= len(keys):
        key_name = keys[int(key_choice)-1]
        result, msg = api_manager.assign_key_to_model(model, key_name)
        if result:
            print(f"\n{C.BRIGHT_GREEN}✅ {msg}{C.RESET}")
        else:
            print(f"\n{C.BRIGHT_RED}❌ {msg}{C.RESET}")
    
    input(f"\n{C.DIM}Press Enter...{C.RESET}")

def test_api_key():
    print_banner()
    print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
    print(f"║{C.BRIGHT_WHITE}              🧪 TEST API KEY                   {C.BRIGHT_CYAN}║")
    print(f"╚{'═' * 58}╝{C.RESET}")
    
    keys = api_manager.list_keys()
    if not keys:
        print(f"\n{C.BRIGHT_YELLOW}⚠ No API keys to test{C.RESET}")
        print(f"\n{C.CYAN}You can also test a custom key:{C.RESET}")
        custom = input(f"{C.BRIGHT_GREEN}Enter key to test (or press Enter): {C.RESET}").strip()
        if custom:
            print(f"\n{C.YELLOW}Testing...{C.RESET}")
            success, message = api_manager.test_key(custom)
            if success:
                print(f"\n{C.BRIGHT_GREEN}✅ {message}{C.RESET}")
            else:
                print(f"\n{C.BRIGHT_RED}❌ {message}{C.RESET}")
        input(f"\n{C.DIM}Press Enter...{C.RESET}")
        return
    
    print(f"\n{C.BRIGHT_GREEN}Select key to test:{C.RESET}\n")
    for i, name in enumerate(keys, 1):
        print(f"  {C.BRIGHT_CYAN}{i}.{C.RESET} {name}")
    print(f"  {C.BRIGHT_CYAN}0.{C.RESET} Test custom key")
    
    choice = input(f"\n{C.BRIGHT_GREEN}Select: {C.RESET}").strip()
    
    if choice == '0':
        custom = input(f"{C.CYAN}Enter key to test: {C.RESET}").strip()
        if custom:
            print(f"\n{C.YELLOW}Testing...{C.RESET}")
            success, message = api_manager.test_key(custom)
            if success:
                print(f"\n{C.BRIGHT_GREEN}✅ {message}{C.RESET}")
            else:
                print(f"\n{C.BRIGHT_RED}❌ {message}{C.RESET}")
    elif choice.isdigit() and 1 <= int(choice) <= len(keys):
        name = keys[int(choice)-1]
        info = api_manager.get_key_info(name)
        if info:
            print(f"\n{C.YELLOW}Testing key '{name}'...{C.RESET}")
            success, message = api_manager.test_key(api_manager.keys[name]['key'])
            if success:
                print(f"\n{C.BRIGHT_GREEN}✅ {message}{C.RESET}")
            else:
                print(f"\n{C.BRIGHT_RED}❌ {message}{C.RESET}")
    
    input(f"\n{C.DIM}Press Enter...{C.RESET}")

def view_key_details():
    print_banner()
    print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
    print(f"║{C.BRIGHT_WHITE}              📋 KEY DETAILS                   {C.BRIGHT_CYAN}║")
    print(f"╚{'═' * 58}╝{C.RESET}")
    
    keys = api_manager.list_keys()
    if not keys:
        print(f"\n{C.BRIGHT_YELLOW}⚠ No API keys configured{C.RESET}")
        input(f"\n{C.DIM}Press Enter...{C.RESET}")
        return
    
    print(f"\n{C.BRIGHT_GREEN}Select key:{C.RESET}\n")
    for i, name in enumerate(keys, 1):
        print(f"  {C.BRIGHT_CYAN}{i}.{C.RESET} {name}")
    
    choice = input(f"\n{C.BRIGHT_GREEN}Select: {C.RESET}").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(keys):
        name = keys[int(choice)-1]
        info = api_manager.get_key_info(name)
        if info:
            print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
            print(f"║{C.BRIGHT_WHITE} Key: {name:<52}{C.BRIGHT_CYAN}║")
            print(f"╠{'═' * 58}╣")
            print(f"║  Created: {info['created']:<49}{C.BRIGHT_CYAN}║")
            print(f"║  Last Used: {info['last_used']:<48}{C.BRIGHT_CYAN}║")
            print(f"║  Assigned to: {', '.join(info['assigned_to']) if info['assigned_to'] else 'None':<46}{C.BRIGHT_CYAN}║")
            print(f"║  Key Value: {info.get('key', '')[:20]}...{' ' * (35 - len(info.get('key', '')[:20]))}{C.BRIGHT_CYAN}║")
            print(f"╚{'═' * 58}╝{C.RESET}")
    
    input(f"\n{C.DIM}Press Enter...{C.RESET}")

# ==================== FEATURE FUNCTIONS ====================
def copy_to_clipboard(text):
    if not text:
        return f"{C.YELLOW}⚠ Nothing to copy{C.RESET}"
    try:
        subprocess.run(['termux-clipboard-set', text[:5000]], timeout=1, capture_output=True)
        return f"{C.GREEN}✓ Copied to clipboard{C.RESET}"
    except:
        return f"{C.YELLOW}⚠ Install termux-api for clipboard{C.RESET}"

def paste_from_clipboard():
    try:
        result = subprocess.run(['termux-clipboard-get'], capture_output=True, text=True, timeout=1)
        if result.stdout:
            return f"{C.CYAN}📋 Clipboard:\n\n{result.stdout[:2000]}{C.RESET}"
        return f"{C.YELLOW}📋 Clipboard empty{C.RESET}"
    except:
        return f"{C.YELLOW}⚠ Install termux-api for clipboard{C.RESET}"

def generate_image(prompt):
    if not prompt:
        return f"{C.YELLOW}⚠ Usage: /imagine description{C.RESET}"
    try:
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}"
        filename = os.path.join(files.base_dir, f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        print(f"{C.BRIGHT_GREEN}🎨 Generating...{C.RESET}")
        urllib.request.urlretrieve(url, filename)
        return f"{C.GREEN}✅ Image saved: {filename}{C.RESET}"
    except Exception as e:
        return f"{C.RED}❌ Failed: {str(e)[:50]}{C.RESET}"

def smart_calc(expression):
    if not expression:
        return f"{C.YELLOW}⚠ Usage: /calc 2+2{C.RESET}"
    try:
        result = eval(expression.replace(" ", ""), {"__builtins__": {}}, {})
        return f"{C.GREEN}🧮 {expression} = {result}{C.RESET}"
    except:
        return f"{C.RED}❌ Invalid expression{C.RESET}"

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
            output = f"{C.CYAN}🔍 '{query}':{C.RESET}\n\n"
            for i, title in enumerate(results[:5], 1):
                output += f"  {i}. {title}\n"
            return output if results else f"{C.YELLOW}No results{C.RESET}"
    except:
        return f"{C.RED}❌ Search failed{C.RESET}"

def get_weather(city):
    if not city:
        return f"{C.YELLOW}⚠ Usage: /weather city{C.RESET}"
    try:
        url = f"https://wttr.in/{city}?format=%C:+%t,+%w"
        with urllib.request.urlopen(url, timeout=8) as response:
            weather = response.read().decode('utf-8').strip()
            return f"{C.CYAN}🌤️ {city}: {weather}{C.RESET}"
    except:
        return f"{C.RED}❌ Weather failed{C.RESET}"

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(chars) for _ in range(length))
    return f"{C.GREEN}🔐 Password: {password}{C.RESET}"

def save_current_chat():
    global HISTORY
    if not HISTORY:
        return f"{C.YELLOW}⚠ No conversation to save{C.RESET}"
    
    name = input(f"{C.CYAN}📁 Name (Enter for auto): {C.RESET}").strip()
    if not name:
        name = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    files.save_chat(name, HISTORY, CURRENT_MODEL)
    return f"{C.GREEN}✅ Saved: {name}{C.RESET}"

def load_chat_session():
    global HISTORY
    if not os.path.exists(files.chats_dir):
        return f"{C.YELLOW}⚠ No saved chats{C.RESET}"
    
    sessions = [f.replace('.json', '') for f in os.listdir(files.chats_dir) if f.endswith('.json')]
    if not sessions:
        return f"{C.YELLOW}⚠ No saved chats{C.RESET}"
    
    print(f"\n{C.CYAN}📂 Saved chats:{C.RESET}")
    for i, s in enumerate(sessions, 1):
        print(f"  {i}. {s}")
    
    try:
        choice = int(input(f"\n{C.GREEN}Select (1-{len(sessions)}): {C.RESET}")) - 1
        if 0 <= choice < len(sessions):
            data = files.load_chat(sessions[choice])
            if data:
                HISTORY = data.get('history', [])
                return f"{C.GREEN}✅ Loaded {len(HISTORY)//2} exchanges{C.RESET}"
    except:
        pass
    return f"{C.YELLOW}Cancelled{C.RESET}"

# ==================== DUAL MODE & TURBO ====================
def dual_mode_chat(user_input, system_prompt):
    print(f"\n{C.BRIGHT_CYAN}🔥 DUAL MODE: Comparing responses...{C.RESET}\n")
    
    print(f"{C.BRIGHT_BLUE}[Model 1: {CURRENT_MODEL[:35]}]{C.RESET}")
    response1, error1 = send_api_request(user_input, system_prompt, CURRENT_MODEL)
    
    print(f"{C.BRIGHT_MAGENTA}[Model 2: {SECONDARY_MODEL[:35]}]{C.RESET}")
    response2, error2 = send_api_request(user_input, system_prompt, SECONDARY_MODEL)
    
    print(f"\n{C.BRIGHT_YELLOW}{'─' * 50}{C.RESET}")
    print(f"{C.BRIGHT_GREEN}📊 RESULTS:{C.RESET}")
    print(f"{C.BRIGHT_YELLOW}{'─' * 50}{C.RESET}\n")
    
    print(f"{C.BRIGHT_BLUE}┌─ MODEL 1 ─────────────────────────────┐{C.RESET}")
    if error1:
        print(f"{C.RED}❌ {error1}{C.RESET}")
    else:
        fast_print(highlight_code(response1))
    
    print(f"\n{C.BRIGHT_MAGENTA}┌─ MODEL 2 ─────────────────────────────┐{C.RESET}")
    if error2:
        print(f"{C.RED}❌ {error2}{C.RESET}")
    else:
        fast_print(highlight_code(response2))
    
    print(f"\n{C.BRIGHT_YELLOW}{'─' * 50}{C.RESET}")
    print(f"{C.CYAN}Which response to keep?{C.RESET}")
    print(f"  {C.GREEN}[1]{C.RESET} Model 1")
    print(f"  {C.GREEN}[2]{C.RESET} Model 2")
    print(f"  {C.GREEN}[3]{C.RESET} Both")
    print(f"  {C.GREEN}[0]{C.RESET} Discard")
    
    choice = input(f"\n{C.YELLOW}Select: {C.RESET}").strip()
    
    if choice == '1' and not error1 and response1:
        return response1
    elif choice == '2' and not error2 and response2:
        return response2
    elif choice == '3':
        if response1 and response2:
            return f"{response1}\n\n--- Alternative ---\n\n{response2}"
        return response1 or response2
    return None

def turbo_rewrite(text):
    if not text:
        return None
    
    print(f"\n{C.BRIGHT_MAGENTA}⚡ TURBO MODE: Enhancing...{C.RESET}")
    prompt = f"Rewrite this to be clearer and more polished:\n\n{text[:500]}"
    enhanced, error = send_api_request(prompt, "You are a text enhancement assistant.", CURRENT_MODEL)
    
    if error:
        return text
    return enhanced or text

# ==================== MAIN CHAT ====================
def ai_chat():
    global HISTORY, CURRENT_MODEL, SECONDARY_MODEL, CUSTOM_PROMPT, DUAL_MODE
    
    # Check if API keys exist
    if not api_manager.list_keys():
        print(f"\n{C.BRIGHT_RED}❌ No API keys configured!{C.RESET}")
        print(f"{C.YELLOW}Please add an API key in Settings → API Key Manager{C.RESET}")
        input("\nPress Enter...")
        return
    
    system_prompt = CUSTOM_PROMPT if CUSTOM_PROMPT else f"You are {APP_NAME}, a helpful AI assistant."
    
    while True:
        clear()
        print_banner()
        
        mode_icon = "🔥" if DUAL_MODE else "🔄"
        mode_text = "DUAL MODE" if DUAL_MODE else "SINGLE MODE"
        
        # Get key status
        key_count = len(api_manager.list_keys())
        key_status = f"{C.BRIGHT_GREEN}{key_count} key(s){C.RESET}" if key_count > 0 else f"{C.BRIGHT_RED}No keys{C.RESET}"
        
        print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
        print(f"║{C.BRIGHT_WHITE}  Model: {CURRENT_MODEL[:35]}{' ' * (20 - len(CURRENT_MODEL[:35]))}{C.BRIGHT_CYAN}║")
        print(f"║{C.BRIGHT_YELLOW}  {mode_icon} {mode_text}{' ' * (48 - len(mode_text))}{C.BRIGHT_CYAN}║")
        print(f"║{C.BRIGHT_GREEN}  💬 {len(HISTORY)//2} exchanges | 💾 {len(cache.cache)} cached{C.BRIGHT_CYAN}{' ' * (15 - len(str(len(cache.cache))))}║")
        print(f"║{C.BRIGHT_MAGENTA}  🔑 {key_status}{' ' * (57 - len(key_status))}{C.BRIGHT_CYAN}║")
        if DUAL_MODE:
            print(f"║{C.BRIGHT_MAGENTA}  🔀 Secondary: {SECONDARY_MODEL[:30]}{' ' * (25 - len(SECONDARY_MODEL[:30]))}{C.BRIGHT_CYAN}║")
        print(f"╚{'═' * 58}╝{C.RESET}")
        
        print(f"\n{C.BRIGHT_GREEN}┌─ You ─────────────────────────────────────────┐{C.RESET}")
        user_input = input(f"{C.BRIGHT_WHITE}  > {C.RESET}")
        
        if not user_input.strip():
            continue
        
        cmd = user_input.lower().strip()
        
        if cmd in ['/quit', 'quit', 'exit']:
            break
        elif cmd == '/clear':
            HISTORY = []
            print(f"\n{C.GREEN}✓ Chat history cleared{C.RESET}")
            input("\nPress Enter...")
            continue
        elif cmd == '/help':
            help_text = f"""
{C.BRIGHT_CYAN}╔════════════════════════════════════════════════╗
║{C.BRIGHT_WHITE}                    COMMANDS{C.BRIGHT_CYAN}                    ║
╠════════════════════════════════════════════════╣
║ {C.GREEN}/help{C.RESET}      - Show this help                     {C.BRIGHT_CYAN}║
║ {C.GREEN}/clear{C.RESET}     - Clear conversation history         {C.BRIGHT_CYAN}║
║ {C.GREEN}/save{C.RESET}      - Save current session               {C.BRIGHT_CYAN}║
║ {C.GREEN}/load{C.RESET}      - Load a saved session               {C.BRIGHT_CYAN}║
║ {C.GREEN}/copy{C.RESET}      - Copy last response                 {C.BRIGHT_CYAN}║
║ {C.GREEN}/paste{C.RESET}     - Paste from clipboard                {C.BRIGHT_CYAN}║
║ {C.GREEN}/imagine{C.RESET}   - Generate an image                   {C.BRIGHT_CYAN}║
║ {C.GREEN}/calc{C.RESET}      - Calculate math expression           {C.BRIGHT_CYAN}║
║ {C.GREEN}/search{C.RESET}    - Search the web                      {C.BRIGHT_CYAN}║
║ {C.GREEN}/weather{C.RESET}   - Get weather info                    {C.BRIGHT_CYAN}║
║ {C.GREEN}/password{C.RESET}  - Generate random password            {C.BRIGHT_CYAN}║
║ {C.GREEN}/dual{C.RESET}      - Toggle Dual AI mode                 {C.BRIGHT_CYAN}║
║ {C.GREEN}/turbo{C.RESET}     - Enhance last response               {C.BRIGHT_CYAN}║
║ {C.GREEN}/quit{C.RESET}      - Exit to menu                        {C.BRIGHT_CYAN}║
╚════════════════════════════════════════════════╝{C.RESET}
"""
            print(help_text)
            input("\nPress Enter...")
            continue
        elif cmd == '/copy' and HISTORY:
            result = copy_to_clipboard(HISTORY[-1]['content'])
            print(f"\n{result}")
            input("\nPress Enter...")
            continue
        elif cmd == '/paste':
            print(f"\n{paste_from_clipboard()}")
            input("\nPress Enter...")
            continue
        elif cmd.startswith('/imagine '):
            print(f"\n{generate_image(user_input[9:])}")
            input("\nPress Enter...")
            continue
        elif cmd.startswith('/calc '):
            print(f"\n{smart_calc(user_input[6:])}")
            input("\nPress Enter...")
            continue
        elif cmd.startswith('/search '):
            print(f"\n{web_search(user_input[8:])}")
            input("\nPress Enter...")
            continue
        elif cmd.startswith('/weather '):
            print(f"\n{get_weather(user_input[9:])}")
            input("\nPress Enter...")
            continue
        elif cmd == '/password':
            print(f"\n{generate_password()}")
            input("\nPress Enter...")
            continue
        elif cmd == '/save':
            print(f"\n{save_current_chat()}")
            input("\nPress Enter...")
            continue
        elif cmd == '/load':
            print(f"\n{load_chat_session()}")
            input("\nPress Enter...")
            continue
        elif cmd == '/dual':
            DUAL_MODE = not DUAL_MODE
            save_config()
            status = "ENABLED" if DUAL_MODE else "DISABLED"
            print(f"\n{C.GREEN}✓ Dual Mode {status}{C.RESET}")
            input("\nPress Enter...")
            continue
        elif cmd == '/turbo' and HISTORY:
            last = HISTORY[-1].get('content')
            if last:
                enhanced = turbo_rewrite(last)
                if enhanced:
                    print(f"\n{C.BRIGHT_GREEN}✨ Enhanced Response:{C.RESET}\n")
                    fast_print(highlight_code(enhanced))
                    HISTORY[-1]['content'] = enhanced
            input("\nPress Enter...")
            continue
        
        cached = cache.get(user_input, CURRENT_MODEL) if not DUAL_MODE else None
        if cached:
            print(f"\n{C.BRIGHT_CYAN}┌─ AI (cached) ───────────────────────────┐{C.RESET}")
            fast_print(highlight_code(cached))
            HISTORY.append({"role": "user", "content": user_input})
            HISTORY.append({"role": "assistant", "content": cached})
            files.log_message("USER", user_input)
            files.log_message("ASSISTANT", cached)
            print(f"\n{C.BRIGHT_YELLOW}{'─' * 50}{C.RESET}")
            input(f"{C.DIM}[Enter] continue{C.RESET}")
            continue
        
        print(f"\n{C.BRIGHT_CYAN}┌─ AI ────────────────────────────────────┐{C.RESET}")
        
        if DUAL_MODE:
            content = dual_mode_chat(user_input, system_prompt)
        else:
            content, error = send_api_request(user_input, system_prompt, CURRENT_MODEL)
            if error:
                print(f"{C.RED}❌ {error}{C.RESET}")
                print(f"\n{C.BRIGHT_YELLOW}{'─' * 50}{C.RESET}")
                input(f"{C.DIM}[Enter] continue{C.RESET}")
                continue
        
        if content:
            if not DUAL_MODE:
                cache.put(user_input, CURRENT_MODEL, content)
            
            fast_print(highlight_code(content))
            HISTORY.append({"role": "user", "content": user_input})
            HISTORY.append({"role": "assistant", "content": content})
            files.log_message("USER", user_input)
            files.log_message("ASSISTANT", content)
        
        print(f"\n{C.BRIGHT_YELLOW}{'─' * 50}{C.RESET}")
        input(f"{C.DIM}[Enter] continue  |  /help  |  /dual  |  /quit{C.RESET}")

# ==================== SETTINGS MENUS ====================
def switch_model():
    global CURRENT_MODEL
    print_banner()
    print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
    print(f"║{C.BRIGHT_WHITE}                   AI MODELS                     {C.BRIGHT_CYAN}║")
    print(f"╚{'═' * 58}╝{C.RESET}")
    
    models = [
        ("1", "openrouter/free", "Fastest, auto-select"),
        ("2", "google/gemini-2.0-flash-lite-preview-02-05:free", "Google Gemini (fast)"),
        ("3", "deepseek/deepseek-chat:free", "DeepSeek (coding)"),
        ("4", "qwen/qwen-2.5-coder-32b-instruct:free", "Qwen Coder (expert)"),
    ]
    
    print(f"\n{C.YELLOW}Current: {C.GREEN}{CURRENT_MODEL}{C.RESET}\n")
    for key, model, desc in models:
        print(f"  {C.BRIGHT_CYAN}[{key}]{C.RESET} {model[:35]}")
        print(f"      {C.DIM}{desc}{C.RESET}")
    
    print(f"\n  {C.BRIGHT_CYAN}[5]{C.RESET} Custom model ID")
    choice = input(f"\n{C.BRIGHT_GREEN}Select (1-5): {C.RESET}").strip()
    
    model_map = {k: m for k, m, _ in models}
    if choice in model_map:
        CURRENT_MODEL = model_map[choice]
        save_config()
        print(f"\n{C.GREEN}✓ Switched to {CURRENT_MODEL}{C.RESET}")
    elif choice == '5':
        custom = input(f"{C.CYAN}Enter model ID: {C.RESET}").strip()
        if custom:
            CURRENT_MODEL = custom
            save_config()
            print(f"\n{C.GREEN}✓ Switched to {custom}{C.RESET}")
    input(f"\n{C.DIM}Press Enter...{C.RESET}")

def custom_prompt():
    global CUSTOM_PROMPT
    print_banner()
    print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
    print(f"║{C.BRIGHT_WHITE}              CUSTOM SYSTEM PROMPT               {C.BRIGHT_CYAN}║")
    print(f"╚{'═' * 58}╝{C.RESET}")
    
    print(f"\n{C.YELLOW}Current: {C.GREEN}{CUSTOM_PROMPT[:100] if CUSTOM_PROMPT else 'Default'}{C.RESET}")
    print(f"\n{C.CYAN}Enter new prompt (type 'END' on new line):{C.RESET}\n")
    
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    
    if lines:
        CUSTOM_PROMPT = '\n'.join(lines)
        save_config()
        print(f"\n{C.GREEN}✓ Custom prompt saved!{C.RESET}")
    input(f"\n{C.DIM}Press Enter...{C.RESET}")

def dual_mode_settings():
    global DUAL_MODE, SECONDARY_MODEL
    print_banner()
    print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
    print(f"║{C.BRIGHT_WHITE}                DUAL MODE SETTINGS                {C.BRIGHT_CYAN}║")
    print(f"╚{'═' * 58}╝{C.RESET}")
    
    print(f"\n{C.YELLOW}Status: {C.GREEN}{'ENABLED' if DUAL_MODE else 'DISABLED'}{C.RESET}")
    print(f"{C.YELLOW}Secondary Model: {C.GREEN}{SECONDARY_MODEL}{C.RESET}")
    
    print(f"\n{C.CYAN}[1] Toggle Dual Mode (on/off){C.RESET}")
    print(f"{C.CYAN}[2] Change secondary model{C.RESET}")
    print(f"{C.CYAN}[0] Back{C.RESET}")
    
    choice = input(f"\n{C.BRIGHT_GREEN}Select: {C.RESET}").strip()
    
    if choice == '1':
        DUAL_MODE = not DUAL_MODE
        save_config()
        print(f"\n{C.GREEN}✓ Dual Mode {'ENABLED' if DUAL_MODE else 'DISABLED'}{C.RESET}")
        input(f"\n{C.DIM}Press Enter...{C.RESET}")
    elif choice == '2':
        print(f"\n{C.CYAN}Models you can use:{C.RESET}")
        print(f"  {C.DIM}1. openrouter/free{C.RESET}")
        print(f"  {C.DIM}2. google/gemini-2.0-flash-lite:free{C.RESET}")
        print(f"  {C.DIM}3. deepseek/deepseek-chat:free{C.RESET}")
        print(f"  {C.DIM}4. qwen/qwen-2.5-coder-32b:free{C.RESET}")
        print(f"\n{C.CYAN}Enter secondary model ID:{C.RESET}")
        new_model = input(f"{C.BRIGHT_GREEN}> {C.RESET}").strip()
        if new_model:
            SECONDARY_MODEL = new_model
            save_config()
            print(f"\n{C.GREEN}✓ Secondary model updated!{C.RESET}")
        input(f"\n{C.DIM}Press Enter...{C.RESET}")

def update_menu():
    print_banner()
    print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
    print(f"║{C.BRIGHT_WHITE}                UPDATE CHECKER                   {C.BRIGHT_CYAN}║")
    print(f"╚{'═' * 58}╝{C.RESET}")
    
    print(f"\n{C.YELLOW}Current version: {C.GREEN}v{VERSION}{C.RESET}")
    print(f"\n{C.CYAN}[1] Check for updates{C.RESET}")
    print(f"{C.CYAN}[2] View changelog{C.RESET}")
    print(f"{C.CYAN}[3] Download latest{C.RESET}")
    print(f"{C.CYAN}[0] Back{C.RESET}")
    
    choice = input(f"\n{C.BRIGHT_GREEN}Select: {C.RESET}").strip()
    
    if choice == '1':
        print(f"\n{C.YELLOW}Checking...{C.RESET}")
        try:
            url = f"https://api.github.com/repos/{GITHUB_USER}/TerminusAI/releases/latest"
            req = urllib.request.Request(url, headers={'User-Agent': 'TerminusAI'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest = data.get('tag_name', '').replace('v', '')
                if latest > VERSION:
                    print(f"{C.GREEN}✓ Update available! v{latest}{C.RESET}")
                else:
                    print(f"{C.GREEN}✓ You're on the latest version!{C.RESET}")
        except:
            print(f"{C.RED}❌ Could not check for updates{C.RESET}")
        input(f"\n{C.DIM}Press Enter...{C.RESET}")
    elif choice == '2':
        print(f"\n{C.CYAN}📋 Changelog v{VERSION}:{C.RESET}")
        print(f"{C.GREEN}  • Professional API Key Manager{C.RESET}")
        print(f"{C.GREEN}  • Assign keys to specific models{C.RESET}")
        print(f"{C.GREEN}  • Test API keys before saving{C.RESET}")
        print(f"{C.GREEN}  • Beautiful new menu system{C.RESET}")
        print(f"{C.GREEN}  • Dual AI Mode (/dual){C.RESET}")
        print(f"{C.GREEN}  • Turbo Mode (/turbo){C.RESET}")
        input(f"\n{C.DIM}Press Enter...{C.RESET}")

def storage_info():
    print_banner()
    print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
    print(f"║{C.BRIGHT_WHITE}              STORAGE INFORMATION                {C.BRIGHT_CYAN}║")
    print(f"╚{'═' * 58}╝{C.RESET}")
    
    def get_size(path):
        if not os.path.exists(path):
            return 0
        if os.path.isfile(path):
            return os.path.getsize(path)
        total = 0
        for root, dirs, files in os.walk(path):
            for f in files:
                total += os.path.getsize(os.path.join(root, f))
        return total
    
    sizes = {
        'Config': get_size(files.config_file),
        'Chats': get_size(files.chats_dir),
        'Logs': get_size(files.logs_dir),
        'Cache': get_size(files.cache_dir),
        'Prompts': get_size(files.prompts_dir),
    }
    
    print(f"\n{C.YELLOW}Location: {files.base_dir}{C.RESET}\n")
    for name, size in sizes.items():
        if size > 0:
            print(f"  {name:<10}: {size/1024:.1f} KB")
    
    total = sum(sizes.values())
    print(f"\n{C.GREEN}  Total     : {total/1024:.1f} KB{C.RESET}")
    
    print(f"\n{C.CYAN}[1] Clear cache{C.RESET}")
    print(f"{C.CYAN}[0] Back{C.RESET}")
    
    choice = input(f"\n{C.BRIGHT_GREEN}Select: {C.RESET}").strip()
    if choice == '1':
        cache.cache.clear()
        cache.save()
        print(f"\n{C.GREEN}✓ Cache cleared!{C.RESET}")
        input(f"\n{C.DIM}Press Enter...{C.RESET}")

def about():
    print_banner()
    print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
    print(f"║{C.BRIGHT_WHITE}                   ABOUT                       {C.BRIGHT_CYAN}║")
    print(f"╚{'═' * 58}╝{C.RESET}")
    
    key_count = len(api_manager.list_keys())
    
    print(f"""
{C.BRIGHT_GREEN}{APP_NAME} v{VERSION}{C.RESET}
{C.DIM}Your Terminal AI Companion{C.RESET}

{C.YELLOW}Created by:{C.RESET} {AUTHOR}
{C.YELLOW}Discord:{C.RESET} {AUTHOR_DISCORD}
{C.YELLOW}GitHub:{C.RESET} {REPO_URL}

{C.BRIGHT_CYAN}Features:{C.RESET}
  • {C.GREEN}🔑 Professional API Key Manager{C.RESET}
  • {C.GREEN}🔥 Dual AI Mode{C.RESET} - Compare 2 models
  • {C.GREEN}⚡ Turbo Mode{C.RESET} - Enhance responses
  • {C.GREEN}🔄 Update Checker{C.RESET} - Auto updates
  • {C.GREEN}🎨 Image Generation{C.RESET} - AI art
  • {C.GREEN}🔍 Web Search{C.RESET} - DuckDuckGo
  • {C.GREEN}🌤️ Weather{C.RESET} - Real-time
  • {C.GREEN}📋 Clipboard{C.RESET} - Copy/Paste
  • {C.GREEN}💾 Save/Load{C.RESET} - Chats

{C.BRIGHT_MAGENTA}API Keys: {C.GREEN}{key_count} configured{C.RESET}

{C.DIM}All data stored in: ~/.terminusai/{C.RESET}
""")
    input(f"\n{C.DIM}Press Enter...{C.RESET}")

# ==================== SETUP ====================
def check_and_install_dependencies():
    print_banner()
    print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
    print(f"║{C.BRIGHT_WHITE}                 FIRST TIME SETUP                 {C.BRIGHT_CYAN}║")
    print(f"╚{'═' * 58}╝{C.RESET}")
    
    if not os.path.exists('/data/data/com.termux'):
        print(f"\n{C.RED}❌ Termux required!{C.RESET}")
        sys.exit(1)
    
    print(f"\n{C.YELLOW}📡 Checking internet...{C.RESET}")
    try:
        urllib.request.urlopen('https://8.8.8.8', timeout=2)
        print(f"{C.GREEN}✓ Connected{C.RESET}")
    except:
        print(f"{C.RED}❌ No internet{C.RESET}")
        sys.exit(1)
    
    print(f"\n{C.YELLOW}⚡ Installing dependencies...{C.RESET}")
    subprocess.run(['pkg', 'install', 'python', '-y'], capture_output=True)
    
    print(f"\n{C.BRIGHT_GREEN}✅ Setup complete!{C.RESET}")
    print(f"\n{C.CYAN}Next steps:{C.RESET}")
    print(f"  1. Go to {C.BRIGHT_YELLOW}API Key Manager{C.RESET} (Option 3)")
    print(f"  2. Add your OpenRouter API key")
    print(f"  3. Start chatting!")
    
    time.sleep(2)

# ==================== MAIN MENU ====================
def main_menu():
    global DUAL_MODE
    
    while True:
        print_banner()
        
        key_count = len(api_manager.list_keys())
        key_icon = "✅" if key_count > 0 else "❌"
        key_color = C.GREEN if key_count > 0 else C.RED
        mode_icon = "🔥" if DUAL_MODE else "🔄"
        
        print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
        print(f"║{C.BRIGHT_WHITE}  {key_icon} API Keys: {key_color}{key_count} configured{' ' * (33 - len(str(key_count)))}{C.BRIGHT_CYAN}║")
        print(f"║{C.BRIGHT_YELLOW}  {mode_icon} Mode: {'DUAL' if DUAL_MODE else 'SINGLE'}{' ' * 49}{C.BRIGHT_CYAN}║")
        print(f"║{C.BRIGHT_GREEN}  📡 Model: {CURRENT_MODEL[:35]}{' ' * (20 - len(CURRENT_MODEL[:35]))}{C.BRIGHT_CYAN}║")
        print(f"║{C.BRIGHT_MAGENTA}  💾 Cache: {len(cache.cache)} items{' ' * 48}{C.BRIGHT_CYAN}║")
        print(f"╚{'═' * 58}╝{C.RESET}")
        
        print(f"\n{C.BRIGHT_CYAN}╔{'═' * 58}╗")
        print(f"║{C.BRIGHT_WHITE}                    MAIN MENU                     {C.BRIGHT_CYAN}║")
        print(f"╠{'═' * 58}╣{C.RESET}")
        print(f"║  {C.BRIGHT_GREEN}1.{C.RESET} 💬 Start Chat                          {C.BRIGHT_CYAN}║{C.RESET}")
        print(f"║  {C.BRIGHT_MAGENTA}2.{C.RESET} 🎨 Custom Prompt                      {C.BRIGHT_CYAN}║{C.RESET}")
        print(f"║  {C.BRIGHT_YELLOW}3.{C.RESET} 🔑 API Key Manager                    {C.BRIGHT_CYAN}║{C.RESET}")
        print(f"║  {C.BRIGHT_BLUE}4.{C.RESET} 📡 Switch AI Model                    {C.BRIGHT_CYAN}║{C.RESET}")
        print(f"║  {C.BRIGHT_CYAN}5.{C.RESET} 🔥 Dual Mode Settings                 {C.BRIGHT_CYAN}║{C.RESET}")
        print(f"║  {C.BRIGHT_CYAN}6.{C.RESET} 🔄 Update Checker                     {C.BRIGHT_CYAN}║{C.RESET}")
        print(f"║  {C.BRIGHT_YELLOW}7.{C.RESET} 💾 Storage Manager                    {C.BRIGHT_CYAN}║{C.RESET}")
        print(f"║  {C.BRIGHT_WHITE}8.{C.RESET} ℹ️  About                             {C.BRIGHT_CYAN}║{C.RESET}")
        print(f"║  {C.BRIGHT_RED}9.{C.RESET} 🚪 Exit                              {C.BRIGHT_CYAN}║{C.RESET}")
        print(f"╚{'═' * 58}╝{C.RESET}")
        
        choice = input(f"\n{C.BRIGHT_GREEN}┌─[SELECT]─► {C.RESET}")
        
        if choice == '1':
            ai_chat()
        elif choice == '2':
            custom_prompt()
        elif choice == '3':
            api_key_manager_menu()
        elif choice == '4':
            switch_model()
        elif choice == '5':
            dual_mode_settings()
        elif choice == '6':
            update_menu()
        elif choice == '7':
            storage_info()
        elif choice == '8':
            about()
        elif choice == '9':
            print(f"\n{C.BRIGHT_GREEN}Goodbye! 👋{C.RESET}")
            sys.exit()

# ==================== ENTRY POINT ====================
def main():
    if not os.path.exists(files.config_file):
        check_and_install_dependencies()
    
    load_config()
    main_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.BRIGHT_GREEN}Goodbye! 👋{C.RESET}")
        sys.exit()
    except Exception as e:
        print(f"\n{C.BRIGHT_RED}Fatal error: {e}{C.RESET}")
        sys.exit()