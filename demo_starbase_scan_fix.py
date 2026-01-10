#!/usr/bin/env python3
"""
Demonstration of the starbase scan fix.
Shows before/after comparison and comprehensive statistics display.
"""

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from src.game_engine import GameEngine

def main():
    print("=" * 70)
    print("STARBASE SCAN ENHANCEMENT DEMONSTRATION")
    print("=" * 70)
    
    engine = GameEngine(universe_seed=42)
    player_ship = engine.player_ship
    
    # Setup test starbases
    from src.universe_objects import Starbase
    starbases = [(obj_id, obj) for obj_id, obj in engine.universe_objects.items() 
                 if isinstance(obj, Starbase)][:3]
    
    scenarios = [
        {
            'name': 'Friendly Starbase (Full Health)',
            'stance': 'friendly',
            'damage': 0.0,
            'energy': 100.0,
            'shields': 100.0,
            'torpedos': 500,
            'x_offset': 25.0,
            'y_offset': 10.0
        },
        {
            'name': 'Hostile Starbase (Damaged)',
            'stance': 'hostile',
            'damage': 35.0,
            'energy': 65.0,
            'shields': 65.0,
            'torpedos': 300,
            'x_offset': 40.0,
            'y_offset': -15.0
        },
        {
            'name': 'Neutral Starbase (Low Resources)',
            'stance': 'neutral',
            'damage': 15.0,
            'energy': 40.0,
            'shields': 85.0,
            'torpedos': 150,
            'x_offset': 35.0,
            'y_offset': 20.0
        }
    ]
    
    print("\n" + "=" * 70)
    print("BEFORE THE FIX")
    print("=" * 70)
    print("Starbase scans only showed:")
    print("  Scan of sb1234: ⊕ at 25.0 AU")
    print("\nMissing critical information:")
    print("  • Status, Damage, Energy")
    print("  • Shields, Torpedos")
    print("  • Service range, Defense range")
    print("  • Stance")
    
    print("\n" + "=" * 70)
    print("AFTER THE FIX")
    print("=" * 70)
    
    for i, scenario in enumerate(scenarios):
        if i >= len(starbases):
            break
            
        sb_id, sb = starbases[i]
        
        # Configure starbase
        sb.position.x = player_ship.position.x + scenario['x_offset']
        sb.position.y = player_ship.position.y + scenario['y_offset']
        sb.stances[player_ship.id] = scenario['stance']
        sb.damage = scenario['damage']
        sb.energy = scenario['energy']
        sb.shields = scenario['shields']
        sb.torpedos = scenario['torpedos']
        
        distance = player_ship.position.distance_to(sb.position)
        
        print(f"\n{'─' * 70}")
        print(f"Scenario {i+1}: {scenario['name']}")
        print(f"{'─' * 70}")
        
        # Execute scan
        engine.messages.clear()
        engine._execute_scan(player_ship, sb_id)
        
        for msg in engine.messages:
            print(msg)
        
        # Tactical assessment
        print(f"\n{'→ Tactical Assessment:':>20}")
        if scenario['stance'] == 'hostile':
            threat = "HIGH" if scenario['torpedos'] > 200 else "MEDIUM"
            print(f"{'  Threat Level:':>20} {threat}")
            print(f"{'  Recommendation:':>20} {'Avoid' if threat == 'HIGH' else 'Approach with caution'}")
        elif scenario['stance'] == 'friendly':
            can_repair = distance <= sb.service_range
            print(f"{'  Threat Level:':>20} NONE")
            print(f"{'  Recommendation:':>20} {'Safe for repairs' if can_repair else 'Safe - move closer for repairs'}")
        else:
            print(f"{'  Threat Level:':>20} UNKNOWN")
            print(f"{'  Recommendation:':>20} Monitor closely")
    
    print("\n" + "=" * 70)
    print("KEY BENEFITS")
    print("=" * 70)
    print("✓ Complete tactical information at a glance")
    print("✓ Assess threat level before engagement")
    print("✓ Plan resupply missions based on torpedo counts")
    print("✓ Identify weakened starbases for strategic advantage")
    print("✓ Know service range for repair planning")
    print("✓ Understand defensive capabilities (defense range)")
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    main()
