
#!/usr/bin/env python3

"""
Create sample assets for Axarion Engine demos
Generates sprites, animations, and sounds
"""

import pygame
import os
from pathlib import Path

def create_sample_assets():
    """Create sample game assets"""
    
    # Initialize pygame for asset creation
    pygame.init()
    
    # Create asset directories
    base_path = Path(__file__).parent
    assets_path = base_path / "assets"
    images_path = assets_path / "images"
    sounds_path = assets_path / "sounds"
    animations_path = assets_path / "animations"
    fonts_path = assets_path / "fonts"
    
    # Create directories
    for path in [assets_path, images_path, sounds_path, animations_path, fonts_path]:
        path.mkdir(exist_ok=True)
    
    print("🎨 Creating sample assets...")
    
    # Create sample images
    create_sample_images(images_path)
    create_sample_animations(animations_path)
    
    print("✅ Sample assets created successfully!")
    print(f"📁 Assets location: {assets_path}")

def create_sample_images(images_path):
    """Create sample sprite images"""
    
    # Small ship sprite
    ship = pygame.Surface((32, 24), pygame.SRCALPHA)
    # Ship body (blue-gray)
    pygame.draw.polygon(ship, (100, 120, 180), [(16, 0), (32, 20), (16, 16), (0, 20)])
    # Ship details
    pygame.draw.polygon(ship, (150, 170, 220), [(16, 4), (28, 18), (16, 14), (4, 18)])
    # Engine glow
    pygame.draw.circle(ship, (255, 100, 100), (16, 20), 3)
    pygame.image.save(ship, images_path / "ship.png")
    
    # Alternative small ship
    small_ship = pygame.Surface((24, 18), pygame.SRCALPHA)
    pygame.draw.polygon(small_ship, (80, 150, 200), [(12, 0), (24, 14), (12, 12), (0, 14)])
    pygame.draw.circle(small_ship, (255, 150, 50), (12, 16), 2)
    pygame.image.save(small_ship, images_path / "small_ship.png")
    
    # Enemy ship
    enemy = pygame.Surface((28, 20), pygame.SRCALPHA)
    pygame.draw.polygon(enemy, (180, 50, 50), [(14, 20), (0, 4), (14, 0), (28, 4)])
    pygame.draw.polygon(enemy, (220, 80, 80), [(14, 16), (4, 6), (14, 4), (24, 6)])
    pygame.image.save(enemy, images_path / "enemy.png")
    
    # Asteroid
    asteroid = pygame.Surface((30, 30), pygame.SRCALPHA)
    # Irregular asteroid shape
    points = [(15, 0), (25, 5), (30, 15), (25, 25), (15, 30), (5, 25), (0, 15), (5, 5)]
    pygame.draw.polygon(asteroid, (120, 80, 60), points)
    # Add some texture
    pygame.draw.circle(asteroid, (100, 60, 40), (10, 10), 3)
    pygame.draw.circle(asteroid, (100, 60, 40), (20, 20), 2)
    pygame.image.save(asteroid, images_path / "asteroid.png")
    
    # Gold coin
    coin = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(coin, (255, 215, 0), (10, 10), 9)
    pygame.draw.circle(coin, (218, 165, 32), (10, 10), 9, 2)
    pygame.draw.circle(coin, (255, 255, 100), (10, 10), 6)
    pygame.image.save(coin, images_path / "coin.png")
    
    # Power-up
    powerup = pygame.Surface((24, 24), pygame.SRCALPHA)
    # Star shape
    points = []
    for i in range(10):
        angle = i * 36 * 3.14159 / 180
        if i % 2 == 0:
            radius = 10
        else:
            radius = 5
        x = 12 + radius * pygame.math.Vector2(1, 0).rotate_rad(angle).x
        y = 12 + radius * pygame.math.Vector2(1, 0).rotate_rad(angle).y
        points.append((x, y))
    
    pygame.draw.polygon(powerup, (0, 255, 255), points)
    pygame.draw.circle(powerup, (255, 255, 255), (12, 12), 6)
    pygame.image.save(powerup, images_path / "powerup.png")
    
    print("✅ Created sample images")

def create_sample_animations(animations_path):
    """Create sample animation sequences"""
    
    # Explosion animation
    explosion_path = animations_path / "explosion"
    explosion_path.mkdir(exist_ok=True)
    
    for i in range(8):
        frame = pygame.Surface((40, 40), pygame.SRCALPHA)
        
        # Explosion grows and fades
        progress = i / 7.0
        radius = int(5 + progress * 15)
        alpha = int(255 * (1 - progress))
        
        # Multiple explosion circles
        colors = [
            (255, 100, 0, alpha),   # Orange core
            (255, 200, 0, alpha//2), # Yellow middle
            (255, 50, 50, alpha//3)  # Red outer
        ]
        
        for j, color in enumerate(colors):
            r = radius - j * 3
            if r > 0:
                # Create surface with per-pixel alpha
                circle_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                pygame.draw.circle(circle_surf, color, (r, r), r)
                frame.blit(circle_surf, (20-r, 20-r))
        
        pygame.image.save(frame, explosion_path / f"frame_{i:02d}.png")
    
    # Spinning coin animation
    coin_path = animations_path / "spinning_coin"
    coin_path.mkdir(exist_ok=True)
    
    for i in range(8):
        frame = pygame.Surface((24, 24), pygame.SRCALPHA)
        
        # Create oval for rotation effect
        angle = i * 45
        width = int(20 * abs(pygame.math.cos(pygame.math.radians(angle))))
        
        if width < 4:
            width = 4
        
        # Gold coin with perspective
        pygame.draw.ellipse(frame, (255, 215, 0), (12 - width//2, 2, width, 20))
        pygame.draw.ellipse(frame, (218, 165, 32), (12 - width//2, 2, width, 20), 2)
        
        pygame.image.save(frame, coin_path / f"frame_{i:02d}.png")
    
    # Engine thrust animation
    thrust_path = animations_path / "engine_thrust"
    thrust_path.mkdir(exist_ok=True)
    
    for i in range(6):
        frame = pygame.Surface((16, 12), pygame.SRCALPHA)
        
        # Thrust flame
        length = 8 + (i % 3) * 2
        
        # Blue core
        pygame.draw.rect(frame, (100, 100, 255), (2, 4, length//2, 4))
        # Orange/red flame
        pygame.draw.rect(frame, (255, 150, 50), (2 + length//2, 3, length//2, 6))
        
        pygame.image.save(frame, thrust_path / f"frame_{i:02d}.png")
    
    print("✅ Created sample animations")

if __name__ == "__main__":
    create_sample_assets()
