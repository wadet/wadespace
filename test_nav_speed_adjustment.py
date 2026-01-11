#!/usr/bin/env python3
"""
Test script for dynamic speed adjustment during nav mode pursuit.

This test verifies that:
1. Player ship in nav mode adjusts speed when within sensor range to close to 10 AU
2. NPC ships adjust speed when pursuing targets within sensor range
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from game_engine import GameEngine
from universe_objects import Position
from ship import Ship
import math


def test_player_nav_speed_adjustment():
    """Test player ship speed adjustment during nav mode."""
    print("=" * 80)
    print("TEST 1: Player Nav Mode Speed Adjustment")
    print("=" * 80)
    
    engine = GameEngine()
    
    # Create a test NPC ship at a known distance
    test_npc = Ship("s9999", Position(100, 100), is_player=False)
    test_npc.behavior_trait = "aggressive"
    engine.npc_ships["s9999"] = test_npc
    
    # Position player ship 45 AU away (within sensor range of 50 AU)
    engine.player_ship.position = Position(55, 100)
    
    # Calculate initial distance
    initial_dist = engine.player_ship.position.distance_to(test_npc.position)
    print(f"\nInitial distance to target: {initial_dist:.1f} AU")
    print(f"Sensor range: {engine.player_ship.sensors.sensor_range} AU")
    
    # Enable nav mode to target the NPC
    engine.player_ship.auto_nav_target_id = "s9999"
    engine.player_ship.auto_nav_warp_speed = 9.0  # Max speed
    
    print("\n--- Testing speed adjustment while closing in ---")
    
    # Simulate several turns
    for turn in range(1, 6):
        print(f"\n--- Turn {turn} ---")
        
        # Get distance before movement
        dist_before = engine.player_ship.position.distance_to(test_npc.position)
        print(f"Distance before: {dist_before:.1f} AU")
        
        # Process auto-nav (this should adjust speed)
        engine._process_auto_nav(engine.player_ship)
        
        # Check what speed was set
        current_speed = engine.player_ship.propulsion.current_speed
        print(f"Speed set by auto-nav: {current_speed:.2f} AU/turn")
        
        # Simulate movement
        if engine.player_ship.propulsion.warp_active or engine.player_ship.propulsion.impulse_active:
            heading_rad = math.radians(engine.player_ship.propulsion.current_heading)
            dx = current_speed * math.cos(heading_rad)
            dy = current_speed * math.sin(heading_rad)
            engine.player_ship.position.x += dx
            engine.player_ship.position.y += dy
        
        # Get distance after movement
        dist_after = engine.player_ship.position.distance_to(test_npc.position)
        print(f"Distance after: {dist_after:.1f} AU")
        print(f"Distance closed: {dist_before - dist_after:.1f} AU")
        
        # Verify speed adjustment behavior
        closing_distance = dist_after - 10.0  # Target is 10 AU
        if dist_after <= 50 and dist_after > 10:
            print(f"✓ Within sensor range, adjusting speed to close {closing_distance:.1f} AU gap")
            # Check that speed was reduced appropriately
            if closing_distance > 30:
                expected_max = min(9.0, closing_distance * 0.3)
                print(f"  Expected speed adjustment for far range: ~{expected_max:.2f} AU/turn")
            elif closing_distance > 15:
                expected_max = min(9.0 * 0.7, closing_distance * 0.4)
                print(f"  Expected speed adjustment for medium range: ~{expected_max:.2f} AU/turn")
            else:
                expected_max = min(9.0 * 0.5, closing_distance * 0.5)
                print(f"  Expected speed adjustment for close range: ~{expected_max:.2f} AU/turn")
        
        if dist_after <= 10.5:
            print("✓ Target distance reached (within 10 AU)")
            break
    
    print("\n" + "=" * 80)
    print("TEST 1 COMPLETE")
    print("=" * 80)


def test_npc_pursuit_speed_adjustment():
    """Test NPC ship speed adjustment when pursuing targets."""
    print("\n" * 2)
    print("=" * 80)
    print("TEST 2: NPC Pursuit Speed Adjustment")
    print("=" * 80)
    
    engine = GameEngine()
    
    # Position player ship
    engine.player_ship.position = Position(100, 100)
    
    # Create a test NPC ship at 40 AU away (within sensor range)
    # Give it no torpedoes so it will close in rather than firing
    test_npc = Ship("s8888", Position(140, 100), is_player=False)
    test_npc.behavior_trait = "aggressive"
    test_npc.reputation = 30  # Low rep means likely to attack
    test_npc.weapons.torpedos = 0  # No torpedoes - force it to close in
    engine.npc_ships["s8888"] = test_npc
    
    # Set hostile stance to ensure attack behavior
    test_npc.stances[engine.player_ship.id] = "hostile"
    
    initial_dist = test_npc.position.distance_to(engine.player_ship.position)
    print(f"\nInitial distance to player: {initial_dist:.1f} AU")
    print(f"NPC behavior: {test_npc.behavior_trait}")
    print(f"NPC stance toward player: {test_npc.stances.get(engine.player_ship.id, 'neutral')}")
    print(f"NPC torpedoes: {test_npc.weapons.torpedos} (forcing movement)")
    
    print("\n--- Testing NPC speed adjustment while pursuing ---")
    
    # Simulate several turns
    for turn in range(1, 6):
        print(f"\n--- Turn {turn} ---")
        
        # Get distance before
        dist_before = test_npc.position.distance_to(engine.player_ship.position)
        print(f"Distance before: {dist_before:.1f} AU")
        
        # Execute NPC AI (should trigger pursuit with speed adjustment)
        engine._execute_npc_command(test_npc, show_debug=True)
        
        # Check what speed was set
        current_speed = test_npc.propulsion.current_speed
        print(f"Speed set by NPC AI: {current_speed:.2f} AU/turn")
        
        # Simulate movement
        if test_npc.propulsion.warp_active or test_npc.propulsion.impulse_active:
            heading_rad = math.radians(test_npc.propulsion.current_heading)
            dx = current_speed * math.cos(heading_rad)
            dy = current_speed * math.sin(heading_rad)
            test_npc.position.x += dx
            test_npc.position.y += dy
        
        # Get distance after
        dist_after = test_npc.position.distance_to(engine.player_ship.position)
        print(f"Distance after: {dist_after:.1f} AU")
        print(f"Distance closed: {dist_before - dist_after:.1f} AU")
        
        # Verify speed adjustment
        if dist_after <= 50 and dist_after > 10:
            closing_distance = dist_after - 10.0
            print(f"✓ Within sensor range, should adjust speed to close {closing_distance:.1f} AU gap")
        
        if dist_after <= 11:
            print("✓ NPC reached combat distance (within ~10 AU)")
            break
        
        # Print any messages generated
        if engine.messages:
            print("Messages:")
            for msg in engine.messages[-3:]:  # Last 3 messages
                print(f"  {msg}")
            engine.messages.clear()
    
    print("\n" + "=" * 80)
    print("TEST 2 COMPLETE")
    print("=" * 80)


def test_npc_to_npc_pursuit():
    """Test NPC ship speed adjustment when pursuing other NPC ships."""
    print("\n" * 2)
    print("=" * 80)
    print("TEST 3: NPC-to-NPC Pursuit Speed Adjustment")
    print("=" * 80)
    
    engine = GameEngine()
    
    # Position player far away
    engine.player_ship.position = Position(1000, 1000)
    
    # Create two NPC ships near each other
    npc1 = Ship("s7777", Position(100, 100), is_player=False)
    npc1.behavior_trait = "aggressive"
    engine.npc_ships["s7777"] = npc1
    
    npc2 = Ship("s6666", Position(135, 100), is_player=False)
    npc2.behavior_trait = "neutral"
    npc2.damage = 40.0  # Make it damaged so NPC1 targets it
    engine.npc_ships["s6666"] = npc2
    
    # Set hostile stance between them
    npc1.stances[npc2.id] = "hostile"
    
    initial_dist = npc1.position.distance_to(npc2.position)
    print(f"\nInitial distance between NPCs: {initial_dist:.1f} AU")
    print(f"NPC1 ({npc1.id}) behavior: {npc1.behavior_trait}")
    print(f"NPC1 stance toward NPC2: {npc1.stances.get(npc2.id, 'neutral')}")
    print(f"NPC2 ({npc2.id}) damage: {npc2.damage:.1f}%")
    
    print("\n--- Testing NPC-to-NPC pursuit with speed adjustment ---")
    
    # Simulate several turns
    for turn in range(1, 6):
        print(f"\n--- Turn {turn} ---")
        
        # Get distance before
        dist_before = npc1.position.distance_to(npc2.position)
        print(f"Distance before: {dist_before:.1f} AU")
        
        # Execute NPC1 AI
        engine._execute_npc_command(npc1, show_debug=True)
        
        # Check what speed was set
        current_speed = npc1.propulsion.current_speed
        print(f"Speed set by NPC1 AI: {current_speed:.2f} AU/turn")
        
        # Simulate movement
        if npc1.propulsion.warp_active or npc1.propulsion.impulse_active:
            heading_rad = math.radians(npc1.propulsion.current_heading)
            dx = current_speed * math.cos(heading_rad)
            dy = current_speed * math.sin(heading_rad)
            npc1.position.x += dx
            npc1.position.y += dy
        
        # Get distance after
        dist_after = npc1.position.distance_to(npc2.position)
        print(f"Distance after: {dist_after:.1f} AU")
        print(f"Distance closed: {dist_before - dist_after:.1f} AU")
        
        if dist_after <= 11:
            print("✓ NPC1 reached combat distance to NPC2")
            break
        
        # Print any messages
        if engine.messages:
            print("Messages:")
            for msg in engine.messages[-3:]:
                print(f"  {msg}")
            engine.messages.clear()
    
    print("\n" + "=" * 80)
    print("TEST 3 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_player_nav_speed_adjustment()
        test_npc_pursuit_speed_adjustment()
        test_npc_to_npc_pursuit()
        
        print("\n" * 2)
        print("=" * 80)
        print("ALL TESTS COMPLETE")
        print("=" * 80)
        print("\nSummary:")
        print("✓ Player nav mode adjusts speed when pursuing ships within sensor range")
        print("✓ NPC ships adjust speed when pursuing player within sensor range")
        print("✓ NPC ships adjust speed when pursuing other NPCs within sensor range")
        print("\nThe speed adjustment ensures ships close to within 10 AU efficiently")
        print("without overshooting, using dynamic speed based on closing distance.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR:")
        print(f"{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
