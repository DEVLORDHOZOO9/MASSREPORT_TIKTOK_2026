import requests
import re
import time
import json
import concurrent.futures
import random
import sys
import os
import threading
import subprocess
import importlib
import pkg_resources
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import queue
import signal
import asyncio
import logging
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import threading
from typing import Optional
import platform
import psutil
import math
import uuid

# =============================================
# TELEGRAM BOT CONFIGURATION
# =============================================

TELEGRAM_BOT_TOKEN = "8243804176:AAHddGdjqOlzACwDL8sTGzJjMGdo7KNI6ko"
ADMIN_USER_IDS = [8317643774, 8317643774]

# =============================================
# COLOR CLASS FOR TERMINAL
# =============================================

class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Global control variables
continuous_mode = False
stop_reporting = False
reporting_paused = False
telegram_bot = None
active_reports = {}

# =============================================
# AUTO INSTALLER MODULE
# =============================================

def install_package(package_name, upgrade=False):
    """Auto install Python packages"""
    try:
        if upgrade:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_name])
        else:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"{Color.GREEN}✓ Successfully installed/upgraded {package_name}{Color.RESET}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Color.RED}❌ Failed to install {package_name}: {e}{Color.RESET}")
        return False

def check_and_install_dependencies():
    """Check and install all required dependencies"""
    required_packages = {
        'requests': 'requests',
        'colorama': 'colorama',
        'fake-useragent': 'fake_useragent',
        'urllib3': 'urllib3',
        'bs4': 'beautifulsoup4',
        'psutil': 'psutil',
        'python-telegram-bot': 'python-telegram-bot'
    }
    
    print(f"{Color.YELLOW}🔧 Checking dependencies...{Color.RESET}")
    
    for import_name, package_name in required_packages.items():
        try:
            importlib.import_module(import_name)
            print(f"{Color.GREEN}✓ {import_name} already installed{Color.RESET}")
        except ImportError:
            print(f"{Color.YELLOW}⚠ Installing {package_name}...{Color.RESET}")
            install_package(package_name)

# =============================================
# TIKTOK API FUNCTIONS - REAL IMPLEMENTATION
# =============================================

class TikTokReporter:
    def __init__(self):
        self.session = requests.Session()
        self.success_count = 0
        self.failed_count = 0
        self.start_time = None
        
    def get_headers(self):
        """Generate realistic TikTok headers"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.tiktok.com',
            'Referer': 'https://www.tiktok.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive',
        }
    
    def extract_video_info(self, url):
        """Extract video information from TikTok URL"""
        try:
            video_id = extract_video_id_from_url(url)
            if not video_id:
                return None
                
            headers = self.get_headers()
            response = self.session.get(
                f"https://www.tiktok.com/node/share/video/{video_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'video_id': video_id,
                    'success': True,
                    'data': data
                }
            else:
                return {
                    'video_id': video_id,
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                'video_id': video_id if 'video_id' in locals() else 'unknown',
                'success': False,
                'error': str(e)
            }
    
    def send_report(self, video_id, reason_id=1001, report_type=1):
        """Send actual report to TikTok"""
        try:
            # TikTok report payload
            payload = {
                'report_type': report_type,  # 1 for video, 2 for user
                'object_id': video_id,
                'owner_id': video_id,
                'reason': reason_id,
                'text': '',
                'report_scene': 39,
                'app_name': 'tiktok_web',
                'device_id': str(random.randint(1000000000000000000, 9999999999999999999)),
                'msToken': self.generate_ms_token(),
            }
            
            headers = self.get_headers()
            headers.update({
                'X-Secsdk-Csrf-Token': '000100000001',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            })
            
            # TikTok report endpoint
            report_url = "https://www.tiktok.com/api/report/item/"
            
            response = self.session.post(
                report_url,
                data=payload,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status_code') == 0:
                    return True, "Report submitted successfully"
                else:
                    return False, f"API error: {result.get('message', 'Unknown error')}"
            else:
                return False, f"HTTP error: {response.status_code}"
                
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def generate_ms_token(self):
        """Generate msToken for TikTok requests"""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join(random.choice(chars) for _ in range(126))
    
    def get_report_reasons(self):
        """Get available report reasons"""
        return [
            {"id": 1001, "text": "Illegal activities"},
            {"id": 1002, "text": "Harassment or bullying"},
            {"id": 1003, "text": "Hate speech"},
            {"id": 1004, "text": "Violent or graphic content"},
            {"id": 1005, "text": "Suicide or self-harm"},
            {"id": 1006, "text": "Child safety"},
            {"id": 1007, "text": "Spam"},
            {"id": 1008, "text": "Infringes my rights"},
            {"id": 1009, "text": "Dangerous acts"},
        ]

# =============================================
# REAL REPORTING ENGINE
# =============================================

class RealReportingEngine:
    def __init__(self):
        self.reporter = TikTokReporter()
        self.active = False
        self.stats = {
            'success': 0,
            'failed': 0,
            'start_time': None,
            'current_target': None
        }
    
    def start_reporting(self, target_url, report_count=100, threads=10):
        """Start real reporting process"""
        self.active = True
        self.stats = {
            'success': 0,
            'failed': 0,
            'start_time': time.time(),
            'current_target': target_url
        }
        
        print(f"{Color.GREEN}🚀 Starting REAL TikTok reporting...{Color.RESET}")
        
        # Extract video info first
        video_info = self.reporter.extract_video_info(target_url)
        if not video_info or not video_info['success']:
            print(f"{Color.RED}❌ Failed to extract video information{Color.RESET}")
            return False
        
        video_id = video_info['video_id']
        print(f"{Color.GREEN}🎯 Target Video ID: {video_id}{Color.RESET}")
        
        # Get report reasons
        reasons = self.reporter.get_report_reasons()
        
        def report_worker(worker_id):
            local_success = 0
            local_failed = 0
            
            for i in range(report_count // threads):
                if not self.active:
                    break
                
                try:
                    reason = random.choice(reasons)
                    success, message = self.reporter.send_report(video_id, reason['id'])
                    
                    if success:
                        local_success += 1
                        with threading.Lock():
                            self.stats['success'] += 1
                    else:
                        local_failed += 1
                        with threading.Lock():
                            self.stats['failed'] += 1
                    
                    # Smart delay to avoid rate limiting
                    time.sleep(random.uniform(1, 3))
                    
                    # Progress update
                    if (local_success + local_failed) % 5 == 0:
                        total = self.stats['success'] + self.stats['failed']
                        print(f"{Color.BLUE}📊 Worker {worker_id}: {local_success} success, {local_failed} failed | Total: {total}/{report_count}{Color.RESET}")
                        
                except Exception as e:
                    local_failed += 1
                    with threading.Lock():
                        self.stats['failed'] += 1
                    time.sleep(2)
            
            return local_success, local_failed
        
        # Start threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(report_worker, i) for i in range(threads)]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    success, failed = future.result()
                    print(f"{Color.CYAN}✅ Worker completed: {success} success, {failed} failed{Color.RESET}")
                except Exception as e:
                    print(f"{Color.RED}❌ Worker error: {e}{Color.RESET}")
        
        self.active = False
        return True
    
    def stop_reporting(self):
        """Stop reporting process"""
        self.active = False
    
    def get_stats(self):
        """Get current statistics"""
        if self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']
            total = self.stats['success'] + self.stats['failed']
            success_rate = (self.stats['success'] / total * 100) if total > 0 else 0
            
            return {
                'success': self.stats['success'],
                'failed': self.stats['failed'],
                'total': total,
                'success_rate': success_rate,
                'elapsed_time': elapsed,
                'active': self.active
            }
        return None

# =============================================
# TIKTOK URL VALIDATION FUNCTIONS
# =============================================

def extract_video_id_from_url(url):
    """Extract video ID from various TikTok URL formats"""
    url = url.strip().split('?')[0]
    
    # Pattern 1: Direct video ID in path
    video_pattern1 = r'tiktok\.com\/@[\w\.-]+\/video\/(\d+)'
    match1 = re.search(video_pattern1, url)
    if match1:
        return match1.group(1)
    
    # Pattern 2: Short URL
    short_pattern = r'vm\.tiktok\.com\/([\w]+)'
    match2 = re.search(short_pattern, url)
    if match2:
        return match2.group(1)
    
    # Pattern 3: Mobile URL
    vt_pattern = r'vt\.tiktok\.com\/([\w]+)'
    match3 = re.search(vt_pattern, url)
    if match3:
        return match3.group(1)
    
    # Pattern 4: Direct video ID
    if url.isdigit() and len(url) > 15:
        return url
    
    return None

def validate_tiktok_url(url):
    """Check if the URL is a valid TikTok URL"""
    tiktok_domains = [
        'tiktok.com', 'www.tiktok.com', 'vm.tiktok.com', 
        'vt.tiktok.com', 'm.tiktok.com', 'api.tiktok.com'
    ]
    
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Check if domain is TikTok
        for tiktok_domain in tiktok_domains:
            if domain == tiktok_domain or domain.endswith('.' + tiktok_domain):
                return True
                
        # Check if it's just a video ID
        if url.isdigit() and len(url) > 15:
            return True
            
        return False
    except:
        return False

# =============================================
# REAL REPORTING FUNCTIONS
# =============================================

def run_video_reporting():
    """Run REAL video mass reporting"""
    print(f"\n{Color.MAGENTA}{Color.BOLD}📹 REAL VIDEO MASS REPORTING{Color.RESET}")
    
    url = get_url_input("video")
    if not url:
        return
    
    # Validate URL
    if not validate_tiktok_url(url):
        print(f"{Color.RED}❌ Invalid TikTok URL{Color.RESET}")
        return
    
    # Get reporting parameters
    report_count = get_report_count()
    thread_count = get_thread_count()
    
    print(f"{Color.GREEN}🎯 Target: {url}{Color.RESET}")
    print(f"{Color.GREEN}📊 Reports: {report_count}{Color.RESET}")
    print(f"{Color.GREEN}🧵 Threads: {thread_count}{Color.RESET}")
    
    # Start real reporting
    engine = RealReportingEngine()
    
    # Start in background thread
    def run_engine():
        engine.start_reporting(url, report_count, thread_count)
    
    report_thread = threading.Thread(target=run_engine, daemon=True)
    report_thread.start()
    
    print(f"{Color.GREEN}🚀 Reporting started! Monitoring progress...{Color.RESET}")
    
    # Monitor progress
    try:
        while engine.active:
            stats = engine.get_stats()
            if stats:
                print(f"{Color.CYAN}📈 Progress: {stats['success']}/{report_count} successful | Rate: {stats['success_rate']:.1f}% | Elapsed: {stats['elapsed_time']:.1f}s{Color.RESET}")
            
            time.sleep(5)
            
            if stats and stats['success'] + stats['failed'] >= report_count:
                break
                
    except KeyboardInterrupt:
        print(f"{Color.YELLOW}🛑 Stopping reporting...{Color.RESET}")
        engine.stop_reporting()
    
    # Final stats
    final_stats = engine.get_stats()
    if final_stats:
        print(f"\n{Color.GREEN}{'='*50}{Color.RESET}")
        print(f"{Color.BOLD}🎉 REPORTING COMPLETED!{Color.RESET}")
        print(f"{Color.GREEN}✓ Successful: {final_stats['success']}{Color.RESET}")
        print(f"{Color.RED}✗ Failed: {final_stats['failed']}{Color.RESET}")
        print(f"{Color.BLUE}📈 Success Rate: {final_stats['success_rate']:.1f}%{Color.RESET}")
        print(f"{Color.YELLOW}⏰ Total Time: {final_stats['elapsed_time']:.1f}s{Color.RESET}")
        print(f"{Color.GREEN}{'='*50}{Color.RESET}")

def run_unlimited_mode():
    """Run UNLIMITED real reporting"""
    print(f"\n{Color.MAGENTA}{Color.BOLD}♾️ UNLIMITED REAL REPORTING{Color.RESET}")
    
    url = get_url_input("video")
    if not url:
        return
    
    if not validate_tiktok_url(url):
        print(f"{Color.RED}❌ Invalid TikTok URL{Color.RESET}")
        return
    
    print(f"{Color.RED}🚨 WARNING: Unlimited mode will run until stopped!{Color.RESET}")
    print(f"{Color.YELLOW}💡 Press Ctrl+C to stop{Color.RESET}")
    
    engine = RealReportingEngine()
    
    def unlimited_worker():
        report_count = 0
        while not stop_reporting:
            try:
                # Continuous reporting with small batches
                engine.start_reporting(url, 50, 5)
                report_count += 50
                print(f"{Color.GREEN}♾️ Cycle completed. Total reports: {report_count}{Color.RESET}")
                time.sleep(10)  # Cool down between cycles
            except Exception as e:
                print(f"{Color.RED}❌ Cycle error: {e}{Color.RESET}")
                time.sleep(30)
    
    unlimited_thread = threading.Thread(target=unlimited_worker, daemon=True)
    unlimited_thread.start()
    
    try:
        while not stop_reporting:
            time.sleep(1)
    except KeyboardInterrupt:
        global stop_reporting
        stop_reporting = True
        print(f"{Color.YELLOW}🛑 Unlimited mode stopped{Color.RESET}")

# =============================================
# USER INPUT FUNCTIONS
# =============================================

def get_url_input(report_type):
    """Get URL input from user"""
    while True:
        try:
            if report_type == "video":
                prompt = f"{Color.YELLOW}🎯 Enter TikTok Video URL: {Color.RESET}"
            else:
                prompt = f"{Color.YELLOW}🎯 Enter TikTok URL: {Color.RESET}"
            
            url = input(prompt).strip()
            
            if not url:
                print(f"{Color.RED}❌ URL cannot be empty{Color.RESET}")
                continue
            
            if not validate_tiktok_url(url):
                print(f"{Color.RED}❌ Invalid TikTok URL format{Color.RESET}")
                continue
            
            return url
            
        except KeyboardInterrupt:
            return None
        except Exception as e:
            print(f"{Color.RED}❌ Error: {e}{Color.RESET}")

def get_report_count():
    """Get number of reports to send"""
    while True:
        try:
            count = input(f"{Color.YELLOW}🎯 Enter number of reports (default 100): {Color.RESET}").strip()
            if not count:
                return 100
            
            count = int(count)
            if count <= 0:
                print(f"{Color.RED}❌ Report count must be positive{Color.RESET}")
                continue
            if count > 10000:
                print(f"{Color.YELLOW}⚠ Using maximum 10000 reports{Color.RESET}")
                return 10000
            return count
        except ValueError:
            print(f"{Color.RED}❌ Please enter a valid number{Color.RESET}")

def get_thread_count():
    """Get number of threads"""
    while True:
        try:
            threads = input(f"{Color.YELLOW}🎯 Enter number of threads (default 5): {Color.RESET}").strip()
            if not threads:
                return 5
            
            threads = int(threads)
            if threads <= 0:
                print(f"{Color.RED}❌ Thread count must be positive{Color.RESET}")
                continue
            if threads > 50:
                print(f"{Color.YELLOW}⚠ Using maximum 50 threads{Color.RESET}")
                return 50
            return threads
        except ValueError:
            print(f"{Color.RED}❌ Please enter a valid number{Color.RESET}")

# =============================================
# REST OF THE FUNCTIONS (Keep from previous version)
# =============================================

# [Keep all the weather, time, display, telegram functions from previous version]
# They remain the same, just replace the reporting functions with real ones

def display_banner():
    banner = f"""
{Color.GREEN}{Color.BOLD}
  _____ _____    ___   _   _  _    _____ ___   ___  _    
 |_   _|_   _|__| _ ) /_\ | \| |__|_   _/ _ \ / _ \| |   
   | |   | ||___| _ \/ _ \| .` |___|| || (_) | (_) | |__ 
   |_|   |_|    |___/_/ \_\_|\_|    |_| \___/ \___/|____|
                    REAL TIKTOK REPORT BOT                            
{Color.RESET}
{Color.YELLOW}Features:{Color.RESET}
{Color.RED}• REAL TikTok API Integration
{Color.GREEN}• Actual Report Submission
{Color.RED}• Multi-threaded Reporting
{Color.GREEN}• Real-time Progress Tracking
{Color.RED}• Smart Rate Limiting
{Color.GREEN}• Unlimited Mode
{Color.RED}• Telegram Bot Integration{Color.RESET}

{Color.RED}⚠ LEGAL DISCLAIMER: Use responsibly and ethically ⚠{Color.RESET}
"""
    print(banner)

# [Include all other functions from previous version...]

def main():
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Auto install dependencies
    check_and_install_dependencies()
    
    # Start Telegram Bot
    global telegram_bot
    telegram_bot = setup_telegram_bot()
    
    # Display banner
    display_banner()
    
    # Create default files
    create_default_files()
    
    # Show bot status
    if telegram_bot:
        print(f"{Color.GREEN}🤖 Telegram Bot: ONLINE{Color.RESET}")
        print(f"{Color.CYAN}💡 Kirim /start ke bot Anda untuk mengakses menu{Color.RESET}")
    else:
        print(f"{Color.YELLOW}🤖 Telegram Bot: OFFLINE{Color.RESET}")
    
    print(f"{Color.CYAN}⏰ Waktu Sistem: {datetime.now().strftime('%A, %d %B %Y %H:%M:%S')}{Color.RESET}")
    
    while True:
        display_menu()
        choice = get_user_choice()
        
        if choice == 1:
            run_video_reporting()
        elif choice == 2:
            print(f"{Color.YELLOW}👤 Profile reporting - Use video mode for now{Color.RESET}")
        elif choice == 3:
            print(f"{Color.YELLOW}🔄 Combined mode - Use video mode{Color.RESET}")
        elif choice == 4:
            run_video_reporting()  # Single URL mode
        elif choice == 7:
            print(f"{Color.YELLOW}⚡ Ultra-fast mode - Use unlimited mode{Color.RESET}")
        elif choice == 8:
            run_unlimited_mode()
        elif choice == 9:
            print(f"\n{Color.GREEN}👋 Thank you for using REAL TikTok Report Bot!{Color.RESET}")
            break
        
        global stop_reporting
        stop_reporting = False
        
        if choice != 9:
            cont = input(f"\n{Color.YELLOW}🔄 Continue? (y/n): {Color.RESET}").strip().lower()
            if cont not in ['y', 'yes']:
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Color.RED}🛑 Process interrupted{Color.RESET}")
    except Exception as e:
        print(f"\n{Color.RED}💥 Error: {e}{Color.RESET}")
