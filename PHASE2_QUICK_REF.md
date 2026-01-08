# Wade Space - Phase 2 Quick Reference

## 🚀 Launch the Game

```bash
cd /home/wadet/workspace/wadespace
source venv/bin/activate
python -m src.ui_main
```

## 🎮 Keyboard Controls

| Key | Action |
|-----|--------|
| **ENTER** | Execute command |
| **BACKSPACE** | Delete character |
| **↑** | Previous command |
| **↓** | Next command |
| **ESC** | Clear input |
| **Scroll ↑** | Minimap zoom in |
| **Scroll ↓** | Minimap zoom out |

## ⚡ Commands

### Navigation
```
warp 5                Set warp speed (2-9 AU/turn)
impulse on/off        Impulse drive (1 AU/turn)
heading 180           Set course (0-359°)
stop                  All stop (end movement)
nav st12345           Auto-navigate to object
skip                  End turn without action
```

### Scanning
```
scan                  List nearby objects (50 AU range)
scan st12345          Detailed scan of specific object
status                Show ship vitals & position
```

### Combat
```
shields up            Raise shields
shields down          Lower shields
lock on s1            Lock phasers on target
fire                  Fire phasers (5% damage, 10 AU range)
tor s1                Fire torpedo (10% damage, 20 AU range)
```

### Communication
```
tell s1 message       Send message to other ship
ask [question]        Query the system
```

## 📊 UI Layout

```
┌────────────────────────────────────────────┐
│ Main Map (60%)        │ Status Panel (35%)  │
│ 20×20 AU viewport     │ • Energy bar        │
│ Player & npcs      │ • Shields bar       │
│ Objects nearby        │ • Damage bar        │
│                       │ • Hull bar          │
│                       │ • Vital stats       │
├───────────────────────┼────────────────────┤
│                       │ Minimap (35%)       │
│                       │ 500 AU view        │
│                       │ Zoom ±300 AU       │
├───────────────────────┼────────────────────┤
│                       │ Messages (20%)      │
│                       │ Last 50 events      │
├───────────────────────┼────────────────────┤
│                       │ Command Input (10%) │
│                       │ Type & execute      │
└────────────────────────────────────────────┘
```

## 🗺️ Object Symbols

| Symbol | Object | Color |
|--------|--------|-------|
| ★ | Star | Yellow |
| ● | Planet | Cyan |
| ⊗ | Black Hole | Black |
| ◇ | Pulsar | Magenta |
| ◎ | Wormhole | Cyan |
| ⊕ | Starbase | Green/Red |
| ✕ | Asteroid | Gray |
| △ | Player Ship | Green |
| ▽ | NPC Ship | Red |

## 💊 Vitals & Resources

| Stat | Range | Notes |
|------|-------|-------|
| Energy | 0-100% | Powers everything |
| Shields | 0-100% | Protect hull |
| Damage | 0-100% | Hull condition |
| Crew | 0-1,000 | Needed for repairs |
| Cash | $0+ | Buy torpedos/supplies |
| Torpedos | 0-50 | Ammo reserve |
| Warp Temp | 0-100% | Warp core heat |

## 🎯 Command Tips

### Fuel Management
- **Stars**: Free energy (10%/turn within 1 AU)
- **Starbases**: Repair, refuel, restock
- **Impulse**: Efficient (1 AU/turn, 1% energy)
- **Warp**: Fast but energy expensive (2-9 AU/turn)

### Combat Strategy
- **Shields**: Reduce incoming damage
- **Phasers**: Instant fire, 10 AU range
- **Torpedos**: Slower, 20 AU range, more damage
- **Movement**: Change heading to evade

### Resources
- **Mining asteroids**: Cash reward (0-1,000$)
- **Recruit crew**: On planets
- **Buy torpedos**: At starbases
- **Repair hull**: At starbases (costs crew)

### Exploration
- **Scan**: Find nearby objects
- **Navigate**: Auto-go to waypoint
- **Minimap**: See 500 AU overview
- **Zoom**: +300 AU on minimap

## ⚠️ Hazards

| Hazard | Effect | Avoidance |
|--------|--------|-----------|
| Black Hole | Instant destruction (3 AU radius) | Stay >3 AU away |
| Pulsar | Sensor disruption (2 AU radius) | Use manual navigation |
| Wormhole | Teleportation | Use if needed |
| Enemy ships | Weapons fire | Keep distance |

## 📈 Game Statistics

```
Universe Size:  10,000 × 10,000 AU
Objects:        12,340 total
NPC Ships:    50 active
Commands:       14 types
Energy Cap:     100%
Shield Cap:     100%
Crew Max:       1,000
Torpedo Max:    50
```

## 🔧 Customization (Advanced)

Edit `src/ui.py` to customize:

**Screen Size**
```python
FONT_SIZE = 14              # UI font size
VIEWPORT_SIZE = 20.0        # AU visible on map
MINIMAP_SIZE = 500.0        # AU on minimap
TARGET_FPS = 60             # Frame rate
```

**Colors**
```python
Colors.HEALTHY = (0, 200, 0)        # Green
Colors.WARNING = (255, 200, 0)      # Orange
Colors.DANGER = (255, 0, 0)         # Red
```

## 🐛 Troubleshooting

### UI won't start
```bash
# Check pygame installed
python -c "import pygame; print(pygame.__version__)"

# Verify virtual environment
which python  # Should show venv/bin/python

# Try explicit Python version
python3 -m src.ui_main
```

### Slow performance
- Reduce window size
- Close other applications
- Disable visual effects (modify effects.py)

### No display error
- On headless: Use X11 forwarding
- Or run text mode: `python -m src.main`

### Command not working
- Check spelling (case-insensitive)
- Use arrow keys for history
- ESC to clear bad input

## 📚 Full Guides

- **UI_GUIDE.md** - Complete UI documentation
- **GETTING_STARTED.md** - Gameplay tutorial
- **PHASE2_SUMMARY.md** - Technical details

## 🎮 Example Play Session

```
Starting position: Near star st1

1. $ scan
   → See nearby objects

2. $ heading 180
   → Set course

3. $ warp 5
   → Travel at high speed

4. $ shields up
   → Prepare for combat

5. $ scan s1
   → Identify npc

6. $ lock on s1
   → Target locked

7. $ fire
   → Launch phasers

8. $ tor s1
   → Fire torpedo

9. $ status
   → Check health

10. $ nav sb1
    → Head to starbase
```

---

**Ready to play Wade Space? Launch with `python -m src.ui_main`! 🚀**
