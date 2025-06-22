
#!/usr/bin/env python3

"""
Axarion Engine Assets Demo
Shows off sprite loading, animations, sounds, and visual effects
"""

import pygame
import sys
import os
import math

# Add engine to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.core import AxarionEngine
from engine.game_object import GameObject
from engine.scene import Scene
from engine.asset_manager import asset_manager

def create_sample_assets():
    """Create sample assets if they don't exist"""
    from assets.create_sample_assets import create_sample_assets
    create_sample_assets()

def create_assets_demo():
    """Create demo scene with various assets"""
    
    # Create sample assets first
    create_sample_assets()
    
    # Create engine
    engine = AxarionEngine(1000, 700)
    if not engine.initialize():
        print("Failed to initialize engine")
        return None
    
    # Load all assets
    asset_manager.load_all_assets()
    
    # Create scene
    scene = Scene("Assets Demo")
    engine.current_scene = scene
    
    # Set scene properties
    scene.set_gravity(0, 150)  # Light gravity
    scene.set_bounds(0, 0, 1000, 700)
    
    # Create ground
    ground = GameObject("Ground", "rectangle")
    ground.position = (0, 650)
    ground.set_property("width", 1000)
    ground.set_property("height", 50)
    ground.set_property("color", (80, 120, 80))
    ground.is_static = True
    ground.add_tag("platform")
    scene.add_object(ground)
    
    # Create player ship with sprite
    player = GameObject("Player", "sprite")
    player.position = (100, 400)
    player.mass = 1.0
    player.bounce = 0.3
    player.friction = 0.8
    player.add_tag("player")
    
    # Set ship sprite
    if player.set_sprite("ship"):
        print("✅ Player sprite loaded")
    else:
        # Fallback
        player.object_type = "rectangle"
        player.set_property("width", 32)
        player.set_property("height", 24)
        player.set_property("color", (0, 150, 255))
    
    # Player movement script
    player.script_code = """
var thrustPower = 300;
var rotationSpeed = 120;

function update() {
    // Rotation
    if (keyPressed("ArrowLeft") || keyPressed("a")) {
        rotate(-rotationSpeed * 0.016);
    }
    if (keyPressed("ArrowRight") || keyPressed("d")) {
        rotate(rotationSpeed * 0.016);
    }
    
    // Thrust
    if (keyPressed("ArrowUp") || keyPressed("w")) {
        var angle = getProperty("rotation") * Math.PI / 180;
        var thrustX = Math.cos(angle) * thrustPower;
        var thrustY = Math.sin(angle) * thrustPower;
        applyForce(thrustX, thrustY);
    }
    
    // Keep in bounds
    var pos = getProperty("position");
    if (pos.x < 0) setProperty("position", {x: 0, y: pos.y});
    if (pos.x > 968) setProperty("position", {x: 968, y: pos.y});
}
"""
    scene.add_object(player)
    
    # Create enemy ships with sprites
    for i in range(3):
        enemy = GameObject(f"Enemy_{i}", "sprite")
        enemy.position = (300 + i * 200, 200 + i * 50)
        enemy.mass = 0.8
        enemy.bounce = 0.5
        enemy.add_tag("enemy")
        
        # Try to set enemy sprite
        if not enemy.set_sprite("enemy"):
            enemy.object_type = "rectangle"
            enemy.set_property("width", 28)
            enemy.set_property("height", 20)
            enemy.set_property("color", (200, 50, 50))
        
        # Simple AI
        enemy.script_code = f"""
var angle = {i * 60};
var centerX = {300 + i * 200};
var centerY = {200 + i * 50};
var radius = 80;
var speed = 0.5;

function update() {{
    angle += speed;
    
    var newX = centerX + Math.cos(angle * Math.PI / 180) * radius;
    var newY = centerY + Math.sin(angle * Math.PI / 180) * radius;
    
    setProperty("position", {{x: newX, y: newY}});
    
    // Look at movement direction
    setProperty("rotation", angle);
}}
"""
        scene.add_object(enemy)
    
    # Create animated coins
    for i in range(5):
        coin = GameObject(f"Coin_{i}", "animated_sprite")
        coin.position = (150 + i * 150, 300)
        coin.mass = 0.5
        coin.bounce = 0.8
        coin.friction = 0.2
        coin.add_tag("collectible")
        
        # Set spinning coin animation
        if not coin.set_animation("spinning_coin", 1.5):
            # Fallback to simple sprite
            if not coin.set_sprite("coin"):
                coin.object_type = "circle"
                coin.set_property("radius", 10)
                coin.set_property("color", (255, 215, 0))
        
        # Floating movement
        coin.script_code = f"""
var time = {i * 30};
var baseY = {300};
var floatHeight = 20;

function update() {{
    time += 1;
    var newY = baseY + Math.sin(time * 0.05) * floatHeight;
    var pos = getProperty("position");
    setProperty("position", {{x: pos.x, y: newY}});
}}
"""
        scene.add_object(coin)
    
    # Create asteroids
    for i in range(4):
        asteroid = GameObject(f"Asteroid_{i}", "sprite")
        asteroid.position = (200 + i * 200, 100)
        asteroid.mass = 2.0
        asteroid.bounce = 0.3
        asteroid.friction = 0.1
        asteroid.velocity = (30 - i * 20, 50 + i * 10)
        asteroid.add_tag("obstacle")
        
        # Set asteroid sprite
        if not asteroid.set_sprite("asteroid"):
            asteroid.object_type = "polygon"
            # Create irregular shape
            points = []
            for j in range(8):
                angle = j * 45 * math.pi / 180
                radius = 15 + (j % 3) * 5
                x = asteroid.position[0] + math.cos(angle) * radius
                y = asteroid.position[1] + math.sin(angle) * radius
                points.append((x, y))
            asteroid.set_property("points", points)
            asteroid.set_property("color", (100, 80, 60))
        
        # Rotating movement
        asteroid.script_code = f"""
var rotationSpeed = {20 + i * 10};

function update() {{
    rotate(rotationSpeed * 0.016);
    
    // Bounce off edges
    var pos = getProperty("position");
    var vel = getProperty("velocity");
    
    if (pos.x <= 20 || pos.x >= 980) {{
        setProperty("velocity", {{x: -vel.x, y: vel.y}});
    }}
    if (pos.y <= 20) {{
        setProperty("velocity", {{x: vel.x, y: Math.abs(vel.y)}});
    }}
}}
"""
        scene.add_object(asteroid)
    
    # Create power-ups
    for i in range(3):
        powerup = GameObject(f"PowerUp_{i}", "sprite")
        powerup.position = (100 + i * 300, 500)
        powerup.mass = 0.3
        powerup.bounce = 0.9
        powerup.add_tag("powerup")
        
        # Set powerup sprite
        if not powerup.set_sprite("powerup"):
            powerup.object_type = "circle"
            powerup.set_property("radius", 12)
            powerup.set_property("color", (0, 255, 255))
        
        # Pulsing effect
        powerup.script_code = f"""
var time = {i * 45};
var originalScale = 1.0;
var pulseAmount = 0.3;

function update() {{
    time += 2;
    var scale = originalScale + Math.sin(time * 0.1) * pulseAmount;
    setProperty("scale", {{x: scale, y: scale}});
}}
"""
        scene.add_object(powerup)
    
    # Set up renderer
    engine.renderer.enable_debug(True)
    engine.renderer.show_object_bounds(False)
    
    return engine

def main():
    """Main demo function"""
    print("🎮 Axarion Engine Assets Demo")
    print("=" * 50)
    
    # Create demo scene
    engine = create_assets_demo()
    if not engine:
        return
    
    print("✅ Engine initialized with assets")
    print("✅ Scene created with sprites and animations")
    print("\n🎯 Controls:")
    print("   WASD / Arrow Keys - Control ship")
    print("   W/Up - Thrust")
    print("   A,D/Left,Right - Rotate")
    print("   ESC - Exit")
    print("   F - Toggle debug mode")
    print("   C - Toggle collision bounds")
    print("\n🎨 Assets loaded:")
    
    # Show loaded assets
    assets = asset_manager.list_assets()
    for asset_type, asset_list in assets.items():
        if asset_list:
            print(f"   {asset_type.title()}: {', '.join(asset_list)}")
    
    print("\n🚀 Starting assets demo...")
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    try:
        while running:
            delta_time = clock.tick(60) / 1000.0
            
            # Handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_f:
                        # Toggle debug mode
                        engine.renderer.debug_mode = not engine.renderer.debug_mode
                        print(f"Debug mode: {'ON' if engine.renderer.debug_mode else 'OFF'}")
                    elif event.key == pygame.K_c:
                        # Toggle collision bounds
                        engine.renderer.show_bounds = not engine.renderer.show_bounds
                        engine.renderer.show_object_bounds(engine.renderer.show_bounds)
                        print(f"Collision bounds: {'ON' if engine.renderer.show_bounds else 'OFF'}")
            
            # Update engine
            engine.current_scene.update(delta_time)
            
            # Follow player with camera
            player = engine.current_scene.get_object("Player")
            if player:
                engine.renderer.follow_object(player, 0, -100)
            
            # Render
            engine.renderer.clear()
            engine.current_scene.render(engine.renderer)
            
            # Draw UI
            engine.renderer.draw_text("Axarion Engine - Assets Demo", 10, 10, (255, 255, 255))
            engine.renderer.draw_text("WASD: Move Ship | F: Debug | C: Bounds | ESC: Exit", 10, 30, (200, 200, 200))
            
            # Show asset info
            y_offset = 60
            for asset_type, count in [(k, len(v)) for k, v in asset_manager.list_assets().items() if v]:
                engine.renderer.draw_text(f"{asset_type.title()}: {count}", 10, y_offset, (150, 200, 255))
                y_offset += 20
            
            engine.renderer.present()
            
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🧹 Cleaning up...")
        engine.cleanup()
        pygame.quit()
        print("✅ Demo completed")

if __name__ == "__main__":
    main()
