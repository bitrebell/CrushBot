"""
Media commands plugin for CrushBot
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from PIL import Image, ImageFilter, ImageDraw
import io
import os
import aiohttp

@Client.on_message(filters.command("sticker", prefixes="."))
async def photo_to_sticker(client: Client, message: Message):
    """Convert photo to sticker"""
    reply = message.reply_to_message
    
    if not reply or not reply.photo:
        await message.edit_text("❌ Reply to a photo to convert it to sticker")
        return
    
    try:
        await message.edit_text("🖼️ Converting to sticker...")
        
        # Download photo
        photo_path = await reply.download()
        
        # Process image
        with Image.open(photo_path) as img:
            # Resize to sticker size (512x512 max)
            img.thumbnail((512, 512), Image.Resampling.LANCZOS)
            
            # Convert to RGBA
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Save as WebP
            output = io.BytesIO()
            img.save(output, 'WEBP', quality=95)
            output.seek(0)
        
        # Send sticker
        await message.delete()
        await client.send_sticker(
            chat_id=message.chat.id,
            sticker=output
        )
        
        # Clean up
        os.remove(photo_path)
        
    except Exception as e:
        await message.edit_text(f"❌ Error converting to sticker: {str(e)}")

@Client.on_message(filters.command("circle", prefixes="."))
async def make_circle(client: Client, message: Message):
    """Make profile photo circular"""
    reply = message.reply_to_message
    
    if not reply or not reply.photo:
        await message.edit_text("❌ Reply to a photo to make it circular")
        return
    
    try:
        await message.edit_text("⭕ Making circular...")
        
        # Download photo
        photo_path = await reply.download()
        
        # Process image
        with Image.open(photo_path) as img:
            # Convert to RGB
            img = img.convert('RGB')
            
            # Resize to square
            size = min(img.size)
            img = img.crop(((img.width - size) // 2,
                           (img.height - size) // 2,
                           (img.width + size) // 2,
                           (img.height + size) // 2))
            
            # Create circular mask
            mask = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + img.size, fill=255)
            
            # Apply mask
            output_img = Image.new('RGBA', img.size, (255, 255, 255, 0))
            output_img.paste(img, (0, 0))
            output_img.putalpha(mask)
            
            # Save to bytes
            output = io.BytesIO()
            output_img.save(output, 'PNG')
            output.seek(0)
        
        # Send photo
        await message.delete()
        await client.send_photo(
            chat_id=message.chat.id,
            photo=output,
            caption="⭕ **Circular Photo**"
        )
        
        # Clean up
        os.remove(photo_path)
        
    except Exception as e:
        await message.edit_text(f"❌ Error making circular: {str(e)}")

@Client.on_message(filters.command("blur", prefixes="."))
async def blur_image(client: Client, message: Message):
    """Blur an image"""
    reply = message.reply_to_message
    
    if not reply or not reply.photo:
        await message.edit_text("❌ Reply to a photo to blur it")
        return
    
    # Get blur amount
    blur_amount = 5  # Default
    if len(message.command) > 1:
        try:
            blur_amount = int(message.command[1])
            if blur_amount < 1 or blur_amount > 50:
                await message.edit_text("❌ Blur amount must be between 1-50")
                return
        except ValueError:
            await message.edit_text("❌ Invalid blur amount")
            return
    
    try:
        await message.edit_text(f"🌫️ Applying blur (amount: {blur_amount})...")
        
        # Download photo
        photo_path = await reply.download()
        
        # Process image
        with Image.open(photo_path) as img:
            # Apply gaussian blur
            blurred = img.filter(ImageFilter.GaussianBlur(radius=blur_amount))
            
            # Save to bytes
            output = io.BytesIO()
            blurred.save(output, 'JPEG', quality=95)
            output.seek(0)
        
        # Send photo
        await message.delete()
        await client.send_photo(
            chat_id=message.chat.id,
            photo=output,
            caption=f"🌫️ **Blurred (amount: {blur_amount})**"
        )
        
        # Clean up
        os.remove(photo_path)
        
    except Exception as e:
        await message.edit_text(f"❌ Error blurring image: {str(e)}")

@Client.on_message(filters.command("grayscale", prefixes="."))
async def grayscale_image(client: Client, message: Message):
    """Convert image to grayscale"""
    reply = message.reply_to_message
    
    if not reply or not reply.photo:
        await message.edit_text("❌ Reply to a photo to convert to grayscale")
        return
    
    try:
        await message.edit_text("⚫ Converting to grayscale...")
        
        # Download photo
        photo_path = await reply.download()
        
        # Process image
        with Image.open(photo_path) as img:
            # Convert to grayscale
            grayscale = img.convert('L')
            
            # Save to bytes
            output = io.BytesIO()
            grayscale.save(output, 'JPEG', quality=95)
            output.seek(0)
        
        # Send photo
        await message.delete()
        await client.send_photo(
            chat_id=message.chat.id,
            photo=output,
            caption="⚫ **Grayscale Image**"
        )
        
        # Clean up
        os.remove(photo_path)
        
    except Exception as e:
        await message.edit_text(f"❌ Error converting to grayscale: {str(e)}")

@Client.on_message(filters.command("flip", prefixes="."))
async def flip_image(client: Client, message: Message):
    """Flip image horizontally or vertically"""
    reply = message.reply_to_message
    
    if not reply or not reply.photo:
        await message.edit_text("❌ Reply to a photo to flip it")
        return
    
    # Get flip direction
    direction = "horizontal"  # Default
    if len(message.command) > 1:
        direction = message.command[1].lower()
        if direction not in ["horizontal", "vertical", "h", "v"]:
            await message.edit_text("❌ Use 'horizontal' or 'vertical' (or 'h'/'v')")
            return
    
    try:
        await message.edit_text(f"🔄 Flipping {direction}...")
        
        # Download photo
        photo_path = await reply.download()
        
        # Process image
        with Image.open(photo_path) as img:
            # Flip image
            if direction in ["horizontal", "h"]:
                flipped = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                flip_text = "horizontally"
            else:  # vertical
                flipped = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                flip_text = "vertically"
            
            # Save to bytes
            output = io.BytesIO()
            flipped.save(output, 'JPEG', quality=95)
            output.seek(0)
        
        # Send photo
        await message.delete()
        await client.send_photo(
            chat_id=message.chat.id,
            photo=output,
            caption=f"🔄 **Flipped {flip_text}**"
        )
        
        # Clean up
        os.remove(photo_path)
        
    except Exception as e:
        await message.edit_text(f"❌ Error flipping image: {str(e)}")

@Client.on_message(filters.command("rotate", prefixes="."))
async def rotate_image(client: Client, message: Message):
    """Rotate image by specified degrees"""
    reply = message.reply_to_message
    
    if not reply or not reply.photo:
        await message.edit_text("❌ Reply to a photo to rotate it")
        return
    
    # Get rotation angle
    angle = 90  # Default
    if len(message.command) > 1:
        try:
            angle = int(message.command[1])
            if angle < -360 or angle > 360:
                await message.edit_text("❌ Angle must be between -360 and 360")
                return
        except ValueError:
            await message.edit_text("❌ Invalid angle")
            return
    
    try:
        await message.edit_text(f"🔄 Rotating {angle}°...")
        
        # Download photo
        photo_path = await reply.download()
        
        # Process image
        with Image.open(photo_path) as img:
            # Rotate image
            rotated = img.rotate(angle, expand=True, fillcolor='white')
            
            # Save to bytes
            output = io.BytesIO()
            rotated.save(output, 'JPEG', quality=95)
            output.seek(0)
        
        # Send photo
        await message.delete()
        await client.send_photo(
            chat_id=message.chat.id,
            photo=output,
            caption=f"🔄 **Rotated {angle}°**"
        )
        
        # Clean up
        os.remove(photo_path)
        
    except Exception as e:
        await message.edit_text(f"❌ Error rotating image: {str(e)}")
