#!/usr/bin/env python3
"""
Keyboard functionality test script
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_keyboards():
    """Test keyboard functionality"""
    try:
        from keyboards.inline import (
            get_main_menu, get_play_again_keyboard, get_buy_stars_keyboard,
            get_profile_keyboard, get_daily_bonus_keyboard, get_referral_keyboard,
            get_channel_subscription_keyboard, get_admin_menu
        )
        
        print("🔄 Testing main menu keyboard...")
        main_menu = get_main_menu()
        if main_menu and hasattr(main_menu, 'inline_keyboard'):
            print("✅ Main menu keyboard: OK")
        else:
            print("❌ Main menu keyboard: FAILED")
            return False
        
        print("🔄 Testing play again keyboard...")
        play_again = get_play_again_keyboard()
        if play_again and hasattr(play_again, 'inline_keyboard'):
            print("✅ Play again keyboard: OK")
        else:
            print("❌ Play again keyboard: FAILED")
            return False
        
        print("🔄 Testing buy stars keyboard...")
        buy_stars = get_buy_stars_keyboard()
        if buy_stars and hasattr(buy_stars, 'inline_keyboard'):
            print("✅ Buy stars keyboard: OK")
        else:
            print("❌ Buy stars keyboard: FAILED")
            return False
        
        print("🔄 Testing profile keyboard...")
        profile = get_profile_keyboard()
        if profile and hasattr(profile, 'inline_keyboard'):
            print("✅ Profile keyboard: OK")
        else:
            print("❌ Profile keyboard: FAILED")
            return False
        
        print("🔄 Testing daily bonus keyboard...")
        daily_bonus = get_daily_bonus_keyboard(True)  # Can claim
        if daily_bonus and hasattr(daily_bonus, 'inline_keyboard'):
            print("✅ Daily bonus keyboard (can claim): OK")
        else:
            print("❌ Daily bonus keyboard (can claim): FAILED")
            return False
        
        daily_bonus = get_daily_bonus_keyboard(False)  # Cannot claim
        if daily_bonus and hasattr(daily_bonus, 'inline_keyboard'):
            print("✅ Daily bonus keyboard (cannot claim): OK")
        else:
            print("❌ Daily bonus keyboard (cannot claim): FAILED")
            return False
        
        print("🔄 Testing referral keyboard...")
        referral = get_referral_keyboard()
        if referral and hasattr(referral, 'inline_keyboard'):
            print("✅ Referral keyboard: OK")
        else:
            print("❌ Referral keyboard: FAILED")
            return False
        
        print("🔄 Testing channel subscription keyboard...")
        channel_sub = get_channel_subscription_keyboard("https://t.me/test")
        if channel_sub and hasattr(channel_sub, 'inline_keyboard'):
            print("✅ Channel subscription keyboard: OK")
        else:
            print("❌ Channel subscription keyboard: FAILED")
            return False
        
        print("🔄 Testing admin keyboard...")
        admin = get_admin_menu()
        if admin and hasattr(admin, 'inline_keyboard'):
            print("✅ Admin keyboard: OK")
        else:
            print("❌ Admin keyboard: FAILED")
            return False
        
        print("\n🎉 All keyboard tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Keyboard test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_keyboards()
    sys.exit(0 if success else 1)
