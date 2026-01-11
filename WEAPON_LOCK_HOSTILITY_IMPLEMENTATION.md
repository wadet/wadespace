# Weapon Lock Hostility Implementation

## Summary
Modified the behavior of NPC ships and starbases to treat weapon locks as hostile actions. When the player or another NPC ship locks their weapons on an NPC ship or starbase, the target now responds defensively **according to their behavior/personality traits**, making reactions more realistic and varied.

## Changes Made

### 1. Game Engine (`src/game_engine.py`)

#### NPC Ship Weapon Lock Detection
- Added weapon lock detection in `_get_llm_decision()` to identify all ships that have locked weapons on an NPC
- Passes this information to the LLM handler as `locked_by` parameter
- Modified `_execute_basic_npc_ai()` to detect weapon locks and respond **based on behavior trait**:

**Aggressive NPCs:**
- Immediately raise shields
- Aggressively lock weapons back on the aggressor
- Prepare for offensive combat
- Debug message: "Aggressively locking weapons on [aggressor] in response!"

**Timid NPCs:**
- Always raise shields as defensive reflex
- If damaged >20%: Prioritize evasion, don't lock back
  - Debug message: "Weapon lock detected - preparing evasive maneuvers! (timid)"
- If not damaged: Cautiously lock back on aggressor
  - Debug message: "Cautiously locking weapons on [aggressor]"

**Neutral NPCs:**
- Raise shields
- Lock weapons back (proportional response)
- Debug message: "Locking weapons on [aggressor] in response"

#### Starbase Weapon Lock Detection
- Modified `_process_starbase_actions()` to detect weapon locks on starbases
- When a weapon lock is detected:
  - Adds the aggressor to the starbase's `fired_upon_by` set (triggering hostile response)
  - Raises shields immediately
  - Displays a message to the player about the defensive response

### 2. LLM Handler (`src/llm_handler.py`)

#### Updated Function Signatures
- Modified `get_npc_decision()` to accept `locked_by` parameter (list of ship IDs)
- Modified `_build_decision_prompt()` to accept and use `locked_by` parameter

#### Enhanced AI Prompts with Behavior-Specific Guidance
The weapon lock warning now provides **personality-appropriate response guidance**:

**Aggressive NPCs receive:**
```
YOUR AGGRESSIVE RESPONSE:
- This is an act of WAR! Lock weapons back immediately!
- Prepare to engage and destroy the aggressor
- Close distance and attack unless severely damaged (>80%)
```

**Timid NPCs receive:**
```
YOUR CAUTIOUS RESPONSE:
- This is a serious threat! Prioritize survival
- If damaged (>20%), consider immediate evasion
- Only engage if you have tactical advantage (enemy damaged >50%)
- Consider fleeing to nearest friendly starbase
```

**Neutral NPCs receive:**
```
YOUR BALANCED RESPONSE:
- Assess the tactical situation carefully
- Lock weapons back to show you're not defenseless
- Engage if conditions favor you, evade if outmatched
- Consider your damage level and enemy's condition
```

### 3. Test Scripts

**`test_weapon_lock_hostility.py`**
- Comprehensive test with three scenarios
- Tests basic weapon lock detection and response

**`test_behavior_weapon_lock.py`** (New)
- Tests behavior-specific responses
- Verifies aggressive, timid, and neutral NPCs respond differently
- Tests timid NPCs both when damaged and undamaged

## Behavior Details

### For NPC Ships:

**All Personalities:**
- Shields automatically raised when locked on (if energy > 10%)

**Aggressive:**
- ✅ Immediately locks weapons back
- ✅ Prepares for offensive engagement
- ✅ Will attack unless severely damaged (>80%)

**Timid:**
- ✅ Raises shields defensively
- ✅ When damaged (>20%): Prepares to flee, doesn't lock back
- ✅ When not damaged: Cautiously locks back but ready to evade
- ✅ Prioritizes survival over confrontation

**Neutral:**
- ✅ Raises shields
- ✅ Locks weapons back (measured response)
- ✅ Decides next action based on tactical situation

### For Starbases:
When a weapon lock is detected:
1. **Hostile Status** - Aggressor is added to `fired_upon_by` set, triggering defensive protocols
2. **Shields** - Automatically raised if energy > 10%
3. **Message** - Player is notified when a starbase detects the weapon lock

### Debug Messages:
When debug mode is enabled (`debug on`), behavior-specific messages appear:
- Aggressive: `[DEBUG] {ship_id}: Aggressively locking weapons on {aggressor} in response!`
- Timid (damaged): `[DEBUG] {ship_id}: Weapon lock detected - preparing evasive maneuvers! (timid)`
- Timid (undamaged): `[DEBUG] {ship_id}: Cautiously locking weapons on {aggressor}`
- Neutral: `[DEBUG] {ship_id}: Locking weapons on {aggressor} in response`

## Testing

All tests pass successfully:
- ✅ NPC response to player lock
- ✅ Starbase response to player lock  
- ✅ NPC-to-NPC weapon lock response
- ✅ Aggressive NPC behavior-specific response
- ✅ Timid NPC behavior-specific response (damaged and undamaged)
- ✅ Neutral NPC behavior-specific response

Run tests with:
```bash
python test_weapon_lock_hostility.py
python test_behavior_weapon_lock.py
```

## Impact on Gameplay

Players now face more realistic and varied combat scenarios:
- **Aggressive NPCs** are dangerous - they'll lock back immediately and engage
- **Timid NPCs** are more predictable - damaged ones will try to flee, making them easier targets
- **Neutral NPCs** provide balanced encounters - they'll defend themselves but won't necessarily escalate
- Locking weapons is no longer a "free" action - it immediately alerts and provokes the target
- Tactical considerations: Lock on aggressive enemies only when ready to fight, but timid enemies might flee when locked on
- Personality becomes a key factor in predicting enemy behavior

## Future Enhancements

Potential improvements for future iterations:
1. Graduated stance-based responses (friendly ships might just raise shields without locking back)
2. NPC communication about weapon locks to nearby allies
3. Reputation impact from weapon locks on neutral or friendly targets
4. Time delay before target notices the lock (simulating sensor detection time)
5. Distance-based detection (harder to detect locks from far away)
