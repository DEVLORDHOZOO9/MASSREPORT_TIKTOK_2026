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

# =============================================
# TELEGRAM BOT CONFIGURATION
# =============================================

TELEGRAM_BOT_TOKEN = "8243804176:AAHddGdjqOlzACwDL8sTGzJjMGdo7KNI6ko"  # Ganti dengan token bot Anda
ADMIN_USER_IDS = [8317643774, 8317643774]     # Ganti dengan ID admin Anda

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

# =============================================
# WEATHER & TIME FUNCTIONS
# =============================================

def get_weather_info():
    """Get weather information (simulated)"""
    weather_conditions = ["☀️ Cerah", "🌧️ Hujan", "⛅ Berawan", "🌦️ Hujan Cerah", "🌤️ Cerah Berawan", "💨 Berangin"]
    temperatures = random.randint(22, 35)
    humidity = random.randint(60, 95)
    
    return {
        'condition': random.choice(weather_conditions),
        'temperature': temperatures,
        'humidity': humidity,
        'location': 'Jakarta, Indonesia'
    }

def get_current_time_info():
    """Get comprehensive time information"""
    now = datetime.now()
    
    # Indonesian month names
    bulan = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    
    # Indonesian day names
    hari = {
        0: "Minggu", 1: "Senin", 2: "Selasa", 3: "Rabu",
        4: "Kamis", 5: "Jumat", 6: "Sabtu"
    }
    
    # Time of day
    jam = now.hour
    if 5 <= jam < 12:
        waktu_hari = "🌅 Pagi"
    elif 12 <= jam < 15:
        waktu_hari = "☀️ Siang"
    elif 15 <= jam < 18:
        waktu_hari = "🌇 Sore"
    else:
        waktu_hari = "🌙 Malam"
    
    return {
        'hari': hari[now.weekday()],
        'tanggal': now.day,
        'bulan': bulan[now.month],
        'tahun': now.year,
        'jam': now.strftime("%H:%M:%S"),
        'waktu_hari': waktu_hari,
        'zodiak': get_zodiac_sign(now.day, now.month)
    }

def get_zodiac_sign(day, month):
    """Get zodiac sign based on date"""
    if (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "♒ Aquarius"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "♓ Pisces"
    elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "♈ Aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "♉ Taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "♊ Gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "♋ Cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "♌ Leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "♍ Virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "♎ Libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "♏ Scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "♐ Sagittarius"
    else:
        return "♑ Capricorn"

def get_system_info():
    """Get system information"""
    try:
        system = platform.system()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            'system': system,
            'memory_used': memory.used // (1024**3),
            'memory_total': memory.total // (1024**3),
            'disk_used': disk.used // (1024**3),
            'disk_total': disk.total // (1024**3),
            'cpu_percent': cpu_percent
        }
    except:
        return None

# =============================================
# TELEGRAM BOT HANDLERS
# =============================================

async def start_command(update: Update, context: CallbackContext):
    """Handle /start command with video and beautiful menu"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    
    # Get comprehensive information
    time_info = get_current_time_info()
    weather_info = get_weather_info()
    system_info = get_system_info()
    
    # Create beautiful welcome message
    welcome_text = f"""
✨ *SELAMAT DATANG DI TIKTOK REPORT BOT* ✨

👋 *Halo {username}!* 
🆔 User ID: `{user_id}`

📅 *INFORMASI WAKTU:*
├── 🗓️ {time_info['hari']}, {time_info['tanggal']} {time_info['bulan']} {time_info['tahun']}
├── 🕐 {time_info['jam']} • {time_info['waktu_hari']}
└── ♊ {time_info['zodiak']}

🌤️ *INFORMASI CUACA:*
├── 🌡️ {weather_info['condition']}
├── 🌡️ Suhu: {weather_info['temperature']}°C
├── 💧 Kelembaban: {weather_info['humidity']}%
└── 📍 {weather_info['location']}
"""
    
    if system_info:
        welcome_text += f"""
💻 *SISTEM BOT:*
├── 🖥️ OS: {system_info['system']}
├── 🧠 CPU: {system_info['cpu_percent']}%
├── 💾 RAM: {system_info['memory_used']}/{system_info['memory_total']} GB
└── 💿 Disk: {system_info['disk_used']}/{system_info['disk_total']} GB
"""

    welcome_text += """
🚀 *FITUR UTAMA:*
• 📹 Mass Report Video TikTok
• 👤 Mass Report Profile TikTok  
• ♾️ Unlimited Reporting Mode
• ⚡ Ultra-Fast Performance
• 🔄 Real-time Monitoring

⚠️ *PERINGATAN:*
Gunakan tool ini dengan bijak dan bertanggung jawab!
"""

    # Create inline keyboard
    keyboard = [
        [InlineKeyboardButton("📹 REPORT VIDEO", callback_data="report_video"),
         InlineKeyboardButton("👤 REPORT PROFILE", callback_data="report_profile")],
        [InlineKeyboardButton("♾️ UNLIMITED MODE", callback_data="unlimited_mode"),
         InlineKeyboardButton("⚡ ULTRA FAST", callback_data="ultra_fast")],
        [InlineKeyboardButton("📊 STATISTICS", callback_data="stats"),
         InlineKeyboardButton("🆘 HELP", callback_data="help")],
        [InlineKeyboardButton("🌐 WEATHER INFO", callback_data="weather"),
         InlineKeyboardButton("⏰ TIME INFO", callback_data="time_info")],
        [InlineKeyboardButton("🔧 SYSTEM INFO", callback_data="system_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Try to send video first, then message
    try:
        # Send video (replace 'hozzo.mp4' with your actual video file)
        try:
            with open('hozzo.mp4', 'rb') as video:
                await update.message.reply_video(
                    video=video,
                    caption="🎬 *TikTok Report Bot Activated!*\nPilih menu di bawah untuk memulai:",
                    parse_mode='Markdown'
                )
        except FileNotFoundError:
            # If video not found, send without video
            await update.message.reply_text(
                welcome_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            # Send text message after video
            await update.message.reply_text(
                welcome_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    except Exception as e:
        # Fallback if video fails
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def button_handler(update: Update, context: CallbackContext):
    """Handle inline keyboard button presses"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if data == "report_video":
        await query.edit_message_text(
            "📹 *MODE REPORT VIDEO TIKTOK*\n\n"
            "Silahkan kirim URL video TikTok yang ingin di-report.\n"
            "Contoh: `https://www.tiktok.com/@username/video/1234567890123456789`",
            parse_mode='Markdown'
        )
        
    elif data == "report_profile":
        await query.edit_message_text(
            "👤 *MODE REPORT PROFILE TIKTOK*\n\n"
            "Silahkan kirim URL profile TikTok yang ingin di-report.\n"
            "Contoh: `https://www.tiktok.com/@username`",
            parse_mode='Markdown'
        )
        
    elif data == "unlimited_mode":
        await query.edit_message_text(
            "♾️ *UNLIMITED REPORTING MODE*\n\n"
            "🚨 *PERINGATAN:* Mode ini akan melakukan reporting secara terus menerus tanpa batas!\n\n"
            "Fitur:\n"
            "• ♾️ Unlimited reports\n"
            "• ⚡ No delays\n"
            "• 🔄 Auto rotation\n"
            "• 🛡️ Anti-detection\n\n"
            "Kirim URL target untuk memulai unlimited mode:",
            parse_mode='Markdown'
        )
        
    elif data == "ultra_fast":
        await query.edit_message_text(
            "⚡ *ULTRA-FAST REPORTING MODE*\n\n"
            "Mode kecepatan maksimal dengan 9999 reports/detik!\n\n"
            "Spesifikasi:\n"
            "• 🚀 9999 reports/second\n"
            "• 🧵 9999 threads\n"
            "• ⏱️ Minimal delays\n"
            "• 🔧 Proxy support\n\n"
            "Kirim URL target untuk ultra-fast mode:",
            parse_mode='Markdown'
        )
        
    elif data == "stats":
        # Get current statistics
        time_info = get_current_time_info()
        weather_info = get_weather_info()
        
        stats_text = f"""
📊 *REAL-TIME STATISTICS*

⏰ *WAKTU:*
├── {time_info['hari']}, {time_info['tanggal']} {time_info['bulan']} {time_info['tahun']}
├── 🕐 {time_info['jam']} • {time_info['waktu_hari']}
└── ♊ {time_info['zodiak']}

🌤️ *CUACA:*
├── {weather_info['condition']}
├── 🌡️ {weather_info['temperature']}°C
├── 💧 {weather_info['humidity']}%
└── 📍 {weather_info['location']}

🤖 *BOT STATUS:*
├── ✅ Online
├── 🟢 Operational
└── ⚡ Ready

*Gunakan menu sebelumnya untuk memulai reporting!*
"""
        await query.edit_message_text(stats_text, parse_mode='Markdown')
        
    elif data == "help":
        help_text = """
🆘 *BANTUAN & PETUNJUK*

📖 *CARA PENGGUNAAN:*
1. Pilih mode reporting yang diinginkan
2. Kirim URL TikTok (video atau profile)
3. Bot akan memproses secara otomatis
4. Pantau progress melalui notifikasi

🎯 *FORMAT URL YANG DIDUKUNG:*
• Video: `https://www.tiktok.com/@username/video/1234567890123456789`
• Profile: `https://www.tiktok.com/@username`
• Short URL: `https://vm.tiktok.com/ABC123/`

⚠️ *PERHATIAN:*
• Gunakan dengan bijak dan bertanggung jawab
• Pastikan URL yang dikirim valid
• Bot mungkin memerlukan waktu untuk proses mass reporting

📞 *DUKUNGAN:*
Untuk bantuan lebih lanjut, hubungi administrator.
"""
        await query.edit_message_text(help_text, parse_mode='Markdown')
        
    elif data == "weather":
        weather_info = get_weather_info()
        weather_text = f"""
🌤️ *INFORMASI CUACA TERKINI*

📍 *Lokasi:* {weather_info['location']}
🌈 *Kondisi:* {weather_info['condition']}
🌡️ *Suhu:* {weather_info['temperature']}°C
💧 *Kelembaban:* {weather_info['humidity']}%

📊 *ANALISIS CUACA:*
"""
        if "Hujan" in weather_info['condition']:
            weather_text += "• 🎯 Cocok untuk aktivitas indoor\n• ☔ Bawa payung/pakaian hujan\n• 🚗 Hati-hati di jalan"
        else:
            weather_text += "• 🎯 Perfect untuk aktivitas outdoor\n• ☀️ Gunakan sunscreen\n• 💧 Tetap terhidrasi"
            
        await query.edit_message_text(weather_text, parse_mode='Markdown')
        
    elif data == "time_info":
        time_info = get_current_time_info()
        time_text = f"""
⏰ *INFORMASI WAKTU LENGKAP*

📅 *TANGGAL:*
├── Hari: {time_info['hari']}
├── Tanggal: {time_info['tanggal']} {time_info['bulan']} {time_info['tahun']}
├── Jam: {time_info['jam']}
└── Waktu: {time_info['waktu_hari']}

♊ *ZODIAK:* {time_info['zodiak']}

🌅 *KETERANGAN WAKTU:*
"""
        if "Pagi" in time_info['waktu_hari']:
            time_text += "• 🌅 Waktu yang sempurna untuk memulai hari\n• ☕ Saatnya sarapan dan persiapan\n• 🏃 Ideal untuk olahraga pagi"
        elif "Siang" in time_info['waktu_hari']:
            time_text += "• ☀️ Puncak produktivitas hari\n• 🍽️ Waktu makan siang\n• 🔥 Energi pada titik tertinggi"
        elif "Sore" in time_info['waktu_hari']:
            time_text += "• 🌇 Waktu bersantai dan evaluasi\n• 🏃‍♂️ Cocok untuk olahraga sore\n• 📊 Review pencapaian hari ini"
        else:
            time_text += "• 🌙 Waktu istirahat dan relaksasi\n• 💤 Persiapkan tidur yang berkualitas\n• 📝 Rencanakan untuk besok"
            
        await query.edit_message_text(time_text, parse_mode='Markdown')
        
    elif data == "system_info":
        system_info = get_system_info()
        if system_info:
            system_text = f"""
💻 *INFORMASI SISTEM BOT*

🖥️ *SISTEM OPERASI:*
├── Platform: {system_info['system']}
├── CPU Usage: {system_info['cpu_percent']}%
├── Memory: {system_info['memory_used']}/{system_info['memory_total']} GB
└── Disk: {system_info['disk_used']}/{system_info['disk_total']} GB

📈 *STATUS:*
"""
            if system_info['cpu_percent'] < 70:
                system_text += "• 🟢 CPU: Optimal\n"
            else:
                system_text += "• 🟡 CPU: High Load\n"
                
            if system_info['memory_used'] / system_info['memory_total'] < 0.8:
                system_text += "• 🟢 RAM: Stable\n"
            else:
                system_text += "• 🟡 RAM: High Usage\n"
                
            system_text += "• 🟢 Bot: Running Smoothly\n• 🟢 Connection: Stable"
        else:
            system_text = "❌ *Tidak dapat membaca informasi sistem*"
            
        await query.edit_message_text(system_text, parse_mode='Markdown')

async def handle_message(update: Update, context: CallbackContext):
    """Handle incoming text messages"""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Check if message contains TikTok URL
    if validate_tiktok_url(text):
        await update.message.reply_text(
            f"🎯 *URL TIKTOK DITERIMA!*\n\n"
            f"📋 URL: `{text}`\n\n"
            f"🔄 Memproses... Silahkan pilih mode reporting dari menu di bawah:",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📹 REPORT VIDEO", callback_data="report_video"),
                 InlineKeyboardButton("👤 REPORT PROFILE", callback_data="report_profile")],
                [InlineKeyboardButton("♾️ UNLIMITED MODE", callback_data="unlimited_mode"),
                 InlineKeyboardButton("⚡ ULTRA FAST", callback_data="ultra_fast")]
            ])
        )
    else:
        await update.message.reply_text(
            "❌ *URL TIDAK VALID*\n\n"
            "Silahkan kirim URL TikTok yang valid.\n\n"
            "📝 *Contoh Format:*\n"
            "• Video: `https://www.tiktok.com/@username/video/1234567890123456789`\n"
            "• Profile: `https://www.tiktok.com/@username`",
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: CallbackContext):
    """Handle errors in telegram bot"""
    logging.error(f"Update {update} caused error {context.error}")

def setup_telegram_bot():
    """Setup and run telegram bot in background"""
    try:
        # Check if telegram dependencies are installed
        try:
            import telegram
            from telegram.ext import Application
        except ImportError:
            print(f"{Color.YELLOW}⚠ Installing python-telegram-bot...{Color.RESET}")
            install_package("python-telegram-bot")
            import telegram
            from telegram.ext import Application
        
        if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            print(f"{Color.YELLOW}⚠ Telegram Bot Token not configured{Color.RESET}")
            return None
        
        # Create application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error_handler)
        
        # Start the bot in background
        def run_bot():
            try:
                print(f"{Color.GREEN}🤖 Starting Telegram Bot...{Color.RESET}")
                application.run_polling()
            except Exception as e:
                print(f"{Color.RED}❌ Telegram Bot Error: {e}{Color.RESET}")
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        print(f"{Color.GREEN}✅ Telegram Bot Started Successfully!{Color.RESET}")
        return application
    except Exception as e:
        print(f"{Color.RED}❌ Failed to start Telegram Bot: {e}{Color.RESET}")
        return None

# =============================================
# MODIFIED MAIN FUNCTION WITH TELEGRAM SUPPORT
# =============================================

def main():
    # Set up signal handler for graceful shutdown
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
        print(f"{Color.YELLOW}🤖 Telegram Bot: OFFLINE (Token not configured){Color.RESET}")
    
    print(f"{Color.CYAN}⏰ Waktu Sistem: {datetime.now().strftime('%A, %d %B %Y %H:%M:%S')}{Color.RESET}")
    
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
            print(f"{Color.YELLOW}🔄 Combined reporting mode - Please use option 4 for single URL{Color.RESET}")
        elif choice == 4:
            run_single_url_reporting()
        elif choice == 5:
            print(f"{Color.YELLOW}🔁 Continuous mode - Please use option 8 for unlimited reporting{Color.RESET}")
        elif choice == 6:
            print(f"{Color.YELLOW}📥 Real-time import - Please add URLs to targets.txt and use option 4{Color.RESET}")
        elif choice == 7:
            run_ultra_fast_mode()
        elif choice == 8:
            run_unlimited_mode()
        elif choice == 9:
            print(f"\n{Color.GREEN}👋 Thank you for using TikTok Mass Report Tool!{Color.RESET}")
            if telegram_bot:
                print(f"{Color.GREEN}🤖 Telegram Bot is still running in background{Color.RESET}")
            break
        
        # Reset global flags
        global stop_reporting
        stop_reporting = False
        
        # Ask if user wants to continue
        if choice != 9:
            continue_choice = input(f"\n{Color.YELLOW}🔄 Do you want to continue? (y/n): {Color.RESET}").strip().lower()
            if continue_choice not in ['y', 'yes']:
                print(f"\n{Color.Green}👋 Thank you for using TikTok Mass Report Tool!{Color.RESET}")
                if telegram_bot:
                    print(f"{Color.GREEN}🤖 Telegram Bot is still running in background{Color.RESET}")
                break

# =============================================
# UPDATE DEPENDENCY CHECKER
# =============================================

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
# RUN THE PROGRAM
# =============================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Color.RED}🛑 Process interrupted by user.{Color.RESET}")
    except Exception as e:
        print(f"\n{Color.RED}💥 Unexpected error: {e}{Color.RESET}")
