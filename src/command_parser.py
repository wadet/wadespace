"""
Wade Space Game - Command Parser

Parses natural language commands from the player.
"""

from typing import Optional, Tuple, List
import re


class CommandParser:
    """Parses natural language commands into structured format."""
    
    def __init__(self):
        self.last_command = None
    
    def parse(self, input_text: str) -> Optional[dict]:
        """
        Parse player input into a command structure.
        
        Returns:
            Dictionary with 'command' and optional 'args', or None if invalid
        """
        input_text = input_text.strip().lower()
        
        if not input_text:
            return None
        
        # Try to match known commands
        if self._match_warp(input_text):
            return self._match_warp(input_text)
        elif self._match_impulse(input_text):
            return self._match_impulse(input_text)
        elif self._match_heading(input_text):
            return self._match_heading(input_text)
        elif self._match_scan(input_text):
            return self._match_scan(input_text)
        elif self._match_shields(input_text):
            return self._match_shields(input_text)
        elif self._match_lock(input_text):
            return self._match_lock(input_text)
        elif self._match_fire(input_text):
            return self._match_fire(input_text)
        elif self._match_torpedo(input_text):
            return self._match_torpedo(input_text)
        elif self._match_status(input_text):
            return self._match_status(input_text)
        elif self._match_skip(input_text):
            return {'command': 'skip'}
        elif self._match_stop(input_text):
            return {'command': 'stop'}
        elif self._match_tell(input_text):
            return self._match_tell(input_text)
        elif self._match_nav(input_text):
            return self._match_nav(input_text)
        elif self._match_hal(input_text):
            return self._match_hal(input_text)
        elif self._match_targets(input_text):
            return {'command': 'targets'}
        elif self._match_debug(input_text):
            return self._match_debug(input_text)
        
        return None
    
    def _match_warp(self, text: str) -> Optional[dict]:
        """Match warp command: 'warp 8' or 'set warp to 8'"""
        patterns = [
            r'warp\s+(\d+)',
            r'set\s+warp\s+(?:to\s+)?(\d+)',
            r'warp\s+speed\s+(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                speed = int(match.group(1))
                self.last_command = {'command': 'warp', 'speed': speed}
                return self.last_command
        
        return None
    
    def _match_impulse(self, text: str) -> Optional[dict]:
        """Match impulse command: 'imp 50' (percentage 1-100), 'impulse on', 'impulse off', etc."""
        # Match impulse with percentage: 'imp 50', 'impulse 75'
        percentage_match = re.search(r'imp(?:ulse)?\s+(\d+)', text)
        if percentage_match:
            percent = int(percentage_match.group(1))
            # Clamp to 1-100 range
            percent = max(1, min(100, percent))
            self.last_command = {'command': 'impulse', 'active': True, 'percent': percent}
            return self.last_command
        
        # Match on/off patterns
        on_patterns = [r'imp(?:ulse)?\s+(?:on|activate|engage)', r'engage\s+impulse']
        off_patterns = [r'imp(?:ulse)?\s+(?:off|deactivate|disable)', r'disable\s+impulse']
        
        for pattern in on_patterns:
            if re.search(pattern, text):
                self.last_command = {'command': 'impulse', 'active': True, 'percent': 100}
                return self.last_command
        
        for pattern in off_patterns:
            if re.search(pattern, text):
                self.last_command = {'command': 'impulse', 'active': False, 'percent': 0}
                return self.last_command
        
        return None
    
    def _match_heading(self, text: str) -> Optional[dict]:
        """Match heading command: 'heading 180', 'head 90', 'set course 270'"""
        patterns = [
            r'(?:head(?:ing)?|course)\s+(?:to\s+)?(\d+)',
            r'set\s+(?:heading|course)\s+(?:to\s+)?(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                heading = float(match.group(1)) % 360
                self.last_command = {'command': 'heading', 'degrees': heading}
                return self.last_command
        
        return None
    
    def _match_scan(self, text: str) -> Optional[dict]:
        """Match scan command: 'scan' or 'scan st12345' or 'scan s1'"""
        if re.search(r'scan\s*$', text):
            self.last_command = {'command': 'scan', 'target_id': None}
            return self.last_command
        
        match = re.search(r'scan\s+([a-z]{1,2}\d+)', text)
        if match:
            target_id = match.group(1)
            self.last_command = {'command': 'scan', 'target_id': target_id}
            return self.last_command
        
        return None
    
    def _match_shields(self, text: str) -> Optional[dict]:
        """Match shields command: 'shields up', 'shields down', 'shi on'"""
        up_patterns = [r'sh(?:ields?)?\s+(?:up|on|raise|activate)', r'raise\s+shields?']
        down_patterns = [r'sh(?:ields?)?\s+(?:down|off|lower|deactivate)', r'lower\s+shields?']
        
        for pattern in up_patterns:
            if re.search(pattern, text):
                self.last_command = {'command': 'shields', 'active': True}
                return self.last_command
        
        for pattern in down_patterns:
            if re.search(pattern, text):
                self.last_command = {'command': 'shields', 'active': False}
                return self.last_command
        
        return None
    
    def _match_lock(self, text: str) -> Optional[dict]:
        """Match lock command: 'lock s1', 'lock on s1', or 'lock phasers on st12345'"""
        match = re.search(r'lock\s+(?:phasers\s+)?(?:on\s+)?([a-z]{1,2}\d+)', text)
        if match:
            target_id = match.group(1)
            self.last_command = {'command': 'lock', 'target_id': target_id}
            return self.last_command
        
        return None
    
    def _match_fire(self, text: str) -> Optional[dict]:
        """Match fire command: 'fire' or 'fire phasers'"""
        if re.search(r'fire\s*(?:phasers?)?\s*$', text):
            self.last_command = {'command': 'fire'}
            return self.last_command
        
        return None
    
    def _match_torpedo(self, text: str) -> Optional[dict]:
        """Match torpedo command: 'tor', 'torpedo', 'fire torpedo at s1', 'tor st12345'"""
        # First, try to match with explicit target
        patterns = [
            r'(?:tor|torp)(?:edo)?\s+(?:at\s+)?([a-z]{1,2}\d+)',
            r'fire\s+(?:torpedo|torp)\s+(?:at\s+)?([a-z]{1,2}\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                target_id = match.group(1)
                self.last_command = {'command': 'torpedo', 'target_id': target_id}
                return self.last_command
        
        # Match torpedo command without target (will use locked target)
        if re.search(r'(?:tor|torp)(?:edo)?\s*$|fire\s+(?:torpedo|torp)\s*$', text):
            self.last_command = {'command': 'torpedo'}
            return self.last_command
        
        return None
    
    def _match_status(self, text: str) -> Optional[dict]:
        """Match status command: 'status', 'sta', 'ship status'"""
        if re.search(r'(?:sta(?:tus)?|ship\s+status|shields?|energy|damage|systems)\s*$', text):
            self.last_command = {'command': 'status'}
            return self.last_command
        
        return None
    
    def _match_skip(self, text: str) -> Optional[dict]:
        """Match skip command: 'skip', 'skip turn'"""
        if re.search(r'skip\s*(?:turn)?\s*$', text):
            self.last_command = {'command': 'skip'}
            return self.last_command
        return None
    
    def _match_stop(self, text: str) -> Optional[dict]:
        """Match stop command: 'stop', 'all stop', 'halt'"""
        if re.search(r'(?:all\s+)?(?:stop|halt)\s*$', text):
            self.last_command = {'command': 'stop'}
            return self.last_command
        
        return None
    
    def _match_tell(self, text: str) -> Optional[dict]:
        """Match tell command: 'tell s1 hello' or 'talk to st12345 ...'"""
        match = re.search(r'(?:tell|talk\s+to)\s+([a-z]{1,2}\d+)\s+(.+)', text)
        if match:
            target_id = match.group(1)
            message = match.group(2)
            self.last_command = {'command': 'tell', 'target_id': target_id, 'message': message}
            return self.last_command
        
        return None
    
    def _match_nav(self, text: str) -> Optional[dict]:
        """Match navigation command: 'navigate to st12345' or 'nav s1'"""
        patterns = [
            r'(?:nav|navigate|auto-nav|auto\s+nav)\s+(?:to\s+)?([a-z]{1,2}\d+)',
            r'go\s+to\s+([a-z]{1,2}\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                target_id = match.group(1)
                self.last_command = {'command': 'nav', 'target_id': target_id}
                return self.last_command
        
        return None
    
    def _match_hal(self, text: str) -> Optional[dict]:
        """Match hal command: 'hal which is the nearest star'"""
        match = re.search(r'hal\s+(.+)', text)
        if match:
            question = match.group(1)
            self.last_command = {'command': 'hal', 'question': question}
            return self.last_command
        
        return None
    
    def _match_targets(self, text: str) -> Optional[dict]:
        """Match targets command: 'targets', 'list targets', 'enemy ships'"""
        if re.search(r'(?:list\s+)?targets?\s*$|enemy\s+ships?\s*$', text):
            self.last_command = {'command': 'targets'}
            return self.last_command
        return None
    
    def _match_debug(self, text: str) -> Optional[dict]:
        """Match debug command: 'debug on' or 'debug off'"""
        match = re.search(r'debug\s+(on|off)\s*$', text)
        if match:
            mode = match.group(1) == 'on'
            self.last_command = {'command': 'debug', 'mode': mode}
            return self.last_command
        
        return None
    
    def get_last_command(self) -> Optional[dict]:
        """Return the last parsed command."""
        return self.last_command
