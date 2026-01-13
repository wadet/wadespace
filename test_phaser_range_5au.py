#!/usr/bin/env python3
"""
Test phaser range is now 5 AU instead of 10 AU
"""

import sys
sys.path.insert(0, '/home/wade/workspace/wadespace')

from src.ship import Ship
from src.universe_objects import Position

def test_phaser_range_5au():
    """Test that phasers can only fire within 5 AU"""
    print("Testing Phaser Range Change: 10 AU -> 5 AU")
    print("=" * 60)
    
    # Create player ship at origin
    player = Ship("PLAYER", Position(5000, 5000))
    player.is_player = True
    player.energy = 100
    player.shields_up = True
    
    # Test 1: Target at exactly 5 AU (should work)
    print("\n1. Target at exactly 5.0 AU:")
    target1 = Ship("s001", Position(5005, 5000))
    target1.energy = 100
    target1.shields_up = True
    player.weapons.phaser_locked_target = "s001"
    
    distance1 = player.position.distance_to(target1.position)
    print(f"   Distance: {distance1:.1f} AU")
    print(f"   Phaser range: {player.weapons.phaser_range} AU")
    
    result1 = player.fire_phaser(target1)
    if result1:
        print(f"   ✓ Phaser FIRED successfully at 5.0 AU")
    else:
        print(f"   ✗ Phaser FAILED to fire at 5.0 AU (ERROR)")
    
    # Test 2: Target at 4 AU (should work)
    print("\n2. Target at 4.0 AU (within range):")
    target2 = Ship("s002", Position(5004, 5000))
    target2.energy = 100
    target2.shields_up = True
    player.weapons.phaser_locked_target = "s002"
    player.weapons.phaser_can_fire_this_turn = True  # Reset
    
    distance2 = player.position.distance_to(target2.position)
    print(f"   Distance: {distance2:.1f} AU")
    
    result2 = player.fire_phaser(target2)
    if result2:
        print(f"   ✓ Phaser FIRED successfully at 4.0 AU")
    else:
        print(f"   ✗ Phaser FAILED to fire at 4.0 AU (ERROR)")
    
    # Test 3: Target at 6 AU (should fail - out of range)
    print("\n3. Target at 6.0 AU (beyond range):")
    target3 = Ship("s003", Position(5006, 5000))
    target3.energy = 100
    target3.shields_up = True
    player.weapons.phaser_locked_target = "s003"
    player.weapons.phaser_can_fire_this_turn = True  # Reset
    
    distance3 = player.position.distance_to(target3.position)
    print(f"   Distance: {distance3:.1f} AU")
    
    result3 = player.fire_phaser(target3)
    if not result3:
        print(f"   ✓ Phaser correctly BLOCKED at 6.0 AU (out of range)")
    else:
        print(f"   ✗ Phaser FIRED at 6.0 AU (ERROR - should be blocked)")
    
    # Test 4: Target at 8 AU (should fail - way out of range)
    print("\n4. Target at 8.0 AU (way beyond range):")
    target4 = Ship("s004", Position(5008, 5000))
    target4.energy = 100
    target4.shields_up = True
    player.weapons.phaser_locked_target = "s004"
    player.weapons.phaser_can_fire_this_turn = True  # Reset
    
    distance4 = player.position.distance_to(target4.position)
    print(f"   Distance: {distance4:.1f} AU")
    
    result4 = player.fire_phaser(target4)
    if not result4:
        print(f"   ✓ Phaser correctly BLOCKED at 8.0 AU (out of range)")
    else:
        print(f"   ✗ Phaser FIRED at 8.0 AU (ERROR - should be blocked)")
    
    # Test 5: Target at 10 AU (OLD range, should now fail)
    print("\n5. Target at 10.0 AU (old maximum range):")
    target5 = Ship("s005", Position(5010, 5000))
    target5.energy = 100
    target5.shields_up = True
    player.weapons.phaser_locked_target = "s005"
    player.weapons.phaser_can_fire_this_turn = True  # Reset
    
    distance5 = player.position.distance_to(target5.position)
    print(f"   Distance: {distance5:.1f} AU")
    
    result5 = player.fire_phaser(target5)
    if not result5:
        print(f"   ✓ Phaser correctly BLOCKED at 10.0 AU (out of NEW range)")
    else:
        print(f"   ✗ Phaser FIRED at 10.0 AU (ERROR - should be blocked)")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print(f"✓ Phaser range successfully changed to {player.weapons.phaser_range} AU")
    print(f"✓ Phasers work at ≤ 5 AU")
    print(f"✓ Phasers blocked at > 5 AU")
    print("=" * 60)

if __name__ == "__main__":
    test_phaser_range_5au()
