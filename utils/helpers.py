"""
Helper functions for CrushBot
"""

import time
import psutil
import asyncio
from datetime import datetime, timedelta

# Bot start time
start_time = time.time()

def get_readable_time(seconds: int) -> str:
    """Convert seconds to readable time format"""
    result = ""
    (days, remainder) = divmod(seconds, 86400)
    (hours, remainder) = divmod(remainder, 3600)
    (minutes, seconds) = divmod(remainder, 60)
    
    if days:
        result += f"{int(days)}d "
    if hours:
        result += f"{int(hours)}h "
    if minutes:
        result += f"{int(minutes)}m "
    if seconds:
        result += f"{int(seconds)}s"
    
    return result.strip()

def get_bot_uptime() -> str:
    """Get bot uptime"""
    uptime_seconds = time.time() - start_time
    return get_readable_time(uptime_seconds)

def get_system_info() -> str:
    """Get system information"""
    try:
        # CPU information
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory information
        memory = psutil.virtual_memory()
        memory_total = memory.total / (1024**3)  # GB
        memory_used = memory.used / (1024**3)    # GB
        memory_percent = memory.percent
        
        # Disk information
        disk = psutil.disk_usage('/')
        disk_total = disk.total / (1024**3)      # GB
        disk_used = disk.used / (1024**3)        # GB
        disk_percent = (disk_used / disk_total) * 100
        
        # System uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        system_uptime = datetime.now() - boot_time
        
        info = f"""
🖥️ **System Information**

**CPU:**
• Usage: `{cpu_usage}%`
• Cores: `{cpu_count}`

**Memory:**
• Used: `{memory_used:.1f}GB` / `{memory_total:.1f}GB` (`{memory_percent}%`)

**Disk:**
• Used: `{disk_used:.1f}GB` / `{disk_total:.1f}GB` (`{disk_percent:.1f}%`)

**Uptime:**
• System: `{get_readable_time(system_uptime.total_seconds())}`
• Bot: `{get_bot_uptime()}`
        """
        return info.strip()
    except Exception as e:
        return f"❌ Error getting system info: {str(e)}"

async def progress_bar(current: int, total: int, text: str = "Progress") -> str:
    """Create a progress bar"""
    percentage = (current / total) * 100
    bar_length = 20
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    return f"{text}: {bar} {percentage:.1f}%"

def get_size(bytes_size: int) -> str:
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"

def escape_markdown(text: str) -> str:
    """Escape markdown characters"""
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

async def typing_effect(message, text: str, delay: float = 0.1):
    """Create a typing effect for messages"""
    current_text = ""
    for char in text:
        current_text += char
        try:
            await message.edit_text(current_text)
            await asyncio.sleep(delay)
        except:
            break
