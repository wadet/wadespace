"""
Wade Space Game - Visual Effects

Handles animations, explosions, and visual effects.
"""

import pygame
import math
from typing import List, Tuple, Optional


class Particle:
    """A single particle for visual effects."""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 color: Tuple[int, int, int], lifetime: float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
        self.size = 2
    
    def update(self, dt: float) -> bool:
        """Update particle. Returns True if still alive."""
        self.age += dt
        if self.age > self.lifetime:
            return False
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Fade out
        alpha = 1.0 - (self.age / self.lifetime)
        faded_color = (
            int(self.color[0] * alpha),
            int(self.color[1] * alpha),
            int(self.color[2] * alpha),
        )
        self.color = faded_color
        
        return True
    
    def draw(self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0):
        """Draw the particle."""
        pygame.draw.circle(surface, self.color, 
                          (int(self.x + offset_x), int(self.y + offset_y)), 
                          self.size)


class ExplosionEffect:
    """Star Wars-style explosion effect."""
    
    def __init__(self, x: float, y: float, size: float = 1.0):
        self.x = x
        self.y = y
        self.size = size
        self.age = 0.0
        self.lifetime = 1.0
        self.particles: List[Particle] = []
        self._generate_particles()
    
    def _generate_particles(self):
        """Generate explosion particles."""
        colors = [
            (255, 200, 0),   # Orange/yellow
            (255, 100, 0),   # Dark orange
            (255, 255, 0),   # Yellow
            (200, 200, 0),   # Dark yellow
        ]
        
        particle_count = int(20 * self.size)
        for i in range(particle_count):
            angle = (i / particle_count) * 2 * math.pi
            speed = 100 * self.size + (i % 5) * 20
            
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            
            color = colors[i % len(colors)]
            particle = Particle(self.x, self.y, vx, vy, color, self.lifetime)
            self.particles.append(particle)
    
    def update(self, dt: float) -> bool:
        """Update explosion. Returns True if still alive."""
        self.age += dt
        
        alive_particles = []
        for particle in self.particles:
            if particle.update(dt):
                alive_particles.append(particle)
        
        self.particles = alive_particles
        return self.age < self.lifetime and len(self.particles) > 0
    
    def draw(self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0):
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(surface, offset_x, offset_y)


class ProjectileTrail:
    """Visual trail for projectiles."""
    
    def __init__(self, x: float, y: float, target_x: float, target_y: float):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.age = 0.0
        self.lifetime = 0.5
        self.active = True
    
    def update(self, dt: float) -> bool:
        """Update trail. Returns True if still visible."""
        self.age += dt
        return self.age < self.lifetime
    
    def draw(self, surface: pygame.Surface, color: Tuple[int, int, int],
             offset_x: float = 0, offset_y: float = 0):
        """Draw the projectile trail."""
        # Fade out effect
        alpha = 1.0 - (self.age / self.lifetime)
        faded_color = (
            int(color[0] * alpha),
            int(color[1] * alpha),
            int(color[2] * alpha),
        )
        
        # Draw line from start to target
        pygame.draw.line(surface, faded_color,
                        (int(self.x + offset_x), int(self.y + offset_y)),
                        (int(self.target_x + offset_x), int(self.target_y + offset_y)), 2)


class PhaserBeam:
    """Phaser beam effect."""
    
    def __init__(self, x: float, y: float, target_x: float, target_y: float):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.age = 0.0
        self.lifetime = 0.2
    
    def update(self, dt: float) -> bool:
        """Update beam. Returns True if still visible."""
        self.age += dt
        return self.age < self.lifetime
    
    def draw(self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0):
        """Draw the phaser beam."""
        alpha = 1.0 - (self.age / self.lifetime)
        intensity = int(255 * alpha)
        color = (0, intensity, 255)
        
        # Draw main beam
        pygame.draw.line(surface, color,
                        (int(self.x + offset_x), int(self.y + offset_y)),
                        (int(self.target_x + offset_x), int(self.target_y + offset_y)), 3)
        
        # Draw glow effect
        pygame.draw.line(surface, (100, 200, 255),
                        (int(self.x + offset_x), int(self.y + offset_y)),
                        (int(self.target_x + offset_x), int(self.target_y + offset_y)), 1)


class ImpactEffect:
    """Visual effect for weapon impact."""
    
    def __init__(self, x: float, y: float, effect_type: str = "hit"):
        self.x = x
        self.y = y
        self.effect_type = effect_type  # "hit", "explosion", "phaser"
        self.age = 0.0
        self.lifetime = 0.3
        self.particles: List[Particle] = []
        self._generate_particles()
    
    def _generate_particles(self):
        """Generate impact particles."""
        if self.effect_type == "hit":
            colors = [(0, 100, 255), (100, 150, 255)]
        elif self.effect_type == "explosion":
            colors = [(255, 100, 0), (255, 200, 0)]
        else:  # phaser
            colors = [(0, 200, 255), (100, 255, 255)]
        
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            speed = 50
            
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            
            color = colors[i % len(colors)]
            particle = Particle(self.x, self.y, vx, vy, color, self.lifetime)
            self.particles.append(particle)
    
    def update(self, dt: float) -> bool:
        """Update effect. Returns True if still active."""
        self.age += dt
        
        alive_particles = []
        for particle in self.particles:
            if particle.update(dt):
                alive_particles.append(particle)
        
        self.particles = alive_particles
        return self.age < self.lifetime
    
    def draw(self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0):
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(surface, offset_x, offset_y)


class EffectManager:
    """Manages all visual effects."""
    
    def __init__(self):
        self.explosions: List[ExplosionEffect] = []
        self.phaser_beams: List[PhaserBeam] = []
        self.projectile_trails: List[ProjectileTrail] = []
        self.impact_effects: List[ImpactEffect] = []
    
    def add_explosion(self, x: float, y: float, size: float = 1.0):
        """Add an explosion effect."""
        self.explosions.append(ExplosionEffect(x, y, size))
    
    def add_phaser_beam(self, x: float, y: float, target_x: float, target_y: float):
        """Add a phaser beam effect."""
        self.phaser_beams.append(PhaserBeam(x, y, target_x, target_y))
    
    def add_projectile_trail(self, x: float, y: float, target_x: float, target_y: float):
        """Add a projectile trail effect."""
        self.projectile_trails.append(ProjectileTrail(x, y, target_x, target_y))
    
    def add_impact(self, x: float, y: float, effect_type: str = "hit"):
        """Add an impact effect."""
        self.impact_effects.append(ImpactEffect(x, y, effect_type))
    
    def update(self, dt: float):
        """Update all effects."""
        # Update and remove dead explosions
        self.explosions = [e for e in self.explosions if e.update(dt)]
        
        # Update and remove dead phaser beams
        self.phaser_beams = [b for b in self.phaser_beams if b.update(dt)]
        
        # Update and remove dead projectile trails
        self.projectile_trails = [t for t in self.projectile_trails if t.update(dt)]
        
        # Update and remove dead impact effects
        self.impact_effects = [e for e in self.impact_effects if e.update(dt)]
    
    def draw(self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0):
        """Draw all effects."""
        for explosion in self.explosions:
            explosion.draw(surface, offset_x, offset_y)
        
        for beam in self.phaser_beams:
            beam.draw(surface, offset_x, offset_y)
        
        for trail in self.projectile_trails:
            trail.draw(surface, (255, 0, 0), offset_x, offset_y)
        
        for impact in self.impact_effects:
            impact.draw(surface, offset_x, offset_y)
    
    def clear(self):
        """Clear all effects."""
        self.explosions.clear()
        self.phaser_beams.clear()
        self.projectile_trails.clear()
        self.impact_effects.clear()
