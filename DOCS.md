
# 📚 Axarion Engine - Complete Documentation

## 🎮 Introduction

Axarion Engine is a powerful 2D game engine designed specifically for programmers who prefer writing games in pure code without graphical editors. This advanced evolution features professional development tools, hot reload capabilities, and sophisticated debugging systems.

## ✨ Key Features Overview

### 🎯 Core Features
- **Pure Code Approach**: No GUI editor - games written entirely in code
- **AXScript Integration**: Built-in scripting language with advanced features
- **Hot Reload System**: Instant script reloading for rapid development
- **Advanced Debugging**: Breakpoints, variable inspection, step-through debugging
- **Professional Error Handling**: Graceful recovery from script errors
- **Asset Management**: Comprehensive system for sprites, sounds, and animations
- **Physics System**: Built-in 2D physics simulation with multiple collision types
- **Animation System**: Smooth object animations and particle effects

### 🎨 Asset Support
- **Images**: PNG, JPG, GIF, BMP, TGA
- **Audio**: WAV, MP3, OGG, M4A
- **Animations**: Sprite sheets and frame folders
- **Fonts**: TTF, OTF

## 🚀 Quick Start Guide

### 1. Installation and Setup
```bash
# Run physics demo
python test_fixed_engine.py

# Run complete assets demo
python test_assets_demo.py

# Create sample assets
python assets/create_sample_assets.py
```

### 2. Basic Game Structure
```python
from engine.core import AxarionEngine
from engine.game_object import GameObject
from engine.asset_manager import asset_manager

# Create engine
engine = AxarionEngine(800, 600)
engine.initialize()

# Load assets
asset_manager.load_all_assets()

# Create scene
scene = engine.create_scene("Main")
engine.current_scene = scene

# Create game object
player = GameObject("Player", "sprite")
player.position = (100, 100)
player.set_sprite("ship")  # Use sprite

# Run game
engine.run()
```

## 🔥 Hot Reload System (NEW!)

### How It Works
The hot reload system monitors your script files and automatically reloads them when changes are detected.

```python
# Enable hot reload (enabled by default)
from engine.hot_reload_system import hot_reload_system

hot_reload_system.enable()
hot_reload_system.watch_directory("scripting/")

# Your scripts will now reload automatically when saved!
```

### Development Workflow
1. **Write Script**: Create or modify AXScript code
2. **Save File**: Hot reload automatically detects changes
3. **Instant Update**: See changes immediately without restart
4. **Debug**: Use breakpoints and debug tools
5. **Iterate**: Rapid development cycle

### Best Practices
```python
# Use try-catch for experimental code
player.script_code = """
function update() {
    try {
        experimentalFeature();
    } catch (error) {
        debugLog("Feature failed: " + error);
        // Fallback behavior
        basicMovement();
    }
}
"""
```

## 🐛 Advanced Debugging System (NEW!)

### Debug Functions in AXScript
```javascript
// Set breakpoint - execution will pause here
debugBreak();

// Output to debug console
debugLog("Player health: " + health);

// Watch variable (shows in debug panel)
debugWatch("position");
debugWatch("velocity");

// Performance monitoring
var stats = getEngineStats();
debugLog("FPS: " + stats.fps + ", Frame time: " + stats.frameTime);
```

### Debug Session Features
- **Breakpoint Management**: Set and remove breakpoints dynamically
- **Variable Inspector**: View all variables at breakpoint
- **Step-through Debugging**: Execute code line by line
- **Call Stack**: See function call hierarchy
- **Debug Console**: Interactive debugging environment

### Using the Debugger
```python
# Enable debug mode
from engine.debug_system import debug_system

debug_system.enable()
debug_system.set_log_level("DEBUG")

# Create debug session for object
debug_session = debug_system.create_session("player_debug")
player.set_debug_session(debug_session.session_id)
```

## 🎯 Advanced Collision Detection (NEW!)

### Collision Types

#### 1. Basic Collision (Default)
```python
# Simple bounding box collision
obj1.check_collision(obj2)
```

#### 2. Pixel-Perfect Collision
```python
# Exact collision detection using pixel data
from engine.advanced_collision import collision_system

if collision_system.pixel_perfect_collision(sprite1, sprite2):
    handle_precise_collision()
```

#### 3. SAT (Separating Axis Theorem)
```python
# For polygon collision detection
if collision_system.sat_collision(polygon1, polygon2):
    handle_polygon_collision()
```

#### 4. Continuous Collision Detection
```python
# Prevents tunneling for fast objects
if collision_system.continuous_collision(fast_object, target, delta_time):
    handle_continuous_collision()
```

### AXScript Collision Functions
```javascript
// Advanced collision in scripts
if (pixelPerfectCollision(other)) {
    debugLog("Precise collision detected!");
}

if (satCollision(other)) {
    debugLog("Polygon collision!");
}

// Collision layers
if (checkCollisionLayer("enemies")) {
    takeDamage(10);
}
```

## 🎨 Professional Renderer (NEW!)

### Z-Ordering and Layers
```python
# Set object layer and z-order
player.set_property("layer", "characters")
player.set_property("z_order", 10)

background.set_property("layer", "background")
background.set_property("z_order", -10)

# Configure renderer layers
renderer.add_layer("background", z_order=-10)
renderer.add_layer("characters", z_order=0)
renderer.add_layer("effects", z_order=10)
```

### Sprite Batching
```python
# Batch similar sprites for performance
from engine.advanced_renderer import renderer

# Automatically batches sprites with same texture
renderer.enable_sprite_batching(True)

# Manual batching for maximum control
batch = renderer.create_sprite_batch("enemies")
for enemy in enemies:
    batch.add_sprite(enemy)
renderer.render_batch(batch)
```

### Advanced Rendering Features
```javascript
// AXScript rendering control
setRenderLayer("foreground");
setZOrder(5);
setOpacity(0.8);

// Shader effects (if supported)
setShaderProperty("glow", 1.5);
```

## 🛡️ Error Handling System (NEW!)

### Graceful Error Recovery
The engine continues running even when scripts have errors:

```python
# Error handling is automatic
try:
    obj.execute_script()
except ScriptError as e:
    # Engine logs error but continues
    print(f"Script error in {obj.name}: {e}")
    # Object continues with last valid state
```

### Script Error Recovery
```javascript
// Automatic error recovery in scripts
function update() {
    try {
        complexLogic();
    } catch (error) {
        // Log error and use fallback
        debugLog("Error: " + error);
        fallbackBehavior();
    }
}

function fallbackBehavior() {
    // Simple, safe behavior when errors occur
    if (keyPressed("ArrowLeft")) move(-100, 0);
    if (keyPressed("ArrowRight")) move(100, 0);
}
```

### Error Prevention
```python
# Built-in error checking
from engine.error_handling import error_handler

@error_handler.safe_execute
def risky_operation():
    # This function is protected from crashes
    pass

# Resource validation
if error_handler.validate_asset("missing_sprite.png"):
    obj.set_sprite("missing_sprite")
else:
    obj.set_sprite("default_sprite")
```

## 🎨 Asset Management

### Asset Loading
```python
from engine.asset_manager import asset_manager

# Load individual assets
asset_manager.load_image("ship", "assets/images/ship.png")
asset_manager.load_sound("laser", "assets/sounds/laser.wav")
asset_manager.load_animation("explosion", "assets/animations/explosion/")

# Load sprite sheets
asset_manager.load_sprite_sheet("player_walk", "sprites.png", 32, 48)

# Automatic loading
asset_manager.load_all_assets()
```

### Asset Optimization
```python
# Optimize assets for performance
asset_manager.optimize_images(quality=85)
asset_manager.compress_audio(quality="high")

# Streaming for large assets
asset_manager.enable_streaming(True)
asset_manager.set_streaming_threshold(1024 * 1024)  # 1MB
```

### Folder Structure
```
assets/
├── images/          # Images (.png, .jpg, .gif, .bmp)
├── sounds/          # Audio (.wav, .mp3, .ogg)
├── animations/      # Animations (frame folders)
│   ├── explosion/
│   ├── spinning_coin/
│   └── engine_thrust/
└── fonts/           # Fonts (.ttf, .otf)
```

## 🎮 GameObject API

### Basic Properties
```python
# Create object
obj = GameObject("MyObject", "sprite")
obj.position = (100, 200)
obj.velocity = (50, 0)
obj.rotation = 45
obj.mass = 1.5
obj.friction = 0.3
obj.bounce = 0.8

# Tags for categorization
obj.add_tag("enemy")
obj.add_tag("flying")
```

### Advanced Properties (NEW!)
```python
# Layers and rendering
obj.set_property("layer", "characters")
obj.set_property("z_order", 5)
obj.set_property("opacity", 0.8)

# Collision settings
obj.set_property("collision_type", "pixel_perfect")
obj.set_property("collision_layer", "enemies")

# Debug settings
obj.enable_debug(True)
obj.set_debug_color((255, 0, 0))
```

### Sprites and Animation
```python
# Set sprite
obj.set_sprite("ship")

# Set animation
obj.set_animation("explosion", speed=2.0, loop=False)

# Control animation
obj.play_animation("walk")
obj.pause_animation()
obj.resume_animation()
obj.stop_animation()

# Play sound
obj.play_sound("laser_shot")
```

### Physics
```python
# Apply force
obj.apply_force(100, -200)

# Move towards target
obj.move_towards((400, 300), speed=150)

# Rotation
obj.look_at((mouse_x, mouse_y))

# Ground detection
if obj.is_on_ground():
    obj.velocity = (obj.velocity[0], -jump_force)
```

## 📜 Complete AXScript Reference

### Core Functions
```javascript
// Movement and physics
move(dx, dy)              // Move by offset
rotate(angle)             // Rotate by angle
setProperty(name, value)  // Set object property
getProperty(name)         // Get object property
applyForce(fx, fy)        // Apply physics force

// Position and transformation
var pos = getProperty("position");
setProperty("position", {x: 100, y: 200});
setProperty("rotation", 45);
setProperty("scale", {x: 1.5, y: 1.5});
```

### Input System
```javascript
// Keyboard
if (keyPressed("Space")) {          // Key held down
    jump();
}
if (keyJustPressed("Enter")) {      // Key just pressed
    startGame();
}

// Mouse
if (mousePressed(0)) {              // Left mouse button
    shoot();
}
var mousePos = getMousePos();       // Mouse position
```

### Debug Functions (NEW!)
```javascript
// Debugging and development
debugBreak();                       // Set breakpoint
debugLog(message);                  // Debug output
debugWatch(expression);             // Watch variable
debugClear();                       // Clear debug output

// Performance monitoring
var stats = getEngineStats();
debugLog("FPS: " + stats.fps);
```

### Advanced Collision (NEW!)
```javascript
// Collision detection
if (pixelPerfectCollision(other)) {
    handlePreciseCollision();
}

if (satCollision(other)) {
    handlePolygonCollision();
}

// Collision layers
if (checkCollisionLayer("enemies")) {
    takeDamage(10);
}
```

### Mathematical Functions
```javascript
// Basic math
var result = sin(angle);
var distance = sqrt(dx*dx + dy*dy);
var randomValue = random();         // 0-1
var clamped = clamp(value, 0, 100);

// Utility functions
var dist = distance(x1, y1, x2, y2);
var angle = atan2(dy, dx) * 180 / Math.PI;
```

### Audio System
```javascript
// Sound effects
playSound("explosion");
playSound("music", -1);             // Loop infinitely

// Music control
playMusic("background.mp3");
stopMusic();
setVolume(0.7, 0.5);               // Music, effects
```

### Animation and Effects
```javascript
// Object animation
setAnimation("walk", 1.5, true);    // Name, speed, loop
playAnimation("jump");
pauseAnimation();

// Particle effects
createExplosion(x, y, size);
createSmoke(x, y, duration);
```

### Error Handling (NEW!)
```javascript
// Try-catch for error handling
try {
    riskyOperation();
} catch (error) {
    debugLog("Error occurred: " + error);
    fallbackBehavior();
}

// Validation
if (objectExists("target")) {
    attackTarget();
}
```

## 🎯 Object Types

### rectangle
```python
obj = GameObject("Box", "rectangle")
obj.set_property("width", 100)
obj.set_property("height", 50)
obj.set_property("color", (255, 0, 0))
```

### circle
```python
obj = GameObject("Ball", "circle")
obj.set_property("radius", 25)
obj.set_property("color", (0, 255, 0))
```

### sprite
```python
obj = GameObject("Player", "sprite")
obj.set_sprite("player_idle")  # Load image
```

### animated_sprite
```python
obj = GameObject("Character", "animated_sprite")
obj.set_animation("walk_cycle", speed=1.0, loop=True)
```

## 🎨 Advanced Renderer API

### Basic Drawing
```python
# Access renderer
renderer = engine.renderer

# Basic shapes
renderer.draw_rect(x, y, width, height, color)
renderer.draw_circle(x, y, radius, color)
renderer.draw_line(x1, y1, x2, y2, color, width)

# Sprite rendering
renderer.draw_sprite(x, y, sprite_surface, rotation)

# Text rendering
renderer.draw_text("Hello World", x, y, color, font)
```

### Camera System
```python
# Camera control
renderer.set_camera(x, y)
renderer.move_camera(dx, dy)

# Object following
renderer.follow_object(player, offset_x=0, offset_y=-100)

# Coordinate conversion
world_pos = renderer.screen_to_world(screen_x, screen_y)
screen_pos = renderer.world_to_screen(world_x, world_y)
```

### Layer Management (NEW!)
```python
# Create and manage layers
renderer.add_layer("background", z_order=-10)
renderer.add_layer("characters", z_order=0)
renderer.add_layer("effects", z_order=10)

# Set object layer
obj.set_property("layer", "characters")
obj.set_property("z_order", 5)
```

### Debug Rendering
```python
# Debug features
renderer.enable_debug(True)
renderer.show_object_bounds(True)
renderer.show_velocity_vectors(True)
renderer.show_collision_shapes(True)
```

## 🔧 Scene Management

### Creating Scenes
```python
# New scene
scene = Scene("Level1")
scene.set_gravity(0, 400)          # Gravity
scene.set_bounds(0, 0, 1200, 800)  # World bounds

# Add objects
scene.add_object(player)
scene.add_object(enemy)

# Get objects
player = scene.get_object("Player")
enemies = scene.get_objects_with_tag("enemy")
```

### Scene Management in Engine
```python
# Create and switch scenes
main_scene = engine.create_scene("Main")
menu_scene = engine.create_scene("Menu")

engine.current_scene = main_scene
engine.switch_scene("Menu")
```

## 🎵 Audio System

### Loading Sounds
```python
from engine.asset_manager import asset_manager

# Load sound effects
asset_manager.load_sound("jump", "sounds/jump.wav", volume=0.8)
asset_manager.load_sound("coin", "sounds/coin.wav")

# Play sounds
asset_manager.play_sound("jump")
```

### Music Control
```python
# Music management
from engine.audio_system import audio_system

audio_system.load_music("music/background.mp3")
audio_system.play_music(loops=-1)  # Infinite loop
audio_system.set_music_volume(0.6)
```

## 💫 Animation System

### Simple Animations
```python
from engine.animation_system import animation_system

# Move to position
animation_system.move_to(obj, target_x, target_y, duration=2.0)

# Rotation
animation_system.rotate_to(obj, 180, duration=1.0)

# Scale change
animation_system.scale_to(obj, 2.0, 2.0, duration=0.5)

# Effects
animation_system.bounce(obj, height=50, duration=1.0)
animation_system.pulse(obj, scale_factor=1.5, duration=0.8)
```

### Easing Functions
```python
from engine.animation_system import Easing

# Different easing types
animation_system.move_to(obj, x, y, 2.0, Easing.ease_out_quad)
animation_system.rotate_to(obj, 360, 3.0, Easing.bounce_out)
animation_system.scale_to(obj, 0.5, 0.5, 1.0, Easing.ease_in_out_quad)
```

## 🎪 Particle System

### Basic Effects
```python
from engine.particle_system import particle_system

# Explosion
particle_system.create_explosion(x, y, particle_count=50)

# Smoke
particle_system.create_smoke(x, y, duration=3.0)

# Custom particles
particle_system.emit_particles(
    x, y, 
    count=20,
    velocity_range=(50, 100),
    color=(255, 100, 0),
    lifetime=2.0
)
```

## 🎯 Complete Example: Advanced Space Shooter

```python
#!/usr/bin/env python3
"""
Complete Example: Advanced Space Shooter with Hot Reload and Debugging
"""

from engine.core import AxarionEngine
from engine.game_object import GameObject
from engine.asset_manager import asset_manager
from engine.debug_system import debug_system
from engine.hot_reload_system import hot_reload_system

def create_advanced_space_shooter():
    # Initialize engine
    engine = AxarionEngine(800, 600)
    engine.initialize()
    
    # Enable advanced features
    debug_system.enable()
    hot_reload_system.enable()
    
    # Load assets
    asset_manager.load_all_assets()
    
    # Create scene
    scene = engine.create_scene("AdvancedSpaceShooter")
    engine.current_scene = scene
    
    # Player ship with advanced features
    player = GameObject("Player", "sprite")
    player.position = (400, 500)
    player.set_sprite("ship")
    player.mass = 1.0
    player.add_tag("player")
    
    # Advanced player script with debugging
    player.script_code = """
var speed = 200;
var shootCooldown = 0;
var health = 100;
var powerLevel = 1;

function update() {
    shootCooldown -= 0.016;
    
    // Debug current state
    debugWatch("health");
    debugWatch("powerLevel");
    debugWatch("position");
    
    handleMovement();
    handleShooting();
    handlePowerups();
    
    // Performance check
    var stats = getEngineStats();
    if (stats.fps < 45) {
        debugLog("Performance warning: FPS = " + stats.fps);
    }
}

function handleMovement() {
    try {
        var pos = getProperty("position");
        
        if (keyPressed("ArrowLeft") && pos.x > 32) {
            move(-speed * 0.016, 0);
        }
        if (keyPressed("ArrowRight") && pos.x < 768) {
            move(speed * 0.016, 0);
        }
        if (keyPressed("ArrowUp") && pos.y > 32) {
            move(0, -speed * 0.016);
        }
        if (keyPressed("ArrowDown") && pos.y < 568) {
            move(0, speed * 0.016);
        }
    } catch (error) {
        debugLog("Movement error: " + error);
    }
}

function handleShooting() {
    if (keyPressed("Space") && shootCooldown <= 0) {
        var pos = getProperty("position");
        
        // Create multiple bullets based on power level
        for (var i = 0; i < powerLevel; i++) {
            var offsetX = (i - (powerLevel - 1) / 2) * 20;
            createBullet(pos.x + offsetX, pos.y - 10);
        }
        
        playSound("laser");
        shootCooldown = 0.15;
    }
}

function createBullet(x, y) {
    // Advanced bullet creation
    debugLog("Creating bullet at: " + x + ", " + y);
    
    var bullet = instantiate("circle", x, y);
    bullet.setProperty("radius", 3);
    bullet.setProperty("color", [255, 255, 0]);
    bullet.setProperty("velocity", {x: 0, y: -500});
    bullet.setProperty("collision_type", "pixel_perfect");
    bullet.addTag("bullet");
}

function takeDamage(amount) {
    health -= amount;
    debugLog("Player took " + amount + " damage. Health: " + health);
    
    if (health <= 0) {
        debugBreak(); // Debug when player dies
        gameOver();
    }
}

function powerUp() {
    powerLevel = Math.min(powerLevel + 1, 5);
    debugLog("Power level increased to: " + powerLevel);
    playSound("powerup");
}

function gameOver() {
    debugLog("Game Over! Final score: " + getGlobal("score", 0));
    createExplosion(getProperty("position").x, getProperty("position").y);
}
"""
    
    # Advanced enemy with AI
    enemy = GameObject("SmartEnemy", "sprite")
    enemy.position = (200, 100)
    enemy.set_sprite("enemy")
    enemy.add_tag("enemy")
    
    enemy.script_code = """
var health = 50;
var attackCooldown = 0;
var moveDirection = 1;
var aggroRange = 200;
var attackRange = 150;

function update() {
    attackCooldown -= 0.016;
    
    updateAI();
    updateMovement();
    
    // Debug AI state
    debugWatch("health");
    debugWatch("moveDirection");
}

function updateAI() {
    var player = findObjectByTag("player");
    if (!player) return;
    
    var distance = distanceToObject(player);
    
    if (distance < aggroRange) {
        // Move towards player
        var playerPos = player.getProperty("position");
        var myPos = getProperty("position");
        
        if (playerPos.x > myPos.x) moveDirection = 1;
        else moveDirection = -1;
        
        if (distance < attackRange && attackCooldown <= 0) {
            attack(player);
        }
    }
}

function updateMovement() {
    move(moveDirection * 100 * 0.016, sin(getTime() * 2) * 30 * 0.016);
    
    // Boundary checking
    var pos = getProperty("position");
    if (pos.x < 50 || pos.x > 750) {
        moveDirection *= -1;
    }
}

function attack(target) {
    debugLog("Enemy attacking player!");
    
    var pos = getProperty("position");
    var targetPos = target.getProperty("position");
    
    // Calculate direction to player
    var dx = targetPos.x - pos.x;
    var dy = targetPos.y - pos.y;
    var distance = sqrt(dx*dx + dy*dy);
    
    // Normalize and create bullet
    dx /= distance;
    dy /= distance;
    
    var bullet = instantiate("circle", pos.x, pos.y);
    bullet.setProperty("radius", 4);
    bullet.setProperty("color", [255, 0, 0]);
    bullet.setProperty("velocity", {x: dx * 300, y: dy * 300});
    bullet.addTag("enemy_bullet");
    
    playSound("enemy_shoot");
    attackCooldown = 2.0;
}

function takeDamage(amount) {
    health -= amount;
    debugLog("Enemy took " + amount + " damage. Health: " + health);
    
    if (health <= 0) {
        createExplosion(getProperty("position").x, getProperty("position").y);
        setGlobal("score", getGlobal("score", 0) + 100);
        destroy();
    }
}
"""
    
    scene.add_object(player)
    scene.add_object(enemy)
    
    # Set up debugging
    debug_session = debug_system.create_session("space_shooter_debug")
    player.set_debug_session(debug_session.session_id)
    enemy.set_debug_session(debug_session.session_id)
    
    return engine

# Run the advanced example
if __name__ == "__main__":
    engine = create_advanced_space_shooter()
    
    print("🎮 Advanced Space Shooter with Hot Reload")
    print("=" * 50)
    print("✅ Hot reload enabled - modify scripts and see instant changes!")
    print("✅ Debug system active - use debugBreak() for breakpoints")
    print("✅ Advanced collision and AI systems loaded")
    print("\n🎯 Controls:")
    print("   Arrow Keys - Move ship")
    print("   Space - Shoot")
    print("   ESC - Exit")
    print("\n🐛 Debug Commands:")
    print("   Add debugBreak() to scripts for breakpoints")
    print("   Use debugLog() for debug output")
    print("   Modify scripts and save for hot reload")
    
    engine.run()
```

## 🔧 Advanced Features

### Performance Optimization
```python
# Object pooling for bullets
class BulletPool:
    def __init__(self, size=100):
        self.bullets = []
        for i in range(size):
            bullet = GameObject(f"Bullet_{i}", "circle")
            bullet.active = False
            self.bullets.append(bullet)
    
    def get_bullet(self):
        for bullet in self.bullets:
            if not bullet.active:
                bullet.active = True
                return bullet
        return None

# Use in engine
bullet_pool = BulletPool()
engine.add_game_system(bullet_pool)
```

### Custom Game Systems
```python
class ScoreSystem:
    def __init__(self):
        self.score = 0
        self.high_score = self.load_high_score()
        self.lives = 3
    
    def add_score(self, points):
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
    
    def lose_life(self):
        self.lives -= 1
        return self.lives <= 0

# Add to engine
score_system = ScoreSystem()
engine.add_game_system(score_system)
```

### Save and Load System
```python
# Save game state
engine.save_game("savegame.json")

# Load game state
engine.load_game("savegame.json")

# Project export/import
from utils.file_manager import FileManager
fm = FileManager()
fm.export_project_archive("my_game", "game.zip")
fm.import_project_archive("game.zip", "imported_games/")
```

## 🎮 Tips and Best Practices

### Development Workflow
1. **Start Simple**: Begin with basic movement and collision
2. **Use Hot Reload**: Make changes and see them instantly
3. **Debug Early**: Add debugBreak() and debugLog() liberally
4. **Error Handling**: Use try-catch in complex scripts
5. **Performance**: Monitor FPS and optimize as needed

### Performance Tips
```python
# Culling for large scenes
for obj in scene.get_all_objects():
    if renderer.is_on_screen(obj):
        obj.update(delta_time)

# Batch similar operations
# Use object pooling for frequently created/destroyed objects
# Enable sprite batching for multiple similar sprites
```

### Debugging Strategies
```javascript
// Comprehensive debugging
function update() {
    debugWatch("state");
    debugWatch("health");
    debugWatch("position");
    
    try {
        gameLogic();
    } catch (error) {
        debugLog("Error in gameLogic: " + error);
        debugBreak(); // Stop here to investigate
        fallbackBehavior();
    }
}
```

## 🚀 Deployment Guide

### Preparing for Release
```python
# Optimize assets
asset_manager.optimize_assets()
asset_manager.compress_images(quality=85)

# Disable debug features
debug_system.disable()
hot_reload_system.disable()

# Final export
engine.export_game("my_game_release/")
```
---

## 📞 Support and Community

- **Documentation**: This file plus inline code comments
- **Examples**: `examples/` folder contains complete game examples
- **Assets**: `assets/` folder has sample sprites and sounds

---

## 🎉 Conclusion

Axarion Engine provides a powerful and flexible framework for creating 2D games with a focus on code-first development. With comprehensive asset management, advanced physics, professional debugging tools, and hot reload capabilities, you can create complex games quickly and efficiently.

The combination of hot reload and advanced debugging makes Axarion perfect for rapid prototyping and professional game development. Start with simple examples and gradually work your way up to advanced features.

**Happy Coding! 🎮**
