# NPC System Damage Notifications

## Overview
When NPC ships suffer system damage during combat, the player will be notified **if their scanners are operational**. This provides tactical awareness of enemy ship status.

## Feature Details

### Notification Format
```
[SCAN] {npc_id}'s {SYSTEM} system has been disabled!
```

Examples:
- `[SCAN] s9635's COMPUTERS system has been disabled!`
- `[SCAN] e2104's ENGINES system has been disabled!`
- `[SCAN] Starbase-1's SHIELDS system has been disabled!`

### Requirements
- Player's scanners must be operational (not disabled)
- NPC ship must take damage that triggers system failure
- NPC ship must have >50% damage for system failures to occur

### When Notifications Appear
Notifications appear whenever an NPC's system is disabled due to:
1. **Player phaser fire** - When player fires phasers at NPCs
2. **Player torpedo hits** - When player torpedoes strike NPCs
3. **Starbase weapons** - When starbases fire at NPCs
4. **NPC-on-NPC combat** - When NPCs fight each other

### Implementation Details

#### Helper Method
```python
def _check_npc_system_damage(self, npc_ship, npc_id, systems_before):
    """Check if NPC ship has new disabled systems and notify player if scanners work"""
    # Early return if player scanners disabled
    if 'scanners' in self.player_ship.disabled_systems:
        return
    
    # Compare system states
    new_disabled = npc_ship.disabled_systems - systems_before
    
    # Notify for each newly disabled system
    for system in new_disabled:
        self.messages.append(f"[SCAN] {npc_id}'s {system.upper()} system has been disabled!")
```

#### Integration Points
The helper method is called after damage is applied at:
- `_execute_fire()` - Player phaser fire
- `_starbase_fire_phaser()` - Starbase phaser fire
- `_starbase_fire_torpedo()` - Starbase torpedo fire
- Player torpedo hit code (line ~2676)
- NPC torpedo hit code (line ~2819)

Each location tracks `systems_before = set(npc_ship.disabled_systems)` before damage, then calls `_check_npc_system_damage()` after damage messages.

## Testing

### Test File
`test_npc_system_damage_notifications.py`

### Test Coverage
1. **Notifications with operational scanners**
   - Verifies notifications appear when player scanners work
   - Confirms correct message format with [SCAN] prefix

2. **No notifications with disabled scanners**
   - Verifies no notifications when player scanners disabled
   - Confirms NPC systems can still be damaged without notification

### Test Results
```
✓ Test 1 (Notifications with operational scanners): PASSED
✓ Test 2 (No notifications with disabled scanners): PASSED
```

## Tactical Benefits

### For Players
- **Situational awareness**: Know when enemy ships lose capabilities
- **Target prioritization**: Focus on ships with disabled shields or engines
- **Escape opportunities**: Identify when pursuers lose engine power
- **Weapon efficiency**: See when enemies lose shield regeneration

### System-Specific Tactical Value
- **SHIELDS disabled**: Enemy vulnerable to hull damage
- **ENGINES disabled**: Enemy cannot maneuver or flee
- **TORPEDOES disabled**: Enemy has reduced offensive capability
- **PHASERS disabled**: Enemy has no rapid-fire weapons
- **SCANNERS disabled**: Enemy has limited tactical awareness
- **RADIOS disabled**: Enemy cannot communicate (limited impact)
- **COMPUTERS disabled**: Enemy targeting less accurate

## Usage Example

```
> fire
Phaser fired at s9635! Hit for 10.3% ship damage!
[SCAN] s9635's COMPUTERS system has been disabled!

> fire
Phaser fired at s9635! Hit for 8.7% ship damage!

> fire
Phaser fired at s9635! Hit for 12.1% ship damage!
[SCAN] s9635's ENGINES system has been disabled!

# Enemy ship now has no engines and degraded targeting
```

## Related Systems
- System damage mechanics (SYSTEM_DAMAGE_IMPLEMENTATION.md)
- Scanner functionality
- Combat reputation system
- NPC AI behaviors

## Future Enhancements
Potential improvements:
1. Scanner quality levels (basic/advanced) affecting notification detail
2. Notification range limits based on scanner type
3. Delay in notifications based on distance
4. Probabilistic detection based on scanner damage level
5. Starbase system status if in range
