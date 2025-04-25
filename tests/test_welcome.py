"""
Test welcome message functionality for CrushBot
"""

import unittest
from unittest.mock import MagicMock
from handlers.welcome import format_welcome_message

class TestWelcomeMessages(unittest.TestCase):
    """Test cases for welcome message functionality."""
    
    def test_format_welcome_message(self):
        """Test welcome message formatting."""
        # Create mock User and Chat objects
        mock_user = MagicMock()
        mock_user.id = 123456789
        mock_user.first_name = "TestUser"
        mock_user.last_name = "LastName"
        mock_user.username = "testuser"
        
        mock_chat = MagicMock()
        mock_chat.id = 987654321
        mock_chat.title = "Test Group"
        
        # Test basic placeholders
        template = "Welcome {user} to {group}!"
        result = format_welcome_message(template, mock_user, mock_chat)
        self.assertEqual(result, "Welcome [TestUser](tg://user?id=123456789) to Test Group!")
        
        # Test all placeholders
        template = "Welcome {user} ({username}, {first} {last}, ID: {userid}) to {group} (ID: {chatid})!"
        result = format_welcome_message(template, mock_user, mock_chat)
        expected = "Welcome [TestUser](tg://user?id=123456789) (@testuser, TestUser LastName, ID: 123456789) to Test Group (ID: 987654321)!"
        self.assertEqual(result, expected)
        
        # Test when some user fields are missing
        mock_user.username = None
        mock_user.last_name = None
        
        template = "Welcome {username} {last} to {group}!"
        result = format_welcome_message(template, mock_user, mock_chat)
        self.assertEqual(result, "Welcome TestUser  to Test Group!")

if __name__ == '__main__':
    unittest.main() 