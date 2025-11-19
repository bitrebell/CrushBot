# 🍪 YouTube Cookies Setup Guide

YouTube now requires authentication to download videos (to prevent bots). You need to provide your YouTube cookies to the bot.

## Quick Setup

### Option 1: Browser Extension (Easiest)

1. **Install a cookie exporter extension:**
   - **Chrome/Edge**: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - **Firefox**: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. **Export YouTube cookies:**
   - Go to [youtube.com](https://youtube.com) (make sure you're logged in)
   - Click the extension icon
   - Click "Export" or "Download cookies.txt"
   - Choose "youtube.com" if asked
   - Save the file as `cookies.txt`

3. **Upload to bot directory:**
   - Place `cookies.txt` in `/workspaces/CrushBot/` directory
   - Make sure the file is named exactly `cookies.txt`

4. **Restart the bot** - it will automatically detect and use the cookies

### Option 2: Using yt-dlp Command (Alternative)

If you have yt-dlp installed on your local machine with browser access:

```bash
# Extract cookies from Chrome
yt-dlp --cookies-from-browser chrome --cookies cookies.txt 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'

# Or from Firefox
yt-dlp --cookies-from-browser firefox --cookies cookies.txt 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
```

Then upload the generated `cookies.txt` to your bot directory.

### Option 3: Manual Cookie Export

1. Open YouTube in your browser
2. Open Developer Tools (F12)
3. Go to Application/Storage tab
4. Click on Cookies → https://www.youtube.com
5. Manually export cookies in Netscape format

For detailed instructions: [yt-dlp Cookie FAQ](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)

## Verifying Setup

Run the setup script to check if cookies are configured:

```bash
chmod +x setup_cookies.sh
./setup_cookies.sh
```

## Security Notes

⚠️ **IMPORTANT:**
- `cookies.txt` contains your YouTube login session
- Never share or commit this file to version control
- The `.gitignore` file is already configured to exclude it
- Cookies may expire - you'll need to refresh them periodically

## Troubleshooting

### "No cookies found" warning
- Make sure `cookies.txt` exists in `/workspaces/CrushBot/`
- Check file permissions: `chmod 644 cookies.txt`
- Verify the file format is correct (Netscape cookies format)

### "Sign in to confirm you're not a bot" error
- Your cookies may have expired
- Re-export cookies from your browser
- Make sure you're logged into YouTube when exporting

### Still not working?
- Try logging into YouTube in your browser
- Clear browser cache and cookies, then login again
- Export fresh cookies
- Make sure the cookies file isn't empty

## File Location

The bot looks for cookies in:
```
/workspaces/CrushBot/cookies.txt
```

## Cookie File Format

The file should be in Netscape cookies format and look like:
```
# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	1234567890	CONSENT	YES+...
.youtube.com	TRUE	/	FALSE	1234567890	VISITOR_INFO1_LIVE	...
```

---

**Need more help?** Check the [yt-dlp documentation](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies)
