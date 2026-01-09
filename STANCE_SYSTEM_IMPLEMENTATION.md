# Stance System Implementation - Complete

## Overview
The stance system has been successfully implemented in Wade Space. Each NPC ship and starbase now tracks their stance toward other NPC ships (including the player). The three possible stances are: **hostile**, **neutral**, and **friendly**.

## Implementation Summary

### 1. **Data Structures Added**

#### Ship Class (`src/ship.py`)
- Added `stances: Dict[str, str]` attribute to track stance toward other ships
- Only populated for NPC ships (player ship has empty dict)
- Keys: ship/starbase IDs, Values: 'hostile', 'neutral', or 'friendly'

#### Starbase Class (`src/universe_objects.py`)
- Added `stances: Dict[str, str]` attribute to track stance toward ships
- Keys: ship IDs, Values: 'hostile', 'neutral', or 'friendly'

### 2. **Initialization**

#### Game Engine (`src/game_engine.py`)
- Added `_initialize_stances()` method called after NPC ship creation
- Added `_initialize_npc_stance(npc_ship)` method to set random stances for individual NPCs
- Added `_initialize_starbase_stance(starbase)` method to set random stances for starbases
- Stances are randomly assigned at game start with equal probability (33% each)
- When new NPCs spawn, their stances are initialized via `_spawn_single_npc()`

### 3. **UI Color Rendering**

#### UI System (`src/ui.py`)
Color-coded based on stance toward player:
- **Hostile** = RED
- **Neutral** = YELLOW  
- **Friendly** = GREEN

Updated rendering locations:
- **2D Map NPC Ships**: Bird of Prey ship shapes colored by stance
- **2D Map Starbases**: Square shapes colored by stance
- **Minimap NPC Ships**: Triangles colored by stance
- **Minimap Starbases**: Small squares colored by stance

### 4. **Game Mechanics**

#### NPC Ship Behavior (`src/game_engine.py`)
- Modified `_execute_basic_npc_ai()` to consider stance when selecting targets
- Priority 1: Attack hostile targets (based on stance)
- Priority 2: Consider behavior trait and ship condition
- Hostile NPCs will attack:
  - If stance toward target is 'hostile' AND ship is healthy enough
  - Based on behavior trait (aggressive, neutral, timid) and ship damage
- Friendly stance prevents attacks between ships
- Neutral stance allows opportunistic attacks based on behavior

#### Starbase Behavior (`src/game_engine.py`)
- Added `_process_starbase_actions()` method called each turn
- Starbases attack ships when:
  - Stance toward ship is 'hostile'
  - Ship is within defense range (10 AU)
  - Starbase is healthy (damage < 70%)
- Starbase weapons:
  - **Phasers**: 10% damage (more powerful than ship phasers)
  - **Torpedoes**: 15% damage (instant hit, no travel time)
- Added `_starbase_fire_phaser()` and `_starbase_fire_torpedo()` methods

### 5. **Attack Logic Details**

NPCs now consider:
1. **Stance** (primary factor)
   - Hostile stance = high attack priority
   - Friendly stance = no attacks
   - Neutral stance = behavior-based decisions

2. **Behavior Trait** (secondary factor)
   - Aggressive: Attack hostile targets readily, flee if damage > 80%
   - Neutral: Attack hostile targets or if provoked, flee if damage > 50%
   - Timid: Attack hostile targets or if heavily provoked, flee if damage > 30%

3. **Ship Condition** (tertiary factor)
   - High damage = more likely to flee
   - Healthy = more likely to attack

## Testing

### Test Results
All tests passed successfully:

✅ **Stance Initialization**
- NPC ships track 50 stances (49 other NPCs + player)
- Starbases track 51 stances (50 NPCs + player)
- Player ship has empty stance dict

✅ **Stance Distribution**
- Random distribution approximately 33% each
- Test showed: 26-40% hostile, 34-41% neutral, 33-40% friendly

✅ **Hostile Behavior**
- Hostile starbases attack ships in range
- Test: 9 attacks in 10 turns when player within 7.1 AU
- NPCs attack each other based on hostile stance
- Test: Multiple NPC-to-NPC combat events observed

✅ **Color Coding**
- UI correctly displays stance colors
- Hostile entities appear RED
- Neutral entities appear YELLOW
- Friendly entities appear GREEN

### Test Scripts
- `test_stance_system.py` - Comprehensive initialization and color tests
- `test_stance_combat.py` - Combat behavior verification

## Files Modified

1. **src/ship.py**
   - Added `stances` attribute
   - Added `Dict` import

2. **src/universe_objects.py**
   - Added `stances` attribute to Starbase
   - Added `Dict` import

3. **src/game_engine.py**
   - Added stance initialization methods
   - Modified NPC AI to consider stances
   - Added starbase attack processing
   - Fixed nearby_enemies tuple unpacking

4. **src/ui.py**
   - Updated NPC ship rendering colors (2D map and minimap)
   - Updated starbase rendering colors (2D map and minimap)
   - Changed from hardcoded red/green to stance-based colors

## Backward Compatibility

The implementation maintains backward compatibility:
- Removed dependency on `friendly_to_player` attribute (deprecated but not deleted)
- Stance system is the new primary indicator of relationships
- All existing game mechanics continue to work

## Future Enhancements (Optional)

Potential future improvements:
1. Dynamic stance changes based on player actions
2. Reputation affecting initial stance probability
3. Alliances between friendly NPCs
4. Stance information in sensor scans
5. Diplomatic commands to improve/worsen stance

## Summary

The stance system is **fully implemented and tested**. All requested features are working:
- ✅ NPC ships and starbases track stances toward all ships
- ✅ Stances randomly initialized at game start
- ✅ UI colors reflect stance (hostile=RED, neutral=YELLOW, friendly=GREEN)
- ✅ Hostile NPCs attack based on stance and behavior
- ✅ Hostile starbases attack based on stance and health
- ✅ Shape representations unchanged (only colors changed)
