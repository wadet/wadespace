# System Damage Feature - Quick Reference

## Summary
Added comprehensive system damage mechanics where ships with >50% damage can suffer critical system failures. Systems can be repaired automatically over time.

## Quick Facts
- **Trigger**: Ship damage > 50% + taking additional damage
- **Chance**: 25% per damage instance
- **Systems**: 7 total (shields, engines, torpedoes, phasers, scanners, radios, computers)
- **Repair Rate**: 25% at high damage (≥50%), 50% at low damage (<50%)
- **Repair Limit**: 1 system per turn maximum

## Seven Systems

### 1. Shields
- **Effect**: Cannot raise shields, all damage bypasses shields
- **Message**: "Shields are inoperative due to damage to the ship"

### 2. Engines
- **Effect**: Ship stops immediately, cannot move
- **Message**: "Engines are inoperative due to damage to the ship"

### 3. Torpedoes
- **Effect**: Cannot fire torpedoes
- **Message**: "Torpedoes are inoperative due to damage to the ship"

### 4. Phasers
- **Effect**: Cannot fire phasers
- **Message**: "Phasers are inoperative due to damage to the ship"

### 5. Scanners
- **Effect**: 2D map shows "Scanners are inoperative due to damage"
- **Message**: "Scanners are inoperative due to damage to the ship"

### 6. Radios
- **Effect**: Cannot use `tell` command
- **Message**: "Radios are inoperative due to damage to the ship"

### 7. Computers
- **Effect**: Cannot use `hal`, `targets`, `lock`, `nav` commands
- **Message**: "Computers are inoperative due to damage to the ship"

## Commands Affected

| Command | System Required | Error Message When Disabled |
|---------|----------------|----------------------------|
| `shields` | Shields | "Shields are inoperative due to damage to the ship" |
| `warp` | Engines | "Engines are inoperative due to damage to the ship" |
| `impulse` | Engines | "Engines are inoperative due to damage to the ship" |
| `fire` | Phasers | "Phasers are inoperative due to damage to the ship" |
| `torpedo` | Torpedoes | "Torpedoes are inoperative due to damage to the ship" |
| `scan` | Scanners | "Scanners are inoperative due to damage to the ship" |
| `tell` | Radios | "Radios are inoperative due to damage to the ship" |
| `hal` | Computers | "Computers are inoperative due to damage to the ship" |
| `targets` | Computers | "Computers are inoperative due to damage to the ship" |
| `lock` | Computers | "Computers are inoperative due to damage to the ship" |
| `nav` | Computers | "Computers are inoperative due to damage to the ship" |

## Player Strategy
1. **Monitor Damage**: Be cautious when damage exceeds 50%
2. **Retreat Early**: Consider retreating before multiple systems fail
3. **Repair Priority**: Get damage below 50% to double repair chances
4. **Dock for Repairs**: Use starbases to repair damage faster

## Testing
Two test suites provided:
- `test_system_damage.py` - Unit tests for all mechanics
- `test_system_damage_integration.py` - Integration test in game context

Both tests pass successfully.

## Files Modified
- `src/ship.py` - Core system damage logic
- `src/game_engine.py` - Command checks and turn processing
- `src/ui.py` - Scanner disabled visual feedback

## Documentation
- `SYSTEM_DAMAGE_IMPLEMENTATION.md` - Full technical documentation
- `SYSTEM_DAMAGE_QUICK_REF.md` - This quick reference (you are here)
