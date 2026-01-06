#!/usr/bin/env python3
"""
Quick demo showing behavior traits in action during a game turn.
"""

from src.game_engine import GameEngine

def demo_behavior_traits():
    """Demonstrate behavior traits during gameplay."""
    print("="*70)
    print("WADESPACE - BEHAVIOR TRAITS DEMO")
    print("="*70)
    
    # Initialize game
    game = GameEngine(universe_seed=999)
    game.debug_mode = True  # Enable debug messages
    
    print(f"\nGame initialized with {len(game.enemy_ships)} enemy ships")
    print(f"Player reputation: {game.player_ship.reputation}")
    print(f"Player position: ({game.player_ship.position.x:.1f}, {game.player_ship.position.y:.1f})")
    
    # Get nearby enemies
    nearby_enemies = []
    for enemy_id, enemy_ship in game.enemy_ships.items():
        distance = enemy_ship.position.distance_to(game.player_ship.position)
        if distance < 50:  # Within sensor range
            nearby_enemies.append((enemy_id, enemy_ship, distance))
    
    nearby_enemies.sort(key=lambda x: x[2])
    
    print(f"\nNearby enemy ships (within 50 AU): {len(nearby_enemies)}")
    for enemy_id, enemy_ship, distance in nearby_enemies[:5]:
        print(f"  {enemy_id}: {enemy_ship.behavior_trait} captain at {distance:.1f} AU")
    
    # Scan a nearby enemy to show behavior trait
    if nearby_enemies:
        target_id, target_ship, distance = nearby_enemies[0]
        print(f"\n{'='*70}")
        print(f"Scanning nearest enemy ship: {target_id}")
        print(f"{'='*70}")
        game._execute_scan(game.player_ship, target_id)
        for msg in game.messages:
            print(msg)
        game.messages = []
    
    # Simulate a turn to see behavior traits in action
    print(f"\n{'='*70}")
    print("SIMULATING TURN 1 - Enemy AI Decisions")
    print(f"{'='*70}")
    
    # Process one turn
    game.process_turn()
    
    # Show messages from enemy AI
    if game.messages:
        print("\nEnemy actions:")
        for msg in game.messages:
            if 'DEBUG' in msg:
                print(msg)
    else:
        print("\n(No enemy actions this turn - enemies may be out of range)")
    
    # Show behavior distribution
    print(f"\n{'='*70}")
    print("BEHAVIOR TRAIT DISTRIBUTION")
    print(f"{'='*70}")
    
    trait_counts = {'aggressive': 0, 'neutral': 0, 'timid': 0}
    for enemy_ship in game.enemy_ships.values():
        if enemy_ship.behavior_trait:
            trait_counts[enemy_ship.behavior_trait] += 1
    
    total = sum(trait_counts.values())
    for trait, count in sorted(trait_counts.items()):
        percentage = (count / total) * 100 if total > 0 else 0
        print(f"  {trait.capitalize()}: {count:2d} ({percentage:5.1f}%)")
    
    print(f"\n{'='*70}")
    print("DEMO COMPLETE")
    print(f"{'='*70}")
    print("\nBehavior traits are now active in the game!")
    print("Enemy captains will behave according to their personality traits.")
    print("Use 'scan <ship_id>' to see an enemy's behavior trait.")

if __name__ == '__main__':
    demo_behavior_traits()
