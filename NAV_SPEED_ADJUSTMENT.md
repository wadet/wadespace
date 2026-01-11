# Navigation Speed Adjustment Enhancement

## Overview
This enhancement implements dynamic speed adjustment for ships in navigation/pursuit mode when chasing other ships. The system automatically reduces speed as ships close in on their targets, allowing for efficient approach without overshooting.

## Implementation Details

### Key Features

1. **Player Ship Nav Mode Adjustment**
   - When the player uses `nav` command to chase an NPC ship
   - Once within sensor range (50 AU), speed adjusts dynamically
   - Target: Close to within 10 AU of the target ship

2. **NPC Ship Pursuit Adjustment**
   - NPC ships automatically adjust speed when pursuing player or other NPCs
   - Applies both to basic AI and LLM-controlled NPCs
   - Same targeting logic: close to 10 AU efficiently

3. **Dynamic Speed Calculation**
   The speed adjustment uses three distance bands:
   
   - **Far Range (>30 AU from target distance):**
     - Speed = min(max_speed, closing_distance × 0.3)
     - Higher speed for efficient closing
   
   - **Medium Range (15-30 AU from target):**
     - Speed = min(max_speed × 0.7, closing_distance × 0.4)
     - Moderate speed for controlled approach
   
   - **Close Range (<15 AU from target):**
     - Speed = min(max_speed × 0.5, closing_distance × 0.5)
     - Slower speed for precision positioning

### Code Locations

#### Player Nav Mode: `game_engine.py` - `_process_auto_nav()`
```python
# Special handling for ship targets when within sensor range
if is_ship_target and distance <= sensor_range and distance > target_distance_threshold:
    closing_distance = distance - target_distance_threshold
    
    if closing_distance > 30:
        desired_speed = min(max_warp, closing_distance * 0.3)
    elif closing_distance > 15:
        desired_speed = min(max_warp * 0.7, closing_distance * 0.4)
    else:
        desired_speed = min(max_warp * 0.5, closing_distance * 0.5)
```

#### NPC Basic AI: `game_engine.py` - `_execute_basic_npc_ai()`
```python
# Dynamically adjust speed based on distance to target
if target_distance <= sensor_range and target_distance > target_distance_threshold:
    closing_distance = target_distance - target_distance_threshold
    
    if closing_distance > 30:
        desired_speed = min(8.0, closing_distance * 0.3)
    # ... similar logic for medium and close ranges
```

#### NPC LLM-Controlled: `game_engine.py` - `_execute_llm_decision()`
```python
# When pursuing (attack action), adjust speed to close to within 10 AU
if decision['action'] == 'attack' and target_distance > 10.0:
    if target_distance <= sensor_range:
        # Calculate appropriate speed based on closing distance
        # ... similar band logic
```

## Testing

### Test Script: `test_nav_speed_adjustment.py`

The test script validates three scenarios:

1. **Player Nav Mode Speed Adjustment**
   - Player ship starts 45 AU from NPC target
   - Uses `nav` mode to pursue
   - Verifies speed reduces progressively: 9.0 → 6.3 → 4.5 → 4.45 AU/turn
   - Efficiently closes to ~14 AU in 5 turns

2. **NPC Pursuit of Player**
   - NPC starts 40 AU from player
   - Hostile stance triggers pursuit
   - Speed adjusts: 12.0 → 7.2 → 5.4 → 2.7 AU/turn
   - Demonstrates both LLM control and speed adjustment

3. **NPC-to-NPC Pursuit**
   - NPC1 pursues damaged NPC2 from 35 AU
   - Basic AI triggers pursuit
   - Speed adjusts: 6.0 → 6.0 → 4.0 → 4.0 → 2.5 AU/turn
   - Shows non-player pursuit with speed control

### Running Tests
```bash
python3 test_nav_speed_adjustment.py
```

All tests pass, demonstrating:
- ✓ Progressive speed reduction as distance closes
- ✓ No overshooting of target distance
- ✓ Consistent behavior across player/NPC and nav/pursuit modes

## Gameplay Impact

### Benefits

1. **Smoother Combat Engagement**
   - Ships naturally settle into combat range (~10 AU)
   - Reduces oscillation where ships repeatedly pass each other
   - More realistic tactical maneuvering

2. **Improved Nav Mode**
   - Player ship automatically slows when approaching ship targets
   - No need to manually cancel nav and adjust speed
   - Maintains nav mode throughout approach

3. **Better NPC Behavior**
   - NPCs no longer overshoot when pursuing
   - More intelligent-looking pursuit patterns
   - Consistent behavior whether LLM-controlled or basic AI

### Sensor Range Behavior

- **Outside Sensor Range (>50 AU):** Standard navigation, no special adjustment
- **Within Sensor Range (≤50 AU):** Dynamic speed adjustment kicks in
- **At Combat Range (≤10 AU):** Speed stabilizes, ready for combat

## Constants

Key values in the implementation:

- `sensor_range`: 50.0 AU (from Ship.sensors)
- `target_distance_threshold`: 10.0 AU (desired combat distance)
- `max_warp`: Usually 9.0 AU/turn (can be customized via nav command)

## Future Enhancements

Potential improvements:
1. Make target distance configurable per ship behavior
2. Add evasive speed adjustment when fleeing
3. Implement formation flying with coordinated speeds
4. Add speed matching when escorting friendly ships
