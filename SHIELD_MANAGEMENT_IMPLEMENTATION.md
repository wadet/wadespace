# Shield Management Implementation

## Overview
Implemented automatic shield management for NPC ships and starbases to raise shields when under attack and lower them when safe to conserve energy.

## Changes Made

### 1. Starbase Class Updates (`src/universe_objects.py`)
- **Added `shields_active` field**: Starbases now track whether their shields are active (defaults to `False`)
- **Added `fired_upon_by` tracking**: Set to track which ships have fired upon the starbase
- **Added damage handling methods**:
  - `take_damage(damage, bypass_shields)`: Properly handles shield absorption and hull damage
  - `take_shield_hit(damage)`: Handles phaser hits to shields or hull
  - Updated `update()` to consume energy (2% per turn) when shields are active

### 2. Shield Management Functions (`src/game_engine.py`)

#### `_manage_npc_shields(ship)`
Automatically manages NPC ship shields based on combat status:
- **Raises shields when**:
  - Under attack (`fired_upon_by` not empty)
  - Has sufficient energy (> 10%)
- **Lowers shields when**:
  - Not under attack and safe
  - Fleeing with low energy (< 30%) to conserve power for warp drive
  - Energy is critical (< 10%)

#### `_manage_starbase_shields(starbase)`
Automatically manages starbase shields based on nearby threats:
- **Raises shields when**:
  - Hostile ships within defense range (10 AU)
  - Fired upon
  - Has sufficient energy (> 10%)
- **Lowers shields when**:
  - No threats nearby
  - Not under attack

### 3. LLM Integration Updates (`src/llm_handler.py`)
- **Added `npc_shields_active` parameter** to `get_npc_decision()` method
- **Updated decision prompt** to include shield status and inform the AI that shields are automatically managed
- **Added shield information** to the tactical context shown to the AI

### 4. Game Loop Integration (`src/game_engine.py`)
- **NPC command execution**: Added call to `_manage_npc_shields()` before executing NPC AI decisions
- **Starbase actions**: Added call to `_manage_starbase_shields()` during starbase action processing
- **Enhanced weapon targeting**: 
  - Phasers can now target starbases
  - Torpedoes properly track `fired_upon_by` for starbases
  - Both weapons properly handle starbase shields

### 5. Weapon Enhancements (`src/game_engine.py`)

#### Phaser Targeting
- Extended `_execute_fire()` to allow targeting starbases
- Properly tracks `fired_upon_by` when firing at starbases
- Handles shield absorption for starbases

#### Torpedo Impact
- Enhanced torpedo hit detection to track `fired_upon_by` for starbases
- Properly applies shield damage (20%) and hull damage (10%) to starbases
- Shows appropriate damage messages

## Behavior Summary

### NPC Ships
1. **Start with shields DOWN** to conserve energy
2. **Raise shields immediately** when attacked
3. **Lower shields** when safe and not under attack
4. **When fleeing with low energy** (< 30%), lower shields to conserve power for warp drive

### Starbases
1. **Start with shields DOWN** to conserve energy
2. **Raise shields** when hostile ships enter defense range (10 AU)
3. **Raise shields** when fired upon
4. **Lower shields** when no threats nearby and not under attack

### Energy Considerations
- Shields consume **2% energy per turn** when active (both ships and starbases)
- NPCs intelligently balance shield usage with other energy needs (warp drive, weapons)
- When fleeing with low energy, NPCs prioritize warp drive over shields

## Testing

Created `test_shield_management.py` with three comprehensive tests:

1. **NPC Shield Raising**: ✅ Verified NPC ships raise shields when attacked
2. **Starbase Shield Raising**: ✅ Verified starbases raise shields when hostile ships nearby
3. **Shield Lowering When Safe**: ✅ Verified NPCs lower shields when threats are gone

All tests pass consistently, confirming the shield management system works as designed.

## Benefits

1. **More realistic combat**: NPCs and starbases now defend themselves appropriately
2. **Better AI strategy**: NPCs balance energy consumption between shields, weapons, and propulsion
3. **Dynamic gameplay**: Players face more challenging opponents who adapt their defenses
4. **Energy management**: NPCs make smart decisions about when to conserve energy
5. **Fleeing behavior**: NPCs fleeing at low energy will sacrifice shields to maintain speed

## Files Modified

- `src/universe_objects.py` - Enhanced Starbase class
- `src/game_engine.py` - Added shield management functions and enhanced weapon targeting
- `src/llm_handler.py` - Updated AI prompts and decision parameters
- `test_shield_management.py` - New comprehensive test suite (created)

## Notes

- Shield management is **automatic** and happens before AI decision-making each turn
- The LLM AI is informed that shields are automatically managed
- Players will now encounter NPCs with shields up when in combat
- Starbases are now more formidable opponents with active shield defense
