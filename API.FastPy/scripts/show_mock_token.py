#!/usr/bin/env python3
"""
Mock Token Information Script

This script displays the mock admin token information for easy testing.
The mock token never expires and doesn't require database authentication.

Usage:
    python scripts/show_mock_token.py

Features:
- Shows the mock token value
- Provides usage examples
- No dependencies on database
- Never expires

Author: Development Team
Created: August 2025
"""

def display_mock_token_info():
    """Display mock token information and usage examples"""
    mock_token = "mock_token_admin"
    
    print("🔑 Mock Admin Token Information")
    print("=" * 50)
    
    print(f"👤 Mock User: mock_admin (Admin)")
    print(f"⏰ Expires: Never (year 2286)")
    print(f"🔑 Token Type: Mock Token")
    print(f"💾 Database: Not required")
    print(f"🚀 Environment: Any")
    
    print(f"\n📋 Mock Token:")
    print("-" * 20)
    print(mock_token)
    
    print(f"\n🔧 Usage Examples:")
    print("-" * 20)
    
    # Curl example
    print("Curl:")
    print(f"""curl -H "Authorization: Bearer {mock_token}" \\
     http://localhost:8000/users/""")
    
    # Python requests example
    print(f"\nPython requests:")
    print(f"""headers = {{
    "Authorization": "Bearer {mock_token}"
}}
response = requests.get("http://localhost:8000/users/", headers=headers)""")
    
    # Postman/Insomnia
    print(f"\nPostman/Insomnia:")
    print(f"Authorization Type: Bearer Token")
    print(f"Token: {mock_token}")
    
    print(f"\n📝 Mock User Details:")
    print("-" * 20)
    print(f"• ID: 999999 (special mock ID)")
    print(f"• Username: mock_admin")
    print(f"• Email: mock_admin@dev.local")
    print(f"• Full Name: Mock Admin User")
    print(f"• Role: Admin")
    print(f"• Status: Active")
    
    print(f"\n💡 Benefits:")
    print("-" * 20)
    print(f"• ✅ No database required")
    print(f"• ✅ Never expires")
    print(f"• ✅ Full admin permissions")
    print(f"• ✅ Works in any environment")
    print(f"• ✅ Perfect for testing")
    print(f"• ✅ No login required")
    
    print(f"\n⚠️  Security Notes:")
    print("-" * 20)
    print(f"• This is a development/testing feature")
    print(f"• Mock tokens should not be used in production")
    print(f"• The token value is hardcoded and public")
    print(f"• Use only for API testing and development")

def main():
    """Main function"""
    try:
        display_mock_token_info()
        
    except KeyboardInterrupt:
        print(f"\n\n👋 Cancelled by user")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
