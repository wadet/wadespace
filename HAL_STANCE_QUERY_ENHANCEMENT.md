# HAL Command Stance-Based Query Enhancement

## Overview

The `hal` command now understands stance-based natural language queries, allowing players to ask about objects based on their stance relationship to the player.

## Changes Made

### 1. Enhanced Query Methods

#### `_query_nearest_npc()`
- Added optional `stance_filter` parameter
- Filters NPC ships by their stance towards the player
- Shows stance information in results

#### `_query_nearest_object()`
- Added optional `stance_filter` parameter
- Applies stance filtering when querying starbases
- Shows stance information for starbases in results

### 2. Updated LLM Universe Data

#### `_get_universe_data_for_llm()`
- NPC ship data now includes `stance_to_player` field
- Starbase data now includes `stance_to_player` field
- Allows LLM to understand and filter by stance relationships

### 3. Enhanced Pattern Matching

#### `_execute_hal()`
- Detects stance keywords in queries:
  - `enemy`/`enemies`/`hostile` → filters for hostile stance
  - `friendly`/`friend`/`allies` → filters for friendly stance
  - `neutral` → filters for neutral stance
- Reordered pattern matching to check starbase queries before general NPC queries
- Passes stance filter to query methods

## Supported Query Examples

### Enemy/Hostile Queries
```
hal nearest enemy
hal closest hostile ship
hal nearest enemy starbase
hal hostile base nearby
```

### Friendly Queries
```
hal nearest friendly ship
hal closest friendly base
hal friendly starbase
hal find allies
```

### Neutral Queries
```
hal nearest neutral npc
hal closest neutral ship
hal neutral starbase
```

### General Queries (No Filter)
```
hal nearest npc
hal nearest starbase
```
Shows nearest object regardless of stance and includes stance information.

## API Changes Summary

### Method Signatures

**Before:**
```python
def _query_nearest_npc(self, ship: Ship) -> None:
def _query_nearest_object(self, ship: Ship, prefix: str, obj_name: str) -> None:
```

**After:**
```python
def _query_nearest_npc(self, ship: Ship, stance_filter: Optional[str] = None) -> None:
def _query_nearest_object(self, ship: Ship, prefix: str, obj_name: str, stance_filter: Optional[str] = None) -> None:
```

### Data Structure Changes

**NPC Ships LLM Data:**
```python
{
    'position': (x, y),
    'distance': distance,
    'damage': damage,
    'shields': shields,
    'energy': energy,
    'is_destroyed': is_destroyed,
    'stance_to_player': stance  # NEW
}
```

**Starbase LLM Data:**
```python
{
    'type': 'Starbase',
    'position': (x, y),
    'distance': distance,
    'friendly': friendly_to_player,
    'stance_to_player': stance  # NEW
}
```

## Implementation Details

### Stance Detection
The hal command detects stance keywords in the query and sets a stance filter:
- Checks for `enemy`, `enemies`, `hostile` → `stance_filter = 'hostile'`
- Checks for `friendly`, `friend`, `allies` → `stance_filter = 'friendly'`
- Checks for `neutral` → `stance_filter = 'neutral'`

### Filtering Logic
When a stance filter is set:
1. **For NPCs:** Check `npc_ship.stances.get(player_ship.id, 'neutral')`
2. **For Starbases:** Check `starbase.stances.get(player_ship.id, 'neutral')`
3. Only include objects matching the filter

### Result Display
- When filtered: Shows stance in parentheses: `"Nearest npc (hostile): s1234"`
- When not filtered: Shows stance as separate field: `"Stance: hostile"`

## Testing

### Test Files Created
1. `test_hal_stance_queries.py` - Tests LLM integration with stance queries
2. `test_hal_stance_fallback.py` - Tests fallback pattern matching with stance queries
3. `demo_hal_stance.py` - Demonstrates all capabilities with example scenarios

### Test Coverage
- ✓ Enemy/hostile queries for NPCs
- ✓ Enemy/hostile queries for starbases
- ✓ Friendly queries for NPCs
- ✓ Friendly queries for starbases
- ✓ Neutral queries for NPCs
- ✓ Neutral queries for starbases
- ✓ General queries without stance filter
- ✓ LLM integration with stance data
- ✓ Fallback pattern matching with stance filtering

## Backward Compatibility

All existing hal queries continue to work as before:
- Queries without stance keywords show all objects
- Stance information is now included in results
- No breaking changes to existing functionality

## Usage in Game

Players can now ask natural language questions like:
- "What's the nearest enemy?" → Finds closest hostile ship
- "Where's a friendly starbase?" → Locates repair/resupply base
- "Show me neutral ships" → Finds potential trading partners
- "Closest hostile base?" → Identifies enemy starbase threat

The LLM integration allows even more natural phrasing, making the game more intuitive and immersive.
