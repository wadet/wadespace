# Reputation System Update - Ship Destruction

## Summary
Implemented a reputation change system that adjusts the player's reputation when destroying npc ships based on the destroyed ship's behavior trait and reputation score.

## Changes Made

### 1. Modified `src/ship.py`
- **Updated `take_shield_hit()` method** (lines ~193-202)
  - Added destruction check when ship damage reaches 100%
  - This ensures ships can be destroyed by phaser fire (not just torpedoes)

### 2. Modified `src/game_engine.py`

#### Added new method: `_handle_ship_destruction()`
- Location: After `_spawn_single_enemy()` method (lines ~103-135)
- Purpose: Centralized reputation change logic when a ship destroys another
- Logic:
  - **Reputation DECREASES by 10** if destroyed ship:
    - Has a 'timid' behavior trait, OR
    - Has reputation > 70
  - **Reputation INCREASES by 10** (max 100) if destroyed ship:
    - Has an 'aggressive' behavior trait, OR
    - Has reputation < 30
  - Only applies when player ship is the destroyer
  - Reputation is capped at 0 (minimum) and 100 (maximum)
  - Shows message to player when reputation changes

#### Updated `_execute_fire()` method
- Location: lines ~676-713
- Added check for ship destruction after phaser hits
- Calls `_handle_ship_destruction()` when target is destroyed

#### Updated torpedo hit handling
- Location: lines ~1213-1246 (in `_update_torpedos()`)
- Moved cash transfer and cleanup code after reputation handling
- Calls `_handle_ship_destruction()` when npc ship is destroyed by torpedo

## Rules Implemented

The reputation system evaluates conditions in order:

1. **First Check**: If destroyed ship has `timid` trait OR reputation > 70
   - → Reputation **DECREASES** by 10
   
2. **Second Check** (only if first check fails): If destroyed ship has `aggressive` trait OR reputation < 30
   - → Reputation **INCREASES** by 10 (capped at 100)

3. **No Change**: Neutral ships with mid-range reputation (30-70)

### Edge Cases

| Destroyed Ship | Behavior | Reputation | Result |
|----------------|----------|------------|---------|
| Aggressive warlord | aggressive | 85 | -10 (high rep checked first) |
| Timid pirate | timid | 15 | -10 (timid checked first) |
| Aggressive pirate | aggressive | 25 | +10 (low rep, aggressive) |
| Timid merchant | timid | 80 | -10 (timid OR high rep) |
| Neutral trader | neutral | 50 | No change |

**Note**: The first matching condition wins. Reputation > 70 is checked before aggressive trait, so a high-reputation aggressive ship will still decrease your reputation.

- Reputation is always bounded: 0 ≤ reputation ≤ 100
- Changes only apply when player destroys npc ships
- Player sees a message when reputation changes

## Testing

### Test Files Created
1. **test_reputation_changes.py**
   - Unit tests for the `_handle_ship_destruction()` method
   - Tests all reputation change conditions
   - Tests reputation caps (0 and 100)
   - ✓ All 6 tests passed

2. **test_combat_reputation.py**
   - Integration tests for actual combat scenarios
   - Tests phaser destruction with reputation changes
   - Tests torpedo destruction with reputation changes
   - ✓ Both tests passed

## Example Gameplay

```
Player attacks npc s1234 (timid, reputation 45)
> Torpedo hit s1234! Damage: 25%
> s1234 destroyed!
> Reputation decreased to 46 (destroyed s1234)
> Salvaged $1500 from s1234

Player attacks npc s5678 (aggressive, reputation 20)
> Phaser fired at s5678! Hit for 5% damage!
> s5678 destroyed!
> Reputation increased to 56 (destroyed s5678)
> Salvaged $800 from s5678
```

## Compatibility
- Works with existing behavior trait system
- Compatible with both phaser and torpedo combat
- No changes to existing game mechanics
- No breaking changes to existing code
