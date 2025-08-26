"""
🎰 Slot Game Bot — O'yin mexanikasi va mantiqiy qismi - Yangilangan algoritm
"""
import random
import logging
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)

class SlotGame:
    """Enhanced slot game with balanced algorithms and advanced features"""
    
    def __init__(self):
        # Game symbols with weighted probabilities
        self.symbols = {
            "💎": {"weight": 5, "value": 100, "rarity": "legendary"},
            "🔔": {"weight": 10, "value": 50, "rarity": "epic"},
            "🍒": {"weight": 20, "value": 25, "rarity": "rare"},
            "⭐": {"weight": 30, "value": 10, "rarity": "uncommon"},
            "🍀": {"weight": 35, "value": 5, "rarity": "common"}
        }
        
        # Winning combinations with multipliers
        self.winning_combinations = {
            "💎💎💎": {"payout": 100, "multiplier": 1.0, "type": "jackpot"},
            "🔔🔔🔔": {"payout": 50, "multiplier": 1.0, "type": "big_win"},
            "🍒🍒🍒": {"payout": 25, "multiplier": 1.0, "type": "win"},
            "⭐⭐⭐": {"payout": 10, "multiplier": 1.0, "type": "win"},
            "🍀🍀🍀": {"payout": 5, "multiplier": 1.0, "type": "small_win"}
        }
        
        # Partial combinations
        self.partial_combinations = {
            2: {"payout": 3, "multiplier": 0.5, "type": "partial"},
            1: {"payout": 1, "multiplier": 0.2, "type": "minimal"}
        }
        
        # Dynamic win probability based on user stats
        self.base_win_probability = 0.7
        self.min_win_probability = 0.3
        self.max_win_probability = 0.9
        
        # Streak bonuses
        self.streak_bonuses = {
            1: {"bonus": 5, "multiplier": 1.0},
            3: {"bonus": 10, "multiplier": 1.2},
            7: {"bonus": 20, "multiplier": 1.5},
            14: {"bonus": 50, "multiplier": 2.0},
            30: {"bonus": 100, "multiplier": 3.0}
        }
        
        # Lucky spin intervals
        self.lucky_spin_intervals = [10, 25, 50, 100, 200, 500]
        
        # Progressive jackpot system
        self.progressive_jackpot = 1000
        self.jackpot_contribution = 0.01  # 1% of each bet
        
    def calculate_dynamic_win_probability(self, user_stats: Dict[str, Any]) -> float:
        """Calculate dynamic win probability based on user performance"""
        try:
            base_prob = self.base_win_probability
            
            # Adjust based on total spins
            total_spins = user_stats.get('total_spins', 0)
            if total_spins > 100:
                # Experienced players get slightly lower win rate
                base_prob -= 0.05
            elif total_spins < 10:
                # New players get slightly higher win rate
                base_prob += 0.05
            
            # Adjust based on recent performance
            recent_wins = user_stats.get('recent_wins', 0)
            recent_games = user_stats.get('recent_games', 10)
            if recent_games > 0:
                recent_win_rate = recent_wins / recent_games
                if recent_win_rate < 0.3:
                    # Losing streak - increase win probability
                    base_prob += 0.1
                elif recent_win_rate > 0.8:
                    # Winning streak - decrease win probability
                    base_prob -= 0.1
            
            # Adjust based on balance
            balance = user_stats.get('balance', 100)
            if balance < 50:
                # Low balance - increase win probability
                base_prob += 0.05
            elif balance > 500:
                # High balance - decrease win probability
                base_prob -= 0.05
            
            # Ensure within bounds
            return max(self.min_win_probability, min(self.max_win_probability, base_prob))
            
        except Exception as e:
            logger.error(f"Error calculating dynamic win probability: {e}")
            return self.base_win_probability
    
    def spin_reels(self, user_stats: Optional[Dict[str, Any]] = None) -> List[str]:
        """Spin the reels with enhanced algorithm"""
        try:
            # Calculate win probability
            win_prob = self.calculate_dynamic_win_probability(user_stats or {})
            
            # Determine if this should be a winning spin
            should_win = random.random() < win_prob
            
            if should_win:
                return self._generate_winning_spin()
            else:
                return self._generate_losing_spin()
                
        except Exception as e:
            logger.error(f"Error spinning reels: {e}")
            return self._generate_random_spin()
    
    def _generate_winning_spin(self) -> List[str]:
        """Generate a winning spin with balanced distribution"""
        try:
            # Choose winning combination type
            combo_type = random.choices(
                list(self.winning_combinations.keys()),
                weights=[5, 10, 20, 30, 35]  # Rarer combinations have lower weights
            )[0]
            
            # Extract symbols from combination
            symbols = list(combo_type)
            
            # Ensure we have exactly 3 symbols
            while len(symbols) < 3:
                # Add random symbols that don't break the win
                available_symbols = [s for s in self.symbols.keys() if s not in symbols]
                if available_symbols:
                    symbols.append(random.choice(available_symbols))
            
            # Shuffle the symbols for randomness
            random.shuffle(symbols)
            
            return symbols[:3]
            
        except Exception as e:
            logger.error(f"Error generating winning spin: {e}")
            return self._generate_random_spin()
    
    def _generate_losing_spin(self) -> List[str]:
        """Generate a losing spin that's close to winning"""
        try:
            # Create a spin that's almost winning
            symbols = list(self.symbols.keys())
            
            # Choose 2 different symbols for partial win
            if random.random() < 0.3:  # 30% chance of partial win
                symbol1 = random.choice(symbols)
                symbol2 = random.choice([s for s in symbols if s != symbol1])
                symbol3 = random.choice([s for s in symbols if s not in [symbol1, symbol2]])
                return [symbol1, symbol2, symbol3]
            else:
                # Completely random losing spin
                return random.choices(symbols, k=3)
                
        except Exception as e:
            logger.error(f"Error generating losing spin: {e}")
            return self._generate_random_spin()
    
    def _generate_random_spin(self) -> List[str]:
        """Generate completely random spin as fallback"""
        symbols = list(self.symbols.keys())
        return random.choices(symbols, k=3)
    
    def check_win(self, reels: List[str]) -> Tuple[bool, int, str, Dict[str, Any]]:
        """Check if reels result in a win with enhanced logic"""
        try:
            if len(reels) != 3:
                return False, 0, "invalid", {}
            
            # Check for exact matches first
            if reels[0] == reels[1] == reels[2]:
                symbol = reels[0]
                combo = f"{symbol}{symbol}{symbol}"
                
                if combo in self.winning_combinations:
                    win_info = self.winning_combinations[combo]
                    payout = win_info["payout"]
                    win_type = win_info["type"]
                    
                    # Apply progressive jackpot for legendary wins
                    if symbol == "💎":
                        payout += int(self.progressive_jackpot * 0.1)
                        self.progressive_jackpot = max(1000, self.progressive_jackpot - int(self.progressive_jackpot * 0.1))
                    
                    return True, payout, combo, {
                        "win_type": win_type,
                        "multiplier": win_info["multiplier"],
                        "symbol": symbol,
                        "rarity": self.symbols[symbol]["rarity"]
                    }
            
            # Check for partial wins
            symbol_counts = {}
            for symbol in reels:
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
            
            # Find most common symbol
            max_count = max(symbol_counts.values())
            if max_count >= 2:
                partial_info = self.partial_combinations.get(max_count)
                if partial_info:
                    return True, partial_info["payout"], f"{max_count}_of_a_kind", {
                        "win_type": partial_info["type"],
                        "multiplier": partial_info["multiplier"],
                        "symbol_count": max_count
                    }
            
            return False, 0, "no_win", {}
            
        except Exception as e:
            logger.error(f"Error checking win: {e}")
            return False, 0, "error", {}
    
    def calculate_streak_bonus(self, current_streak: int) -> Dict[str, Any]:
        """Calculate streak bonus with enhanced rewards"""
        try:
            # Find applicable streak bonus
            applicable_streaks = [s for s in self.streak_bonuses.keys() if current_streak >= s]
            
            if not applicable_streaks:
                return {"bonus": 0, "multiplier": 1.0, "next_streak": 1}
            
            # Get highest applicable streak
            max_streak = max(applicable_streaks)
            streak_info = self.streak_bonuses[max_streak]
            
            # Find next milestone
            next_streaks = [s for s in self.streak_bonuses.keys() if s > current_streak]
            next_streak = min(next_streaks) if next_streaks else current_streak
            
            return {
                "bonus": streak_info["bonus"],
                "multiplier": streak_info["multiplier"],
                "current_streak": current_streak,
                "next_streak": next_streak,
                "progress": current_streak / next_streak if next_streak > current_streak else 1.0
            }
            
        except Exception as e:
            logger.error(f"Error calculating streak bonus: {e}")
            return {"bonus": 0, "multiplier": 1.0, "next_streak": 1}
    
    def check_lucky_spin(self, spin_number: int) -> bool:
        """Check if current spin is a lucky spin"""
        try:
            return spin_number in self.lucky_spin_intervals
        except Exception as e:
            logger.error(f"Error checking lucky spin: {e}")
            return False
    
    def play_round(self, user_stats: Dict[str, Any]) -> Tuple[List[str], bool, int, Dict[str, Any]]:
        """Play a complete round with all features"""
        try:
            # Spin the reels
            reels = self.spin_reels(user_stats)
            
            # Check for win
            is_winner, stars_won, combo, win_info = self.check_win(reels)
            
            # Calculate additional bonuses
            extra_info = {
                "win_type": win_info.get("win_type", "no_win"),
                "combo": combo,
                "reels": reels,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add streak bonus if applicable
            current_streak = user_stats.get('daily_streak', 0)
            if current_streak > 0:
                streak_bonus = self.calculate_streak_bonus(current_streak)
                if streak_bonus["bonus"] > 0:
                    stars_won += streak_bonus["bonus"]
                    extra_info["streak_bonus"] = streak_bonus
            
            # Check for lucky spin
            spin_number = user_stats.get('total_spins', 0) + 1
            if self.check_lucky_spin(spin_number):
                lucky_bonus = 10
                stars_won += lucky_bonus
                extra_info["lucky_spin"] = True
                extra_info["lucky_bonus"] = lucky_bonus
            
            # Update progressive jackpot
            self.progressive_jackpot += int(stars_won * self.jackpot_contribution)
            extra_info["progressive_jackpot"] = self.progressive_jackpot
            
            return reels, is_winner, stars_won, extra_info
            
        except Exception as e:
            logger.error(f"Error playing round: {e}")
            return ["🍀", "🍀", "🍀"], False, 0, {"error": str(e)}
    
    def format_reels_message(self, reels: List[str], is_winner: bool, 
                           stars_won: int, extra_info: Dict[str, Any]) -> str:
        """Format reels result message with enhanced information"""
        try:
            message = f"🎰 **SLOT MASHINALARI** 🎰\n\n"
            message += f"{' '.join(reels)}\n\n"
            
            if is_winner:
                win_type = extra_info.get("win_type", "win")
                combo = extra_info.get("combo", "")
                
                if win_type == "jackpot":
                    message += f"🎉 **JACKPOT!** 🎉\n"
                    message += f"💎 {combo} - {stars_won} yulduz!\n"
                elif win_type == "big_win":
                    message += f"🎊 **Katta yutish!** 🎊\n"
                    message += f"🔔 {combo} - {stars_won} yulduz!\n"
                else:
                    message += f"🎯 **Yutish!** 🎯\n"
                    message += f"✨ {combo} - {stars_won} yulduz!\n"
                
                # Add streak bonus info
                if "streak_bonus" in extra_info:
                    streak_info = extra_info["streak_bonus"]
                    message += f"🔥 Streak bonus: +{streak_info['bonus']} yulduz\n"
                
                # Add lucky spin info
                if extra_info.get("lucky_spin"):
                    message += f"🍀 Lucky spin bonus: +{extra_info['lucky_bonus']} yulduz\n"
                
                # Add progressive jackpot info
                if "progressive_jackpot" in extra_info:
                    jackpot = extra_info["progressive_jackpot"]
                    message += f"💰 Progressive jackpot: {jackpot} yulduz\n"
                
            else:
                message += "😔 Bu safar yutish yo'q\n"
                message += "Keyingi safar omad tilaymiz! 🍀\n"
                
                # Show progress to next lucky spin
                spin_number = extra_info.get("spin_number", 0)
                next_lucky = next((s for s in self.lucky_spin_intervals if s > spin_number), None)
                if next_lucky:
                    remaining = next_lucky - spin_number
                    message += f"🎯 Keyingi lucky spin: {remaining} urinishdan keyin\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting reels message: {e}")
            return "❌ Xabar formatlashda xato yuz berdi"
    
    def get_combination_info(self) -> str:
        """Get information about winning combinations"""
        try:
            message = "🎰 **G'ALABA KOMBINATSIYALARI** 🎰\n\n"
            
            for combo, info in self.winning_combinations.items():
                symbol = combo[0]
                rarity = self.symbols[symbol]["rarity"]
                payout = info["payout"]
                
                message += f"{combo} - {payout} yulduz ({rarity})\n"
            
            message += "\n📊 **Qisman yutishlar:**\n"
            for count, info in self.partial_combinations.items():
                message += f"{count} ta bir xil belgi - {info['payout']} yulduz\n"
            
            message += f"\n💰 **Progressive Jackpot:** {self.progressive_jackpot} yulduz\n"
            message += f"🎯 **Lucky spin:** {', '.join(map(str, self.lucky_spin_intervals))} urinishda\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Error getting combination info: {e}")
            return "❌ Kombinatsiya ma'lumotlarini olishda xato"
    
    def get_game_stats(self) -> Dict[str, Any]:
        """Get current game statistics"""
        try:
            return {
                "progressive_jackpot": self.progressive_jackpot,
                "total_symbols": len(self.symbols),
                "winning_combinations": len(self.winning_combinations),
                "partial_combinations": len(self.partial_combinations),
                "lucky_spin_intervals": self.lucky_spin_intervals,
                "base_win_probability": self.base_win_probability,
                "streak_bonuses": self.streak_bonuses
            }
        except Exception as e:
            logger.error(f"Error getting game stats: {e}")
            return {}

# Global instance
slot_game = SlotGame()
