# System Damage Implementation

## Overview
Implemented a comprehensive system damage mechanic where ships can suffer critical system failures when heavily damaged (>50% damage). This adds strategic depth and consequences to combat, forcing players to be more cautious when their ship is damaged.

## Mechanics

### System Damage Triggering
- **Trigger Condition**: When a ship has >50% damage and takes additional damage
- **Chance**: 25% chance per damage instance
- **Systems**: One of seven major systems can be disabled randomly:
  1. **Shields** - Shield generators
  2. **Engines** - Propulsion systems (warp/impulse)
  3. **Torpedoes** - Torpedo launchers
  4. **Phasers** - Phaser banks
  5. **Scanners** - Sensor arrays
  6. **Radios** - Communication systems
  7. **Computers** - Navigation and targeting computers

### System Effects

#### 1. Shields Disabled
- Shields become ineffective and are automatically lowered
- Cannot be raised until repaired
- All damage bypasses shields and goes directly to hull
- **Message**: ">>> CRITICAL: Shield system disabled due to severe damage! <<<"
- **Attempted Use**: "Shields are inoperative due to damage to the ship"

#### 2. Engines Disabled
- Ship immediately comes to a full stop
- Cannot use warp or impulse drives
- Ship remains stationary until engines are repaired
- **Message**: ">>> CRITICAL: Engine system disabled due to severe damage! <<<"
- **Attempted Use**: "Engines are inoperative due to damage to the ship"

#### 3. Torpedoes Disabled
- Cannot fire torpedoes
- Existing torpedo inventory is preserved
- **Message**: ">>> CRITICAL: Torpedo system disabled due to severe damage! <<<"
- **Attempted Use**: "Torpedoes are inoperative due to damage to the ship"

#### 4. Phasers Disabled
- Cannot fire phasers
- Weapon locks can still be maintained
- **Message**: ">>> CRITICAL: Phaser system disabled due to severe damage! <<<"
- **Attempted Use**: "Phasers are inoperative due to damage to the ship"

#### 5. Scanners Disabled
- Objects no longer appear on 2D map
- Map displays: "Scanners are inoperative due to damage" (centered in red)
- Player ship still visible on map
- **Message**: ">>> CRITICAL: Scanner system disabled due to severe damage! <<<"
- **Attempted Use**: "Scanners are inoperative due to damage to the ship"

#### 6. Radios Disabled
- `tell` command becomes inoperative
- Cannot send or receive messages from other ships/starbases
- **Message**: ">>> CRITICAL: Radio system disabled due to severe damage! <<<"
- **Attempted Use**: "Radios are inoperative due to damage to the ship"

#### 7. Computers Disabled
- `hal`, `targets`, `lock`, and `nav` commands become inoperative
- Existing weapon lock is cleared
- Auto-navigation is cancelled (ship continues on current heading/speed)
- **Message**: ">>> CRITICAL: Computer system disabled due to severe damage! <<<"
- **Attempted Use**: "Computers are inoperative due to damage to the ship"

### System Repair

#### Repair Mechanics
- **Automatic Repair**: Occurs at the end of each turn
- **Repair Rate**:
  - **Damage ≥ 50%**: 25% chance per turn
  - **Damage < 50%**: 50% chance per turn
- **Limitation**: Only ONE system can be repaired per turn
- **Selection**: Random system chosen from disabled systems
- **Notification**: ">> System repair: [SYSTEM] system is now operational <<"

#### Repair Priority
- No priority system - repairs are random
- All disabled systems have equal chance of being repaired
- Strategic consideration: Reduce ship damage below 50% for faster repairs

## Implementation Details

### Code Changes

#### 1. Ship Class (`src/ship.py`)
- **Added**: `disabled_systems` - set tracking disabled systems
- **Added**: `check_for_system_damage(messages)` - checks and disables systems
- **Added**: `attempt_system_repair(messages)` - attempts to repair one system per turn
- **Modified**: `take_damage()` - added system damage checks
- **Modified**: `take_shield_hit()` - added system damage checks
- **Modified**: `can_move()` - checks for disabled engines
- **Modified**: `can_fire_weapons()` - checks for disabled weapons
- **Modified**: `update_shields()` - prevents shield activation if disabled
- **Modified**: `fire_phaser()` - blocks if phasers disabled
- **Modified**: `fire_torpedo()` - blocks if torpedoes disabled
- **Modified**: `get_status_dict()` - includes disabled_systems list

#### 2. Game Engine (`src/game_engine.py`)
- **Modified**: `_update_ship()` - calls `attempt_system_repair()` each turn
- **Modified**: `_update_ship()` - checks engines before allowing movement
- **Added checks** to commands:
  - `warp` - checks engines
  - `impulse` - checks engines
  - `shields` - checks shields
  - `scan` - checks scanners
  - `lock` - checks computers
  - `fire` - checks phasers
  - `torpedo` - checks torpedoes
  - `nav` - checks computers
  - `tell` - checks radios
  - `hal` - checks computers
  - `targets` - checks computers

#### 3. UI (`src/ui.py`)
- **Modified**: `_draw_2d_map()` - displays "Scanners inoperative" message when scanners disabled

### Testing
Comprehensive test suite created in `test_system_damage.py`:
- System damage triggering (>50% damage required)
- All seven systems can be disabled
- Repair rate verification (25% at high damage, 50% at low damage)
- System-specific effects verification
- Command blocking verification
- One-system-per-turn repair limitation

All tests pass successfully.

## Strategic Implications

### Combat Considerations
1. **Damage Threshold**: Ships become vulnerable to system failures at 50% damage
2. **Cascading Failures**: Multiple systems can fail over time if damage isn't repaired
3. **Retreat Decisions**: Damaged ships should consider retreating before system failures
4. **Repair Priority**: Getting damage below 50% doubles repair chance

### Player Tactics
- Monitor damage levels closely
- Retreat and repair when approaching 50% damage
- Prioritize defensive play when multiple systems are disabled
- Use starbases for repairs to restore systems faster

### NPC Behavior
- NPC ships are subject to the same system damage mechanics
- Disabled NPC ships may become easier targets (can't move, fire, etc.)
- Adds unpredictability to combat encounters

## Future Enhancements (Potential)
- Targeted system damage (specific hits to specific systems)
- Repair prioritization (manual selection of which system to repair)
- Repair effectiveness based on crew level
- Starbase repairs that fix all systems immediately
- Engineering crew skill affecting repair rates
- System redundancy (backup systems)

## Compatibility
- Fully compatible with existing game mechanics
- No breaking changes to existing save data
- Works seamlessly with NPC AI and LLM decision-making
- Integrates with existing damage and repair systems

## Known Limitations
- System repairs are random (no player control over which system repairs first)
- No visual indicators for disabled systems (except scanner message on map)
- Status panel doesn't yet show which systems are disabled
- No audio/visual effects for system failures

## Testing Recommendations
1. Test in combat scenarios with >50% damage
2. Verify all seven systems can be disabled
3. Test repair rates at different damage levels
4. Verify command restrictions work correctly
5. Test scanner disable effect on 2D map
6. Verify NPC ships handle system damage correctly
