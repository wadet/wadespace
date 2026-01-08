# Torpedo Damage System Update

## Summary
Updated the torpedo damage system to prioritize shield damage before hull damage.

## New Behavior

### Torpedo Damage Mechanics
- **Shields First**: Torpedoes now damage shields by **20%** per hit
- **Hull Damage**: Once shields reach 0% or are down, torpedoes damage the ship hull by **10%** per hit
- **Partial Shields**: If shields have less than 20% remaining, the torpedo depletes the remaining shields and applies proportional damage to the hull

### Examples
1. **Full Shields (100%)**: Torpedo hits → Shields reduced to 80%, no hull damage
2. **Partial Shields (10%)**: Torpedo hits → Shields depleted (0%), hull takes ~5% damage  
3. **No Shields**: Torpedo hits → Hull takes 10% damage directly
4. **Multiple Hits**: 5 torpedoes will completely deplete shields (100% → 0%), 6th torpedo damages hull

## Files Modified

### Implementation
- **[src/game_engine.py](src/game_engine.py)**: Updated torpedo hit logic in `_update_torpedos_for_ship()` method
  - Player torpedoes vs enemies (lines ~1463-1490)
  - Enemy torpedoes vs player (lines ~1518-1545)
  - Enemy torpedoes vs other enemies (lines ~1563-1589)

### Documentation
- **[wadespace-prompt.txt](wadespace-prompt.txt)**: Updated game design document (line 89)

## Testing

### Test File
- **[test_torpedo_shield_damage.py](test_torpedo_shield_damage.py)**: Comprehensive test suite with 7 test cases

### Test Coverage
1. ✓ Torpedo vs Full Shields (100%)
2. ✓ Torpedo vs Partial Shields (10%)
3. ✓ Torpedo vs No Shields
4. ✓ Multiple Torpedo Hits (5x)
5. ✓ Sixth Torpedo After Shields Depleted
6. ✓ Enemy Torpedo vs Player Shields
7. ✓ Torpedo vs Starbase Shields (documented)

**Result**: 7/7 tests passing ✅

## Gameplay Impact

### Strategic Changes
- **Shields are more valuable**: Can absorb 5 full torpedo hits (vs ~1-2 before)
- **Shield management crucial**: Players should raise shields when under torpedo attack
- **Tactical decisions**: Enemies may prioritize targets with depleted shields

### Balance Considerations
- Torpedoes remain effective against unshielded targets (10% damage)
- Shields provide significantly better protection against torpedo attacks
- Energy management becomes more important (shields cost 2% energy/turn)
