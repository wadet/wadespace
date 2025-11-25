# Wade Space - Getting Started Guide

Welcome to **Wade Space**, a comprehensive 2D turn-based space game written in Python!

## Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
cd /home/wadet/workspace/wadespace
pip install -r requirements.txt
```

### 2. Launch the Game

```bash
python -m src.main
```

You'll see your ship ID and starting position, then the game prompt awaits your commands.

## First Game Session

### Example Gameplay

```
Enter command: warp 5
Warp drive engaged: 5 AU/turn

--- Turn 2 ---
Position: (1466.9, 4642.6)
Energy: 99.5%  Shields: 100.0%
Damage: 0.0%  Crew: 1000

Enter command: scan
Scan results:
  st12345: ★ @ 45.2 AU
  st42185: ★ @ 67.3 AU
  pl87234: ● @ 23.1 AU

Enter command: heading 45
Heading set to 45.0°

Enter command: status
=== s74984 Status ===
Damage: 0.0%
Energy: 99.5%
Shields: 100.0%
Crew: 1000
Cash: $3500
Torpedos: 50
```

## Essential Commands

### Navigation
- **`warp 5`** - Travel at 5 AU per turn (2-9 AU recommended)
- **`impulse on`** - Engage slower impulse drive (1 AU/turn)
- **`heading 180`** - Set course to 180 degrees
- **`stop`** - All stop
- **`nav st12345`** - Auto-navigate to a star or object

### Scanning & Information
- **`scan`** - Scan nearby objects (20 AU range)
- **`scan st12345`** - Get details on specific object
- **`status`** - View your ship's vital statistics
- **`ask which is nearest star`** - Query game system

### Combat
- **`lock on s1`** - Lock phasers on enemy ship
- **`fire`** - Fire locked phasers (instant hit)
- **`tor s1`** - Fire photon torpedo at target
- **`shields up`** - Raise shields (costs 2% energy/turn)
- **`shields down`** - Lower shields

### Interaction
- **`tell s1 stop attacking`** - Send message to enemy
- **`skip`** - Skip turn without action

## Game Systems Explained

### Energy Management
Your ship has 100% energy that powers all systems:

**Energy Drains**:
- Shields: 2% per turn (when active)
- Warp drive: 0.5% per turn
- Impulse drive: 1% per turn
- Weapons: 1% per shot

**Energy Recovery**:
- Stars: +10% per turn (within 1 AU)
- Starbases: +10% per turn (within 1 AU)

### Combat Mechanics

**Phasers**:
- Instant hit weapons
- 10 AU range
- 5% damage to target
- 50-100% accuracy
- Must lock on target first
- Recharge 25% per turn
- Consume 1% energy per shot

**Photon Torpedos**:
- Slow projectiles
- 20 AU maximum range
- 10% damage per hit
- 75% accuracy (25% miss chance)
- Travel 1 AU per turn
- You start with 50 torpedos
- Restock at starbases
- Consume 1% energy per shot

### Shields & Defense

**Shield Management**:
- Blocks up to 100% of incoming damage
- Drain 2% energy per turn when active
- Regenerate slowly over time
- Can be managed strategically

**Hull Integrity**:
- Direct damage when shields are down
- Auto-repair 5% per turn
- Starbase repairs 25% per turn
- Ship destroyed at 100% damage

### Movement & Navigation

**Two Propulsion Modes**:
- **Warp Drive**: Fast travel, 2-9 AU/turn recommended
  - Can exceed 9 AU but causes warp core overheating
  - Each AU over 9 adds 1% warp core temperature
  - Warp core cools 5% per turn when inactive

- **Impulse Drive**: Slow travel, 1 AU/turn
  - Lower energy consumption
  - Warp core cools 10% per turn when inactive

**Cannot use both simultaneously.**

### Special Locations

**Stars**:
- Refuel for +10% energy per turn
- Must be within 1 AU
- Infinite energy source

**Starbases**:
- Repair for 25% damage per turn
- Refuel at 10% energy per turn
- Restock photon torpedos
- Some are friendly (green), some enemy (red)
- Must be within 1 AU
- Player can only use friendly starbases

**Planets**:
- Recruit crew (0-1,000 available)
- Shields must be down to recruit
- Must be within 1 AU

**Asteroid Fields**:
- Mine for cash ($0-1,000 per attempt)
- Must be within 1 AU
- Can mine once per turn

### Hazards

**Black Holes**:
- Instant destruction if within 3 AU
- Cannot be destroyed by weapons
- Permanent universe hazards

**Pulsars**:
- Disrupt sensors if within 2 AU
- Randomizes object detection
- Cannot be destroyed

**Enemy Ships**:
- 50 total in universe at any time
- Up to 3 in your local area
- Can attack, pursue, or flee
- Drop cash when destroyed

### Wormholes
- Paired teleportation portals
- Free travel (no energy cost)
- Appear randomly throughout universe
- Enter from within 1 AU away

## Strategy Tips

### Early Game
1. Locate nearby stars for energy management
2. Find a friendly starbase for repairs
3. Avoid black holes and pulsars
4. Scan regularly to track enemy movement

### Combat
1. Always lock phasers before firing
2. Keep shields up when near enemies
3. Use cover of asteroids and planets
4. Torpedos are more powerful but slower
5. Manage energy carefully - can't fight if drained

### Resource Management
1. Mine asteroids for cash regularly
2. Recruit crew when shields are down
3. Stock torpedos at friendly starbases
4. Time star refueling with warp drive use

### Survival
1. Monitor warp core temperature (don't exceed 100%)
2. Repair regularly at starbases
3. Never let energy drop to zero
4. Keep crew above 1 (ship disables if crew = 0)

## Winning Strategies

1. **Exploration First**: Scan the area, find resources
2. **Strategic Refueling**: Plan routes through stars and starbases
3. **Controlled Combat**: Engage enemies when advantageous
4. **Resource Gathering**: Mine asteroids, recruit crew
5. **Evasion**: Use distance and maneuvering to avoid damage

## Troubleshooting

### Game Won't Start
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Try direct import test
python3 -c "from src.game_engine import GameEngine; print('OK')"
```

### Commands Not Working
- Make sure you're typing exact command syntax
- Try lowercase: `warp 5` not `WARP 5`
- Use object IDs from scan results: `lock on s1` (use exact ID)
- Use spaces between command parts: `shields up` not `shieldsup`

### Game Too Easy/Hard
- **Harder**: Move toward black holes and pulsars
- **Easier**: Stick to stars and starbases for resource gathering

## Project Structure

```
wadespace/
├── src/
│   ├── main.py              # Entry point
│   ├── game_engine.py       # Game loop
│   ├── ship.py              # Ship systems
│   ├── command_parser.py    # Command parsing
│   ├── universe.py          # Universe generation
│   ├── universe_objects.py  # Game objects
│   └── identifiers.py       # ID management
├── tests/
│   └── test_core.py         # Unit tests
└── README.md / ARCHITECTURE.md
```

## Run Unit Tests

```bash
python3 -m pytest tests/test_core.py -v
```

## Advanced Usage

### Custom Seed for Reproducible Games
```python
from src.game_engine import GameEngine
engine = GameEngine(universe_seed=12345)
# Same seed = same universe every time
```

### Analyzing Game State
```python
# Get all nearby objects
nearby = engine.get_objects_in_range(
    engine.player_ship.position, 
    range_au=50.0
)

# Get only ships
ships = engine.get_ships_in_range(
    engine.player_ship.position, 
    range_au=20.0
)
```

## Keyboard Tips

- **Up Arrow**: Repeat last command (when UI implemented)
- **Tab**: Auto-complete object IDs (when UI implemented)
- **Ctrl+C**: Quit game anytime

## Next Features (Coming Soon)

- Full Pygame graphical interface with 2D map
- Minimap with zoom capability
- Visual effects (explosions, phaser beams, torpedo trails)
- GPT-4o AI for enemy ship captains
- Enemy communication and coordination
- Sound effects and music
- High score tracking

---

**Have fun exploring Wade Space!** 🚀

For more technical details, see `ARCHITECTURE.md`.
