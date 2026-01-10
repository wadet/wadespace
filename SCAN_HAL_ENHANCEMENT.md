# Scan and HAL Command Enhancement - Stance and Behavior Display

## Overview

Enhanced the `scan` and `hal` commands to display object stance towards the player and captain behavior traits in all query results.

## Changes Made

### 1. Scan Command - General Scan (No Target Specified)

**Location**: [game_engine.py](src/game_engine.py#L1001-L1021)

**Change**: Modified the nearby objects display to include stance and behavior information in brackets.

**Before**:
```
Scan results (sensor range: 50 AU):
  s4375: SHIP @ 10.0 AU
  sb2707: ⊕ @ 21.2 AU
```

**After**:
```
Scan results (sensor range: 50 AU):
  s4375: SHIP @ 10.0 AU [hostile, aggressive]
  sb2707: ⊕ @ 21.2 AU [friendly]
```

**Implementation**:
- Added logic to check if object is a Ship or Starbase
- For ships: Display `[stance, behavior_trait]`
- For starbases: Display `[stance]`
- Format: Appended to the end of each line as `extra_info`

### 2. Scan Command - Specific Target

**Location**: [game_engine.py](src/game_engine.py#L976-L987)

**Change**: Added stance as a separate field in detailed ship scan results.

**Before**:
```
Scan of s4375: Ship at 10.0 AU
  Status: operational, Damage: 0.0%, Energy: 100.0%
  Shields: down (100.0%), Crew: 1000, Behavior: aggressive
  Speed: 0.0 AU/turn, Heading: 0°
```

**After**:
```
Scan of s4375: Ship at 10.0 AU
  Status: operational, Damage: 0.0%, Energy: 100.0%
  Shields: down (100.0%), Crew: 1000, Behavior: aggressive
  Speed: 0.0 AU/turn, Heading: 0°
  Stance: hostile
```

**Implementation**:
- Retrieve stance using `target_obj.stances.get(ship.id, 'neutral')`
- Add as a new line: `Stance: {stance}`
- Behavior trait was already being displayed (no change needed)

### 3. HAL Command - Object Info Query

**Location**: [game_engine.py](src/game_engine.py#L1514-L1547)

**Changes**:

#### For NPC Ships:
- Added behavior trait to header line
- Added stance as a separate field

**Before**:
```
Enemy ship s8977:
  Location: (5020.0, 5020.0)
  Distance from you: 28.3 AU
  Health: 100.0%
  Shields: 100.0%
  Status: ACTIVE
```

**After**:
```
Enemy ship s8977 (timid):
  Location: (5020.0, 5020.0)
  Distance from you: 28.3 AU
  Health: 100.0%
  Shields: 100.0%
  Status: ACTIVE
  Stance: friendly
```

#### For Starbases:
- Added stance as a separate field

**Before**:
```
Object sb2815 (⊕):
  Type: Starbase
  Location: (5035.0, 4980.0)
  Distance from you: 40.3 AU
```

**After**:
```
Object sb2815 (⊕):
  Type: Starbase
  Location: (5035.0, 4980.0)
  Distance from you: 40.3 AU
  Stance: hostile
```

### 4. LLM Universe Data

**Location**: [game_engine.py](src/game_engine.py#L1590-L1602)

**Change**: Added `behavior_trait` field to NPC ship data sent to LLM for natural language queries.

**Implementation**:
```python
npc_ships_data[npc_id] = {
    'position': (npc_ship.position.x, npc_ship.position.y),
    'distance': distance,
    'damage': npc_ship.damage,
    'shields': npc_ship.shields,
    'energy': npc_ship.energy,
    'is_destroyed': npc_ship.is_destroyed,
    'stance_to_player': stance_to_player,
    'behavior_trait': npc_ship.behavior_trait if npc_ship.behavior_trait else 'neutral'  # NEW
}
```

This allows the LLM to provide more context-aware answers when players ask questions about NPCs.

## Files Modified

1. [src/game_engine.py](src/game_engine.py) - Added stance and behavior display logic to:
   - `_execute_scan()` method (lines ~973-1021)
   - `_query_object_info()` method (lines ~1514-1547)
   - `_get_universe_data_for_llm()` method (lines ~1590-1602)

## Test Files Created

1. **[test_scan_stance_behavior.py](test_scan_stance_behavior.py)**
   - Automated test suite verifying all changes
   - Tests general scan, specific scan, and HAL queries
   - Validates stance and behavior appear correctly

2. **[demo_scan_enhancements.py](demo_scan_enhancements.py)**
   - Interactive demonstration of the enhancements
   - Shows practical use cases and benefits
   - Includes tactical analysis scenarios

## Benefits

### For Players

1. **Quick Threat Assessment**
   - Instantly see if a ship/starbase is hostile, friendly, or neutral
   - Understand captain behavior (aggressive/timid/neutral)
   - Make informed tactical decisions

2. **Combat Planning**
   - Identify which enemies are most dangerous (hostile + aggressive)
   - Know which enemies might flee (timid behavior)
   - Prioritize targets based on stance and behavior

3. **Strategic Navigation**
   - Locate friendly starbases for repairs
   - Avoid hostile territory
   - Find neutral trading partners

### For Gameplay

1. **More Immersive**
   - Richer information in standard commands
   - Better understanding of the game world
   - More strategic depth

2. **Consistent Information Display**
   - Stance and behavior shown in all relevant commands
   - Same information format across scan and HAL queries
   - Predictable and learnable interface

## Usage Examples

### General Scan
```
> scan

Scan results (sensor range: 50 AU):
  s1569: SHIP @ 8.0 AU [hostile, aggressive]  ← Dangerous!
  sb6171: ⊕ @ 25.5 AU [friendly]              ← Safe harbor
  s6805: SHIP @ 26.9 AU [neutral, neutral]    ← Cautious approach
```

### Specific Ship Scan
```
> scan s1569

Scan of s1569: Ship at 8.0 AU
  Status: operational, Damage: 0.0%, Energy: 100.0%
  Shields: down (100.0%), Crew: 1000, Behavior: aggressive
  Speed: 0.0 AU/turn, Heading: 0°
  Stance: hostile                              ← Clear threat indicator
```

### HAL Query
```
> hal what is s6805

Enemy ship s6805 (neutral):                    ← Behavior in header
  Location: (6025.0, 5990.0)
  Distance from you: 26.9 AU
  Health: 100.0%
  Shields: 100.0%
  Status: ACTIVE
  Stance: neutral                              ← Stance as field
```

## Technical Details

### Stance Values
- `hostile` - Object will attack player
- `friendly` - Object will not attack player
- `neutral` - Object's behavior is cautious/neutral

### Behavior Trait Values (Ships Only)
- `aggressive` - Attacks readily, fights until heavily damaged
- `timid` - Avoids combat, flees when damaged
- `neutral` - Balanced behavior, standard tactics

### Starbases
- Starbases have stance but no behavior trait
- Hostile starbases will fire on player ships
- Friendly starbases offer repairs and supplies
- Neutral starbases may offer trading opportunities

## Backward Compatibility

All changes are additive - no existing functionality was removed:
- All previous scan command formats still work
- HAL queries function as before with additional information
- No breaking changes to game mechanics or commands

## Testing

Run the test suite:
```bash
python test_scan_stance_behavior.py
```

Run the interactive demo:
```bash
python demo_scan_enhancements.py
```

## Future Enhancements

Potential future improvements:
1. Color-code stance information in UI
2. Add stance/behavior filters to scan command
3. Display stance changes in real-time during combat
4. Show historical stance changes in ship logs
5. Add reputation system that affects starting stances

---

**Implementation Date**: January 9, 2026  
**Status**: ✅ Complete and Tested  
**Impact**: High - Improves player situational awareness significantly
