"""
Text manipulation commands for CrushBot
"""

from pyrogram import Client, filters
from pyrogram.types import Message
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.formatters import (
    mock_text, fancy_text, reverse_text, bubble_text,
    zalgo_text, emojify_text
)

@Client.on_message(filters.command("reverse", prefixes="."))
async def reverse_command(client: Client, message: Message):
    """Reverse text"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.reverse <text>`")
        return
    
    text = message.text.split(None, 1)[1]
    reversed_text = reverse_text(text)
    await message.edit_text(f"🔄 **Reversed:** {reversed_text}")

@Client.on_message(filters.command("upper", prefixes="."))
async def upper_command(client: Client, message: Message):
    """Convert text to uppercase"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.upper <text>`")
        return
    
    text = message.text.split(None, 1)[1]
    await message.edit_text(f"🔤 **UPPERCASE:** {text.upper()}")

@Client.on_message(filters.command("lower", prefixes="."))
async def lower_command(client: Client, message: Message):
    """Convert text to lowercase"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.lower <text>`")
        return
    
    text = message.text.split(None, 1)[1]
    await message.edit_text(f"🔡 **lowercase:** {text.lower()}")

@Client.on_message(filters.command("mock", prefixes="."))
async def mock_command(client: Client, message: Message):
    """Mock text (alternating case)"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.mock <text>`")
        return
    
    text = message.text.split(None, 1)[1]
    mocked_text = mock_text(text)
    await message.edit_text(f"🤡 **mOcKeD:** {mocked_text}")

@Client.on_message(filters.command("fancy", prefixes="."))
async def fancy_command(client: Client, message: Message):
    """Apply fancy formatting to text"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.fancy <text>` or `.fancy <style> <text>`")
        return
    
    parts = message.text.split(None, 2)
    if len(parts) == 2:
        style = "bold"
        text = parts[1]
    elif len(parts) == 3 and parts[1] in ["bold", "italic"]:
        style = parts[1]
        text = parts[2]
    else:
        style = "bold"
        text = message.text.split(None, 1)[1]
    
    fancy = fancy_text(text, style)
    await message.edit_text(f"✨ **Fancy ({style}):** {fancy}")

@Client.on_message(filters.command("bubble", prefixes="."))
async def bubble_command(client: Client, message: Message):
    """Convert text to bubble letters"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.bubble <text>`")
        return
    
    text = message.text.split(None, 1)[1]
    bubbled = bubble_text(text)
    await message.edit_text(f"🫧 **Bubble:** {bubbled}")

@Client.on_message(filters.command("zalgo", prefixes="."))
async def zalgo_command(client: Client, message: Message):
    """Add zalgo effect to text"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.zalgo <text>` or `.zalgo <intensity> <text>`")
        return
    
    parts = message.text.split(None, 2)
    if len(parts) == 2:
        intensity = 3
        text = parts[1]
    elif len(parts) == 3 and parts[1].isdigit():
        intensity = min(int(parts[1]), 10)  # Max intensity 10
        text = parts[2]
    else:
        intensity = 3
        text = message.text.split(None, 1)[1]
    
    zalgo = zalgo_text(text, intensity)
    await message.edit_text(f"👹 **Z̸̰̈a̷̰̽l̶̰̈ǧ̵̰o̷̰̽:** {zalgo}")

@Client.on_message(filters.command("emoji", prefixes="."))
async def emojify_command(client: Client, message: Message):
    """Convert text to emoji letters"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.emoji <text>`")
        return
    
    text = message.text.split(None, 1)[1]
    emojified = emojify_text(text)
    await message.edit_text(f"😀 **Emojified:** {emojified}")

@Client.on_message(filters.command("title", prefixes="."))
async def title_command(client: Client, message: Message):
    """Convert text to title case"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.title <text>`")
        return
    
    text = message.text.split(None, 1)[1]
    await message.edit_text(f"📖 **Title Case:** {text.title()}")

@Client.on_message(filters.command("replace", prefixes="."))
async def replace_command(client: Client, message: Message):
    """Replace text in a string"""
    if len(message.command) < 4:
        await message.edit_text("❌ Usage: `.replace <old> <new> <text>`")
        return
    
    parts = message.text.split(None, 3)
    old_text = parts[1]
    new_text = parts[2]
    text = parts[3]
    
    replaced = text.replace(old_text, new_text)
    await message.edit_text(f"🔄 **Replaced:** {replaced}")
