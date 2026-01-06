#!/usr/bin/env python3
"""
Visual demonstration of the reputation system in action.
Shows how reputation changes based on different enemy types.
"""

from src.game_engine import GameEngine
from src.universe import Position


def demo_reputation_system():
    """Demonstrate reputation changes with various enemy types."""
    print("=" * 80)
    print("REPUTATION SYSTEM DEMONSTRATION")
    print("=" * 80)
    print("\nThis demo shows how your reputation changes when destroying different")
    print("types of enemy ships based on their behavior and reputation scores.")
    print("=" * 80)
    
    game = GameEngine()
    game.player_ship.position = Position(5000, 5000)
    game.player_ship.reputation = 50  # Start at neutral reputation
    
    print(f"\n🚀 STARTING REPUTATION: {game.player_ship.reputation}")
    print("=" * 80)
    
    # Scenario 1: Destroy aggressive, low-rep pirate
    print("\n📍 SCENARIO 1: Destroying a dangerous pirate")
    print("-" * 80)
    enemy_id = list(game.enemy_ships.keys())[0]
    enemy = game.enemy_ships[enemy_id]
    enemy.behavior_trait = 'aggressive'
    enemy.reputation = 15
    enemy.damage = 100
    enemy.is_destroyed = True
    
    print(f"Target: {enemy_id}")
    print(f"  Type: AGGRESSIVE pirate")
    print(f"  Reputation: {enemy.reputation} (low - notorious criminal)")
    print(f"\n💥 Ship destroyed!")
    
    before = game.player_ship.reputation
    game._handle_ship_destruction(game.player_ship, enemy, enemy_id)
    after = game.player_ship.reputation
    
    print(f"  Your reputation: {before} → {after} ({after-before:+d})")
    print(f"  ✓ You are a hero for stopping this menace!")
    
    # Scenario 2: Destroy timid trader
    print("\n📍 SCENARIO 2: Destroying a peaceful trader")
    print("-" * 80)
    enemy_id2 = list(game.enemy_ships.keys())[1]
    enemy2 = game.enemy_ships[enemy_id2]
    enemy2.behavior_trait = 'timid'
    enemy2.reputation = 60
    enemy2.damage = 100
    enemy2.is_destroyed = True
    
    print(f"Target: {enemy_id2}")
    print(f"  Type: TIMID trader")
    print(f"  Reputation: {enemy2.reputation} (peaceful merchant)")
    print(f"\n💥 Ship destroyed!")
    
    before = game.player_ship.reputation
    game._handle_ship_destruction(game.player_ship, enemy2, enemy_id2)
    after = game.player_ship.reputation
    
    print(f"  Your reputation: {before} → {after} ({after-before:+d})")
    print(f"  ⚠ You attacked an innocent! People will remember this...")
    
    # Scenario 3: Destroy high-reputation diplomat
    print("\n📍 SCENARIO 3: Destroying a respected diplomat")
    print("-" * 80)
    enemy_id3 = list(game.enemy_ships.keys())[2]
    enemy3 = game.enemy_ships[enemy_id3]
    enemy3.behavior_trait = 'neutral'
    enemy3.reputation = 85
    enemy3.damage = 100
    enemy3.is_destroyed = True
    
    print(f"Target: {enemy_id3}")
    print(f"  Type: Neutral captain")
    print(f"  Reputation: {enemy3.reputation} (highly respected diplomat)")
    print(f"\n💥 Ship destroyed!")
    
    before = game.player_ship.reputation
    game._handle_ship_destruction(game.player_ship, enemy3, enemy_id3)
    after = game.player_ship.reputation
    
    print(f"  Your reputation: {before} → {after} ({after-before:+d})")
    print(f"  ⚠ Killing a diplomat has consequences!")
    
    # Scenario 4: Destroy aggressive warlord
    print("\n📍 SCENARIO 4: Destroying an aggressive warlord")
    print("-" * 80)
    enemy_id4 = list(game.enemy_ships.keys())[3]
    enemy4 = game.enemy_ships[enemy_id4]
    enemy4.behavior_trait = 'aggressive'
    enemy4.reputation = 75  # High rep but aggressive
    enemy4.damage = 100
    enemy4.is_destroyed = True
    
    print(f"Target: {enemy_id4}")
    print(f"  Type: AGGRESSIVE warlord")
    print(f"  Reputation: {enemy4.reputation} (feared military commander)")
    print(f"\n💥 Ship destroyed!")
    
    before = game.player_ship.reputation
    game._handle_ship_destruction(game.player_ship, enemy4, enemy_id4)
    after = game.player_ship.reputation
    
    print(f"  Your reputation: {before} → {after} ({after-before:+d})")
    print(f"  ✓ Aggressive trait overrides high reputation!")
    
    # Scenario 5: Destroy neutral mid-rep ship (no change)
    print("\n📍 SCENARIO 5: Destroying a neutral captain (mid reputation)")
    print("-" * 80)
    enemy_id5 = list(game.enemy_ships.keys())[4]
    enemy5 = game.enemy_ships[enemy_id5]
    enemy5.behavior_trait = 'neutral'
    enemy5.reputation = 50
    enemy5.damage = 100
    enemy5.is_destroyed = True
    
    print(f"Target: {enemy_id5}")
    print(f"  Type: Neutral captain")
    print(f"  Reputation: {enemy5.reputation} (average)")
    print(f"\n💥 Ship destroyed!")
    
    before = game.player_ship.reputation
    game._handle_ship_destruction(game.player_ship, enemy5, enemy_id5)
    after = game.player_ship.reputation
    
    if after == before:
        print(f"  Your reputation: {before} (no change)")
        print(f"  ℹ  Mid-range reputation, neutral behavior = no effect")
    else:
        print(f"  Your reputation: {before} → {after} ({after-before:+d})")
    
    # Final summary
    print("\n" + "=" * 80)
    print("SUMMARY OF REPUTATION RULES")
    print("=" * 80)
    print("\n✅ REPUTATION INCREASES (+10) when you destroy:")
    print("   • Aggressive enemies (regardless of their reputation)")
    print("   • Low-reputation enemies (reputation < 30)")
    print("\n⛔ REPUTATION DECREASES (-10) when you destroy:")
    print("   • Timid enemies (regardless of their reputation)")
    print("   • High-reputation enemies (reputation > 70)")
    print("\n➖ NO CHANGE when you destroy:")
    print("   • Neutral enemies with mid-range reputation (30-70)")
    print("\n📊 Reputation is always capped between 0 and 100")
    print("=" * 80)


if __name__ == "__main__":
    demo_reputation_system()
