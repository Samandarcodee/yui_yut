#!/usr/bin/env python3
"""
Game Logic functionality test script
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_game_logic():
    """Test game logic functionality"""
    try:
        from bot.game_logic import slot_game
        
        print("🔄 Testing slot game emojis...")
        if len(slot_game.emojis) == 5:
            print(f"✅ Emojis: OK - {slot_game.emojis}")
        else:
            print(f"❌ Emojis: FAILED - Expected 5, got {len(slot_game.emojis)}")
            return False
        
        print("🔄 Testing winning combinations...")
        if len(slot_game.winning_combinations) == 5:
            print(f"✅ Winning combinations: OK - {len(slot_game.winning_combinations)} combinations")
        else:
            print(f"❌ Winning combinations: FAILED - Expected 5, got {len(slot_game.winning_combinations)}")
            return False
        
        print("🔄 Testing partial combinations...")
        if len(slot_game.partial_combinations) == 2:
            print(f"✅ Partial combinations: OK - {slot_game.partial_combinations}")
        else:
            print(f"❌ Partial combinations: FAILED - Expected 2, got {len(slot_game.partial_combinations)}")
            return False
        
        print("🔄 Testing spin reels...")
        reels = slot_game.spin_reels()
        if len(reels) == 3 and all(emoji in slot_game.emojis for emoji in reels):
            print(f"✅ Spin reels: OK - {reels}")
        else:
            print(f"❌ Spin reels: FAILED - {reels}")
            return False
        
        print("🔄 Testing win checking...")
        # Test winning combination
        winning_reels = ["💎", "💎", "💎"]
        is_winner, stars_won, combo = slot_game.check_win(winning_reels)
        if is_winner and stars_won == 100:
            print(f"✅ Win checking (winning): OK - {stars_won} stars for {combo}")
        else:
            print(f"❌ Win checking (winning): FAILED - {is_winner}, {stars_won}")
            return False
        
        # Test partial combination
        partial_reels = ["💎", "💎", "🔔"]
        is_winner, stars_won, combo = slot_game.check_win(partial_reels)
        if is_winner and stars_won == 3:
            print(f"✅ Win checking (partial): OK - {stars_won} stars for {combo}")
        else:
            print(f"❌ Win checking (partial): FAILED - {is_winner}, {stars_won}")
            return False
        
        # Test losing combination
        losing_reels = ["💎", "🔔", "🍒"]
        is_winner, stars_won, combo = slot_game.check_win(losing_reels)
        if not is_winner and stars_won == 0:
            print(f"✅ Win checking (losing): OK - {stars_won} stars for {combo}")
        else:
            print(f"❌ Win checking (losing): FAILED - {is_winner}, {stars_won}")
            return False
        
        print("🔄 Testing win probability...")
        should_win = slot_game.should_win(1.0)  # 100% probability
        if should_win:
            print("✅ Win probability (100%): OK")
        else:
            print("❌ Win probability (100%): FAILED")
            return False
        
        should_win = slot_game.should_win(0.0)  # 0% probability
        if not should_win:
            print("✅ Win probability (0%): OK")
        else:
            print("❌ Win probability (0%): FAILED")
            return False
        
        print("🔄 Testing winning spin generation...")
        reels, stars_won, win_type = slot_game.generate_winning_spin()
        if len(reels) == 3 and stars_won > 0:
            print(f"✅ Winning spin generation: OK - {reels}, {stars_won} stars, {win_type}")
        else:
            print(f"❌ Winning spin generation: FAILED - {reels}, {stars_won}")
            return False
        
        print("🔄 Testing losing spin generation...")
        reels = slot_game.generate_losing_spin()
        if len(reels) == 3:
            print(f"✅ Losing spin generation: OK - {reels}")
        else:
            print(f"❌ Losing spin generation: FAILED - {reels}")
            return False
        
        print("🔄 Testing lucky spin detection...")
        is_lucky = slot_game.check_lucky_spin(20)  # 20th spin
        if is_lucky:
            print("✅ Lucky spin detection: OK")
        else:
            print("❌ Lucky spin detection: FAILED")
            return False
        
        is_lucky = slot_game.check_lucky_spin(25)  # 25th spin
        if not is_lucky:
            print("✅ Lucky spin detection (non-lucky): OK")
        else:
            print("❌ Lucky spin detection (non-lucky): FAILED")
            return False
        
        print("🔄 Testing daily streak bonus...")
        bonus = slot_game.get_daily_streak_bonus(1)
        if bonus == 5:
            print("✅ Daily streak bonus (1 day): OK")
        else:
            print(f"❌ Daily streak bonus (1 day): FAILED - Expected 5, got {bonus}")
            return False
        
        bonus = slot_game.get_daily_streak_bonus(3)
        if bonus == 10:
            print("✅ Daily streak bonus (3 days): OK")
        else:
            print(f"❌ Daily streak bonus (3 days): FAILED - Expected 10, got {bonus}")
            return False
        
        bonus = slot_game.get_daily_streak_bonus(7)
        if bonus == 20:
            print("✅ Daily streak bonus (7+ days): OK")
        else:
            print(f"❌ Daily streak bonus (7+ days): FAILED - Expected 20, got {bonus}")
            return False
        
        print("🔄 Testing complete play round...")
        reels, is_winner, stars_won, extra_info = slot_game.play_round(0.7, 0, 0)
        if len(reels) == 3 and isinstance(is_winner, bool) and isinstance(stars_won, int):
            print(f"✅ Play round: OK - {reels}, winner: {is_winner}, stars: {stars_won}")
        else:
            print(f"❌ Play round: FAILED - {reels}, {is_winner}, {stars_won}")
            return False
        
        print("🔄 Testing message formatting...")
        message = slot_game.format_reels_message(["💎", "💎", "💎"], True, 100, {"win_type": "big_win"})
        if "JACKPOT" in message and "100 yulduz" in message:
            print("✅ Message formatting (big win): OK")
        else:
            print("❌ Message formatting (big win): FAILED")
            return False
        
        message = slot_game.format_reels_message(["💎", "🔔", "🍒"], False, 0)
        if "Bu safar yutish yo'q" in message:
            print("✅ Message formatting (loss): OK")
        else:
            print("❌ Message formatting (loss): FAILED")
            return False
        
        print("🔄 Testing combination info...")
        info = slot_game.get_combination_info()
        if "G'ALABA KOMBINATSIYALARI" in info and "70%" in info:
            print("✅ Combination info: OK")
        else:
            print("❌ Combination info: FAILED")
            return False
        
        print("\n🎉 All game logic tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Game logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_game_logic()
    sys.exit(0 if success else 1)
