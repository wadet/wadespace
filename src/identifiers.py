"""
Wade Space Game - Identifier and Unique ID Management

Handles creation and management of unique identifiers for all game objects.
"""

import random
from typing import Optional


class ObjectIdentifier:
    """Generates and manages unique identifiers for game objects."""
    
    PREFIX_MAP = {
        'star': 'st',
        'planet': 'pl',
        'black_hole': 'bh',
        'pulsar': 'pu',
        'worm_hole': 'wh',
        'starbase': 'sb',
        'asteroid_field': 'af',
        'ship': 's',
    }
    
    def __init__(self):
        self.used_ids = set()
    
    def generate(self, obj_type: str) -> str:
        """
        Generate a unique identifier for an object.
        
        Format: <2-letter prefix><1-4 digit numeric ID>
        
        Args:
            obj_type: Type of object (e.g., 'star', 'ship')
            
        Returns:
            Unique identifier string (e.g., 'st1234')
            
        Raises:
            ValueError: If obj_type is not recognized
        """
        if obj_type not in self.PREFIX_MAP:
            raise ValueError(f"Unknown object type: {obj_type}")
        
        prefix = self.PREFIX_MAP[obj_type]
        
        # Generate unique numeric ID (1-9999, max 4 digits)
        while True:
            numeric_id = random.randint(1, 9999)
            full_id = f"{prefix}{numeric_id}"
            if full_id not in self.used_ids:
                self.used_ids.add(full_id)
                return full_id
    
    def is_valid(self, obj_id: str, obj_type: Optional[str] = None) -> bool:
        """Check if an identifier is valid."""
        if len(obj_id) < 2:
            return False
        
        # Determine the prefix
        if obj_type is not None:
            # If obj_type is provided, use it to get the prefix
            prefix = self.PREFIX_MAP.get(obj_type, '')
        else:
            # Try to match against all known prefixes
            prefix = None
            for known_prefix in self.PREFIX_MAP.values():
                if obj_id.startswith(known_prefix):
                    if prefix is None or len(known_prefix) > len(prefix):
                        prefix = known_prefix
        
        if not prefix:
            return False
        
        if not obj_id.startswith(prefix):
            return False
        
        # Try to extract and validate numeric part (1-4 digits)
        try:
            numeric_part = obj_id[len(prefix):]
            if not numeric_part:  # Must have at least 1 digit
                return False
            numeric_id = int(numeric_part)
            return 1 <= numeric_id <= 9999
        except ValueError:
            return False
    
    def get_type_from_id(self, obj_id: str) -> Optional[str]:
        """Extract object type from its identifier."""
        for obj_type, prefix in self.PREFIX_MAP.items():
            if obj_id.startswith(prefix):
                return obj_type
        return None
