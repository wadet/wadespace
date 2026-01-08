# Wade Space - 2D Turn-Based Space Game

A modular, Python-based turn-based space game featuring a procedurally generated universe, intelligent npc AI, dynamic combat system, and Star Trek-inspired mechanics.

## Architecture Overview

### Project Structure

```
wadespace/
├── src/                          # Main game source code
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Game entry point and main loop
│   ├── identifiers.py           # Unique ID generation and management
│   ├── universe_objects.py      # Base classes for all universe objects
│   ├── universe.py              # Universe generator
│   ├── ship.py                  # Ship systems and mechanics
│   ├── command_parser.py        # Natural language command parser
│   ├── game_engine.py           # Core game loop and state management
│   ├── ui.py                    # Pygame UI (in development)
│   ├── ai_system.py             # Enemy AI and GPT-4o integration (planned)
│   └── weapon_system.py         # Advanced weapon mechanics (planned)
├── tests/                        # Unit tests
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment configuration template
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

### Core Components

#### 1. **Universe Objects** (`universe_objects.py`, `universe.py`)
- **Base Class**: `UniverseObject` - Abstract base for all universe entities
- **Star Objects**: Infinite energy sources; refuel at 10%/turn
- **Planets**: Inhabitable worlds with crew recruitment (0-1000)
- **Black Holes**: Destroy ships within 3 AU instantly
- **Pulsars**: Disrupt sensors within 2 AU radius
- **Worm Holes**: Paired teleportation portals
- **Starbases**: Repair, refuel, restock; split friendly/npc (50/50)
- **Asteroid Fields**: Mining locations for cash generation

**Universe Generator**:
- Generates 10,000 x 10,000 AU universe
- 1000 stars, 10,000 planets, 100 black holes, 100 pulsars
- 20 wormhole pairs, 100 starbases, 1000 asteroid fields
- Validates minimum spacing between objects

#### 2. **Ship Systems** (`ship.py`)
Ships have three major subsystem categories:

**Weapon Systems**:
- **Phasers**: Instant-hit, 10 AU range, 5% damage, 50-100% accuracy, lock-on required
- **Photon Torpedos**: Slow projectiles, 20 AU range, 10% damage, 2 AU/turn speed
- Both consume energy to fire; weapons can be locked/unlocked
- Special hit mechanics: 1% warp core damage chance

**Propulsion Systems**:
- **Warp Drive**: 2-9 AU/turn (0.5% energy/turn), can exceed 9 AU with core temp buildup
- **Impulse Drive**: 1 AU/turn (1% energy/turn)
- **Warp Core**: Temperature management (overheating at >100°C)
- Cannot use both simultaneously

**Sensor System**:
- 50 AU detection range
- 20 AU detailed scan range
- Disrupted by pulsars within 2 AU
- Always active (no energy drain)

**Vital Statistics**:
- Damage (0-100%, auto-repair 5%/turn)
- Energy (0-100%, consumed by shields/propulsion/weapons)
- Shields (0-100%, drain 2%/turn when active)
- Crew (0-1000, ship disabled at 0)
- Photon Torpedos (0-50, 1% reload per turn at starbase)
- Cash ($, earned from destroyed npcs and mining)

#### 3. **Command Parser** (`command_parser.py`)
Natural language command processing supporting:
- `warp [speed]` - Set warp speed (2-9 AU/turn)
- `impulse [on|off]` - Activate/deactivate impulse drive
- `heading [degrees]` - Set ship heading (0-359°)
- `shields [up|down]` - Raise/lower shields
- `scan [target_id]` - Scan objects within 20 AU or specific target
- `lock [target_id]` - Lock phasers on target
- `fire` - Fire locked phasers
- `torpedo [target_id]` - Fire photon torpedo
- `status` - Display ship status
- `stop` / `all stop` - Stop all movement
- `nav [target_id]` - Auto-navigate to target
- `ask [question]` - Query game system
- `tell [target_id] [message]` - Communicate with objects
- `skip` - Skip turn without action

Supports command history (up arrow) for rapid re-execution.

#### 4. **Game Engine** (`game_engine.py`)
Core state management and turn processing:
- **Turn Processing**: Simultaneous command execution for player and all npcs
- **Universe Management**: 10,000+ objects tracked and updated each turn
- **Object Interactions**: 
  - Star refueling (10%/turn within 1 AU)
  - Asteroid mining (0-1000$ per attempt within 1 AU)
  - Black hole destruction (instant if within 3 AU)
  - Starbase repairs/refueling/restocking
  - Wormhole teleportation (1 AU entry range)

- **Combat Resolution**: Damage calculation, status effects, destruction
- **AI Coordination**: Enemy ship behavior and decision-making
- **Collision/Event Detection**: Special event triggers and interactions
- **Game State**: Win/loss conditions, turn counter, message queue

#### 5. **Identifier System** (`identifiers.py`)
Unique ID generation for all game objects:
- Format: `<2-letter prefix><numeric ID (0-99999)>`
- Prefixes: `st` (star), `pl` (planet), `bh` (black hole), `pu` (pulsar), 
  `wh` (wormhole), `sb` (starbase), `af` (asteroid field), `s` (ship)
- Guarantees uniqueness across entire game session
- Supports type lookups from ID

### Planned Components (Next Phase)

#### UI System (`ui.py`) - Pygame-based
- **Main Map**: 20x20 AU viewport, player ship centered
- **Minimap**: 500x500 AU overview with zoom (±300 AU)
- **Status Panel**: Graphical bars for all vital statistics
- **Message Log**: In-game messages instead of console
- **Command Prompt**: Natural language input field
- **Screen Resolution**: Auto-detect; default 2/3 max resolution
- **Resizable/Maximizable**: Full screen support

#### AI System (`ai_system.py`) - GPT-4o Integration
- 50 concurrent npc ships with personality
- OpenAI API integration for natural language npc responses
- Advanced tactics: coordinated attacks, strategic refueling
- Enemy ship captains respond to player `tell` commands
- Strategy learned through game progression

#### Advanced Weapon System (`weapon_system.py`)
- Torpedo animations and collision detection
- Phaser beam visualization
- Explosion effects (Death Star-style for ship destruction)
- Impact visual feedback
- Damage spreading and cascading failures

## Game Mechanics Summary

### Turn Structure
1. Player issues command (or skips)
2. Enemy ships execute AI-determined actions
3. Simultaneous movement and damage resolution
4. Object updates (damage repair, energy recovery, etc.)
5. Collision and event checking
6. Game state evaluation

### Energy Management
- **Shields**: 2% per turn when active
- **Warp Drive**: 0.5% per turn (+ overheating)
- **Impulse Drive**: 1% per turn
- **Weapons**: 1% per shot (phaser/torpedo)
- **Recovery**: Stars provide 10%/turn within 1 AU
- **Starbases**: 10%/turn refuel rate

### Combat Resolution
- **Phaser**: Instant 5% damage, 50-100% hit rate, 10 AU range
- **Torpedo**: 10% damage, 1-25% miss rate, 20 AU range, 1 AU/turn speed
- **Shields**: Block up to 100% of damage, regenerate slowly
- **Destruction**: At 100% damage, ship explodes
- **Status Effects**: Sensor disruption, warp core overheating

### Special Events
- **Black Hole**: Instant destruction if within 3 AU
- **Pulsar**: Sensor disruption within 2 AU
- **Wormhole**: Free teleportation within 1 AU (appears as paired exit)
- **Mining**: 0-1000$ per attempt at asteroid fields
- **Crew Recruitment**: 0-1000 crew from planets (shields down only)

## Running the Game

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your OpenAI API key (for npc AI)
```

### Launch
```bash
# Text-based version (current)
python -m src.main

# Pygame UI version (when available)
python -m src.ui
```

## Development Roadmap

### Phase 1 (Current): Core Mechanics ✓
- [x] Universe generation and object management
- [x] Ship systems and vital statistics
- [x] Command parsing
- [x] Turn-based game loop
- [x] Basic combat system
- [ ] Text-based UI refinement

### Phase 2: Visual Interface
- [ ] Pygame UI with map and minimap
- [ ] Animated projectiles and explosions
- [ ] Status panel with graphical indicators
- [ ] Minimap zoom functionality

### Phase 3: Advanced AI
- [ ] GPT-4o integration for npc ships
- [ ] Tactical decision-making
- [ ] Inter-ship communication
- [ ] Learning and adaptation

### Phase 4: Content & Polish
- [ ] Sound effects and music
- [ ] Additional universe objects
- [ ] Difficulty levels
- [ ] High score system
- [ ] Tutorial mode

## Technical Specifications

**Language**: Python 3.8+  
**UI Framework**: Pygame 2.5.0 (planned)  
**AI Integration**: OpenAI API (GPT-4o)  
**Dependencies**: numpy, python-dotenv  

**Performance Targets**:
- 60 FPS UI rendering
- Sub-100ms turn processing
- Support for 10,000+ simultaneous objects
- Real-time sensor updates

**Memory Requirements**:
- ~50MB base (all objects and state)
- ~2-5MB per turn (message queue, projectiles)

## Configuration

See `.env.example` for available configuration options:
```
OPENAI_API_KEY=<your-key>
```

## Code Quality

- Modular design: Each component independent and reusable
- Type hints throughout for IDE support
- Comprehensive docstrings on all major functions
- Separation of concerns: UI, logic, AI all decoupled
- Easy to extend: Add new universe objects or ship systems

## Future Enhancements

- Multiplayer networking
- Campaign mode with story progression
- Custom ship configurations
- Alien species with unique behaviors
- Trading and economic system
- Planet colonization
- Fleet management
- PvP competitive mode

---

**Version**: 0.1.0  
**Status**: Alpha (Core mechanics implemented, UI in development)
