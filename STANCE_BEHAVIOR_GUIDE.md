# Quick Reference: Stance and Behavior Traits

## What You'll See Now

### In Scan Results (scan command)

**General Scan:**
```
scan

Scan results (sensor range: 50 AU):
  s4375: SHIP @ 10.0 AU [hostile, aggressive]
  sb2707: ⊕ @ 21.2 AU [friendly]
  s6805: SHIP @ 26.9 AU [neutral, neutral]
  ```

**Specific Scan:**
```
scan s4375

Scan of s4375: Ship at 10.0 AU
  Status: operational, Damage: 0.0%, Energy: 100.0%
  Shields: down (100.0%), Crew: 1000, Behavior: aggressive
  Speed: 0.0 AU/turn, Heading: 0°
  Stance: hostile
```

### In HAL Queries (ask/hal commands)

**Ship Query:**
```
hal what is s4375

Enemy ship s4375 (aggressive):
  Location: (6008.0, 6000.0)
  Distance from you: 8.0 AU
  Health: 100.0%
  Shields: 100.0%
  Status: ACTIVE
  Stance: hostile
```

**Starbase Query:**
```
hal what is sb2707

Object sb2707 (⊕):
  Type: Starbase
  Location: (6018.0, 6018.0)
  Distance from you: 25.5 AU
  Stance: friendly
```

## Understanding Stance

| Stance | Meaning | Color Code (Future) |
|--------|---------|-------------------|
| **hostile** | Will attack you | 🔴 Red |
| **friendly** | Will not attack you | 🟢 Green |
| **neutral** | Cautious, won't initiate attack | 🟡 Yellow |

### Tactical Implications

- **Hostile**: Prepare for combat or avoid
- **Friendly**: Safe to approach, may offer assistance
- **Neutral**: Can become hostile if provoked

## Understanding Behavior Traits (Ships Only)

| Behavior | Combat Style | When They Flee |
|----------|-------------|----------------|
| **aggressive** | Attacks readily, pursues | Only when critically damaged (>70%) |
| **neutral** | Standard tactics | When moderately damaged (>40%) |
| **timid** | Avoids combat if possible | Early, when lightly damaged (>20%) |

### Tactical Implications

**Hostile + Aggressive** = ⚠️ VERY DANGEROUS
- Will attack immediately
- Fights to near-destruction
- High priority threat

**Hostile + Timid** = ⚠️ CAUTIOUS THREAT
- May flee if you're winning
- Easier to chase off
- Lower priority threat

**Hostile + Neutral** = ⚠️ STANDARD THREAT
- Standard enemy behavior
- Will flee when damaged enough
- Medium priority threat

**Friendly + Any Behavior** = ✅ SAFE
- Will not attack you
- May assist in combat
- Potential ally

**Neutral + Any Behavior** = ⚡ UNPREDICTABLE
- Won't attack unless provoked
- May flee or defend if threatened
- Diplomatic approach recommended

## Combat Decision Matrix

### Example Scenarios

**Scenario 1: Multiple Hostiles**
```
Scan results:
  s1001: SHIP @ 8 AU [hostile, aggressive]
  s1002: SHIP @ 12 AU [hostile, timid]
  s1003: SHIP @ 15 AU [hostile, neutral]
```

**Recommended Strategy:**
1. Lock and fire on s1002 (timid) first - will flee quickly
2. Then target s1003 (neutral) - moderate threat
3. Finally engage s1001 (aggressive) - will fight longest

**Scenario 2: Mixed Stances**
```
Scan results:
  s2001: SHIP @ 10 AU [hostile, aggressive]
  s2002: SHIP @ 15 AU [friendly, neutral]
  s2003: SHIP @ 20 AU [neutral, timid]
```

**Recommended Strategy:**
1. Engage s2001 (hostile, aggressive) - immediate threat
2. Avoid s2002 (friendly) - not a threat
3. Ignore s2003 (neutral, timid) - will likely flee anyway

**Scenario 3: Starbase Approach**
```
Scan results:
  sb101: ⊕ @ 5 AU [friendly]
  sb102: ⊕ @ 25 AU [hostile]
  sb103: ⊕ @ 40 AU [neutral]
```

**Recommended Strategy:**
1. Approach sb101 for repairs/supplies
2. Avoid sb102 or prepare for base defenses
3. sb103 may offer trading opportunities

## Commands to Use

```bash
# See all nearby objects with stance/behavior
scan

# Get detailed info on specific object
scan <object_id>

# Query system about object
hal what is <object_id>

# Find nearest by stance (HAL understands stance keywords)
hal nearest hostile
hal friendly starbase
hal neutral ship
```

## Pro Tips

1. **Use scan regularly** - Stance and behavior help you prioritize targets
2. **Timid enemies first** - Easy wins, reduces enemy numbers quickly
3. **Friendly starbases** - Use for repairs during long missions
4. **Aggressive enemies** - Save for last or avoid if outnumbered
5. **Neutral ships** - Potential non-hostile encounters, approach cautiously

---

*Remember: Stance can change based on your reputation and actions!*
