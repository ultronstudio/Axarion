# 🎮 Axarion Engine - Code-Only Game Engine

A powerful 2D game engine designed for programmers who prefer writing games in pure code! Perfect for beginners learning game development and experienced programmers who want full control.

## ✨ Features

- **Pure Code Approach**: No GUI editor - write games directly in code
- **Beginner Friendly**: Comprehensive tutorials and documentation
- **AXScript Integration**: Simple scripting language for game logic
- **Asset Management**: Complete system for images, sounds, and animations
- **Physics System**: Built-in 2D physics simulation with collision detection
- **Audio Support**: Sound effects and background music
- **Particle Effects**: Explosions, fire, smoke and more
- **Animation System**: Smooth object animations and sprite support
- **Scene Management**: Organize your game into scenes

## 🚀 Quick Start (New to Game Development?)

### 1. **See it in action (30 seconds)**
```bash
python test_fixed_engine.py
```
A physics demo with a controllable character, bouncing balls, and platforms!

### 2. **Your first game (5 minutes)**
Create `my_game.py`:
```python
from engine.core import AxarionEngine
from engine.game_object import GameObject

engine = AxarionEngine(800, 600)
engine.initialize()

scene = engine.create_scene("My Game")
engine.current_scene = scene

player = GameObject("Player", "rectangle")
player.position = (100, 100)
player.set_property("color", (100, 200, 255))

player.script_code = """
var speed = 200;
function update() {
    if (keyPressed("ArrowLeft")) move(-speed * 0.016, 0);
    if (keyPressed("ArrowRight")) move(speed * 0.016, 0);
    if (keyPressed("ArrowUp")) move(0, -speed * 0.016);
    if (keyPressed("ArrowDown")) move(0, speed * 0.016);
}
"""

scene.add_object(player)
engine.run()
```

Run it: `python my_game.py` - You now have a controllable character! 🎉

### 3. **Complete tutorials**
- **Absolute Beginners**: Read `GETTING_STARTED.md`
- **Build a Complete Game**: Follow `TUTORIAL_COMPLETE_GAME.md`
- **Quick Reference**: Use `QUICK_REFERENCE.md` for common patterns

## 📚 Learning Path

### 🎯 Complete Beginners (Never coded before?)
1. **Start here**: `GETTING_STARTED.md` - Learn the basics step by step
2. **Follow tutorial**: `TUTORIAL_COMPLETE_GAME.md` - Build a space shooter
3. **Reference guide**: `QUICK_REFERENCE.md` - Common patterns and solutions

### 🎮 Game Developers (Know programming?)
1. **Try the demos**: `python test_fixed_engine.py` and `python test_assets_demo.py`
2. **Read**: `DOCS.md` for complete API reference
3. **Explore**: `examples/` folder for different game genres

### 🚀 Quick Template

```python
from engine.core import AxarionEngine
from engine.game_object import GameObject

# Create engine
engine = AxarionEngine(800, 600)
engine.initialize()

# Create scene
scene = engine.create_scene("Game")
engine.current_scene = scene

# Create game object
player = GameObject("Player", "rectangle")
player.position = (100, 100)
player.set_property("color", (100, 200, 255))

# Add game logic with AXScript
player.script_code = """
var speed = 200;

function update() {
    if (keyPressed("ArrowLeft")) move(-speed * 0.016, 0);
    if (keyPressed("ArrowRight")) move(speed * 0.016, 0);
    if (keyPressed("ArrowUp")) move(0, -speed * 0.016);
    if (keyPressed("ArrowDown")) move(0, speed * 0.016);
}
"""

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

## 🎯 Why Choose Axarion Engine?

### Perfect for Learning
- **No complex setup** - Works immediately 
- **Clear error messages** - Understand what went wrong
- **Progressive complexity** - Start simple, add features gradually
- **Real code** - Learn actual programming, not just visual scripting

### Great for Rapid Prototyping  
- **Fast iteration** - Change code and see results instantly
- **No asset pipeline** - Drop images in folder and use them
- **Pure code workflow** - Version control friendly
- **Deploy anywhere** - Python runs everywhere

## 🎮 Game Examples You Can Build

- **Platformer**: Mario-style jumping and running
- **Space Shooter**: Top-down action with enemies and bullets  
- **Puzzle Game**: Tetris or match-3 style logic games
- **RPG**: Character stats, inventory, and dialogue systems
- **Racing Game**: Physics-based driving simulation

## 🆘 Need Help?

- **Start here**: `GETTING_STARTED.md` - Complete beginner guide
- **Common issues**: `QUICK_REFERENCE.md` - Solutions to frequent problems  
- **Advanced features**: `DOCS.md` - Full engine documentation
- **Working examples**: `examples/` folder - Study complete games

## 🚀 Ready to Start?

1. **Absolute beginner?** → Read `GETTING_STARTED.md`
2. **Want to see it work?** → Run `python test_fixed_engine.py`
3. **Learn by building?** → Follow `TUTORIAL_COMPLETE_GAME.md`

Happy coding! 🎮✨