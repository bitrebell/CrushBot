#!/bin/bash

# YouTube Cookie Setup Script for CrushBot
# This script helps you set up YouTube cookies for the bot

echo "🍪 YouTube Cookie Setup for CrushBot"
echo "===================================="
echo ""
echo "To download YouTube videos, you need to provide YouTube cookies."
echo ""
echo "📋 Steps to get cookies:"
echo ""
echo "Method 1: Using Browser Extension (Recommended)"
echo "------------------------------------------------"
echo "1. Install a cookie extension in your browser:"
echo "   - Chrome/Edge: 'Get cookies.txt LOCALLY' extension"
echo "   - Firefox: 'cookies.txt' extension"
echo ""
echo "2. Go to youtube.com and make sure you're logged in"
echo ""
echo "3. Click the extension icon and export cookies for youtube.com"
echo ""
echo "4. Save the exported file as 'cookies.txt'"
echo ""
echo "5. Upload cookies.txt to this directory: /workspaces/CrushBot/"
echo ""
echo "Method 2: Using yt-dlp (Alternative)"
echo "-------------------------------------"
echo "If you have yt-dlp installed locally on your machine:"
echo ""
echo "  yt-dlp --cookies-from-browser chrome --cookies cookies.txt 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'"
echo ""
echo "This will extract cookies from Chrome and save to cookies.txt"
echo ""
echo "Method 3: Manual Cookie Export"
echo "-------------------------------"
echo "You can also manually create cookies.txt in Netscape format."
echo "See: https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp"
echo ""
echo "⚠️  IMPORTANT: Keep cookies.txt private! It contains your login session."
echo ""
echo "After placing cookies.txt in /workspaces/CrushBot/, restart the bot."
echo ""

# Check if cookies.txt exists
if [ -f "cookies.txt" ]; then
    echo "✅ cookies.txt found!"
    echo ""
    echo "Cookie file details:"
    ls -lh cookies.txt
    echo ""
    echo "You're all set! Run the bot with: python bot.py"
else
    echo "❌ cookies.txt not found in current directory."
    echo ""
    echo "Current directory: $(pwd)"
    echo ""
    echo "Please follow the steps above to create cookies.txt"
fi
