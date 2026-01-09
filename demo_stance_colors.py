#!/usr/bin/env python3
"""
Visual demonstration of stance system colors.
Creates a simple visual report showing how entities appear.
"""

from src.game_engine import GameEngine
from src.universe_objects import Starbase

def visual_stance_demo():
    """Create a visual demonstration of the stance color system."""
    print("=" * 70)
    print("WADE SPACE - STANCE SYSTEM VISUAL DEMONSTRATION")
    print("=" * 70)
    
    engine = GameEngine(universe_seed=42)
    
    # Header
    print("\n┌─────────────────────────────────────────────────────────────────────┐")
    print("│  HOW ENTITIES APPEAR BASED ON THEIR STANCE TOWARD THE PLAYER      │")
    print("└─────────────────────────────────────────────────────────────────────┘")
    
    print("\nColor Legend:")
    print("  🔴 RED    = Hostile  (will attack on sight)")
    print("  🟡 YELLOW = Neutral  (behavior-based, may attack if provoked)")
    print("  🟢 GREEN  = Friendly (will not attack)")
    
    # Show NPC ships
    print("\n" + "─" * 70)
    print("NPC SHIPS (Bird of Prey shape)")
    print("─" * 70)
    
    hostile_npcs = []
    neutral_npcs = []
    friendly_npcs = []
    
    for npc_id, npc_ship in engine.npc_ships.items():
        stance = npc_ship.stances.get(engine.player_ship.id, 'neutral')
        distance = npc_ship.position.distance_to(engine.player_ship.position)
        
        if stance == 'hostile':
            hostile_npcs.append((npc_id, distance, npc_ship.behavior_trait))
        elif stance == 'friendly':
            friendly_npcs.append((npc_id, distance, npc_ship.behavior_trait))
        else:
            neutral_npcs.append((npc_id, distance, npc_ship.behavior_trait))
    
    # Show hostile NPCs
    print(f"\n🔴 HOSTILE NPCs (RED) - {len(hostile_npcs)} total:")
    for npc_id, dist, behavior in sorted(hostile_npcs, key=lambda x: x[1])[:5]:
        print(f"   {npc_id:8s}  Distance: {dist:7.1f} AU  Behavior: {behavior:10s}  Color: RED")
    
    # Show neutral NPCs
    print(f"\n🟡 NEUTRAL NPCs (YELLOW) - {len(neutral_npcs)} total:")
    for npc_id, dist, behavior in sorted(neutral_npcs, key=lambda x: x[1])[:5]:
        print(f"   {npc_id:8s}  Distance: {dist:7.1f} AU  Behavior: {behavior:10s}  Color: YELLOW")
    
    # Show friendly NPCs
    print(f"\n🟢 FRIENDLY NPCs (GREEN) - {len(friendly_npcs)} total:")
    for npc_id, dist, behavior in sorted(friendly_npcs, key=lambda x: x[1])[:5]:
        print(f"   {npc_id:8s}  Distance: {dist:7.1f} AU  Behavior: {behavior:10s}  Color: GREEN")
    
    # Show starbases
    print("\n" + "─" * 70)
    print("STARBASES (Square shape)")
    print("─" * 70)
    
    starbases = [obj for obj in engine.universe_objects.values() if isinstance(obj, Starbase)]
    
    hostile_sbs = []
    neutral_sbs = []
    friendly_sbs = []
    
    for sb in starbases:
        stance = sb.stances.get(engine.player_ship.id, 'neutral')
        distance = sb.position.distance_to(engine.player_ship.position)
        
        if stance == 'hostile':
            hostile_sbs.append((sb.id, distance))
        elif stance == 'friendly':
            friendly_sbs.append((sb.id, distance))
        else:
            neutral_sbs.append((sb.id, distance))
    
    # Show hostile starbases
    print(f"\n🔴 HOSTILE Starbases (RED) - {len(hostile_sbs)} total:")
    for sb_id, dist in sorted(hostile_sbs, key=lambda x: x[1])[:5]:
        print(f"   {sb_id:8s}  Distance: {dist:7.1f} AU  Color: RED")
    
    # Show neutral starbases
    print(f"\n🟡 NEUTRAL Starbases (YELLOW) - {len(neutral_sbs)} total:")
    for sb_id, dist in sorted(neutral_sbs, key=lambda x: x[1])[:5]:
        print(f"   {sb_id:8s}  Distance: {dist:7.1f} AU  Color: YELLOW")
    
    # Show friendly starbases
    print(f"\n🟢 FRIENDLY Starbases (GREEN) - {len(friendly_sbs)} total:")
    for sb_id, dist in sorted(friendly_sbs, key=lambda x: x[1])[:5]:
        print(f"   {sb_id:8s}  Distance: {dist:7.1f} AU  Color: GREEN")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    total_npcs = len(hostile_npcs) + len(neutral_npcs) + len(friendly_npcs)
    total_sbs = len(hostile_sbs) + len(neutral_sbs) + len(friendly_sbs)
    
    print(f"\nPlayer Ship: {engine.player_ship.id}")
    print(f"Position: ({engine.player_ship.position.x:.1f}, {engine.player_ship.position.y:.1f})")
    
    print(f"\nNPC Ships ({total_npcs} total):")
    print(f"  🔴 Hostile:  {len(hostile_npcs):3d} ({len(hostile_npcs)/total_npcs*100:.0f}%)")
    print(f"  🟡 Neutral:  {len(neutral_npcs):3d} ({len(neutral_npcs)/total_npcs*100:.0f}%)")
    print(f"  🟢 Friendly: {len(friendly_npcs):3d} ({len(friendly_npcs)/total_npcs*100:.0f}%)")
    
    print(f"\nStarbases ({total_sbs} total):")
    print(f"  🔴 Hostile:  {len(hostile_sbs):3d} ({len(hostile_sbs)/total_sbs*100:.0f}%)")
    print(f"  🟡 Neutral:  {len(neutral_sbs):3d} ({len(neutral_sbs)/total_sbs*100:.0f}%)")
    print(f"  🟢 Friendly: {len(friendly_sbs):3d} ({len(friendly_sbs)/total_sbs*100:.0f}%)")
    
    print("\n" + "=" * 70)
    print("In the game UI:")
    print("  • All entities are colored based on their stance toward YOU")
    print("  • Shapes remain the same (Birds of Prey, Squares, etc.)")
    print("  • This applies to both the 2D map AND the minimap")
    print("  • Hostile entities will attack you when in range")
    print("=" * 70)


if __name__ == '__main__':
    visual_stance_demo()
