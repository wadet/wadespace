#!/usr/bin/env python3
"""
Comprehensive test of the ask command implementation.
"""

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from src.game_engine import GameEngine
from src.command_parser import CommandParser

def comprehensive_test():
    """Run comprehensive tests on the ask command."""
    print("=" * 70)
    print("COMPREHENSIVE ASK COMMAND TEST")
    print("=" * 70)
    
    engine = GameEngine(universe_seed=42)
    parser = CommandParser()
    
    print(f"\n✓ Game engine initialized")
    print(f"✓ Player at: ({engine.player_ship.position.x:.1f}, {engine.player_ship.position.y:.1f})")
    print(f"✓ LLM enabled: {engine.llm_handler.enabled}")
    
    # Test various natural language questions
    test_cases = [
        ("where is the nearest enemy base?", "Should find hostile starbase sb104"),
        ("find the closest friendly starbase", "Should find friendly starbase sb6698"),
        ("what's the nearest enemy ship?", "Should find enemy ship s8254"),
        ("how far is the closest star?", "Should find star st2663"),
        ("where can I find a black hole?", "Should find nearest black hole"),
        ("are there any wormholes nearby?", "Should search for wormholes"),
        ("locate the nearest planet", "Should find nearest planet"),
        ("how many enemy ships are there?", "Should count all enemy ships"),
    ]
    
    print(f"\n{'='*70}")
    print(f"Running {len(test_cases)} test cases:")
    print(f"{'='*70}\n")
    
    passed = 0
    failed = 0
    
    for i, (question, expected) in enumerate(test_cases, 1):
        print(f"[Test {i}/{len(test_cases)}] {question}")
        print(f"Expected: {expected}")
        
        engine.messages = []
        cmd = parser.parse(f"ask {question}")
        
        if cmd and cmd['command'] == 'ask':
            try:
                engine._execute_ask(engine.player_ship, cmd['question'])
                
                if engine.messages:
                    print(f"✓ Response received ({len(engine.messages)} lines)")
                    # Show first line of response
                    print(f"  → {engine.messages[0][:80]}...")
                    passed += 1
                else:
                    print(f"✗ No response generated")
                    failed += 1
            except Exception as e:
                print(f"✗ Error: {e}")
                failed += 1
        else:
            print(f"✗ Command parsing failed")
            failed += 1
        
        print()
    
    print(f"{'='*70}")
    print(f"TEST RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} total")
    print(f"{'='*70}\n")
    
    # Verify fallback still works when LLM is disabled
    print("Testing fallback to pattern matching...")
    engine.llm_handler.enabled = False
    engine.messages = []
    cmd = parser.parse("ask nearest enemy")
    if cmd:
        engine._execute_ask(engine.player_ship, cmd['question'])
        if engine.messages:
            print("✓ Fallback pattern matching works")
        else:
            print("✗ Fallback failed")
    
    print(f"\n{'='*70}")
    print("COMPREHENSIVE TEST COMPLETE")
    print(f"{'='*70}")

if __name__ == "__main__":
    comprehensive_test()
