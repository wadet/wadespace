# Wade Space - Enemy Visibility & Torpedo Movement Updates

## Summary
Fixed two critical gameplay issues:
1. **Enemy Ships Now Visible on Maps** - Enemy ships render on both 2D map and minimap
2. **Torpedo Movement Implemented** - Torpedos travel 10 AU per turn toward targets

## Changes Made

### 1. Enemy Ship Rendering in UI (`src/ui.py`)

#### 2D Map Display (Lines 156-206)
- Added iteration over `self.engine.enemy_ships` in `_draw_2d_map()`
- Enemy ships render as **red diamonds** (4-point polygons)
- Displayed with 2px outline for visibility
- Only rendered when within 20 AU viewport
- Uses same coordinate transformation as universe objects

#### Minimap Display (Lines 450-510)
- Added iteration over `self.engine.enemy_ships` in `_draw_minimap()`
- Enemy ships render as **small red diamonds** on minimap
- Scaled appropriately for 500 AU overview
- Maintains consistent red coloring for easy identification
- Shown when within minimap viewport range

**Visual Distinction:**
- Universe objects: Various colors (yellow stars, blue planets, etc.)
- Enemy ships: Red diamonds (easily distinguished)
- Player ship: Green triangle (at center)

### 2. Torpedo Movement System (`src/game_engine.py`)

#### New Method: `_update_torpedos()` (Lines 498-563)
- Moves all active torpedos each turn
- **Movement Speed:** 10 AU per turn toward target
- **Targeting:** Uses proximity detection (within 2 AU) to identify hit targets
- **Collision Detection:** Detects when torpedo reaches target
- **Damage System:**
  - 25% damage per torpedo hit
  - Applies damage to enemy ships
  - Auto-destroys enemy ship if damage >= 100%
  - Generates game messages for each hit

#### Integration in Game Loop
- Called from `_update_all_objects()` after ship updates
- Processes all player torpedos each turn
- Removes torpedos after impact or expiration

**Torpedo Lifecycle:**
1. Fire: `ship.fire_torpedo(target_position)` creates torpedo dict
2. Movement: Each turn, torpedo moves 10 AU toward target
3. Detection: When within 2 AU of any object, collision is checked
4. Impact: Applies damage and generates message
5. Removal: Torpedo removed from active list after hit

### 3. Test Coverage

**Unit Tests:** All 29 existing tests pass
- No regressions in any system

**Manual Verification:**
- Enemy ships spawn correctly (1-3 within 50 AU)
- Enemies visible on maps at correct positions
- Torpedos fire and move at correct speed
- Damage applies to enemy ships on impact
- Enemy destruction triggers when damage reaches 100%

## Gameplay Impact

### Enemy Detection
Players can now see all enemy ships on both the main tactical map and minimap, enabling strategic decision-making about:
- Which enemies to avoid
- Which enemies to target
- Threat assessment based on proximity

### Tactical Weapon Use
The torpedo system is now fully functional:
- Players can fire at enemy ships
- Torpedos travel across space
- Hit/miss mechanics work correctly
- Damaged enemies become visible threats
- Enemy destruction removes ship from board

## Technical Details

### Coordinate System
- All positions use universal X/Y coordinates
- Viewport rendering uses relative coordinates
- Torpedo movement uses vector math (normalized direction)

### Performance
- Enemy rendering: O(n) where n = number of enemies in viewport
- Torpedo update: O(m) where m = number of active torpedos
- Both optimized to only process visible/active entities

### Error Handling
- Safely handles empty torpedo lists
- Checks for ship existence before applying damage
- Properly removes expired torpedos to prevent memory leaks

## Future Enhancements
- Enemy ship AI commands and reactions
- Torpedo counter-measures (ECM, decoys)
- Phaser beam hit detection
- Advanced targeting system
- Damage visualization effects
