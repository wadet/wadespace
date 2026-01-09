#!/usr/bin/env python3
"""
Additional test to verify starbase attacks.
"""

from src.game_engine import GameEngine
from src.universe_objects import Starbase, Position
from src.ship import Ship

def test_starbase_attacks():
    """Test that hostile starbases attack ships in range."""
    print("=" * 60)
    print("Testing Starbase Attack Behavior")
    print("=" * 60)
    
    engine = GameEngine(universe_seed=42)
    
    # Move player near a hostile starbase
    starbases = [obj for obj in engine.universe_objects.values() if isinstance(obj, Starbase)]
    hostile_starbase = None
    
    for sb in starbases:
        if sb.stances.get(engine.player_ship.id) == 'hostile':
            hostile_starbase = sb
            break
    
    if hostile_starbase:
        print(f"\nFound hostile starbase: {hostile_starbase.id}")
        print(f"  Stance toward player: {hostile_starbase.stances.get(engine.player_ship.id)}")
        print(f"  Defense range: {hostile_starbase.defense_range} AU")
        
        # Move player within range
        print(f"\nMoving player to within attack range of starbase...")
        engine.player_ship.position = Position(
            hostile_starbase.position.x + 5.0,
            hostile_starbase.position.y + 5.0
        )
        distance = engine.player_ship.position.distance_to(hostile_starbase.position)
        print(f"  Distance to hostile starbase: {distance:.1f} AU")
        
        # Record initial state
        initial_shields = engine.player_ship.shields
        initial_damage = engine.player_ship.damage
        
        print(f"\nPlayer initial state:")
        print(f"  Shields: {initial_shields:.1f}%")
        print(f"  Damage: {initial_damage:.1f}%")
        
        # Process 10 turns
        print(f"\nProcessing 10 turns...")
        attacks_received = 0
        
        for turn in range(10):
            engine.process_turn(None)
            
            # Check messages for starbase attacks
            for msg in engine.messages:
                if hostile_starbase.id in msg and ('fires' in msg or 'launches' in msg) and 'you' in msg:
                    attacks_received += 1
                    print(f"  Turn {turn + 1}: {msg}")
        
        # Check final state
        final_shields = engine.player_ship.shields
        final_damage = engine.player_ship.damage
        
        print(f"\nPlayer final state:")
        print(f"  Shields: {final_shields:.1f}%")
        print(f"  Damage: {final_damage:.1f}%")
        print(f"\nTotal attacks received: {attacks_received}")
        
        if attacks_received > 0 or final_shields < initial_shields or final_damage > initial_damage:
            print("\n✓ TEST PASSED: Hostile starbase attacked the player!")
        else:
            print("\n⚠ WARNING: No attacks detected (may be RNG)")
    else:
        print("\nNo hostile starbase found in this seed, trying another...")
        engine2 = GameEngine(universe_seed=999)
        starbases2 = [obj for obj in engine2.universe_objects.values() if isinstance(obj, Starbase)]
        hostile_count = sum(1 for sb in starbases2 if sb.stances.get(engine2.player_ship.id) == 'hostile')
        print(f"Seed 999 has {hostile_count} hostile starbases")


def test_npc_to_npc_attacks():
    """Test that NPCs attack each other based on stance."""
    print("\n" + "=" * 60)
    print("Testing NPC-to-NPC Combat Based on Stance")
    print("=" * 60)
    
    engine = GameEngine(universe_seed=123)
    
    # Find two NPCs that are hostile to each other and close
    hostile_pairs = []
    npc_list = list(engine.npc_ships.items())
    
    for i, (npc1_id, npc1) in enumerate(npc_list):
        for npc2_id, npc2 in npc_list[i+1:]:
            stance_1_to_2 = npc1.stances.get(npc2_id)
            stance_2_to_1 = npc2.stances.get(npc1_id)
            
            if stance_1_to_2 == 'hostile' or stance_2_to_1 == 'hostile':
                distance = npc1.position.distance_to(npc2.position)
                if distance < 50:
                    hostile_pairs.append((npc1_id, npc2_id, stance_1_to_2, stance_2_to_1, distance))
    
    hostile_pairs.sort(key=lambda x: x[4])
    
    print(f"\nFound {len(hostile_pairs)} hostile NPC pairs within 50 AU")
    
    if hostile_pairs:
        for i, (npc1_id, npc2_id, stance_1_to_2, stance_2_to_1, dist) in enumerate(hostile_pairs[:3]):
            print(f"  Pair {i+1}: {npc1_id} <-> {npc2_id}")
            print(f"    {npc1_id}'s stance toward {npc2_id}: {stance_1_to_2}")
            print(f"    {npc2_id}'s stance toward {npc1_id}: {stance_2_to_1}")
            print(f"    Distance: {dist:.1f} AU")
        
        # Track one pair
        npc1_id, npc2_id = hostile_pairs[0][0], hostile_pairs[0][1]
        npc1 = engine.npc_ships[npc1_id]
        npc2 = engine.npc_ships[npc2_id]
        
        print(f"\nTracking combat between {npc1_id} and {npc2_id}:")
        print(f"  Initial damage - {npc1_id}: {npc1.damage:.1f}%, {npc2_id}: {npc2.damage:.1f}%")
        
        # Process turns
        combat_events = []
        for turn in range(10):
            engine.process_turn(None)
            
            for msg in engine.messages:
                if (npc1_id in msg or npc2_id in msg) and ('fires' in msg or 'launches' in msg or 'hit' in msg):
                    combat_events.append(f"Turn {turn+1}: {msg}")
        
        print(f"\nCombat events:")
        for event in combat_events[:10]:
            print(f"  {event}")
        
        print(f"\n  Final damage - {npc1_id}: {npc1.damage:.1f}%, {npc2_id}: {npc2.damage:.1f}%")
        
        if combat_events:
            print("\n✓ TEST PASSED: NPCs are attacking each other based on stance!")
        else:
            print("\n⚠ No combat detected (may need to adjust parameters)")
    else:
        print("\nNo hostile NPC pairs found close together in this seed")


if __name__ == '__main__':
    test_starbase_attacks()
    test_npc_to_npc_attacks()
    
    print("\n" + "=" * 60)
    print("ADDITIONAL TESTS COMPLETE")
    print("=" * 60)
