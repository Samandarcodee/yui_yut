#!/usr/bin/env python3
"""
Database functionality test script
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_database():
    """Test database functionality"""
    try:
        from db.database import Database
        
        print("🔄 Testing database initialization...")
        db = Database()
        await db.init_db()
        print("✅ Database initialization: OK")
        
        print("🔄 Testing user registration...")
        test_user_id = 999999999
        await db.register_user(test_user_id, "test_user", "Test User")
        print("✅ User registration: OK")
        
        print("🔄 Testing user retrieval...")
        user = await db.get_user(test_user_id)
        if user:
            print(f"✅ User retrieval: OK - User: {user['username']}")
        else:
            print("❌ User retrieval: FAILED")
            return False
        
        print("🔄 Testing user balance update...")
        await db.update_user_balance(test_user_id, 100, 10)
        updated_user = await db.get_user(test_user_id)
        if updated_user['stars'] == 100 and updated_user['attempts'] == 10:
            print("✅ User balance update: OK")
        else:
            print("❌ User balance update: FAILED")
            return False
        
        print("🔄 Testing game result recording...")
        success = await db.record_game_result(test_user_id, "💎💎💎", True, 100)
        if success:
            print("✅ Game result recording: OK")
        else:
            print("❌ Game result recording: FAILED")
            return False
        
        print("🔄 Testing statistics...")
        stats = await db.get_total_stats()
        if stats:
            print(f"✅ Statistics: OK - Total users: {stats.get('total_users', 0)}")
        else:
            print("❌ Statistics: FAILED")
            return False
        
        print("🔄 Testing win probability...")
        prob = await db.get_win_probability()
        if prob is not None:
            print(f"✅ Win probability: OK - {prob}")
        else:
            print("❌ Win probability: FAILED")
            return False
        
        print("🔄 Testing channel subscription...")
        await db.set_channel_subscription(test_user_id, True)
        is_subscribed = await db.is_channel_subscribed(test_user_id)
        if is_subscribed:
            print("✅ Channel subscription: OK")
        else:
            print("❌ Channel subscription: FAILED")
            return False
        
        print("🔄 Testing daily bonus...")
        can_claim = await db.can_claim_daily_bonus(test_user_id)
        if can_claim:
            print("✅ Daily bonus check: OK")
        else:
            print("❌ Daily bonus check: FAILED")
            return False
        
        print("🔄 Testing referral system...")
        await db.add_referral(999999998, test_user_id)
        print("✅ Referral system: OK")
        
        print("🔄 Testing user verification...")
        await db.verify_user(test_user_id)
        verified_user = await db.get_user(test_user_id)
        if verified_user['is_verified']:
            print("✅ User verification: OK")
        else:
            print("❌ User verification: FAILED")
            return False
        
        print("🔄 Testing user banning/unbanning...")
        await db.ban_user(test_user_id)
        banned_user = await db.get_user(test_user_id)
        if banned_user['is_banned']:
            print("✅ User banning: OK")
        else:
            print("❌ User banning: FAILED")
            return False
        
        await db.unban_user(test_user_id)
        unbanned_user = await db.get_user(test_user_id)
        if not unbanned_user['is_banned']:
            print("✅ User unbanning: OK")
        else:
            print("❌ User unbanning: FAILED")
            return False
        
        print("🔄 Testing all users retrieval...")
        all_users = await db.get_all_users()
        if all_users:
            print(f"✅ All users retrieval: OK - Found {len(all_users)} users")
        else:
            print("❌ All users retrieval: FAILED")
            return False
        
        print("\n🎉 All database tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_database())
    sys.exit(0 if success else 1)
