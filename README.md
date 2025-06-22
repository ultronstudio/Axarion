# 🎮 Axarion Engine - Code-Only Game Engine

A powerful 2D game engine designed for programmers who prefer writing games in pure code!

## ✨ Features

- **Pure Code Approach**: No GUI editor - write games directly in code
- **AXScript Integration**: Built-in scripting language for game logic
- **Asset Management**: Complete system for images, sounds, and animations
- **Physics System**: Built-in 2D physics simulation
- **Audio Support**: Sound effects and background music
- **Particle Effects**: Explosions, fire, smoke and more
- **Animation System**: Smooth object animations
- **Scene Management**: Organize your game into scenes

## 🚀 Quick Start

1. **Run the sample game:**
```bash
python test_fixed_engine.py
```

2. **Run the assets demo:**
```bash
python test_assets_demo.py
```

3. **Create sample assets:**
```bash
python assets/create_sample_assets.py
```

## 🎯 Basic Game Structure

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
player.set_sprite("ship")

# Add game logic with AXScript
player.script_code = """
var speed = 200;

function update() {
    if (keyPressed("ArrowLeft")) {
        move(-speed * 0.016, 0);
    }
    if (keyPressed("ArrowRight")) {
        move(speed * 0.016, 0);
    }
}
"""

# Add to scene and run
scene.add_object(player)
engine.run()
```

## 🎮 Object Types

- **rectangle**: Rectangular objects with width/height
- **circle**: Circular objects with radius
- **sprite**: Image-based objects
- **animated_sprite**: Objects with frame animations

## 📝 AXScript Reference

### Movement Functions
```javascript
move(dx, dy)              // Move object by offset
rotate(angle)             // Rotate object
setProperty(name, value)  // Set object property
getProperty(name)         // Get object property
```

### Input Functions
```javascript
keyPressed("key")         // Check if key is held down
keyJustPressed("key")     // Check if key was just pressed
mouseClicked(button)      // Check mouse click
getMousePos()            // Get mouse position
```

### Math Functions
```javascript
sin(x), cos(x), sqrt(x)   // Basic math
distance(x1,y1,x2,y2)    // Distance between points
random()                 // Random 0-1
clamp(val, min, max)     // Clamp value
```

### Audio Functions
```javascript
playSound("file.wav")     // Play sound effect
playMusic("file.mp3")     // Play background music
setVolume(music, sfx)     // Set audio volumes
```

## 🎨 Asset Management

### Loading Assets
```python
from engine.asset_manager import asset_manager

# Load image
asset_manager.load_image("ship", "assets/images/ship.png")

# Load sound
asset_manager.load_sound("laser", "assets/sounds/laser.wav")

# Load animation from folder
asset_manager.load_animation("explosion", "assets/animations/explosion/")

# Load all assets automatically
asset_manager.load_all_assets()
```

### Asset Folder Structure
```
assets/
├── images/          # Images (.png, .jpg, .gif, .bmp)
├── sounds/          # Sounds (.wav, .mp3, .ogg)
├── animations/      # Animations (folders with frames)
│   ├── explosion/
│   ├── spinning_coin/
│   └── engine_thrust/
└── fonts/           # Fonts (.ttf, .otf)
```

## 🏗️ Engine Architecture

- `engine/core.py` - Main engine class
- `engine/game_object.py` - Game object system
- `engine/scene.py` - Scene management
- `engine/renderer.py` - Graphics rendering
- `engine/input_system.py` - Input handling
- `engine/physics.py` - Physics simulation
- `engine/asset_manager.py` - Asset loading and management
- `scripting/` - AXScript interpreter

## 🎪 No Editor - Pure Code!

This engine is designed for programmers who want full control over their games through code. No visual editor, no clicking around - just write your game logic and run it!

Perfect for:
- Learning game programming
- Rapid prototyping
- Code-focused development
- Educational projects
- Minimalist game development

## 🚀 Get Started

Run `python test_fixed_engine.py` to see the physics demo, or `python test_assets_demo.py` to see the asset system in action!

Happy coding! 🎮✨