# HAL Query Fix for Enemy Starbase Queries

## Issue
The query `"hal where is the nearest enemy starbase?"` was not returning the actual nearest enemy starbase. Instead, it was returning an arbitrary hostile starbase.

## Root Cause
The `_query_nearest_object()` function in `game_engine.py` was using the wrong attribute to filter starbases:

- **Incorrect**: Used `obj.stances.get(ship.id, 'neutral')` to determine if a starbase was hostile
- **Problem**: The `stances` dictionary is for dynamic reputation tracking and is randomly initialized. A starbase with `friendly_to_player=False` might have a stance of 'neutral' or even 'friendly' in the stances dict.
- **Correct**: Should use `obj.friendly_to_player` which is the permanent attribute indicating whether a starbase is inherently friendly or hostile to the player

## Solution
Modified the `_query_nearest_object()` function in `/home/wade/workspace/wadespace/src/game_engine.py` to:

1. Check `obj.friendly_to_player` instead of `obj.stances.get(ship.id, 'neutral')` when filtering starbases
2. Filter correctly:
   - For 'hostile' filter: Skip starbases where `obj.friendly_to_player == True`
   - For 'friendly' filter: Skip starbases where `obj.friendly_to_player == False`
3. Display the starbase type (friendly/hostile) in the response based on `friendly_to_player` attribute

## Testing
Verified that the following queries now work correctly:
- `"hal where is the nearest enemy starbase"` ✅
- `"hal where is the nearest hostile starbase"` ✅
- `"hal where is the nearest friendly starbase"` ✅
- `"hal where is the nearest starbase"` ✅

All queries now correctly return the actual nearest starbase of the requested type, sorted by distance from the player's ship.

## Files Changed
- `/home/wade/workspace/wadespace/src/game_engine.py` - Fixed `_query_nearest_object()` method (lines ~1282-1314)
