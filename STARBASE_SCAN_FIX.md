# Starbase Scan Display Enhancement

## Issue
When scanning a specific starbase (e.g., `scan sb1234`), the command only displayed:
- Object ID
- Display symbol (⊕)
- Distance

This was insufficient compared to ship scans, which showed comprehensive statistics including damage, shields, energy, etc.

## Root Cause
In [game_engine.py](src/game_engine.py), the `_execute_scan()` method had special handling for Ship objects to display detailed statistics, but Starbase objects fell through to the generic "universe object" handler which only showed basic information.

## Solution
Added a new `elif` branch specifically for Starbase objects in the scan command handler to display comprehensive statistics similar to ship scans.

### Implementation Details

**File**: [game_engine.py](src/game_engine.py#L1005-L1024)

**Change**: Added starbase-specific scan output between Ship handling and generic universe object handling.

**New Starbase Scan Output**:
```
Scan of sb1234: Starbase at 22.4 AU
  Status: operational, Damage: 0.0%, Energy: 100.0%
  Shields: 100.0%, Torpedos: 500/500
  Service range: 1.0 AU, Defense range: 10.0 AU
  Stance: friendly
```

### Statistics Now Displayed

For starbases, the scan command now shows:
1. **Distance** - How far the starbase is from the scanning ship
2. **Status** - Operational status (always "operational" currently)
3. **Damage** - Current damage percentage (0-100%)
4. **Energy** - Current energy level percentage (0-100%)
5. **Shields** - Shield strength percentage (0-100%)
6. **Torpedos** - Current torpedo count and maximum capacity
7. **Service range** - Distance at which repairs are available (1.0 AU)
8. **Defense range** - Distance at which starbase will fire on hostile ships (10.0 AU)
9. **Stance** - The starbase's stance toward the scanning ship (hostile/neutral/friendly)

### Testing

Created comprehensive test suites:

1. **test_starbase_scan.py** - Basic functionality test
2. **test_starbase_scan_comprehensive.py** - Tests various starbase conditions:
   - Friendly starbase at full health
   - Hostile starbase with damage
   - Neutral starbase with low energy
3. **test_general_scan.py** - Verifies general scan still works correctly
4. **test_hal_starbase_query.py** - Confirms HAL queries still work

All tests pass successfully.

### Backward Compatibility

✓ All existing tests pass (29/29 core tests)
✓ General scan command unchanged
✓ Ship scan command unchanged
✓ HAL queries unchanged
✓ No breaking changes to game mechanics

### Benefits

Players can now:
- **Assess starbase condition** before approaching
- **Check torpedo availability** for resupply missions
- **Evaluate threat level** (hostile starbases with full torpedos are dangerous)
- **Monitor energy status** to know if starbase is functional
- **Plan repairs** by checking service range
- **Make tactical decisions** based on complete information

### Example Usage

```
> scan sb2815

Scan of sb2815: Starbase at 35.0 AU
  Status: operational, Damage: 45.0%, Energy: 60.0%
  Shields: 55.0%, Torpedos: 250/500
  Service range: 1.0 AU, Defense range: 10.0 AU
  Stance: hostile
```

This output tells the player:
- The starbase is damaged (45%) - possibly vulnerable
- It's hostile - will attack if within 10 AU
- It has 250 torpedos remaining - still dangerous
- Low energy (60%) - may be weakened
- Shields at 55% - somewhat compromised defenses

## Files Modified

- [src/game_engine.py](src/game_engine.py) - Added starbase-specific scan handling

## Test Files Created

- test_starbase_scan.py
- test_starbase_scan_comprehensive.py
- test_general_scan.py
- test_hal_starbase_query.py
