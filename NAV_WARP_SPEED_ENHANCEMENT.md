# Nav Command Warp Speed Enhancement

## Overview
Enhanced the `nav` command to support an optional custom warp speed parameter, allowing players to specify the warp speed to use during auto-navigation instead of always using the default maximum warp speed.

## Syntax
The nav command now supports the following formats:

### Original Syntax (Preserved)
- `nav <object_id>` - Navigate using default maximum warp (9 AU/turn)
- `navigate to <object_id>` - Same as above
- `go to <object_id>` - Same as above

### New Syntax (Added)
- `nav <object_id>, <speed>` - Navigate with comma separator
- `nav <object_id> <speed>` - Navigate with space separator
- `nav <object_id>,<speed>` - Navigate with comma, no spaces
- `navigate to <object_id>, <speed>` - Long form with comma
- `navigate to <object_id> <speed>` - Long form with space
- `go to <object_id>, <speed>` - Alternative form with comma
- `go to <object_id> <speed>` - Alternative form with space

## Examples
```
nav st1234        # Navigate to star st1234 at warp 9 (default)
nav st1234, 5     # Navigate to star st1234 at warp 5
nav st1234 5      # Navigate to star st1234 at warp 5 (same as above)
nav s42,3         # Navigate to ship s42 at warp 3
navigate to sb100, 7  # Navigate to starbase sb100 at warp 7
go to pl500 4     # Navigate to planet pl500 at warp 4
```

## Implementation Details

### Files Modified

#### 1. `src/command_parser.py`
- Updated `_match_nav()` method to parse optional warp speed
- Regex patterns now extract both object ID and optional speed parameter
- Supports comma-separated or space-separated format
- Falls back to original behavior when no speed is specified

#### 2. `src/ship.py`
- Added `auto_nav_warp_speed: Optional[float]` field to Ship class
- Stores custom warp speed for current auto-navigation session
- Set to `None` when not in auto-nav or using default speed

#### 3. `src/game_engine.py`
- Updated nav command handler to:
  - Extract and store custom warp speed from command
  - Display warp speed in navigation message when specified
- Updated `_process_auto_nav()` to:
  - Use custom warp speed when available
  - Fall back to default maximum warp (9 AU/turn) when not specified
  - Apply custom speed to both long-distance and medium-distance navigation logic
- Updated all auto-nav cancellation points to clear custom warp speed:
  - When warp/impulse/heading commands are issued
  - When stop command is issued
  - When target is reached
  - When target is not found
  - When target is destroyed

## Behavior

### Warp Speed Constraints
- Custom warp speeds are still subject to normal warp constraints (minimum 2 AU/turn)
- Speeds below 2 AU/turn automatically switch to impulse drive
- Overshoot prevention still applies (speed is reduced near target)
- Warp core temperature effects still apply for speeds above 9 AU/turn

### Auto-Navigation States
- Custom warp speed persists for entire navigation session
- Cleared when navigation completes or is cancelled
- Does not affect manual warp commands after auto-nav ends

### Messages
When a custom warp speed is specified, the navigation engagement message shows:
```
Auto-navigation engaged to Starbase sb1234 (45.3 AU away) at warp 5
```

Without custom speed (default behavior):
```
Auto-navigation engaged to Starbase sb1234 (45.3 AU away)
```

## Testing
A test script `test_nav_warp_speed.py` has been created to verify:
1. Command parsing for all syntax variations
2. Ship class field existence and functionality
3. Proper handling of comma-separated and space-separated formats

All tests pass successfully.

## Backward Compatibility
The enhancement is fully backward compatible:
- Existing `nav <object_id>` commands work exactly as before
- Default behavior (maximum warp) is unchanged when no speed is specified
- No breaking changes to existing functionality
