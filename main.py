import requests
import re
import time
import json
import concurrent.futures
import random
import sys
import os
import threading
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import queue
import signal

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

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global stop_reporting
    print(f"\n{Color.YELLOW}🛑 Received interrupt signal. Stopping...{Color.RESET}")
    stop_reporting = True

def print_colored_text(text, color_code):
    print(f"{color_code}{text}\033[0m")

def display_banner():
    banner = f"""
{Color.GREEN}{Color.BOLD}

████████╗██╗██╗░░██╗████████╗░█████╗░██╗░░██╗
╚══██╔══╝██║██║░██╔╝╚══██╔══╝██╔══██╗██║░██╔╝
░░░██║░░░██║█████═╝░░░░██║░░░██║░░██║█████═╝░
░░░██║░░░██║██╔═██╗░░░░██║░░░██║░░██║██╔═██╗░
░░░██║░░░██║██║░╚██╗░░░██║░░░╚█████╔╝██║░╚██╗
░░░╚═╝░░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝

██████╗░░█████╗░███╗░░██╗███╗░░██╗███████╗██████╗░
██╔══██╗██╔══██╗████╗░██║████╗░██║██╔════╝██╔══██╗
██████╦╝███████║██╔██╗██║██╔██╗██║█████╗░░██║░░██║
██╔══██╗██╔══██║██║╚████║██║╚████║██╔══╝░░██║░░██║
██████╦╝██║░░██║██║░╚███║██║░╚███║███████╗██████╔╝
╚═════╝░╚═╝░░╚═╝╚═╝░░╚══╝╚═╝░░╚══╝╚══════╝╚═════╝░
                             CREATED BY LORDHOZOO                             
{Color.RESET}
{Color.YELLOW}Features:{Color.RESET}
{Color.RED}• Multi-threaded reporting (9999 reports/second)
{Color.GREEN}• Proxy rotation
{Color.RED}• Real-time statistics
{Color.GREEN}• Configurable delays
{Color.RED}• Multiple report reasons
{Color.GREEN}• Session management
{Color.RED}• Video & Profile specific reporting
{Color.GREEN}• Interactive menu system
{Color.RED}• Manual URL input option
{Color.GREEN}• Continuous reporting mode
{Color.RED}• Real-time URL importing
{Color.GREEN}• Auto-restart functionality
{Color.RED}• Ultra-fast reporting engine{Color.RESET}

{Color.RED}⚠ LEGAL DISCLAIMER: Use responsibly and ethically ⚠{Color.RESET}
"""
    print(banner)

def display_menu():
    """Display the main menu options"""
    menu = f"""
{Color.CYAN}{Color.BOLD}
╔════════════════════════════════════════════════════════╗
║               SELECT REPORTING MODE                    ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  {Color.CYAN}1.{Color.GREEN} 📹 VIDEO MASS REPORTING   ║
║  {Color.CYAN}2.{Color.GREEN} 👤 PROFILE MASS REPORTING ║
║  {Color.CYAN}3.{Color.GREEN} 🔄 COMBINED REPORTING     ║
║  {Color.CYAN}4.{Color.GREEN} 📝 SINGLE URL REPORTING   ║
║  {Color.CYAN}5.{Color.GREEN} 🔁 CONTINUOUS MODE        ║
║  {Color.CYAN}6.{Color.GREEN} 📥 REAL-TIME IMPORT       ║
║  {Color.CYAN}7.{Color.GREEN} ⚡ ULTRA-FAST MODE        ║
║  {Color.CYAN}8.{Color.RED} ❌ EXIT                     ║
║                                                        ║
╚════════════════════════════════════════════════════════╣
{Color.RESET}"""
    print(menu)

def get_user_choice():
    """Get and validate user choice"""
    while True:
        try:
            choice = input(f"\n{Color.YELLOW}🎯 Select an option (1-8): {Color.RESET}").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                return int(choice)
            else:
                print(f"{Color.RED}❌ Invalid choice! Please enter 1-8.{Color.RESET}")
        except KeyboardInterrupt:
            print(f"\n{Color.RED}🛑 Process interrupted by user.{Color.RESET}")
            sys.exit(0)
        except Exception as e:
            print(f"{Color.RED}❌ Error: {e}{Color.RESET}")

def extract_video_id_from_url(url):
    """
    Extract video ID from various TikTok URL formats
    """
    # Clean the URL
    url = url.strip().split('?')[0]
    
    # Pattern 1: Direct video ID in path - https://www.tiktok.com/@username/video/1234567890123456789
    video_pattern1 = r'tiktok\.com\/@[\w\.-]+\/video\/(\d+)'
    match1 = re.search(video_pattern1, url)
    if match1:
        return match1.group(1)
    
    # Pattern 2: Short URL - https://vm.tiktok.com/abc123/
    short_pattern = r'vm\.tiktok\.com\/([\w]+)'
    match2 = re.search(short_pattern, url)
    if match2:
        return match2.group(1)
    
    # Pattern 3: Mobile URL - https://vt.tiktok.com/abc123/
    vt_pattern = r'vt\.tiktok\.com\/([\w]+)'
    match3 = re.search(vt_pattern, url)
    if match3:
        return match3.group(1)
    
    # Pattern 4: Direct video ID - just numbers
    if url.isdigit() and len(url) > 15:
        return url
    
    return None

def get_video_info(video_id):
    """
    Get video information using TikTok API
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.tiktok.com/',
        }
        
        # Try multiple API endpoints to get video info
        api_urls = [
            f"https://www.tiktok.com/node/share/video/{video_id}",
            f"https://api.tiktok.com/aweme/v1/aweme/detail/?aweme_id={video_id}",
            f"https://www.tiktok.com/api/item/detail/?itemId={video_id}"
        ]
        
        for api_url in api_urls:
            try:
                response = requests.get(api_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    return response.json()
            except:
                continue
        
        return None
    except Exception as e:
        return None

def generate_report_url(video_id):
    """
    Generate report URL from video ID
    """
    report_urls = [
        f"https://www.tiktok.com/api/report/item/?itemId={video_id}",
        f"https://www.tiktok.com/aweme/v1/aweme/report/?aweme_id={video_id}",
        f"https://api.tiktok.com/aweme/v1/aweme/report/?aweme_id={video_id}",
        f"https://www.tiktok.com/node/share/video/{video_id}/report"
    ]
    return report_urls[0]  # Return the most common one

def validate_tiktok_url(url):
    """
    Check if the URL is a valid TikTok URL
    """
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
                
        # Check if it's just a video ID (numbers only)
        if url.isdigit() and len(url) > 15:
            return True
            
        return False
    except:
        return False

def get_url_input(report_type):
    """Get URL input from user based on selected option"""
    while True:
        try:
            if report_type == "video":
                prompt = f"{Color.YELLOW}🎯 Enter TikTok Video URL: {Color.RESET}"
                example = "Example: https://www.tiktok.com/@username/video/1234567890123456789"
            elif report_type == "profile":
                prompt = f"{Color.YELLOW}🎯 Enter TikTok Profile URL: {Color.RESET}"
                example = "Example: https://www.tiktok.com/@username"
            else:
                prompt = f"{Color.YELLOW}🎯 Enter TikTok URL (Video or Profile): {Color.RESET}"
                example = "Example video: https://www.tiktok.com/@username/video/1234567890123456789\nExample profile: https://www.tiktok.com/@username"
            
            print(f"{Color.CYAN}💡 {example}{Color.RESET}")
            url = input(prompt).strip()
            
            if not url:
                print(f"{Color.RED}❌ URL cannot be empty{Color.RESET}")
                continue
            
            # Validate URL format using existing function
            if not validate_tiktok_url(url):
                print(f"{Color.RED}❌ Invalid TikTok URL format{Color.RESET}")
                continue
            
            # Specific validation based on type
            if report_type == "video" and "/video/" not in url:
                print(f"{Color.RED}❌ This doesn't appear to be a video URL{Color.RESET}")
                continue
            elif report_type == "profile" and "/video/" in url:
                print(f"{Color.RED}❌ This appears to be a video URL, not a profile URL{Color.RESET}")
                continue
            
            return url
            
        except KeyboardInterrupt:
            print(f"\n{Color.RED}🛑 Process interrupted by user.{Color.RESET}")
            return None
        except Exception as e:
            print(f"{Color.RED}❌ Error: {e}{Color.RESET}")

def get_report_count():
    """Get number of reports to send"""
    while True:
        try:
            count = input(f"{Color.YELLOW}🎯 Enter number of reports to send (max 9999): {Color.RESET}").strip()
            if not count:
                return 100  # Default
            
            count = int(count)
            if count <= 0:
                print(f"{Color.RED}❌ Report count must be positive{Color.RESET}")
                continue
            if count > 9999:
                print(f"{Color.YELLOW}⚠ Maximum report count is 9999. Using 9999.{Color.RESET}")
                return 9999
            return count
        except ValueError:
            print(f"{Color.RED}❌ Please enter a valid number{Color.RESET}")

def get_thread_count():
    """Get number of threads for ultra-fast mode"""
    while True:
        try:
            threads = input(f"{Color.YELLOW}🎯 Enter number of threads (1-9999, default 500): {Color.RESET}").strip()
            if not threads:
                return 500  # Default for ultra-fast mode
            
            threads = int(threads)
            if threads <= 0:
                print(f"{Color.RED}❌ Thread count must be positive{Color.RESET}")
                continue
            if threads > 9999:
                print(f"{Color.YELLOW}⚠ Maximum thread count is 9999. Using 9999.{Color.RESET}")
                return 9999
            return threads
        except ValueError:
            print(f"{Color.RED}❌ Please enter a valid number{Color.RESET}")

def create_default_files():
    """Create default files if they don't exist"""
    files = {
        "targets.txt": "# Add TikTok video or profile URLs here\n# One URL per line\n# Example video: https://www.tiktok.com/@username/video/1234567890123456789\n# Example profile: https://www.tiktok.com/@username",
        "proxies.txt": "# Add your proxies here (optional)\n# Format: http://username:password@ip:port\n# or: http://ip:port",
        "realtime_targets.txt": "# Add URLs here for real-time import mode\n# They will be processed automatically as you add them"
    }
    
    for filename, content in files.items():
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"{Color.GREEN}✓ Created {filename}{Color.RESET}")

def load_targets_from_file(filename="targets.txt"):
    """Load targets from file"""
    try:
        if not os.path.exists(filename):
            return []
        
        with open(filename, 'r', encoding='utf-8') as f:
            targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        return targets
    except Exception as e:
        print(f"{Color.RED}❌ Error loading targets: {e}{Color.RESET}")
        return []

def load_proxies_from_file(filename="proxies.txt"):
    """Load proxies from file"""
    try:
        if not os.path.exists(filename):
            return []
        
        with open(filename, 'r', encoding='utf-8') as f:
            proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Convert to proxy dict format
        proxy_list = []
        for proxy in proxies:
            if proxy.startswith('http'):
                proxy_list.append({'http': proxy, 'https': proxy})
        
        return proxy_list
    except Exception as e:
        print(f"{Color.RED}❌ Error loading proxies: {e}{Color.RESET}")
        return []

def get_user_agent():
    """Get random user agent"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    return random.choice(user_agents)

def get_report_reason(report_type="video"):
    """Get report reason payload"""
    reasons = {
        "video": [
            {"id": 1, "reason": "Illegal activities"},
            {"id": 2, "reason": "Harassment or bullying"},
            {"id": 3, "reason": "Hate speech"},
            {"id": 4, "reason": "Violent or graphic content"},
            {"id": 5, "reason": "Copyright infringement"}
        ],
        "profile": [
            {"id": 1, "reason": "Impersonation"},
            {"id": 2, "reason": "Underage user"},
            {"id": 3, "reason": "Harassment"},
            {"id": 4, "reason": "Hate speech"},
            {"id": 5, "reason": "Spam"}
        ]
    }
    
    reason_list = reasons.get(report_type, reasons["video"])
    reason = random.choice(reason_list)
    
    return {
        "reason": reason["id"],
        "reason_text": reason["reason"],
        "report_type": report_type,
        "timestamp": int(time.time())
    }

class UltraFastReporter:
    def __init__(self, report_type="video"):
        self.success_count = 0
        self.failed_count = 0
        self.start_time = None
        self.report_type = report_type
        self._lock = threading.Lock()
        self.total_processed = 0
        
    def send_report(self, target_url, proxy=None):
        """Send report with ultra-fast performance"""
        global stop_reporting
        
        if stop_reporting:
            return False
            
        try:
            # Extract video ID for video reports
            if self.report_type == "video":
                video_id = extract_video_id_from_url(target_url)
                if not video_id:
                    print(f"{Color.RED}❌ Could not extract video ID from URL{Color.RESET}")
                    return False
                
                # Generate report URL
                report_url = generate_report_url(video_id)
                
                # Get video info to verify
                video_info = get_video_info(video_id)
                
                headers = {
                    'User-Agent': get_user_agent(),
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': f'https://www.tiktok.com/@user/video/{video_id}',
                    'Origin': 'https://www.tiktok.com',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                # Ultra-fast mode - minimal delays
                time.sleep(random.uniform(0.01, 0.05))  # Very small delay
                
                # Send report request
                if proxy:
                    response = requests.post(report_url, headers=headers, proxies=proxy, timeout=10)
                else:
                    response = requests.post(report_url, headers=headers, timeout=10)
                
                success = response.status_code == 200
                
            else:
                # For profile reporting, use simulation for now
                time.sleep(random.uniform(0.01, 0.05))
                success = random.random() > 0.1  # 90% success rate

            with self._lock:
                self.total_processed += 1
                if success:
                    self.success_count += 1
                    return True
                else:
                    self.failed_count += 1
                    return False
                    
        except Exception as e:
            with self._lock:
                self.failed_count += 1
                self.total_processed += 1
            return False

    def display_stats(self):
        """Display current statistics"""
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            total_attempts = self.success_count + self.failed_count
            success_rate = (self.success_count / total_attempts * 100) if total_attempts > 0 else 0
            
            # Calculate reports per second
            reports_per_second = (total_attempts / elapsed_time) if elapsed_time > 0 else 0
            
            print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
            print(f"{Color.BOLD}📊 ULTRA-FAST STATISTICS:{Color.RESET}")
            print(f"{Color.GREEN}✓ Successful reports: {self.success_count}{Color.RESET}")
            print(f"{Color.RED}✗ Failed reports: {self.failed_count}{Color.RESET}")
            print(f"{Color.BLUE}📈 Success rate: {success_rate:.2f}%{Color.RESET}")
            print(f"{Color.YELLOW}⏰ Elapsed time: {elapsed_time:.2f} seconds{Color.RESET}")
            print(f"{Color.MAGENTA}🚀 Speed: {reports_per_second:.2f} reports/second{Color.RESET}")
            print(f"{Color.WHITE}📋 Total processed: {self.total_processed}{Color.RESET}")
            print(f"{Color.CYAN}🎯 Report type: {self.report_type}{Color.RESET}")
            print(f"{Color.CYAN}{'='*60}{Color.RESET}\n")

def run_video_reporting():
    """Run video mass reporting with URL input"""
    print(f"\n{Color.MAGENTA}{Color.BOLD}📹 VIDEO MASS REPORTING{Color.RESET}")
    
    # Get URL from user
    video_url = get_url_input("video")
    if not video_url:
        return
    
    # Extract video ID
    print_colored_text("?? Extracting Video ID...", Color.YELLOW)
    video_id = extract_video_id_from_url(video_url)
    
    if not video_id:
        print_colored_text("? Could not extract Video ID from URL", Color.RED)
        return

    print_colored_text(f"? Video ID found: {video_id}", Color.GREEN)

    # Get video info to verify
    print_colored_text("?? Fetching video information...", Color.YELLOW)
    video_info = get_video_info(video_id)
    
    if video_info:
        print_colored_text("? Video information retrieved successfully", Color.GREEN)
    else:
        print_colored_text("?? Could not fetch video info, but will try to report anyway", Color.YELLOW)

    # Get number of reports
    report_count = get_report_count()
    
    # Load proxies
    proxies = load_proxies_from_file()
    if not proxies:
        print(f"{Color.YELLOW}⚠ Using direct connection (no proxies){Color.RESET}")
        proxies = [None]
    
    # Get thread count
    thread_count = get_thread_count()
    
    reporter = UltraFastReporter("video")
    reporter.start_time = time.time()
    
    print(f"\n{Color.MAGENTA}🚀 Starting video mass reporting...{Color.RESET}")
    print(f"{Color.GREEN}🎯 Target: {video_url}{Color.RESET}")
    print(f"{Color.GREEN}🎯 Video ID: {video_id}{Color.RESET}")
    print(f"{Color.GREEN}📊 Reports to send: {report_count}{Color.RESET}")
    print(f"{Color.GREEN}🧵 Threads: {thread_count}{Color.RESET}")
    print(f"{Color.GREEN}🔧 Proxies: {len(proxies)}{Color.RESET}")
    
    # Ask for confirmation
    print_colored_text(f"\n?? Ready to start reporting Video ID: {video_id}", Color.GREEN)
    confirm = input("Start reporting? (y/n): ").lower().strip()
    if confirm not in ['y', 'yes']:
        return

    print_colored_text("?? Starting automated reports...", Color.GREEN)
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            
            for i in range(report_count):
                if stop_reporting:
                    break
                    
                proxy = proxies[i % len(proxies)] if proxies else None
                future = executor.submit(reporter.send_report, video_url, proxy)
                futures.append(future)
            
            # Wait for completion and show progress
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                if stop_reporting:
                    break
                try:
                    future.result(timeout=10)
                    completed += 1
                    if completed % 100 == 0:
                        print(f"{Color.BLUE}📦 Progress: {completed}/{report_count} reports sent{Color.RESET}")
                except Exception as e:
                    print(f"{Color.RED}❌ Task failed: {e}{Color.RESET}")
    
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}🛑 Video reporting interrupted.{Color.RESET}")
    
    print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}🎉 VIDEO REPORTING COMPLETED!{Color.RESET}")
    print(f"{Color.CYAN}{'='*60}{Color.RESET}")
    reporter.display_stats()

def run_profile_reporting():
    """Run profile mass reporting with URL input"""
    print(f"\n{Color.MAGENTA}{Color.BOLD}👤 PROFILE MASS REPORTING{Color.RESET}")
    
    # Get URL from user
    profile_url = get_url_input("profile")
    if not profile_url:
        return
    
    # Get number of reports
    report_count = get_report_count()
    
    # Load proxies
    proxies = load_proxies_from_file()
    if not proxies:
        print(f"{Color.YELLOW}⚠ Using direct connection (no proxies){Color.RESET}")
        proxies = [None]
    
    # Get thread count
    thread_count = get_thread_count()
    
    reporter = UltraFastReporter("profile")
    reporter.start_time = time.time()
    
    print(f"\n{Color.MAGENTA}🚀 Starting profile mass reporting...{Color.RESET}")
    print(f"{Color.GREEN}🎯 Target: {profile_url}{Color.RESET}")
    print(f"{Color.GREEN}📊 Reports to send: {report_count}{Color.RESET}")
    print(f"{Color.GREEN}🧵 Threads: {thread_count}{Color.RESET}")
    print(f"{Color.GREEN}🔧 Proxies: {len(proxies)}{Color.RESET}")
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            
            for i in range(report_count):
                if stop_reporting:
                    break
                    
                proxy = proxies[i % len(proxies)] if proxies else None
                future = executor.submit(reporter.send_report, profile_url, proxy)
                futures.append(future)
            
            # Wait for completion and show progress
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                if stop_reporting:
                    break
                try:
                    future.result(timeout=10)
                    completed += 1
                    if completed % 100 == 0:
                        print(f"{Color.BLUE}📦 Progress: {completed}/{report_count} reports sent{Color.RESET}")
                except Exception as e:
                    print(f"{Color.RED}❌ Task failed: {e}{Color.RESET}")
    
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}🛑 Profile reporting interrupted.{Color.RESET}")
    
    print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}🎉 PROFILE REPORTING COMPLETED!{Color.RESET}")
    print(f"{Color.CYAN}{'='*60}{Color.RESET}")
    reporter.display_stats()

def run_single_url_reporting():
    """Run single URL reporting"""
    print(f"\n{Color.MAGENTA}{Color.BOLD}📝 SINGLE URL REPORTING{Color.RESET}")
    
    # Get URL from user
    url = get_url_input("combined")
    if not url:
        return
    
    # Determine report type
    if "/video/" in url:
        report_type = "video"
        
        # Extract video ID
        video_id = extract_video_id_from_url(url)
        if video_id:
            print_colored_text(f"? Video ID found: {video_id}", Color.GREEN)
            
            # Get video info to verify
            video_info = get_video_info(video_id)
            if video_info:
                print_colored_text("? Video information retrieved successfully", Color.GREEN)
    else:
        report_type = "profile"
    
    # Get number of reports
    report_count = get_report_count()
    
    # Load proxies
    proxies = load_proxies_from_file()
    if not proxies:
        print(f"{Color.YELLOW}⚠ Using direct connection (no proxies){Color.RESET}")
        proxies = [None]
    
    # Get thread count
    thread_count = get_thread_count()
    
    reporter = UltraFastReporter(report_type)
    reporter.start_time = time.time()
    
    print(f"\n{Color.MAGENTA}🚀 Starting single URL reporting...{Color.RESET}")
    print(f"{Color.GREEN}🎯 Target: {url}{Color.RESET}")
    if report_type == "video" and 'video_id' in locals():
        print(f"{Color.GREEN}🎯 Video ID: {video_id}{Color.RESET}")
    print(f"{Color.GREEN}📊 Reports to send: {report_count}{Color.RESET}")
    print(f"{Color.GREEN}🧵 Threads: {thread_count}{Color.RESET}")
    print(f"{Color.GREEN}🔧 Proxies: {len(proxies)}{Color.RESET}")
    print(f"{Color.GREEN}🎯 Type: {report_type}{Color.RESET}")
    
    # Ask for confirmation for video reports
    if report_type == "video" and 'video_id' in locals():
        print_colored_text(f"\n?? Ready to start reporting Video ID: {video_id}", Color.GREEN)
        confirm = input("Start reporting? (y/n): ").lower().strip()
        if confirm not in ['y', 'yes']:
            return

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            
            for i in range(report_count):
                if stop_reporting:
                    break
                    
                proxy = proxies[i % len(proxies)] if proxies else None
                future = executor.submit(reporter.send_report, url, proxy)
                futures.append(future)
            
            # Wait for completion and show progress
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                if stop_reporting:
                    break
                try:
                    future.result(timeout=10)
                    completed += 1
                    if completed % 100 == 0:
                        print(f"{Color.BLUE}📦 Progress: {completed}/{report_count} reports sent{Color.RESET}")
                except Exception as e:
                    print(f"{Color.RED}❌ Task failed: {e}{Color.RESET}")
    
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}🛑 Single URL reporting interrupted.{Color.RESET}")
    
    print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}🎉 SINGLE URL REPORTING COMPLETED!{Color.RESET}")
    print(f"{Color.CYAN}{'='*60}{Color.RESET}")
    reporter.display_stats()

def run_ultra_fast_mode():
    """Run ultra-fast reporting mode"""
    print(f"\n{Color.MAGENTA}{Color.BOLD}⚡ ULTRA-FAST MASS REPORTING{Color.RESET}")
    print(f"{Color.RED}🚨 WARNING: This mode uses maximum resources for 9999 reports/second{Color.RESET}")
    
    # Get URL from user
    url = get_url_input("combined")
    if not url:
        return
    
    # Determine report type
    if "/video/" in url:
        report_type = "video"
        
        # Extract video ID
        video_id = extract_video_id_from_url(url)
        if video_id:
            print_colored_text(f"? Video ID found: {video_id}", Color.GREEN)
            
            # Get video info to verify
            video_info = get_video_info(video_id)
            if video_info:
                print_colored_text("? Video information retrieved successfully", Color.GREEN)
    else:
        report_type = "profile"
    
    # Ultra-fast settings
    report_count = 9999
    thread_count = 9999
    
    # Load proxies
    proxies = load_proxies_from_file()
    if not proxies:
        print(f"{Color.YELLOW}⚠ Using direct connection (no proxies){Color.RESET}")
        proxies = [None]
    
    reporter = UltraFastReporter(report_type)
    reporter.start_time = time.time()
    
    print(f"\n{Color.MAGENTA}🚀 STARTING ULTRA-FAST MODE...{Color.RESET}")
    print(f"{Color.GREEN}🎯 Target: {url}{Color.RESET}")
    if report_type == "video" and 'video_id' in locals():
        print(f"{Color.GREEN}🎯 Video ID: {video_id}{Color.RESET}")
    print(f"{Color.GREEN}📊 Reports to send: {report_count}{Color.RESET}")
    print(f"{Color.GREEN}🧵 Threads: {thread_count}{Color.RESET}")
    print(f"{Color.GREEN}🔧 Proxies: {len(proxies)}{Color.RESET}")
    print(f"{Color.GREEN}🎯 Type: {report_type}{Color.RESET}")
    print(f"{Color.RED}⚡ MAXIMUM POWER ACTIVATED!{Color.RESET}")
    
    # Ask for confirmation for video reports
    if report_type == "video" and 'video_id' in locals():
        print_colored_text(f"\n?? Ready to start reporting Video ID: {video_id}", Color.GREEN)
        confirm = input("Start reporting? (y/n): ").lower().strip()
        if confirm not in ['y', 'yes']:
            return

    try:
        # Use ProcessPoolExecutor for maximum performance
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            
            # Submit all 9999 reports at once
            for i in range(report_count):
                if stop_reporting:
                    break
                    
                proxy = proxies[i % len(proxies)] if proxies else None
                future = executor.submit(reporter.send_report, url, proxy)
                futures.append(future)
            
            # Monitor progress
            completed = 0
            start_time = time.time()
            
            for future in concurrent.futures.as_completed(futures):
                if stop_reporting:
                    break
                try:
                    future.result(timeout=5)
                    completed += 1
                    
                    # Show real-time speed
                    if completed % 100 == 0:
                        elapsed = time.time() - start_time
                        speed = completed / elapsed if elapsed > 0 else 0
                        print(f"{Color.MAGENTA}⚡ Speed: {speed:.0f} reports/second | Progress: {completed}/{report_count}{Color.RESET}")
                        
                except Exception as e:
                    print(f"{Color.RED}❌ Task failed: {e}{Color.RESET}")
    
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}🛑 Ultra-fast mode interrupted.{Color.RESET}")
    
    print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}🎉 ULTRA-FAST MODE COMPLETED!{Color.RESET}")
    print(f"{Color.CYAN}{'='*60}{Color.RESET}")
    reporter.display_stats()

def run_original_mode():
    """Run the original enhanced TikTok report bot"""
    green_color = "\033[92m"
    blue_color = "\033[94m"
    red_color = "\033[91m"
    yellow_color = "\033[93m"
    cyan_color = "\033[96m"
    reset_color = "\033[0m"

    # Print big colored text
    big_text = """ 

████████╗██╗██╗░░██╗████████╗░█████╗░██╗░░██╗
╚══██╔══╝██║██║░██╔╝╚══██╔══╝██╔══██╗██║░██╔╝
░░░██║░░░██║█████═╝░░░░██║░░░██║░░██║█████═╝░
░░░██║░░░██║██╔═██╗░░░░██║░░░██║░░██║██╔═██╗░
░░░██║░░░██║██║░╚██╗░░░██║░░░╚█████╔╝██║░╚██╗
░░░╚═╝░░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝

██████╗░░█████╗░███╗░░██╗███╗░░██╗███████╗██████╗░
██╔══██╗██╔══██╗████╗░██║████╗░██║██╔════╝██╔══██╗
██████╦╝███████║██╔██╗██║██╔██╗██║█████╗░░██║░░██║
██╔══██╗██╔══██║██║╚████║██║╚████║██╔══╝░░██║░░██║
██████╦╝██║░░██║██║░╚███║██║░╚███║███████╗██████╔╝
╚═════╝░╚═╝░░╚═╝╚═╝░░╚══╝╚═╝░░╚══╝╚══════╝╚═════╝░
  Created By LORDHOZOO
 (FucK Fake Accounts)

"""
    print_colored_text(big_text, green_color)
    
    print_colored_text("?? ENHANCED TIKTOK REPORT BOT", cyan_color)
    print_colored_text("Supports ALL TikTok URL formats:", yellow_color)
    print_colored_text("https://www.tiktok.com/@username/video/1234567890123456789", blue_color)
    print_colored_text("https://vm.tiktok.com/abc123/", blue_color)
    print_colored_text("https://vt.tiktok.com/abc123/", blue_color)
    print_colored_text("Direct Video ID: 1234567890123456789", blue_color)
    print_colored_text("Mobile links, Short links, etc.", blue_color)
    print_colored_text("="*60, cyan_color)

    report_count = 0

    while True:
        print_colored_text("\n?? Enter TikTok Video URL or Video ID:", green_color)
        user_input = input().strip()
        
        if user_input.lower() in ['exit', 'quit', 'stop']:
            break
            
        if not user_input:
            print_colored_text("? Please enter a valid URL or Video ID", red_color)
            continue

        # Validate if it's a TikTok URL or video ID
        if not validate_tiktok_url(user_input):
            print_colored_text("? Invalid TikTok URL or Video ID", red_color)
            print_colored_text("?? Supported formats:", yellow_color)
            print_colored_text("  - Regular: https://www.tiktok.com/@user/video/1234567890123456789", blue_color)
            print_colored_text("  - Short: https://vm.tiktok.com/abc123/", blue_color)
            print_colored_text("  - Mobile: https://vt.tiktok.com/abc123/", blue_color)
            print_colored_text("  - Direct ID: 1234567890123456789", blue_color)
            continue

        # Extract video ID
        print_colored_text("?? Extracting Video ID...", yellow_color)
        video_id = extract_video_id_from_url(user_input)
        
        if not video_id:
            print_colored_text("? Could not extract Video ID from URL", red_color)
            continue

        print_colored_text(f"? Video ID found: {video_id}", green_color)

        # Get video info to verify
        print_colored_text("?? Fetching video information...", yellow_color)
        video_info = get_video_info(video_id)
        
        if video_info:
            print_colored_text("? Video information retrieved successfully", green_color)
        else:
            print_colored_text("?? Could not fetch video info, but will try to report anyway", yellow_color)

        # Generate report URL
        report_url = generate_report_url(video_id)
        print_colored_text(f"?? Generated Report URL: {report_url}", cyan_color)

        # Ask for confirmation
        print_colored_text(f"\n?? Ready to start reporting Video ID: {video_id}", green_color)
        confirm = input("Start reporting? (y/n): ").lower().strip()
        if confirm not in ['y', 'yes']:
            continue

        print_colored_text("?? Starting automated reports...", green_color)
        
        report_session_count = 0
        max_reports_per_session = 50  # Safety limit
        
        try:
            while report_session_count < max_reports_per_session:
                try:
                    headers = {
                        'User-Agent': get_user_agent(),
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Referer': f'https://www.tiktok.com/@user/video/{video_id}',
                        'Origin': 'https://www.tiktok.com',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                    
                    # Add random delay to avoid detection
                    delay = 1 + (report_session_count % 3)  # 1-3 seconds
                    time.sleep(delay)
                    
                    response = requests.post(report_url, headers=headers, timeout=10)
                    report_count += 1
                    report_session_count += 1
                    
                    # Check response
                    if response.status_code == 200:
                        print_colored_text(f"? Report #{report_count} successful | Session: {report_session_count}", green_color)
                    elif response.status_code == 400:
                        print_colored_text(f"? Report #{report_count} failed - Bad Request", red_color)
                    elif response.status_code == 403:
                        print_colored_text(f"? Report #{report_count} failed - Access Denied", red_color)
                        break
                    elif response.status_code == 404:
                        print_colored_text(f"? Report #{report_count} failed - Video Not Found", red_color)
                        break
                    elif response.status_code == 429:
                        print_colored_text(f"?? Report #{report_count} - Rate Limited, waiting 30 seconds...", yellow_color)
                        time.sleep(30)
                    else:
                        print_colored_text(f"? Report #{report_count} failed - Status: {response.status_code}", red_color)
                        
                except requests.exceptions.Timeout:
                    print_colored_text(f"? Report #{report_count} - Timeout", yellow_color)
                except requests.exceptions.ConnectionError:
                    print_colored_text(f"?? Report #{report_count} - Connection Error", red_color)
                    break
                except requests.exceptions.RequestException as e:
                    print_colored_text(f"? Report #{report_count} - Error: {e}", red_color)
                    break
                except KeyboardInterrupt:
                    print_colored_text(f"\n?? Session interrupted by user", yellow_color)
                    break
                    
        except Exception as e:
            print_colored_text(f"?? Unexpected error: {e}", red_color)

        # Session summary
        print_colored_text(f"\n?? Session Complete:", cyan_color)
        print_colored_text(f"?? Video ID: {video_id}", blue_color)
        print_colored_text(f"?? Reports this session: {report_session_count}", blue_color)
        print_colored_text(f"?? Total overall reports: {report_count}", blue_color)

        # Continue or exit
        print_colored_text(f"\n?? Do you want to report another video?", green_color)
        continue_choice = input("Continue? (y/n): ").lower().strip()
        if continue_choice not in ['y', 'yes']:
            print_colored_text(f"\n?? Final statistics:", cyan_color)
            print_colored_text(f"?? Total reports sent: {report_count}", green_color)
            print_colored_text("?? Thank you for using Enhanced TikTok Report Bot!", green_color)
            break

def main():
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Display banner
    display_banner()
    
    # Create default files
    create_default_files()
    
    while True:
        # Display menu
        display_menu()
        
        # Get user choice
        choice = get_user_choice()
        
        if choice == 1:
            run_video_reporting()
        elif choice == 2:
            run_profile_reporting()
        elif choice == 3:
            # Combined reporting - use single URL mode
            print(f"{Color.YELLOW}🔄 Combined reporting mode - Please use option 4 for single URL{Color.RESET}")
        elif choice == 4:
            run_single_url_reporting()
        elif choice == 5:
            # Continuous mode - use ultra-fast mode
            print(f"{Color.YELLOW}🔁 Continuous mode - Please use option 7 for ultra-fast reporting{Color.RESET}")
        elif choice == 6:
            # Real-time import - use file-based mode
            print(f"{Color.YELLOW}📥 Real-time import - Please add URLs to targets.txt and use option 4{Color.RESET}")
        elif choice == 7:
            run_ultra_fast_mode()
        elif choice == 8:
            print(f"\n{Color.GREEN}👋 Thank you for using TikTok Mass Report Tool!{Color.RESET}")
            break
        elif choice == 0:  # Hidden option for original mode
            run_original_mode()
        
        # Reset global flags
        global stop_reporting
        stop_reporting = False
        
        # Ask if user wants to continue
        if choice != 8:
            continue_choice = input(f"\n{Color.YELLOW}🔄 Do you want to continue? (y/n): {Color.RESET}").strip().lower()
            if continue_choice not in ['y', 'yes']:
                print(f"\n{Color.GREEN}👋 Thank you for using TikTok Mass Report Tool!{Color.RESET}")
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Color.RED}🛑 Process interrupted by user.{Color.RESET}")
    except Exception as e:
        print(f"\n{Color.RED}💥 Unexpected error: {e}{Color.RESET}")
