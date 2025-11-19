import os
import re
import yt_dlp
from pathlib import Path


# Create downloads directory if it doesn't exist
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


def sanitize_filename(filename):
    """
    Sanitize filename by removing or replacing problematic characters
    """
    # Remove or replace special characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    # Limit length to avoid filesystem issues
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def get_ydl_opts_base():
    """
    Get base yt-dlp options with cookie support
    First tries cookies.txt file, then browser cookies
    """
    # Check for cookies.txt file first
    cookies_file = Path('cookies.txt')
    if cookies_file.exists():
        return {'cookiefile': str(cookies_file)}
    
    # Try browser cookies as fallback
    browsers = ['chrome', 'firefox', 'edge', 'safari']
    
    for browser in browsers:
        try:
            # Test if browser cookies are accessible
            test_opts = {
                'quiet': True,
                'no_warnings': True,
                'cookiesfrombrowser': (browser,),
            }
            with yt_dlp.YoutubeDL(test_opts) as ydl:
                # If no error, use this browser
                return {'cookiesfrombrowser': (browser,)}
        except Exception:
            continue
    
    # If no browser cookies work, return empty dict (will try without cookies)
    print("⚠️ Warning: No cookies found. Some videos may not download.")
    return {}


async def download_audio(url, status_msg=None):
    """
    Download YouTube video as audio (MP3)
    
    Args:
        url: YouTube video URL
        status_msg: Telegram message object for status updates
        
    Returns:
        tuple: (file_path, video_title)
    """
    # Get base options with cookie support
    cookie_opts = get_ydl_opts_base()
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        **cookie_opts,  # Add cookie options if available
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info
            if status_msg:
                await status_msg.edit_text("📝 **Getting video info...**")
            
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'audio')
            sanitized_title = sanitize_filename(video_title)
            
            # Download
            if status_msg:
                await status_msg.edit_text(f"⬇️ **Downloading audio...**\n\n`{video_title}`")
            
            ydl.download([url])
            
            # Find the downloaded file (it might have the original title)
            # Look for both sanitized and original filenames
            possible_files = [
                DOWNLOAD_DIR / f"{video_title}.mp3",
                DOWNLOAD_DIR / f"{sanitized_title}.mp3",
            ]
            
            file_path = None
            for possible_file in possible_files:
                if possible_file.exists():
                    file_path = possible_file
                    break
            
            # If not found, search for any mp3 file that was just created
            if not file_path:
                mp3_files = sorted(DOWNLOAD_DIR.glob("*.mp3"), key=lambda x: x.stat().st_mtime, reverse=True)
                if mp3_files:
                    file_path = mp3_files[0]
            
            if not file_path or not file_path.exists():
                raise FileNotFoundError(f"Downloaded file not found for: {video_title}")
            
            # Rename to sanitized filename if needed
            final_path = DOWNLOAD_DIR / f"{sanitized_title}.mp3"
            if file_path != final_path:
                file_path.rename(final_path)
                file_path = final_path
            
            return str(file_path), video_title
            
    except Exception as e:
        raise Exception(f"Failed to download audio: {str(e)}")


async def download_video(url, status_msg=None):
    """
    Download YouTube video as MP4
    
    Args:
        url: YouTube video URL
        status_msg: Telegram message object for status updates
        
    Returns:
        tuple: (file_path, video_title)
    """
    # Get base options with cookie support
    cookie_opts = get_ydl_opts_base()
    
    ydl_opts = {
        'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        **cookie_opts,  # Add cookie options if available
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info
            if status_msg:
                await status_msg.edit_text("📝 **Getting video info...**")
            
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'video')
            sanitized_title = sanitize_filename(video_title)
            
            # Download
            if status_msg:
                await status_msg.edit_text(f"⬇️ **Downloading video...**\n\n`{video_title}`")
            
            ydl.download([url])
            
            # Find the downloaded file (it might have the original title)
            # Look for both sanitized and original filenames
            possible_files = [
                DOWNLOAD_DIR / f"{video_title}.mp4",
                DOWNLOAD_DIR / f"{sanitized_title}.mp4",
            ]
            
            file_path = None
            for possible_file in possible_files:
                if possible_file.exists():
                    file_path = possible_file
                    break
            
            # If not found, search for any mp4 file that was just created
            if not file_path:
                mp4_files = sorted(DOWNLOAD_DIR.glob("*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)
                if mp4_files:
                    file_path = mp4_files[0]
            
            if not file_path or not file_path.exists():
                raise FileNotFoundError(f"Downloaded file not found for: {video_title}")
            
            # Rename to sanitized filename if needed
            final_path = DOWNLOAD_DIR / f"{sanitized_title}.mp4"
            if file_path != final_path:
                file_path.rename(final_path)
                file_path = final_path
            
            return str(file_path), video_title
            
    except Exception as e:
        raise Exception(f"Failed to download video: {str(e)}")


def get_video_info(url):
    """
    Get information about a YouTube video without downloading
    
    Args:
        url: YouTube video URL
        
    Returns:
        dict: Video information
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader'),
                'thumbnail': info.get('thumbnail'),
            }
    except Exception as e:
        raise Exception(f"Failed to get video info: {str(e)}")
