"""
Wade Space Game - LLM Handler

Integrates OpenAI's GPT-4o for enemy ship AI decision making.
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class LLMHandler:
    """Handles communication with GPT-4o for enemy ship decision making."""
    
    def __init__(self):
        """Initialize the LLM handler with OpenAI API key."""
        self.enabled = OPENAI_AVAILABLE
        self.client = None
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            self.enabled = False
            print("[WARNING] OPENAI_API_KEY not found in .env file. LLM disabled.")
            return
        
        try:
            self.client = OpenAI(api_key=self.api_key)
            self.enabled = True
            print("[INFO] OpenAI LLM handler initialized successfully")
        except Exception as e:
            self.enabled = False
            print(f"[ERROR] Failed to initialize OpenAI client: {e}")
    
    def get_enemy_decision(self, 
                          enemy_ship_id: str,
                          enemy_position: tuple,
                          enemy_damage: float,
                          enemy_energy: float,
                          enemy_shields: float,
                          player_position: tuple,
                          player_damage: float,
                          nearby_objects: list,
                          turn_count: int) -> Dict[str, Any]:
        """
        Use GPT-4o to determine enemy ship behavior.
        
        Args:
            enemy_ship_id: ID of the enemy ship
            enemy_position: (x, y) position of enemy ship
            enemy_damage: Damage percentage of enemy ship (0-100)
            enemy_energy: Energy percentage of enemy ship (0-100)
            enemy_shields: Shield percentage of enemy ship (0-100)
            player_position: (x, y) position of player ship
            player_damage: Damage percentage of player ship (0-100)
            nearby_objects: List of nearby objects with their positions
            turn_count: Current turn number
        
        Returns:
            Dictionary with decision keys:
            - action: 'attack', 'evade', 'patrol', 'dock'
            - heading: 0-359 degrees
            - speed: 0-20 AU/turn
            - fire_phasers: True/False
            - fire_torpedos: True/False
            - reason: brief explanation
        """
        if not self.enabled or not self.client:
            return self._default_decision()
        
        try:
            # Build context for GPT-4o
            distance_to_player = (
                (player_position[0] - enemy_position[0])**2 + 
                (player_position[1] - enemy_position[1])**2
            ) ** 0.5
            
            prompt = self._build_decision_prompt(
                enemy_ship_id, enemy_position, enemy_damage, enemy_energy,
                enemy_shields, player_position, player_damage, distance_to_player,
                nearby_objects, turn_count
            )
            
            # Call GPT-4o
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using mini for faster/cheaper inference
                messages=[
                    {"role": "system", "content": "You are an AI captain of a hostile spacecraft engaged in combat. Make tactical decisions in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            decision = self._parse_gpt_response(response.choices[0].message.content)
            return decision
            
        except Exception as e:
            print(f"[ERROR] LLM decision failed: {e}")
            return self._default_decision()
    
    def _build_decision_prompt(self, 
                               enemy_ship_id: str,
                               enemy_position: tuple,
                               enemy_damage: float,
                               enemy_energy: float,
                               enemy_shields: float,
                               player_position: tuple,
                               player_damage: float,
                               distance_to_player: float,
                               nearby_objects: list,
                               turn_count: int) -> str:
        """Build a prompt for GPT-4o decision making."""
        
        nearby_desc = ""
        for i, obj in enumerate(nearby_objects[:5]):  # Limit to 5 nearest objects
            obj_id, obj_type, distance, direction = obj
            nearby_desc += f"  - {obj_id} ({obj_type}) at {distance:.1f} AU, heading {direction:.0f}°\n"
        
        prompt = f"""You are commanding enemy spacecraft {enemy_ship_id} in a space combat scenario.

CURRENT SITUATION (Turn {turn_count}):
Your Ship Status:
- Position: ({enemy_position[0]:.1f}, {enemy_position[1]:.1f})
- Damage: {enemy_damage:.1f}%
- Energy: {enemy_energy:.1f}%
- Shields: {enemy_shields:.1f}%

Enemy Ship (PLAYER):
- Position: ({player_position[0]:.1f}, {player_position[1]:.1f})
- Distance: {distance_to_player:.1f} AU
- Damage: {player_damage:.1f}%

Nearby Objects:
{nearby_desc if nearby_desc else "  None"}

TACTICAL CONTEXT:
- Sensor range: 50 AU
- Phaser range: 10 AU
- Torpedo range: 50 AU (travels 1 AU/turn)
- Warp range: 2-20 AU/turn
- Impulse range: 1 AU/turn

Make a tactical decision. Return ONLY valid JSON (no markdown, no code blocks):
{{
    "action": "attack"|"evade"|"patrol"|"dock",
    "heading": <0-359>,
    "speed": <0-20>,
    "fire_phasers": true|false,
    "fire_torpedos": true|false,
    "reason": "brief tactical explanation"
}}

Priorities:
1. If player is in phaser range (10 AU) and you're healthy, attack with phasers
2. If player is in torpedo range (50 AU) and you're healthy, fire torpedos for additional damage
3. If heavily damaged ({90 if enemy_damage >= 50 else 100}% damage), evade or seek repairs
4. If shields low, reposition or evade
5. Otherwise patrol the area

Weapons Strategy:
- Use phasers for close-range combat (< 10 AU)
- Use torpedos for medium-range attacks (10-50 AU) and as additional firepower
- Fire both phasers AND torpedos when player is in range and you have ammo
- Coordinate heading to keep approaching player while firing
"""
        return prompt
    
    def _parse_gpt_response(self, response_text: str) -> Dict[str, Any]:
        """Parse GPT-4o JSON response."""
        import json
        try:
            # Try to parse as JSON directly
            decision = json.loads(response_text)
            
            # Validate and normalize values
            decision['heading'] = max(0, min(359, int(decision.get('heading', 0))))
            decision['speed'] = max(0, min(20, float(decision.get('speed', 0))))
            decision['action'] = decision.get('action', 'patrol').lower()
            decision['fire_phasers'] = bool(decision.get('fire_phasers', False))
            decision['fire_torpedos'] = bool(decision.get('fire_torpedos', False))
            decision['reason'] = str(decision.get('reason', 'tactical decision'))
            
            return decision
        except json.JSONDecodeError:
            print(f"[WARNING] Failed to parse LLM response: {response_text[:100]}")
            return self._default_decision()
    
    def _default_decision(self) -> Dict[str, Any]:
        """Return a safe default decision."""
        return {
            'action': 'patrol',
            'heading': 0,
            'speed': 0,
            'fire_phasers': False,
            'fire_torpedos': False,
            'reason': 'LLM unavailable, using default patrol'
        }
    
    def get_enemy_response(self, enemy_ship_id: str, player_message: str) -> str:
        """Get a conversational response from enemy ship captain."""
        if not self.enabled or not self.client:
            return f"[{enemy_ship_id}]: No response."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"You are the captain of hostile spacecraft {enemy_ship_id} in space combat. Respond in character, briefly (1-2 sentences)."},
                    {"role": "user", "content": player_message}
                ],
                temperature=0.8,
                max_tokens=100
            )
            
            return f"[{enemy_ship_id}]: {response.choices[0].message.content}"
        except Exception as e:
            print(f"[ERROR] Failed to get enemy response: {e}")
            return f"[{enemy_ship_id}]: *no response*"
