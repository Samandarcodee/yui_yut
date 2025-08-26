#!/usr/bin/env python3
"""
Security functionality test script
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_security():
    """Test security functionality"""
    try:
        from bot.security import setup_middleware, SecurityManager
        
        print("🔄 Testing security manager...")
        security_manager = SecurityManager()
        print("✅ Security manager: OK")
        
        print("🔄 Testing basic rate limiting...")
        # Test rate limiting
        is_limited = security_manager.is_rate_limited(12345)
        if not is_limited:
            print("✅ Rate limiting (initial): OK")
        else:
            print("❌ Rate limiting (initial): FAILED")
            return False
        
        print("🔄 Testing payment validation...")
        valid_amount = security_manager.validate_payment_amount(50)
        if valid_amount:
            print("✅ Payment validation (valid): OK")
        else:
            print("❌ Payment validation (valid): FAILED")
            return False
        
        invalid_amount = security_manager.validate_payment_amount(0)
        if not invalid_amount:
            print("✅ Payment validation (invalid): OK")
        else:
            print("❌ Payment validation (invalid): FAILED")
            return False
        
        print("🔄 Testing bonus validation...")
        valid_bonus = security_manager.validate_bonus_amount(100)
        if valid_bonus:
            print("✅ Bonus validation (valid): OK")
        else:
            print("❌ Bonus validation (valid): FAILED")
            return False
        
        invalid_bonus = security_manager.validate_bonus_amount(15000)
        if not invalid_bonus:
            print("✅ Bonus validation (invalid): OK")
        else:
            print("❌ Bonus validation (invalid): FAILED")
            return False
        
        print("🔄 Testing win probability validation...")
        valid_prob = security_manager.validate_win_probability(0.7)
        if valid_prob:
            print("✅ Win probability validation (valid): OK")
        else:
            print("❌ Win probability validation (valid): FAILED")
            return False
        
        invalid_prob = security_manager.validate_win_probability(1.5)
        if not invalid_prob:
            print("✅ Win probability validation (invalid): OK")
        else:
            print("❌ Win probability validation (invalid): FAILED")
            return False
        
        print("🔄 Testing username sanitization...")
        sanitized = security_manager.sanitize_username("test@user#123")
        if sanitized == "testuser123":
            print("✅ Username sanitization: OK")
        else:
            print(f"❌ Username sanitization: FAILED - Expected 'testuser123', got '{sanitized}'")
            return False
        
        print("🔄 Testing security event logging...")
        security_manager.log_security_event("test_event", 12345, "test_details")
        print("✅ Security event logging: OK")
        
        print("🔄 Testing middleware setup...")
        try:
            from db.database import Database
            db = Database()
            channel_middleware, admin_middleware = setup_middleware(db)
            if channel_middleware and admin_middleware:
                print("✅ Middleware setup: OK")
            else:
                print("❌ Middleware setup: FAILED")
                return False
        except Exception as e:
            print(f"❌ Middleware setup: FAILED - {e}")
            return False
        
        print("\n🎉 All security tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_security()
    sys.exit(0 if success else 1)
