#!/usr/bin/env python3
"""
Interactive demo showing the enhanced scan and HAL commands with stance and behavior.
"""

from src.game_engine import GameEngine
from src.command_parser import CommandParser


def demo_stance_behavior_display():
    """Demo the stance and behavior display in scan and HAL commands."""
    print("=" * 70)
    print(" DEMO: Enhanced Scan & HAL with Stance and Behavior Traits")
    print("=" * 70)
    print()
    print("This demo shows how the scan and hal commands now display:")
    print("  • Object stance towards the player (hostile/friendly/neutral)")
    print("  • Captain behavior traits (aggressive/timid/neutral)")
    print()
    print("=" * 70)
    
    # Initialize game
    engine = GameEngine(universe_seed=99999)
    player_ship = engine.player_ship
    parser = CommandParser()
    
    # Position player
    player_ship.position.x = 6000.0
    player_ship.position.y = 6000.0
    
    print("\n[SCENARIO: You're in a contested sector of space]")
    print("-" * 70)
    
    # Set up an interesting scenario with various NPCs and starbases
    npc_ids = list(engine.npc_ships.keys())[:5]
    
    npc_configs = [
        (8.0, 0.0, 'hostile', 'aggressive', 'Klingon Warship - very dangerous!'),
        (15.0, 15.0, 'hostile', 'neutral', 'Romulan Cruiser - standard threat'),
        (25.0, -10.0, 'neutral', 'neutral', 'Independent Trader - non-hostile'),
        (35.0, 20.0, 'friendly', 'timid', 'Federation Patrol - will avoid combat'),
        (45.0, -30.0, 'hostile', 'timid', 'Pirate Scout - will flee if damaged')
    ]
    
    print("\nNearby Ships:")
    for i, (x_offset, y_offset, stance, behavior, desc) in enumerate(npc_configs):
        if i < len(npc_ids):
            npc_id = npc_ids[i]
            npc = engine.npc_ships[npc_id]
            npc.position.x = 6000.0 + x_offset
            npc.position.y = 6000.0 + y_offset
            npc.stances[player_ship.id] = stance
            npc.behavior_trait = behavior
            distance = player_ship.position.distance_to(npc.position)
            print(f"  {npc_id}: {desc}")
            print(f"    Distance: {distance:.1f} AU | Stance: {stance} | Behavior: {behavior}")
    
    # Configure starbases
    sb_ids = [obj_id for obj_id in engine.universe_objects.keys() if obj_id.startswith('sb')][:3]
    sb_configs = [
        (18.0, 18.0, 'friendly', 'Starfleet Command - repairs available'),
        (40.0, -25.0, 'hostile', 'Enemy Outpost - dangerous territory'),
        (55.0, 35.0, 'neutral', 'Trading Station - neutral ground')
    ]
    
    print("\nNearby Starbases:")
    for i, (x_offset, y_offset, stance, desc) in enumerate(sb_configs):
        if i < len(sb_ids):
            sb_id = sb_ids[i]
            sb = engine.universe_objects[sb_id]
            sb.position.x = 6000.0 + x_offset
            sb.position.y = 6000.0 + y_offset
            sb.stances[player_ship.id] = stance
            distance = player_ship.position.distance_to(sb.position)
            print(f"  {sb_id}: {desc}")
            print(f"    Distance: {distance:.1f} AU | Stance: {stance}")
    
    # Demonstrate the commands
    print("\n" + "=" * 70)
    print(" COMMAND EXAMPLES")
    print("=" * 70)
    
    # Example 1: General scan
    print("\n[EXAMPLE 1] Command: scan")
    print("-" * 70)
    print("Shows all nearby objects with stance and behavior info:")
    print()
    engine.messages.clear()
    engine._execute_scan(player_ship)
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Example 2: Scan specific hostile ship
    print("\n" + "=" * 70)
    print(f"[EXAMPLE 2] Command: scan {npc_ids[0]}")
    print("-" * 70)
    print("Detailed scan of a specific ship shows stance and behavior:")
    print()
    engine.messages.clear()
    engine._execute_scan(player_ship, npc_ids[0])
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Example 3: HAL query for ship info
    print("\n" + "=" * 70)
    print(f"[EXAMPLE 3] Command: hal what is {npc_ids[2]}")
    print("-" * 70)
    print("HAL query shows behavior in header and stance as a field:")
    print()
    engine.messages.clear()
    engine._query_object_info(f"what is {npc_ids[2]}")
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Example 4: Scan friendly starbase
    if len(sb_ids) > 0:
        print("\n" + "=" * 70)
        print(f"[EXAMPLE 4] Command: scan {sb_ids[0]}")
        print("-" * 70)
        print("Scanning a starbase (starbases don't have behavior traits):")
        print()
        engine.messages.clear()
        engine._execute_scan(player_ship, sb_ids[0])
        for msg in engine.messages:
            print(f"  {msg}")
    
    # Example 5: HAL query for hostile starbase
    if len(sb_ids) > 1:
        print("\n" + "=" * 70)
        print(f"[EXAMPLE 5] Command: hal what is {sb_ids[1]}")
        print("-" * 70)
        print("HAL query for starbase shows stance:")
        print()
        engine.messages.clear()
        engine._query_object_info(f"what is {sb_ids[1]}")
        for msg in engine.messages:
            print(f"  {msg}")
    
    # Summary
    print("\n" + "=" * 70)
    print(" BENEFITS OF THIS ENHANCEMENT")
    print("=" * 70)
    print()
    print("Players can now quickly assess:")
    print()
    print("  1. THREAT LEVEL:")
    print("     • Hostile + Aggressive = Very dangerous, will attack")
    print("     • Hostile + Timid = Dangerous but may flee")
    print("     • Friendly = Safe, won't attack")
    print("     • Neutral = Cautious approach recommended")
    print()
    print("  2. COMBAT TACTICS:")
    print("     • Aggressive enemies: Prepare for immediate combat")
    print("     • Timid enemies: May flee if you're winning")
    print("     • Neutral captains: Predictable behavior")
    print()
    print("  3. STARBASE STRATEGY:")
    print("     • Friendly starbases: Safe harbor for repairs")
    print("     • Hostile starbases: Avoid or prepare for battle")
    print("     • Neutral starbases: Possible trading opportunities")
    print()
    print("=" * 70)
    print(" DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    demo_stance_behavior_display()
