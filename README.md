
# 🎮 Axarion Engine - Advanced 2D Game Engine

**Enhanced Evolution of VoidRay Engine**

A powerful, code-first 2D game engine designed for programmers who prefer writing games in pure code rather than using visual editors. Built as an advanced evolution of the original VoidRay engine with significantly improved physics, asset management, and scripting capabilities.

## ✨ Key Features

### 🚀 Core Engine
- **Pure Code Philosophy**: No GUI editor required - create games entirely through code
- **AXScript Integration**: Built-in JavaScript-like scripting language for game logic
- **Advanced Physics**: Realistic 2D physics with gravity, collision detection, and force application
- **Multi-Scene Management**: Organize complex games with multiple scenes
- **Real-time Performance**: 60 FPS target with delta-time based updates

### 🎨 Asset Management System
- **Universal Asset Loading**: Images, sprites, animations, sounds, and fonts
- **Smart Animation System**: Frame-based animations with configurable speeds
- **Sprite Sheets**: Automatic splitting and frame extraction
- **Audio Support**: Sound effects and background music (WAV, MP3, OGG)
- **Asset Optimization**: Automatic scaling and format optimization

### 🔧 Advanced Systems
- **Particle Effects**: Explosions, fire, smoke, magic effects
- **Animation Engine**: Smooth object animations and tweening
- **Input System**: Comprehensive keyboard and mouse handling
- **Collision Layers**: Organized collision detection with layer management
- **Debug Tools**: Visual debugging with bounds display and performance stats

### 🎯 Game Object Types
- **Rectangles**: Basic rectangular objects with physics
- **Circles**: Circular objects with radius-based collision
- **Sprites**: Image-based objects with texture support
- **Animated Sprites**: Objects with frame-based animations
- **Particles**: Dynamic particle effects

## 🚀 Quick Start

### 1. Run Demo Games
```bash
# Physics and movement demo
python test_fixed_engine.py

# Complete assets and sprites demo
python test_assets_demo.py

# Generate sample assets
python assets/create_sample_assets.py
```

### 2. Basic Game Structure
```python
from engine.core import AxarionEngine
from engine.game_object import GameObject
from engine.asset_manager import asset_manager

# Initialize engine
engine = AxarionEngine(800, 600)
engine.initialize()

# Load all assets automatically
asset_manager.load_all_assets()

# Create and set up scene
scene = engine.create_scene("MainGame")
scene.set_gravity(0, 800)  # Realistic gravity
engine.current_scene = scene

# Create player with sprite
player = GameObject("Player", "sprite")
player.position = (100, 100)
player.set_sprite("ship")  # Load from assets/images/ship.png
player.mass = 1.0
player.friction = 0.8

# Add game logic with AXScript
player.script_code = """
var speed = 300;
var jumpPower = 400;

function update() {
    // Movement controls
    if (keyPressed("ArrowLeft") || keyPressed("a")) {
        applyForce(-speed, 0);
    }
    if (keyPressed("ArrowRight") || keyPressed("d")) {
        applyForce(speed, 0);
    }
    
    // Jumping with ground detection
    if ((keyPressed("ArrowUp") || keyPressed("w") || keyPressed(" ")) && isOnGround()) {
        applyForce(0, -jumpPower);
        playSound("jump");
    }
}
"""

# Add to scene and run
scene.add_object(player)
engine.run()
```

## 🎨 Asset System

### Folder Structure
```
assets/
├── images/          # Sprites (.png, .jpg, .gif, .bmp)
│   ├── ship.png
│   ├── enemy.png
│   └── coin.png
├── sounds/          # Audio (.wav, .mp3, .ogg)
│   ├── laser.wav
│   └── music.mp3
├── animations/      # Animation folders
│   ├── explosion/   # Contains frame_00.png, frame_01.png, etc.
│   └── spinning_coin/
└── fonts/           # Fonts (.ttf, .otf)
    └── game_font.ttf
```

### Loading Assets
```python
from engine.asset_manager import asset_manager

# Automatic loading (recommended)
asset_manager.load_all_assets()

# Manual loading
asset_manager.load_image("player", "assets/images/ship.png")
asset_manager.load_sound("laser", "assets/sounds/laser.wav")
asset_manager.load_animation("explosion", "assets/animations/explosion/")

# Using in objects
player.set_sprite("player")
coin.set_animation("spinning_coin", speed=2.0)
player.play_sound("laser")
```

## 📝 AXScript Reference

### Core Functions
```javascript
// Movement and physics
move(dx, dy)                    // Move by offset
applyForce(fx, fy)             // Apply physics force
setProperty(name, value)        // Set object property
getProperty(name)              // Get object property
rotate(angle)                  // Rotate object

// Input handling
keyPressed("key")              // Check if key is held
keyJustPressed("key")          // Check if key was just pressed
mouseClicked(button)           // Check mouse click
getMousePos()                  // Get mouse position

// Physics queries
isOnGround()                   // Check if touching ground/platform
getVelocity()                  // Get current velocity
setVelocity(vx, vy)           // Set velocity directly

// Audio
playSound("sound_name")        // Play sound effect
playMusic("music_name")        // Play background music

// Animation
playAnimation("anim_name")     // Play animation
stopAnimation()                // Stop current animation

// Math utilities
sin(x), cos(x), sqrt(x)        // Trigonometry
distance(x1,y1,x2,y2)         // Distance calculation
random()                       // Random 0-1
clamp(val, min, max)          // Clamp value to range
```

### Advanced Scripting
```javascript
// Timer system
startTimer("myTimer", 3.0);
if (isTimerFinished("myTimer")) {
    // Timer completed
}

// Object interaction
var nearbyObjects = getObjectsInRange(100);
var target = findObjectByTag("enemy");

// Stats and RPG elements
takeDamage(25);
heal(10);
var health = getStat("health");

// Inventory
addItem({name: "sword", damage: 15});
if (hasItem("key")) {
    // Player has key
}
```

## 🏗️ Engine Architecture

### Core Components
- **`engine/core.py`** - Main engine coordination and game loop
- **`engine/game_object.py`** - Base game object with physics and scripting
- **`engine/scene.py`** - Scene management and object organization
- **`engine/physics.py`** - 2D physics simulation and collision detection
- **`engine/renderer.py`** - Graphics rendering and camera system
- **`engine/asset_manager.py`** - Comprehensive asset loading and management

### Advanced Systems
- **`engine/animation_system.py`** - Object animation and tweening
- **`engine/particle_system.py`** - Particle effects and visual systems
- **`engine/audio_system.py`** - Sound management and music playback
- **`engine/input_system.py`** - Input handling and event processing
- **`scripting/`** - AXScript interpreter and language implementation

## 🎯 Engine Evolution: VoidRay → Axarion

### What's New in Axarion
**Axarion Engine** represents a complete evolution of the original **VoidRay engine**, featuring:

#### Major Improvements Over VoidRay:
- **🔧 Advanced Physics**: Complete rewrite with proper force application, friction, and realistic collision resolution
- **🎨 Asset Pipeline**: Professional asset management system supporting sprites, animations, and audio
- **📝 AXScript Language**: Full scripting language implementation (VoidRay had basic scripting)
- **🎮 Multiple Object Types**: Support for sprites, animated sprites, particles (VoidRay was mainly rectangles)
- **🎪 Particle Systems**: Built-in particle effects for explosions, magic, weather
- **🎵 Audio Integration**: Complete audio system with music and sound effects
- **📱 Scene Management**: Multi-scene architecture for complex games
- **🛠️ Debug Tools**: Visual debugging, performance monitoring, and development aids

#### Maintained VoidRay Philosophy:
- **Code-First Approach**: No visual editor, pure programming focus
- **Lightweight Design**: Fast startup and minimal dependencies
- **Educational Focus**: Perfect for learning game development concepts
- **Python-Based**: Easy to understand and modify engine internals

## 🎮 Game Examples

### Platformer Game
```python
# Create platformer with physics
player = GameObject("Player", "sprite")
player.set_sprite("hero")
player.mass = 1.2
player.friction = 0.8

# Ground and platforms
ground = GameObject("Ground", "rectangle")
ground.is_static = True
ground.add_tag("platform")

# Enemy with AI
enemy = GameObject("Enemy", "animated_sprite")
enemy.set_animation("enemy_walk")
enemy.script_code = """
var patrolSpeed = 50;
var direction = 1;

function update() {
    move(direction * patrolSpeed * 0.016, 0);
    
    // Turn around at edges
    if (getProperty("position").x > 700 || getProperty("position").x < 100) {
        direction *= -1;
    }
}
"""
```

### Space Shooter
```python
# Player ship
ship = GameObject("Ship", "sprite")
ship.set_sprite("spaceship")
ship.script_code = """
var speed = 200;

function update() {
    if (keyPressed("ArrowLeft")) move(-speed * 0.016, 0);
    if (keyPressed("ArrowRight")) move(speed * 0.016, 0);
    if (keyPressed(" ")) {
        // Create bullet
        createObject("Bullet", getProperty("position").x, getProperty("position").y - 10);
        playSound("laser");
    }
}
"""
```

## 🚀 Deployment on Replit

The engine is fully compatible with Replit and ready to run:

1. **Direct Execution**: Run demos immediately with the Run button
2. **Web Deployment**: Use Replit's deployment features for web games
3. **Asset Management**: Assets are automatically detected and loaded
4. **Performance**: Optimized for Replit's environment

```bash
# Run physics demo
python test_fixed_engine.py

# Run complete game demo
python test_assets_demo.py
```

## 🎯 Perfect For

- **Learning Game Development**: Understand engine internals through code
- **Rapid Prototyping**: Quick game concept testing
- **Educational Projects**: Teaching game programming concepts
- **Indie Development**: Lightweight engine for small to medium games
- **Code-Focused Developers**: Full control through programming

## 📚 Documentation

- **Complete Docs**: [`DOCS.md`](DOCS.md) - Comprehensive engine documentation
- **Code Examples**: [`examples/`](examples/) - Genre-specific game examples
- **Asset Samples**: [`assets/`](assets/) - Sample sprites, sounds, and animations
- **Script Reference**: Inline AXScript documentation in code

## 🔗 Key Differences from Other Engines

| Feature | Axarion | Godot | Unity | GameMaker |
|---------|---------|-------|-------|-----------|
| Editor | None (Pure Code) | Visual Editor | Visual Editor | Visual Editor |
| Language | Python + AXScript | GDScript/C# | C#/UnityScript | GML |
| Learning Curve | Low | Medium | High | Medium |
| File Size | <1MB | ~150MB | ~3GB | ~500MB |
| Asset Pipeline | Code-Based | Node System | Inspector | Drag & Drop |
| Physics | Custom 2D | Built-in 2D/3D | Built-in 3D | Built-in 2D |

---

**From VoidRay's simplicity to Axarion's power** - Experience the evolution of code-first game development! 🎮✨

Happy coding! 🚀
