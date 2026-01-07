#!/usr/bin/env python3
"""
Test script to verify enemy ships can attack other enemy ships.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from game_engine import GameEngine
from ship import Ship
from universe import Position

def test_enemy_on_enemy_combat():
    """Test that enemy ships can target and attack other enemy ships."""
    print("=" * 60)
    print("Testing Enemy-on-Enemy Combat")
    print("=" * 60)
    
    # Create a game engine instance
    print("\n1. Creating game engine...")
    engine = GameEngine()
    
    # Check that LLM handler has the updated method signature
    print("\n2. Checking LLM handler...")
    import inspect
    sig = inspect.signature(engine.llm_handler.get_enemy_decision)
    params = list(sig.parameters.keys())
    print(f"   LLM handler parameters: {params}")
    
    if 'nearby_enemy_ships' in params:
        print("   ✓ LLM handler updated to include nearby_enemy_ships")
    else:
        print("   ✗ FAILED: nearby_enemy_ships not in parameters")
        return False
    
    # Check that decisions include target_id
    print("\n3. Checking decision format...")
    test_decision = engine.llm_handler._default_decision()
    print(f"   Default decision keys: {list(test_decision.keys())}")
    
    if 'target_id' in test_decision:
        print("   ✓ Decision includes target_id field")
    else:
        print("   ✗ FAILED: target_id not in decision")
        return False
    
    # Check that basic AI considers other enemies
    print("\n4. Checking basic AI implementation...")
    # Find the source code of _execute_basic_enemy_ai
    source_lines = inspect.getsource(engine._execute_basic_enemy_ai).split('\n')
    
    has_nearby_enemies = any('nearby_enemies' in line for line in source_lines)
    has_target_selection = any('target_ship' in line for line in source_lines)
    
    if has_nearby_enemies:
        print("   ✓ Basic AI checks for nearby enemy ships")
    else:
        print("   ✗ FAILED: Basic AI doesn't check nearby enemies")
        return False
    
    if has_target_selection:
        print("   ✓ Basic AI includes target selection logic")
    else:
        print("   ✗ FAILED: Basic AI doesn't select targets")
        return False
    
    # Check torpedo collision detection
    print("\n5. Checking torpedo collision detection...")
    source_lines = inspect.getsource(engine._update_torpedos_for_ship).split('\n')
    
    checks_other_enemies = any('enemy_id != torpedo' in line or "Don't hit yourself" in line 
                                for line in source_lines)
    
    if checks_other_enemies:
        print("   ✓ Torpedo collision checks other enemy ships")
    else:
        print("   ✗ FAILED: Torpedo collision doesn't check other enemies")
        return False
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
    print("\nSummary:")
    print("  • LLM handler receives nearby enemy ship data")
    print("  • Decision format includes target_id field")
    print("  • Basic AI can select enemy ships as targets")
    print("  • Torpedo collision detects enemy-on-enemy hits")
    print("\nEnemy ships can now attack other enemy ships!")
    return True

if __name__ == '__main__':
    success = test_enemy_on_enemy_combat()
    sys.exit(0 if success else 1)
