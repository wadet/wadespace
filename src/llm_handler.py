"""
Wade Space Game - LLM Handler

Integrates OpenAI's GPT-4o for npc ship AI decision making.
"""

import os
import json
import datetime
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
    """Handles communication with GPT-4o for npc ship decision making."""
    
    def __init__(self):
        """Initialize the LLM handler with OpenAI API key."""
        self.enabled = OPENAI_AVAILABLE
        self.client = None
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.log_file = 'llm-queries.log'
        
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
    
    def get_npc_decision(self, 
                          npc_ship_id: str,
                          npc_position: tuple,
                          npc_damage: float,
                          npc_energy: float,
                          npc_shields: float,
                          npc_behavior: str,                        stance_to_player: str,                          player_position: tuple,
                          player_damage: float,
                          player_reputation: int,
                          nearby_objects: list,
                          nearby_npc_ships: list,
                          turn_count: int) -> Dict[str, Any]:
        """
        Use GPT-4o to determine npc ship behavior.
        
        Args:
            npc_ship_id: ID of the npc ship
            npc_position: (x, y) position of npc ship
            npc_damage: Damage percentage of npc ship (0-100)
            npc_energy: Energy percentage of npc ship (0-100)
            npc_shields: Shield percentage of npc ship (0-100)
            npc_behavior: Behavior trait ('aggressive', 'neutral', 'timid')
            player_position: (x, y) position of player ship
            player_damage: Damage percentage of player ship (0-100)
            player_reputation: Player's reputation (0-100)
            nearby_objects: List of nearby objects with their positions
            nearby_npc_ships: List of nearby npc ships (id, position, damage, distance)
            turn_count: Current turn number
        
        Returns:
            Dictionary with decision keys:
            - action: 'attack', 'evade', 'patrol', 'dock'
            - target_id: ship ID to target (player or npc ship)
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
                (player_position[0] - npc_position[0])**2 + 
                (player_position[1] - npc_position[1])**2
            ) ** 0.5
            
            prompt = self._build_decision_prompt(
                npc_ship_id, npc_position, npc_damage, npc_energy,
                npc_shields, npc_behavior, stance_to_player, player_position, player_damage, 
                player_reputation, distance_to_player, nearby_objects, nearby_npc_ships, turn_count
            )
            
            # Prepare request data for logging
            request_data = {
                'model': 'gpt-4o-mini',
                'messages': [
                    {"role": "system", "content": "You are an AI captain of a hostile spacecraft engaged in combat. Make tactical decisions in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                'temperature': 0.7,
                'max_tokens': 300,
                'response_format': {"type": "json_object"},
                'headers': {
                    'Authorization': f'Bearer {self.api_key[:10]}...{self.api_key[-4:]}',  # Masked API key
                    'Content-Type': 'application/json'
                }
            }
            
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
            
            # Log the API call
            response_data = {
                'id': response.id,
                'model': response.model,
                'choices': [{
                    'message': {
                        'role': response.choices[0].message.role,
                        'content': response.choices[0].message.content
                    },
                    'finish_reason': response.choices[0].finish_reason
                }],
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
            self._log_api_call('get_npc_decision', request_data, response_data)
            
            # Parse response
            decision = self._parse_gpt_response(response.choices[0].message.content)
            return decision
            
        except Exception as e:
            print(f"[ERROR] LLM decision failed: {e}")
            # Log the error
            self._log_api_call('get_npc_decision', request_data if 'request_data' in locals() else {}, None, str(e))
            return self._default_decision()
    
    def _build_decision_prompt(self, 
                               npc_ship_id: str,
                               npc_position: tuple,
                               npc_damage: float,
                               npc_energy: float,
                               npc_shields: float,
                               npc_behavior: str,
                               stance_to_player: str,
                               player_position: tuple,
                               player_damage: float,
                               player_reputation: int,
                               distance_to_player: float,
                               nearby_objects: list,
                               nearby_npc_ships: list,
                               turn_count: int) -> str:
        """Build a prompt for GPT-4o decision making."""
        
        nearby_desc = ""
        for i, obj in enumerate(nearby_objects[:5]):  # Limit to 5 nearest objects
            obj_id, obj_type, distance, direction = obj
            nearby_desc += f"  - {obj_id} ({obj_type}) at {distance:.1f} AU, heading {direction:.0f}°\n"
        
        # Format nearby npc ships
        nearby_enemies_desc = ""
        for i, npc_data in enumerate(nearby_npc_ships[:5]):  # Limit to 5 nearest npc ships
            npc_id, pos, damage, dist = npc_data
            nearby_enemies_desc += f"  - {npc_id} at {dist:.1f} AU, Damage: {damage:.1f}%, Position: ({pos[0]:.1f}, {pos[1]:.1f})\n"
        
        # Define behavior-specific attack and flee thresholds
        if npc_behavior == 'aggressive':
            attack_rep_threshold = 70
            flee_damage_threshold = 80
            behavior_desc = """You are an AGGRESSIVE captain. Your behavior:
- Attack any ship with reputation < 70
- Only withdraw from combat if your ship damage > 80%
- Prefer direct confrontation and offensive maneuvers"""
        elif npc_behavior == 'timid':
            attack_rep_threshold = 25
            flee_damage_threshold = 30
            behavior_desc = """You are a TIMID captain. Your behavior:
- Only attack if provoked (have taken damage) or target reputation < 25
- Flee if your ship damage > 30% (unless target reputation < 10)
- Prefer evasive tactics and cautious approaches"""
        else:  # neutral
            attack_rep_threshold = 50
            flee_damage_threshold = 50
            behavior_desc = """You are a NEUTRAL captain. Your behavior:
- Attack only if provoked (have taken damage) or target reputation < 50
- Engage in combat until your ship damage > 50%
- Balance between offense and defense"""
        
        # Format stance for display
        stance_display = stance_to_player.upper()
        stance_instruction = ""
        if stance_to_player == 'friendly':
            stance_instruction = "\n⚠️  CRITICAL: You are FRIENDLY toward the player. DO NOT attack them under any circumstances. Focus on patrolling or engaging other hostile NPCs."
        elif stance_to_player == 'hostile':
            stance_instruction = "\n⚠️  You are HOSTILE toward the player. Engage them according to your behavior trait."
        else:
            stance_instruction = "\n⚠️  You are NEUTRAL toward the player. Only engage if your behavior trait justifies it."
        
        prompt = f"""You are commanding npc spacecraft {npc_ship_id} in a space combat scenario.

CAPTAIN PERSONALITY: {npc_behavior.upper()}
{behavior_desc}

YOUR STANCE TOWARD PLAYER: {stance_display}{stance_instruction}

CURRENT SITUATION (Turn {turn_count}):
Your Ship Status:
- Position: ({npc_position[0]:.1f}, {npc_position[1]:.1f})
- Damage: {npc_damage:.1f}%
- Energy: {npc_energy:.1f}%
- Shields: {npc_shields:.1f}%
- Behavior Type: {npc_behavior}
- Stance to Player: {stance_display}

Player Ship:
- ID: PLAYER
- Position: ({player_position[0]:.1f}, {player_position[1]:.1f})
- Distance: {distance_to_player:.1f} AU
- Damage: {player_damage:.1f}%
- Reputation: {player_reputation}/100

Nearby NPC Ships (potential targets or threats):
{nearby_enemies_desc if nearby_enemies_desc else "  None"}

Nearby Objects:
{nearby_desc if nearby_desc else "  None"}

TACTICAL CONTEXT:
- Sensor range: 50 AU
- Phaser range: 10 AU
- Torpedo range: 50 AU (travels 1 AU/turn)
- Warp range: 2-20 AU/turn
- Impulse range: 1 AU/turn

TARGET SELECTION:
- You can attack the PLAYER or any nearby npc ships
- PRIORITIZE opportunistic targets: damaged npc ships are easier kills and less risky
- Consider these factors when choosing targets:
  * Distance: Closer targets are easier to engage
  * Damage: Enemies with >30% damage are vulnerable and good targets
  * Threat level: Who poses the biggest immediate threat?
- Attack damaged nearby enemies BEFORE the player if they're easier targets
- Heavily damaged enemies (>50% damage) should be prioritized for quick kills
- If multiple threats exist, attack the weakest/closest first

BEHAVIOR-SPECIFIC RULES:
- Attack threshold: Target reputation/damage justifies attack OR you have been provoked (damage > 0%)
- Flee threshold: Your damage > {flee_damage_threshold}%
{f"- Special rule: Continue attacking even when damaged if target is very weak (damage > 70%)" if npc_behavior == 'timid' else ""}

Make a tactical decision based on your {npc_behavior} personality. Return ONLY valid JSON (no markdown, no code blocks):
{{
    "action": "attack"|"evade"|"patrol"|"dock",
    "target_id": "PLAYER"|"<npc_ship_id>"|null,
    "heading": <0-359>,
    "speed": <0-20>,
    "fire_phasers": true|false,
    "fire_torpedos": true|false,
    "reason": "brief tactical explanation"
}}

Decision priorities based on personality:
1. Check if you should flee based on damage threshold ({flee_damage_threshold}%)
2. Select best target: PLAYER or a nearby npc ship (consider distance, damage, threat level)
3. If attacking: Use phasers if close (< 10 AU), torpedos for medium range (10-50 AU)
4. If fleeing/evading: Move away from threats (return fire only if already fired upon by target)
5. If not attacking or fleeing: patrol the area
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
            decision['target_id'] = decision.get('target_id', 'PLAYER')  # Default to player
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
            'target_id': 'PLAYER',
            'heading': 0,
            'speed': 0,
            'fire_phasers': False,
            'fire_torpedos': False,
            'reason': 'LLM unavailable, using default patrol'
        }
    
    def _log_api_call(self, method_name: str, request_data: Dict[str, Any], response_data: Any, error: Optional[str] = None):
        """Log API request and response to file."""
        try:
            timestamp = datetime.datetime.now().isoformat()
            
            log_entry = {
                'timestamp': timestamp,
                'method': method_name,
                'request': request_data,
                'response': response_data,
                'error': error
            }
            
            with open(self.log_file, 'a') as f:
                f.write('=' * 80 + '\n')
                f.write(f'TIMESTAMP: {timestamp}\n')
                f.write(f'METHOD: {method_name}\n')
                f.write('-' * 80 + '\n')
                f.write('REQUEST:\n')
                f.write(json.dumps(request_data, indent=2))
                f.write('\n' + '-' * 80 + '\n')
                if error:
                    f.write(f'ERROR: {error}\n')
                else:
                    f.write('RESPONSE:\n')
                    f.write(json.dumps(response_data, indent=2))
                f.write('\n' + '=' * 80 + '\n\n')
        except Exception as e:
            print(f"[WARNING] Failed to log API call: {e}")
    
    def get_npc_response(self, npc_ship_id: str, player_message: str) -> str:
        """Get a conversational response from npc ship captain."""
        if not self.enabled or not self.client:
            return f"[{npc_ship_id}]: No response."
        
        try:
            # Prepare request data for logging
            request_data = {
                'model': 'gpt-4o-mini',
                'messages': [
                    {"role": "system", "content": f"You are the captain of hostile spacecraft {npc_ship_id} in space combat. Respond in character, briefly (1-2 sentences)."},
                    {"role": "user", "content": player_message}
                ],
                'temperature': 0.8,
                'max_tokens': 100,
                'headers': {
                    'Authorization': f'Bearer {self.api_key[:10]}...{self.api_key[-4:]}',
                    'Content-Type': 'application/json'
                }
            }
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"You are the captain of hostile spacecraft {npc_ship_id} in space combat. Respond in character, briefly (1-2 sentences)."},
                    {"role": "user", "content": player_message}
                ],
                temperature=0.8,
                max_tokens=100
            )
            
            # Log the API call
            response_data = {
                'id': response.id,
                'model': response.model,
                'choices': [{
                    'message': {
                        'role': response.choices[0].message.role,
                        'content': response.choices[0].message.content
                    },
                    'finish_reason': response.choices[0].finish_reason
                }],
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
            self._log_api_call('get_npc_response', request_data, response_data)
            
            return f"[{npc_ship_id}]: {response.choices[0].message.content}"
        except Exception as e:
            print(f"[ERROR] Failed to get npc response: {e}")
            self._log_api_call('get_npc_response', request_data if 'request_data' in locals() else {}, None, str(e))
            return f"[{npc_ship_id}]: *no response*"
    
    def get_npc_taunt(self, npc_ship_id: str, context: Dict[str, Any]) -> str:
        """
        Generate a context-aware taunt from an npc ship captain or starbase commander.
        
        Args:
            npc_ship_id: ID of the npc ship or starbase
            context: Dictionary with combat context:
                - player_message: The message sent by the player
                - distance: Distance between ships in AU
                - player_damage: Player ship damage percentage (0-100)
                - npc_damage: NPC ship damage percentage (0-100)
                - player_shields: Player shield strength (0-100)
                - npc_shields: NPC shield strength (0-100)
                - turn_count: Current game turn
                - entity_type: 'ship' or 'starbase'
        
        Returns:
            String with npc captain's/commander's taunt/response
        """
        if not self.enabled or not self.client:
            return f"[{npc_ship_id}]: *no response*"
        
        try:
            # Build a rich prompt with combat context
            player_message = context.get('player_message', '')
            distance = context.get('distance', 0)
            player_damage = context.get('player_damage', 0)
            npc_damage = context.get('npc_damage', 0)
            player_shields = context.get('player_shields', 0)
            npc_shields = context.get('npc_shields', 0)
            entity_type = context.get('entity_type', 'ship')
            
            # Determine tactical situation
            situation_notes = []
            
            if entity_type == 'starbase':
                # Starbases are defensive installations
                situation_notes.append("you are a heavily fortified starbase with powerful weapons")
                if npc_damage < 30:
                    situation_notes.append("your defenses are at full strength")
                elif npc_damage < 60:
                    situation_notes.append("your station has sustained some damage")
                else:
                    situation_notes.append("your station is heavily damaged but still operational")
            else:
                # Ships are mobile combat vessels
                if npc_damage < 30:
                    situation_notes.append("your ship is in excellent condition")
                elif npc_damage < 60:
                    situation_notes.append("your ship has taken some damage")
                else:
                    situation_notes.append("your ship is badly damaged")
            
            if player_damage > 60:
                situation_notes.append("the player's ship is crippled")
            elif player_damage > 30:
                situation_notes.append("the player's ship is damaged")
            else:
                situation_notes.append("the player's ship is still strong")
            
            if distance < 5:
                situation_notes.append("they are very close (in weapons range)")
            elif distance < 15:
                situation_notes.append("they are at medium range")
            else:
                situation_notes.append("they are far away")
            
            # Build role-specific prompt
            if entity_type == 'starbase':
                role_description = f"You are the commander of hostile starbase {npc_ship_id}, a fortified military installation in space."
                personality = """Respond as a stern, authoritative station commander. Be intimidating and territorial.
- Emphasize your station's superior firepower and defenses
- Warn intruders they're in hostile territory
- Be commanding and imperious
- If damaged: be resolute and unyielding, promising reinforcements"""
            else:
                role_description = f"You are the captain of hostile spacecraft {npc_ship_id} engaged in space combat."
                personality = """Respond as a fierce, confident npc captain. Be taunting, threatening, or defiant depending on the situation.
- If winning: be arrogant and mocking
- If losing: be defiant and threatening revenge
- If evenly matched: be cocky and challenging"""
            
            system_prompt = f"""{role_description}
Tactical situation: {', '.join(situation_notes)}.
Your damage: {npc_damage:.0f}%, shields: {npc_shields:.0f}%
NPC damage: {player_damage:.0f}%, shields: {player_shields:.0f}%
Distance: {distance:.1f} AU

The player says: "{player_message}"

{personality}
Keep your response to 1-2 sentences maximum. Make it punchy and dramatic."""
            
            # Prepare request data for logging
            request_data = {
                'model': 'gpt-4o-mini',
                'messages': [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": player_message}
                ],
                'temperature': 0.9,
                'max_tokens': 100,
                'headers': {
                    'Authorization': f'Bearer {self.api_key[:10]}...{self.api_key[-4:]}',
                    'Content-Type': 'application/json'
                }
            }
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": player_message}
                ],
                temperature=0.9,  # Higher temperature for more varied/creative taunts
                max_tokens=100
            )
            
            # Log the API call
            response_data = {
                'id': response.id,
                'model': response.model,
                'choices': [{
                    'message': {
                        'role': response.choices[0].message.role,
                        'content': response.choices[0].message.content
                    },
                    'finish_reason': response.choices[0].finish_reason
                }],
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
            self._log_api_call('get_npc_taunt', request_data, response_data)
            
            return f"[{npc_ship_id}]: {response.choices[0].message.content}"
        except Exception as e:
            print(f"[ERROR] Failed to generate npc taunt: {e}")
            self._log_api_call('get_npc_taunt', request_data if 'request_data' in locals() else {}, None, str(e))
            return f"[{npc_ship_id}]: *static*"
    
    def answer_player_question(self, question: str, universe_data: Dict[str, Any]) -> str:
        """
        Use GPT-4o to answer player questions about the universe.
        
        Args:
            question: The player's natural language question
            universe_data: Dictionary containing:
                - player_position: (x, y) tuple
                - universe_objects: dict of all objects with their data
                - npc_ships: dict of all npc ships with their data
                - nearby_objects: list of objects within sensor range
        
        Returns:
            String answer to the question
        """
        if not self.enabled or not self.client:
            return "Ship's computer offline. LLM unavailable."
        
        try:
            # Build context for the AI
            prompt = self._build_question_prompt(question, universe_data)
            
            # Prepare request data for logging
            request_data = {
                'model': 'gpt-4o-mini',
                'messages': [
                    {"role": "system", "content": "You are the ship's onboard computer AI assistant. Answer the captain's questions about the universe, objects, and tactical situation. Be concise and factual. Format your responses clearly with object IDs, coordinates, and distances."},
                    {"role": "user", "content": prompt}
                ],
                'temperature': 0.3,
                'max_tokens': 500,
                'headers': {
                    'Authorization': f'Bearer {self.api_key[:10]}...{self.api_key[-4:]}',
                    'Content-Type': 'application/json'
                }
            }
            
            # Call GPT-4o
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are the ship's onboard computer AI assistant. Answer the captain's questions about the universe, objects, and tactical situation. Be concise and factual. Format your responses clearly with object IDs, coordinates, and distances."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for factual responses
                max_tokens=500
            )
            
            # Log the API call
            response_data = {
                'id': response.id,
                'model': response.model,
                'choices': [{
                    'message': {
                        'role': response.choices[0].message.role,
                        'content': response.choices[0].message.content
                    },
                    'finish_reason': response.choices[0].finish_reason
                }],
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
            self._log_api_call('answer_player_question', request_data, response_data)
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"[ERROR] Failed to answer question: {e}")
            self._log_api_call('answer_player_question', request_data if 'request_data' in locals() else {}, None, str(e))
            return f"Error processing question: {str(e)}"
    
    def _build_question_prompt(self, question: str, universe_data: Dict[str, Any]) -> str:
        """Build a prompt for the AI to answer player questions."""
        player_pos = universe_data.get('player_position', (0, 0))
        all_objects = universe_data.get('nearby_objects', [])
        npc_ships = universe_data.get('npc_ships', {})
        search_entire_universe = universe_data.get('search_entire_universe', False)
        sensor_range = universe_data.get('sensor_range', 50)
        
        # Determine search scope message
        search_scope = "ENTIRE UNIVERSE" if search_entire_universe else f"SENSOR RANGE ({sensor_range} AU)"
        
        # Smart filtering: Prioritize relevant object types based on the question
        lower_q = question.lower()
        priority_types = set()
        
        # Check for friendly/hostile/enemy filters for starbases
        starbase_filter = None  # None, 'friendly', or 'hostile'
        if any(word in lower_q for word in ['base', 'starbase', 'station']):
            priority_types.add('Starbase')
            # Check if asking for friendly or hostile starbases specifically
            if any(word in lower_q for word in ['friendly', 'allied']):
                starbase_filter = 'friendly'
            elif any(word in lower_q for word in ['hostile', 'enemy', 'npc', 'unfriendly']):
                starbase_filter = 'hostile'
        
        # Determine which object types are relevant to the question
        if any(word in lower_q for word in ['star', 'sun']):
            priority_types.add('Star')
        if any(word in lower_q for word in ['planet', 'world']):
            priority_types.add('Planet')
        if any(word in lower_q for word in ['black hole', 'blackhole']):
            priority_types.add('BlackHole')
        if any(word in lower_q for word in ['wormhole', 'worm hole']):
            priority_types.add('WormHole')
        if any(word in lower_q for word in ['pulsar']):
            priority_types.add('Pulsar')
        if any(word in lower_q for word in ['asteroid']):
            priority_types.add('AsteroidField')
        
        # If no specific type mentioned, show a reasonable mix
        if not priority_types:
            priority_types = {'Starbase', 'Star', 'Planet', 'BlackHole'}
        
        # Separate objects by priority and apply starbase filter if needed
        priority_objects = []
        other_objects = []
        
        for obj_id, obj_data in all_objects:
            obj_type = obj_data['type']
            
            # Apply starbase filtering if specified
            if obj_type == 'Starbase' and starbase_filter:
                stance = obj_data.get('stance', 'neutral')
                if starbase_filter == 'friendly' and stance != 'friendly':
                    continue  # Skip non-friendly starbases when asking for friendly
                elif starbase_filter == 'hostile' and stance != 'hostile':
                    continue  # Skip non-hostile starbases when asking for hostile
            
            if obj_type in priority_types:
                priority_objects.append((obj_id, obj_data))
            else:
                other_objects.append((obj_id, obj_data))
        
        # Sort both lists by distance to maintain ascending order
        priority_objects.sort(key=lambda x: x[1].get('distance', 0))
        other_objects.sort(key=lambda x: x[1].get('distance', 0))
        
        # Combine: show all priority objects (up to 100), then fill remaining with others
        max_display = 100
        display_objects = priority_objects[:max_display]
        remaining_slots = max_display - len(display_objects)
        if remaining_slots > 0:
            display_objects.extend(other_objects[:remaining_slots])
        
        # Build object counts summary
        object_count_by_type = {}
        starbase_counts_by_stance = {'hostile': 0, 'friendly': 0, 'neutral': 0}
        
        for obj_id, obj_data in all_objects:
            obj_type = obj_data['type']
            object_count_by_type[obj_type] = object_count_by_type.get(obj_type, 0) + 1
            
            # Track starbase counts by stance
            if obj_type == 'Starbase':
                stance = obj_data.get('stance', 'neutral')
                starbase_counts_by_stance[stance] = starbase_counts_by_stance.get(stance, 0) + 1
        
        # Build nearby objects summary  
        nearby_desc = ""
        
        if search_entire_universe and len(all_objects) > max_display:
            nearby_desc += f"TOTAL OBJECTS SCANNED: {len(all_objects)}\n"
            nearby_desc += "Object counts by type:\n"
            for obj_type, count in sorted(object_count_by_type.items()):
                if obj_type == 'Starbase':
                    nearby_desc += f"  - {obj_type}: {count} total "
                    nearby_desc += f"(Hostile: {starbase_counts_by_stance['hostile']}, "
                    nearby_desc += f"Friendly: {starbase_counts_by_stance['friendly']}, "
                    nearby_desc += f"Neutral: {starbase_counts_by_stance['neutral']})\n"
                else:
                    nearby_desc += f"  - {obj_type}: {count}\n"
            nearby_desc += f"\nShowing {len(display_objects)} most relevant objects (prioritized by question):\n"
        
        # Show individual objects
        for obj_id, obj_data in display_objects:
            obj_type = obj_data.get('type', 'unknown')
            pos = obj_data.get('position', (0, 0))
            distance = obj_data.get('distance', 0)
            
            # Add starbase status
            if obj_type == 'Starbase':
                stance = obj_data.get('stance', 'neutral')
                status = stance.upper()
                nearby_desc += f"  - {obj_id} ({obj_type} - {status}): Position ({pos[0]:.1f}, {pos[1]:.1f}), Distance {distance:.1f} AU\n"
            else:
                nearby_desc += f"  - {obj_id} ({obj_type}): Position ({pos[0]:.1f}, {pos[1]:.1f}), Distance {distance:.1f} AU\n"
        
        # Build npc ships summary (with stance information)
        npc_desc = ""
        npc_ships_by_distance = sorted(
            [(npc_id, npc_data) for npc_id, npc_data in npc_ships.items() if not npc_data.get('is_destroyed', False)],
            key=lambda x: x[1].get('distance', 0)
        )
        
        for npc_id, npc_data in npc_ships_by_distance:
            pos = npc_data.get('position', (0, 0))
            distance = npc_data.get('distance', 0)
            health = 100.0 - npc_data.get('damage', 0)
            shields = npc_data.get('shields', 0)
            stance = npc_data.get('stance_to_player', 'neutral')
            stance_label = stance.upper()
            npc_desc += f"  - {npc_id} (Stance: {stance_label}): Position ({pos[0]:.1f}, {pos[1]:.1f}), Distance {distance:.1f} AU, Health {health:.1f}%, Shields {shields:.1f}%\n"
        
        prompt = f"""The captain asks: "{question}"

CURRENT SITUATION:
Your Ship Position: ({player_pos[0]:.1f}, {player_pos[1]:.1f})
Search Scope: {search_scope}

OBJECTS (sorted by distance from your ship, filtered by relevance to question):
{nearby_desc if nearby_desc else "  None detected"}

NPC SHIPS (sorted by distance, with their stance toward you):
{npc_desc if npc_desc else "  None detected"}

AVAILABLE OBJECT TYPES IN UNIVERSE:
- Stars (st####): Energy sources
- Planets (pl####): Some are inhabited  
- Starbases (sb####): Repairs and supplies. Each starbase has a stance: FRIENDLY, NEUTRAL, or HOSTILE
- Black Holes (bh####): Dangerous gravitational anomalies
- Pulsars (pu####): Disrupt sensors
- Wormholes (wh####): Teleport to paired wormhole
- Asteroid Fields (af####): Mining opportunities
- NPC Ships (s####): Other vessels with varying stances (HOSTILE, NEUTRAL, or FRIENDLY)

IMPORTANT NOTES:
- When asked about "enemy base", "hostile base", or "npc base", look for Starbase objects with stance HOSTILE.
- When asked about "friendly base", look for Starbase objects with stance FRIENDLY.
- When asked about "neutral base", look for Starbase objects with stance NEUTRAL.
- When asked about "enemy ship", "hostile ship", look for NPC Ships with stance HOSTILE.
- When asked about "friendly ship", look for NPC Ships with stance FRIENDLY.
- When asked about "neutral ship", look for NPC Ships with stance NEUTRAL.
- Starbases show their stance in the object list (e.g., "sb1234 (Starbase - HOSTILE)").
- NPC Ships show their stance in the ship list (e.g., "s1234 (Stance: HOSTILE)").
- The objects are already sorted by distance from your ship - the first matching object of any type is the nearest.

Based on the available data, answer the captain's question concisely and accurately. 
If asking for "nearest" or "closest" object, search through all listed objects and identify the closest one of that type.
For enemy/hostile bases, ONLY report starbases with stance HOSTILE.
For friendly bases, ONLY report starbases with stance FRIENDLY.
For enemy/hostile ships, ONLY report NPC ships with stance HOSTILE.
For friendly ships, ONLY report NPC ships with stance FRIENDLY.
Always include the object ID, position coordinates, and distance in your answer.
If you don't have enough data to answer, say so clearly."""
        
        return prompt
