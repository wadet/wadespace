# System Damage Trigger Bug Fix

## Issue
System damage was not triggering correctly when ships crossed the 50% damage threshold. The check was evaluating damage **before** applying new damage, rather than **after**.

## Bug Description

### Original Buggy Code
```python
def take_damage(self, damage: float, bypass_shields: bool = False, messages: list = None) -> None:
    # Track if damage was already over 50% before this hit
    was_heavily_damaged = self.damage > 50.0
    
    # ... apply damage ...
    
    # Check for system damage if ship was already heavily damaged
    if was_heavily_damaged and self.damage > 50.0 and messages is not None:
        self.check_for_system_damage(messages)
```

### Problem
The variable `was_heavily_damaged` was set **before** damage was applied. This meant:

- ❌ Ship at 45% takes 10% damage → Now at 55% → **No system check** (wasn't above 50% before)
- ✓ Ship at 55% takes 5% damage → Now at 60% → System check occurs
- ✓ Ship at 60% takes 5% damage → Now at 65% → System check occurs

This violated the intended mechanic: "When a ship has >50% damage and takes additional damage, there's a 25% chance for system failure."

## Fix

### Corrected Code
```python
def take_damage(self, damage: float, bypass_shields: bool = False, messages: list = None) -> None:
    # ... apply damage ...
    
    # Check for system damage if ship is now heavily damaged
    if self.damage > 50.0 and messages is not None:
        self.check_for_system_damage(messages)
```

### Solution
Simply check if damage is >50% **after** applying damage, not before. Now:

- ✓ Ship at 45% takes 10% damage → Now at 55% → System check occurs
- ✓ Ship at 55% takes 5% damage → Now at 60% → System check occurs
- ✓ Ship at 60% takes 5% damage → Now at 65% → System check occurs

## Files Modified
1. `/home/wade/workspace/wadespace/src/ship.py`
   - `take_damage()` method (line ~268)
   - `take_shield_hit()` method (line ~292)

## Changes Made
Both methods had the same issue:

**Before:**
```python
# Track if damage was already over 50% before this hit
was_heavily_damaged = self.damage > 50.0

# ... damage application code ...

# Check for system damage if ship was already heavily damaged
if was_heavily_damaged and self.damage > 50.0 and messages is not None:
    self.check_for_system_damage(messages)
```

**After:**
```python
# ... damage application code ...

# Check for system damage if ship is now heavily damaged
if self.damage > 50.0 and messages is not None:
    self.check_for_system_damage(messages)
```

## Testing

### Test Created: `test_system_damage_trigger_bug.py`
Demonstrates the bug and verifies the fix:

1. **Test crossing 50% threshold**: Ship at 45% takes 10% damage
   - Before fix: ❌ 0/50 system failures
   - After fix: ✓ ~15/50 system failures (25% expected)

2. **Test already above 50%**: Ship at 55% takes 5% damage
   - Before fix: ✓ ~15/50 system failures
   - After fix: ✓ ~15/50 system failures

### All Existing Tests Pass
- ✓ `test_system_damage.py` - All 10 tests pass
- ✓ `test_system_damage_integration.py` - Integration test passes
- ✓ `test_npc_system_damage_notifications.py` - Notification tests pass
- ✓ `test_system_damage_comprehensive.py` - Comprehensive demonstration passes

## Impact
This fix ensures that:
1. System damage can trigger **as soon as** a ship crosses 50% damage
2. The mechanic works as documented and intended
3. Players will notice system failures happening earlier in combat
4. The 25% probability applies consistently to all damage taken above 50%

## Related Documentation
- [SYSTEM_DAMAGE_IMPLEMENTATION.md](SYSTEM_DAMAGE_IMPLEMENTATION.md) - Main implementation guide
- [SYSTEM_DAMAGE_QUICK_REF.md](SYSTEM_DAMAGE_QUICK_REF.md) - Quick reference
- [NPC_SYSTEM_DAMAGE_NOTIFICATIONS.md](NPC_SYSTEM_DAMAGE_NOTIFICATIONS.md) - NPC notification system

## Date Fixed
January 16, 2026
