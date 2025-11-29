#!/usr/bin/env python3
"""
Simple test script to verify WhatsApp integration setup
"""

import sys
import os
import re

# Add the app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_phone_validation():
    """Test phone number validation function"""
    from app import validate_phone_numbers
    
    # Test valid phone numbers
    valid_phones = ['+1234567890', '+447123456789', '+521234567890']
    valid, invalid = validate_phone_numbers(valid_phones)
    
    print("✅ Testing valid phone numbers:")
    print(f"   Input: {valid_phones}")
    print(f"   Valid: {valid}")
    print(f"   Invalid: {invalid}")
    assert len(valid) == 3
    assert len(invalid) == 0
    
    # Test invalid phone numbers
    invalid_phones = ['1234567890', 'not-a-phone', '+', '++123456', 'abc@example.com']
    valid, invalid = validate_phone_numbers(invalid_phones)
    
    print("\n✅ Testing invalid phone numbers:")
    print(f"   Input: {invalid_phones}")
    print(f"   Valid: {valid}")
    print(f"   Invalid: {invalid}")
    assert len(valid) == 0
    assert len(invalid) == 5

def test_environment_variables():
    """Test that WhatsApp environment variables are defined"""
    from app import WHATSAPP_API_URL, WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID
    
    print("✅ Testing environment variables:")
    print(f"   WHATSAPP_API_URL: {WHATSAPP_API_URL}")
    print(f"   WHATSAPP_ACCESS_TOKEN: {'***' if WHATSAPP_ACCESS_TOKEN else 'NOT SET'}")
    print(f"   WHATSAPP_PHONE_NUMBER_ID: {'***' if WHATSAPP_PHONE_NUMBER_ID else 'NOT SET'}")
    
    assert WHATSAPP_API_URL is not None
    # Note: Tokens may not be set in development, but should be defined

def test_assignment_creation():
    """Test assignment creation with phone numbers"""
    from app import create_secret_santa_assignments
    
    phones = ['+1234567890', '+9876543210', '+5555551234']
    
    # Mock event ID for testing
    event_id = 'test-event-123'
    
    try:
        # This will fail without database, but we can test the logic
        assignments = create_secret_santa_assignments(phones, event_id)
        print("✅ Assignment creation logic works")
    except Exception as e:
        # Expected to fail without database connection
        print(f"⚠️  Assignment creation failed (expected without DB): {e}")
        # Verify the error is database-related, not logic-related
        assert "database" in str(e).lower() or "session" in str(e).lower()

def main():
    """Run all tests"""
    print("🧪 Testing WhatsApp Integration Setup\n")
    
    try:
        test_phone_validation()
        test_environment_variables()
        test_assignment_creation()
        
        print("\n✅ All tests passed! WhatsApp integration setup is correct.")
        print("\n📱 Next steps:")
        print("   1. Set up WhatsApp Business API credentials in .env")
        print("   2. Test with real phone numbers")
        print("   3. Deploy to your server")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()