# HAL Enemy/Hostile Ship Query Fix

## Issue
The queries "hal where is the nearest enemy ship?" and "hal where is the nearest hostile ship?" were returning incorrect results. They would return the nearest ship by distance regardless of stance, instead of filtering by hostile stance.

## Root Cause
In `src/llm_handler.py`, the `_build_question_prompt()` method was building the LLM prompt with the following issues:

1. **Section Header Mislabeling**: NPC ships were listed under the section "ENEMY SHIPS:" even though not all NPC ships are enemies.

2. **Missing Stance Information**: The prompt did not include the `stance_to_player` field when listing NPC ships, even though this data was available in the `npc_data` dictionary.

3. **No Stance Filtering Instructions**: The prompt did not instruct the LLM to filter ships by stance when answering "enemy" or "hostile" queries.

## Solution
Modified `src/llm_handler.py` in the `_build_question_prompt()` method (lines ~743-800):

### Change 1: Added Stance Information to NPC Ship Listings
```python
# Before:
npc_desc += f"  - {npc_id}: Position ({pos[0]:.1f}, {pos[1]:.1f}), Distance {distance:.1f} AU, Health {health:.1f}%, Shields {shields:.1f}%\n"

# After:
stance = npc_data.get('stance_to_player', 'neutral')
stance_label = stance.upper()
npc_desc += f"  - {npc_id} (Stance: {stance_label}): Position ({pos[0]:.1f}, {pos[1]:.1f}), Distance {distance:.1f} AU, Health {health:.1f}%, Shields {shields:.1f}%\n"
```

### Change 2: Sort NPC Ships by Distance
Added sorting to ensure NPC ships are listed in order of distance:
```python
npc_ships_by_distance = sorted(
    [(npc_id, npc_data) for npc_id, npc_data in npc_ships.items() if not npc_data.get('is_destroyed', False)],
    key=lambda x: x[1].get('distance', 0)
)
```

### Change 3: Updated Section Header and Instructions
Changed the section header from "ENEMY SHIPS:" to "NPC SHIPS (sorted by distance, with their stance toward you):"

Added clear instructions to the prompt:
```
- When asked about "enemy ship", "hostile ship", look for NPC Ships with stance HOSTILE.
- When asked about "friendly ship", look for NPC Ships with stance FRIENDLY.
- When asked about "neutral ship", look for NPC Ships with stance NEUTRAL.
- NPC Ships show their stance in the ship list (e.g., "s1234 (Stance: HOSTILE)").
- For enemy/hostile ships, ONLY report NPC ships with stance HOSTILE.
- For friendly ships, ONLY report NPC ships with stance FRIENDLY.
```

## Testing
Created comprehensive tests to verify the fix:

1. **test_enemy_query_bug.py** - Reproduces the original bug and verifies the fix
2. **test_query_variations.py** - Tests various query phrasings

All existing tests continue to pass:
- test_hal_stance_queries.py ✓
- test_hal_stance_fallback.py ✓

## Example Queries Now Working Correctly
- "hal where is the nearest enemy ship?"
- "hal where is the nearest hostile ship?"
- "hal nearest enemy"
- "hal closest hostile"
- "hal find nearest enemy ship"
- "hal show me the nearest enemy ship"
- "hal where is the nearest friendly ship?"
- "hal nearest friendly"
- "hal closest friendly ship"

## Impact
This fix ensures that:
1. The LLM correctly filters NPC ships by their stance toward the player
2. "Enemy" and "hostile" queries only return ships with hostile stance
3. "Friendly" queries only return ships with friendly stance
4. The stance information is visible in the ship listings
5. Both LLM-based queries and fallback pattern matching work correctly
