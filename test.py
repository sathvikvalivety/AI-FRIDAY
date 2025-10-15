# test_email_complete.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("📧 COMPLETE EMAIL SYSTEM TEST")
print("=" * 50)

# Test 1: Check Environment Variables
print("\n1. 🔍 ENVIRONMENT VARIABLES:")
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")

print(f"   SENDER_EMAIL: {sender_email}")
print(f"   SENDER_PASSWORD: {'*' * len(sender_password) if sender_password else 'NOT SET'}")
print(f"   Password length: {len(sender_password) if sender_password else 0}")

if not sender_email or not sender_password:
    print("   ❌ Missing environment variables!")
    exit(1)
else:
    print("   ✅ Environment variables found")

# Test 2: Check EMAIL_CONFIG
print("\n2. 🔍 EMAIL_CONFIG:")
from config import EMAIL_CONFIG

print(f"   sender_email: {EMAIL_CONFIG.get('sender_email')}")
print(f"   sender_password: {'*' * len(EMAIL_CONFIG.get('sender_password', ''))}")
print(f"   imap_server: {EMAIL_CONFIG.get('imap_server')}")

if not EMAIL_CONFIG.get('sender_email') or not EMAIL_CONFIG.get('sender_password'):
    print("   ❌ EMAIL_CONFIG not properly loaded!")
    exit(1)
else:
    print("   ✅ EMAIL_CONFIG loaded correctly")

# Test 3: Test EmailReader
print("\n3. 🔍 EMAIL READER:")
try:
    from utilities.email_reader import EmailReader
    reader = EmailReader()
    print("   ✅ EmailReader imported successfully")
    
    # Test connection
    print("   Testing IMAP connection...")
    mail = reader.connect_to_inbox()
    if mail:
        print("   ✅ IMAP connection successful")
        
        # Test email count
        count = reader.get_email_count()
        print(f"   📬 Unread emails: {count}")
        
        mail.close()
        mail.logout()
    else:
        print("   ❌ IMAP connection failed")
        
except Exception as e:
    print(f"   ❌ EmailReader test failed: {e}")

# Test 4: Test EmailManager
print("\n4. 🔍 EMAIL MANAGER:")
try:
    from utilities.email_manager import EmailManager
    manager = EmailManager()
    print("   ✅ EmailManager imported successfully")
    
    # Test unread count
    unread_count = manager.get_unread_count()
    print(f"   📬 Unread count via manager: {unread_count}")
    
except Exception as e:
    print(f"   ❌ EmailManager test failed: {e}")

print("\n" + "=" * 50)
print("🎯 TEST COMPLETE")

if sender_email and sender_password:
    print("💡 Next: Run 'python main.py' and try 'check my emails'")
else:
    print("❌ Fix environment variables first!")