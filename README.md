# Wade Space Game

A comprehensive 2D turn-based space game inspired by Star Trek, featuring a procedurally generated 10,000 x 10,000 AU universe with dynamic combat, intelligent enemies, and deep ship management mechanics.

## Quick Start

```bash
# Install dependencies (text-based version)
pip install -r requirements.txt

# Configure environment (optional, for AI features in Phase 2)
cp .env.example .env

# Run the game
python -m src.main
```

## Game Features

### Universe
- **10,000 x 10,000 AU** procedurally generated universe
- **1,000 stars** for refueling
- **10,000 planets** with crew recruitment opportunities
- **100 black holes** that destroy ships
- **100 pulsars** that disrupt sensors
- **20 wormhole pairs** for rapid transit
- **100 starbases** for repairs and supplies
- **1,000 asteroid fields** for mining resources

### Your Ship
Control a Federation starship with full Star Trek-inspired systems:

**Weapons**:
- Phaser arrays (instant-hit, 10 AU range, 5% damage)
- Photon torpedos (slow projectiles, 20 AU range, 10% damage)

**Propulsion**:
- Warp drive (2-9 AU/turn, 0.5% energy)
- Impulse drive (1 AU/turn, 1% energy)
- Warp core temperature management

**Defense**:
- Deflector shields (50% energy drain, block damage)
- Damage repair (5% recovery per turn)
- Hull integrity management

**Sensors**:
- 50 AU detection range
- Detailed scans of nearby objects
- Pulsar disruption effects

**Resources**:
- Crew (starts with 1,000, lost in combat, recruited from planets)
- Energy (0-100%, consumed by all systems)
- Cash (earned from mining and destroyed enemies)
- Photon torpedos (50 max, restocked at starbases)

### Gameplay Mechanics

**Each Turn**:
1. Issue a command (warp, fire, scan, navigate, etc.)
2. Enemy ships execute AI-driven commands
3. All actions resolve simultaneously
4. Objects update and interactions trigger
5. Check for game-ending conditions

**Combat System**:
- Lock phasers on targets for instant-hit attacks
- Fire torpedos in straight lines at moving targets
- Shields absorb damage before hull takes hits
- Ships destroyed at 100% damage with explosion
- Enemies drop cash and resources when destroyed

**Survival Elements**:
- Refuel at stars (10%/turn within 1 AU)
- Repair at starbases (25%/turn within 1 AU)
- Mine asteroids (0-1,000$ per attempt)
- Recruit crew from planets (shields must be down)
- Manage energy between weapons, shields, and propulsion

### Commands

**Navigation**:
- `warp 5` - Set warp speed (2-9 AU/turn recommended)
- `impulse on/off` - Activate impulse drive
- `heading 180` - Set course (0-359 degrees)
- `nav st12345` - Auto-navigate to object
- `stop` - All stop

**Combat**:
- `scan` - Scan nearby objects (20 AU)
- `scan st12345` - Scan specific object
- `lock st12345` - Lock phasers on target
- `fire` - Fire locked phasers
- `torpedo s1` - Fire torpedo at target

**Ship Systems**:
- `shields up/down` - Raise/lower shields
- `status` - Display vital statistics
- `ask what is nearest star` - Query system

**Communication**:
- `tell s1 cease fire` - Send message to enemy ship
- `skip` - End turn without action

## Architecture

The game is built with modular, maintainable code organized in `src/`:

- **`universe.py`** - Procedural universe generation
- **`universe_objects.py`** - All space objects (stars, planets, etc.)
- **`ship.py`** - Ship systems and combat mechanics
- **`identifiers.py`** - Unique ID management
- **`command_parser.py`** - Natural language command parsing
- **`game_engine.py`** - Core game loop and state management
- **`main.py`** - Text-based interface and entry point

See `ARCHITECTURE.md` for detailed component documentation.

## Game Rules

### Energy System
All ship systems consume energy:
- Shields: 2% per turn when active
- Warp drive: 0.5% per turn
- Impulse drive: 1% per turn
- Phaser/torpedo fire: 1% per shot

Energy regenerates at:
- Stars: 10% per turn (within 1 AU)
- Starbases: 10% per turn (within 1 AU)

### Combat Damage
- **Phasers**: 5% damage with 50-100% accuracy
- **Torpedos**: 10% damage with 75% accuracy (25% miss chance)
- **Shields**: Block damage first, regenerate at starbases
- **Hull**: Takes damage after shields depleted
- **Destruction**: Ship destroyed at 100% damage

### Repair & Maintenance
- Ships auto-repair 5% damage per turn
- Starbases repair 25% damage per turn (within 1 AU)
- Shields regenerate slowly over time
- Warp core cools 5% per turn (warp) or 10% (impulse) when inactive

### Special Events
- **Black Holes**: Instant destruction if within 3 AU
- **Pulsars**: Randomize sensor readings within 2 AU
- **Wormholes**: Free teleportation within 1 AU
- **Asteroid Mining**: 0-1,000 credits per attempt
- **Crew Recruitment**: Up to 1,000 crew from planets

### Losing Conditions
- Ship destroyed (100% damage)
- Ship disabled (0 crew)

## Future Updates

### Next Phase: Visual Interface
- 2D map showing 20x20 AU viewport
- Minimap with zoom (±300 AU)
- Animated phasers and torpedo trails
- Graphical status indicators
- Message log display
- Mouse support for targeting

### Advanced Features
- Enemy ship AI with GPT-4o integration
- Coordinated multi-ship tactics
- Alien species with unique behaviors
- Trading and economic system
- Fleet management
- PvP online multiplayer

## Technical Specs

- **Language**: Python 3.8+
- **Dependencies**: pygame, numpy, openai, python-dotenv
- **Universe Size**: 10,000 x 10,000 AU
- **Maximum Objects**: 10,000+
- **Turn Resolution**: <100ms
- **UI Rendering**: 60 FPS (when available)

## Development

For detailed architecture and development guidelines, see `ARCHITECTURE.md`.

### Quick Contribute
1. Create a feature branch
2. Implement in modular fashion (separate file per major system)
3. Add docstrings and type hints
4. Test with `python -m pytest tests/`
5. Submit pull request

---

**Version**: 0.1.0 (Alpha)  
**Status**: Core mechanics implemented, UI in development  
**Author**: Wade Space Development Team
