"""
Fun commands plugin for CrushBot
"""

from pyrogram import Client, filters
from pyrogram.types import Message
import random
import asyncio

@Client.on_message(filters.command("dice", prefixes="."))
async def dice_command(client: Client, message: Message):
    """Roll a dice"""
    dice_value = random.randint(1, 6)
    dice_emoji = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'][dice_value - 1]
    await message.edit_text(f"🎲 **Dice Roll:** {dice_emoji} (`{dice_value}`)")

@Client.on_message(filters.command("coin", prefixes="."))
async def coin_command(client: Client, message: Message):
    """Flip a coin"""
    result = random.choice(["Heads", "Tails"])
    emoji = "🪙" if result == "Heads" else "🪙"
    await message.edit_text(f"{emoji} **Coin Flip:** {result}")

@Client.on_message(filters.command(["8ball", "eightball"], prefixes="."))
async def eight_ball(client: Client, message: Message):
    """Magic 8-ball"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.8ball <question>`")
        return
    
    responses = [
        "�� It is certain",
        "🎱 It is decidedly so",
        "🎱 Without a doubt",
        "🎱 Yes definitely",
        "🎱 You may rely on it",
        "🎱 As I see it, yes",
        "🎱 Most likely",
        "🎱 Outlook good",
        "🎱 Yes",
        "🎱 Signs point to yes",
        "🎱 Reply hazy, try again",
        "🎱 Ask again later",
        "🎱 Better not tell you now",
        "🎱 Cannot predict now",
        "🎱 Concentrate and ask again",
        "🎱 Don't count on it",
        "🎱 My reply is no",
        "🎱 My sources say no",
        "🎱 Outlook not so good",
        "🎱 Very doubtful"
    ]
    
    question = message.text.split(None, 1)[1]
    response = random.choice(responses)
    await message.edit_text(f"**Question:** {question}\n\n**Answer:** {response}")

@Client.on_message(filters.command("random", prefixes="."))
async def random_number(client: Client, message: Message):
    """Generate random number"""
    if len(message.command) == 1:
        # Default range 1-100
        number = random.randint(1, 100)
        await message.edit_text(f"🎲 **Random Number (1-100):** `{number}`")
    elif len(message.command) == 2:
        try:
            max_num = int(message.command[1])
            number = random.randint(1, max_num)
            await message.edit_text(f"🎲 **Random Number (1-{max_num}):** `{number}`")
        except ValueError:
            await message.edit_text("❌ Please provide a valid number")
    elif len(message.command) == 3:
        try:
            min_num = int(message.command[1])
            max_num = int(message.command[2])
            if min_num >= max_num:
                await message.edit_text("❌ Minimum number must be less than maximum")
                return
            number = random.randint(min_num, max_num)
            await message.edit_text(f"🎲 **Random Number ({min_num}-{max_num}):** `{number}`")
        except ValueError:
            await message.edit_text("❌ Please provide valid numbers")

@Client.on_message(filters.command("choose", prefixes="."))
async def choose_command(client: Client, message: Message):
    """Choose randomly from options"""
    if len(message.command) < 3:
        await message.edit_text("❌ Usage: `.choose <option1> <option2> [option3] ...`")
        return
    
    options = message.command[1:]
    choice = random.choice(options)
    await message.edit_text(f"🤔 **I choose:** `{choice}`")

@Client.on_message(filters.command("slots", prefixes="."))
async def slot_machine(client: Client, message: Message):
    """Play slot machine"""
    slots = ['🍎', '🍊', '🍋', '🍇', '🍓', '🥝', '🍑', '🥥']
    
    await message.edit_text("🎰 **Spinning...**")
    await asyncio.sleep(1)
    
    result = [random.choice(slots) for _ in range(3)]
    result_text = " | ".join(result)
    
    if len(set(result)) == 1:  # All same
        await message.edit_text(f"🎰 **JACKPOT!** 🎉\n\n{result_text}\n\n💰 You won!")
    elif len(set(result)) == 2:  # Two same
        await message.edit_text(f"🎰 **Almost!** 😅\n\n{result_text}\n\n🪙 Small win!")
    else:  # All different
        await message.edit_text(f"🎰 **Try again!** 😔\n\n{result_text}\n\n❌ No luck this time!")

@Client.on_message(filters.command("roll", prefixes="."))
async def roll_dice(client: Client, message: Message):
    """Roll multiple dice or custom dice"""
    if len(message.command) == 1:
        # Single d6
        result = random.randint(1, 6)
        await message.edit_text(f"🎲 **Roll:** `{result}`")
    else:
        try:
            dice_notation = message.command[1]
            if 'd' in dice_notation.lower():
                # Format: XdY (e.g., 2d6, 3d20)
                parts = dice_notation.lower().split('d')
                num_dice = int(parts[0]) if parts[0] else 1
                sides = int(parts[1])
                
                if num_dice > 20:
                    await message.edit_text("❌ Maximum 20 dice allowed")
                    return
                if sides > 100:
                    await message.edit_text("❌ Maximum 100 sides allowed")
                    return
                
                results = [random.randint(1, sides) for _ in range(num_dice)]
                total = sum(results)
                
                if num_dice == 1:
                    await message.edit_text(f"🎲 **Roll d{sides}:** `{results[0]}`")
                else:
                    results_str = ", ".join(map(str, results))
                    await message.edit_text(f"🎲 **Roll {num_dice}d{sides}:**\n`{results_str}`\n**Total:** `{total}`")
            else:
                # Simple number (sides of dice)
                sides = int(dice_notation)
                result = random.randint(1, sides)
                await message.edit_text(f"🎲 **Roll d{sides}:** `{result}`")
        except (ValueError, IndexError):
            await message.edit_text("❌ Usage: `.roll` or `.roll <sides>` or `.roll <num>d<sides>`\nExample: `.roll 20` or `.roll 3d6`")

@Client.on_message(filters.command("fortune", prefixes="."))
async def fortune_cookie(client: Client, message: Message):
    """Get a fortune cookie message"""
    fortunes = [
        "🥠 A journey of a thousand miles begins with a single step.",
        "🥠 Your future is bright and full of possibilities.",
        "🥠 Good things come to those who wait.",
        "🥠 The best time to plant a tree was 20 years ago. The second best time is now.",
        "�� You will find luck is just a matter of preparation meeting opportunity.",
        "🥠 A wise person learns from the mistakes of others.",
        "�� The only impossible journey is the one you never begin.",
        "🥠 Success is not final, failure is not fatal: it is the courage to continue that counts.",
        "🥠 Be yourself; everyone else is already taken.",
        "🥠 Life is what happens to you while you're busy making other plans.",
        "🥠 The greatest glory in living lies not in never falling, but in rising every time we fall.",
        "🥠 In the middle of difficulty lies opportunity.",
        "🥠 It is during our darkest moments that we must focus to see the light."
    ]
    
    fortune = random.choice(fortunes)
    await message.edit_text(f"**Fortune Cookie**\n\n{fortune}")
