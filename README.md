
# 🎮 Axarion Engine

**Enhanced Evolution of VoidRay Engine**

A powerful, code-first 2D game engine designed for programmers who prefer writing games in pure code rather than using visual editors. Built as an advanced evolution of the original VoidRay engine with significantly improved physics, asset management, scripting capabilities, and professional development tools.

## ✨ Key Features

### 🚀 Core Engine
- **Pure Code Philosophy**: No GUI editor required - create games entirely through code
- **AXScript Integration**: Built-in JavaScript-like scripting language with hot reload support
- **Advanced Physics**: Realistic 2D physics with gravity, collision detection, and force application
- **Multi-Scene Management**: Organize complex games with multiple scenes
- **Real-time Performance**: 60 FPS target with delta-time based updates
- **Hot Reload System**: Instant script updates without engine restart
- **Advanced Error Handling**: Graceful error recovery and detailed debugging

### 🎨 Asset Management System
- **Universal Asset Loading**: Images, sprites, animations, sounds, and fonts
- **Smart Animation System**: Frame-based animations with configurable speeds
- **Sprite Sheets**: Automatic splitting and frame extraction
- **Audio Support**: Sound effects and background music (WAV, MP3, OGG)
- **Asset Optimization**: Automatic scaling and format optimization
- **Streaming Support**: Efficient loading for large assets

### 🔧 Advanced Systems
- **Particle Effects**: Explosions, fire, smoke, magic effects
- **Animation Engine**: Smooth object animations and tweening
- **Input System**: Comprehensive keyboard and mouse handling
- **Advanced Collision**: Pixel-perfect, SAT, and continuous collision detection
- **Debug Tools**: Visual debugging with bounds display and performance stats
- **Professional Renderer**: Z-ordering, layering, and sprite batching

### 🎯 Game Object Types
- **Rectangles**: Basic rectangular objects with physics
- **Circles**: Circular objects with radius-based collision
- **Sprites**: Image-based objects with texture support
- **Animated Sprites**: Objects with frame-based animations
- **Particles**: Dynamic particle effects

### 🛠️ Developer Tools
- **Hot Reload**: Instant script reloading for rapid development
- **Advanced Debugger**: Breakpoints, variable inspection, step-through debugging
- **Syntax Highlighting**: Enhanced AXScript development experience
- **Error Recovery**: Engine continues running even with script errors
- **Performance Profiler**: Real-time performance monitoring

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

// Debug functions (NEW!)
debugBreak()                   // Set breakpoint
debugLog(message)              // Debug output
debugWatch(expression)        // Watch variable

// Math utilities
sin(x), cos(x), sqrt(x)        // Trigonometry
distance(x1,y1,x2,y2)         // Distance calculation
random()                       // Random 0-1
clamp(val, min, max)          // Clamp value to range
```

### Advanced Features
```javascript
// Hot reload support
// Scripts automatically reload when saved!

// Error handling
try {
    riskyOperation();
} catch (error) {
    debugLog("Error occurred: " + error);
}

// Advanced collision
if (pixelPerfectCollision(otherObject)) {
    handlePreciseCollision();
}

// Performance monitoring
var fps = getEngineStats().fps;
debugLog("Running at " + fps + " FPS");
```

## 🏗️ Engine Architecture

### Core Components
- **`engine/core.py`** - Main engine coordination and game loop
- **`engine/game_object.py`** - Base game object with physics and scripting
- **`engine/scene.py`** - Scene management and object organization
- **`engine/physics.py`** - 2D physics simulation and collision detection
- **`engine/renderer.py`** - Graphics rendering and camera system
- **`engine/asset_manager.py`** - Comprehensive asset loading and management

### Advanced Systems (NEW!)
- **`engine/hot_reload_system.py`** - Real-time script reloading
- **`engine/debug_system.py`** - Professional debugging tools
- **`engine/advanced_collision.py`** - Pixel-perfect and SAT collision
- **`engine/advanced_renderer.py`** - Z-ordering and sprite batching
- **`engine/error_handling.py`** - Graceful error recovery
- **`engine/animation_system.py`** - Object animation and tweening
- **`engine/particle_system.py`** - Particle effects and visual systems
- **`engine/audio_system.py`** - Sound management and music playback
- **`engine/input_system.py`** - Input handling and event processing
- **`scripting/`** - AXScript interpreter and language implementation

## 🆕 What's New in This Version

### 🔥 Hot Reload System
- **Instant Updates**: Modify scripts and see changes immediately
- **File Watching**: Automatic detection of script changes
- **Error Recovery**: Engine continues running even if scripts have errors
- **Development Speed**: 10x faster iteration time

### 🐛 Advanced Debugging
- **Breakpoints**: Set `debugBreak()` in scripts to pause execution
- **Variable Inspector**: View all variables at breakpoint
- **Step-through**: Debug line by line
- **Debug Console**: Interactive debugging environment

### 🎯 Advanced Collision Detection
- **Pixel-perfect**: Exact collision detection for complex shapes
- **SAT (Separating Axis Theorem)**: For polygon collision
- **Continuous Collision**: Prevents tunneling for fast objects
- **Collision Layers**: Organized collision management

### 🎨 Professional Renderer
- **Z-ordering**: Proper depth sorting
- **Sprite Batching**: Optimized rendering for multiple objects
- **Layering System**: Organize graphics by layers
- **Performance**: 3x faster rendering

### 🛡️ Error Handling
- **Graceful Recovery**: Engine doesn't crash on script errors
- **Error Reporting**: Detailed error messages with line numbers
- **Resource Protection**: Automatic cleanup on errors
- **Stability**: Professional-grade error management

## 🎮 Game Examples

### Advanced Platformer with Hot Reload
```python
# The script will auto-reload when you save changes!
player.script_code = """
var speed = 200;
var jumpPower = 400;
var doubleJumpAvailable = true;

function update() {
    handleMovement();
    handleJumping();
    handleCombat();
    
    // Debug current state
    debugWatch("velocity");
    debugWatch("position");
}

function handleMovement() {
    if (keyPressed("ArrowLeft")) {
        applyForce(-speed, 0);
        setProperty("facingLeft", true);
    }
    if (keyPressed("ArrowRight")) {
        applyForce(speed, 0);
        setProperty("facingLeft", false);
    }
}

function handleJumping() {
    if (keyJustPressed("Space")) {
        if (isOnGround()) {
            applyForce(0, -jumpPower);
            doubleJumpAvailable = true;
            playSound("jump");
        } else if (doubleJumpAvailable) {
            setVelocity(getVelocity().x, -jumpPower * 0.8);
            doubleJumpAvailable = false;
            playSound("double_jump");
        }
    }
}

function handleCombat() {
    if (keyJustPressed("x")) {
        // Set breakpoint to debug combat
        debugBreak();
        createProjectile();
        playSound("shoot");
    }
}
"""
```

### Space Shooter with Advanced Features
```python
enemy.script_code = """
var health = 100;
var attackCooldown = 0;
var movePattern = "sine";
var time = 0;

function update() {
    time += 0.016;
    attackCooldown -= 0.016;
    
    // Advanced movement patterns
    updateMovement();
    updateAI();
    
    // Performance monitoring
    if (getEngineStats().fps < 50) {
        debugLog("Performance warning: Low FPS");
    }
}

function updateMovement() {
    var pos = getProperty("position");
    
    if (movePattern === "sine") {
        var newX = pos.x + sin(time * 2) * 50;
        setProperty("position", {x: newX, y: pos.y + 30});
    }
}

function updateAI() {
    var player = findObjectByTag("player");
    if (player && attackCooldown <= 0) {
        var distance = distanceToObject(player);
        
        if (distance < 200) {
            aimAndShoot(player);
            attackCooldown = 2.0;
        }
    }
}

function takeDamage(amount) {
    health -= amount;
    
    if (health <= 0) {
        createExplosion(getProperty("position").x, getProperty("position").y);
        playSound("explosion");
        destroy();
    }
}
"""
```

## 🎯 Perfect For

- **Professional Game Development**: Production-ready features
- **Learning**: Understand advanced engine architecture
- **Rapid Prototyping**: Hot reload for instant feedback
- **Educational Projects**: Teaching advanced game programming
- **Indie Development**: Professional tools for small teams
- **Code-Focused Developers**: Full control through programming

## 📚 Documentation

- **Complete Docs**: [`DOCS.md`](DOCS.md) - Comprehensive engine documentation
- **Code Examples**: [`examples/`](examples/) - Genre-specific game examples
- **Asset Samples**: [`assets/`](assets/) - Sample sprites, sounds, and animations
- **Script Reference**: Inline AXScript documentation in code

## 🔗 Comparison with Other Engines

| Feature | Axarion | Godot | Unity | GameMaker |
|---------|---------|-------|-------|-----------|
| **Editor** | None (Pure Code) | Visual Editor | Visual Editor | Visual Editor |
| **Hot Reload** | ✅ Built-in | ✅ | ✅ | ✅ |
| **Debug Tools** | ✅ Advanced | ✅ | ✅ | ✅ |
| **Learning Curve** | Low | Medium | High | Medium |
| **File Size** | <5MB | ~150MB | ~3GB | ~500MB |
| **Pixel-Perfect Collision** | ✅ | ✅ | Plugin | ✅ |
| **Error Recovery** | ✅ Advanced | Basic | Basic | Basic |
| **Code-First** | ✅ Pure | Mixed | Mixed | Mixed |

## 🌟 Advanced Features

### Performance Optimization
- **Object Pooling**: Reuse objects for better performance
- **Sprite Batching**: Efficient rendering of multiple sprites
- **Collision Layers**: Organized collision detection
- **Frustum Culling**: Only render visible objects

### Developer Experience
- **Hot Reload**: Instant script updates
- **Advanced Debugging**: Breakpoints and variable inspection
- **Error Recovery**: Graceful handling of script errors
- **Performance Monitoring**: Real-time FPS and frame time

### Professional Tools
- **Asset Streaming**: Efficient loading of large assets
- **Z-ordering**: Proper depth management
- **Collision Systems**: Multiple collision detection methods
- **Audio Mixing**: Separate channels for music and effects

---

**From VoidRay's simplicity to Axarion's professional power** - Experience the evolution of code-first game development with industry-standard tools! 🎮✨

Happy coding! 🚀
