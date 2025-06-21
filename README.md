
# 🎮 Axarion Engine - Code-Only Game Engine

A powerful 2D game engine designed for programmers who prefer writing games in pure code!

## ✨ Features

- **Pure Code Approach**: No GUI editor - write games directly in code
- **AXScript Integration**: Built-in scripting language for game logic
- **Pygame-Based Rendering**: Fast 2D graphics and input handling
- **Physics System**: Built-in physics simulation
- **Audio Support**: Sound effects and background music
- **Particle Effects**: Explosions, fire, smoke and more
- **Animation System**: Smooth object animations
- **Scene Management**: Organize your game into scenes

## 🚀 Quick Start

1. **Run the sample game:**
```bash
python main.py
```

2. **Create your own game:**
Edit the `create_your_game()` function in `main.py` to build your game!

## 🎯 Basic Game Structure

```python
from engine.core import AxarionEngine
from engine.game_object import GameObject

# Create engine
engine = AxarionEngine(800, 600)
engine.initialize()

# Create scene
scene = engine.create_scene("Main")
engine.current_scene = scene

# Create game object
player = GameObject("Player", "rectangle")
player.position = (100, 100)
player.set_property("width", 50)
player.set_property("height", 50)
player.set_property("color", (255, 100, 100))

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
- **diamond**: Diamond-shaped objects
- **video**: Video display objects

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

## 🎨 Creating Game Objects

```python
# Rectangle
obj = GameObject("MyRect", "rectangle")
obj.set_property("width", 100)
obj.set_property("height", 50)
obj.set_property("color", (255, 0, 0))

# Circle
obj = GameObject("MyCircle", "circle")
obj.set_property("radius", 30)
obj.set_property("color", (0, 255, 0))

# Diamond
obj = GameObject("MyDiamond", "diamond")
obj.set_property("size", 40)
obj.set_property("color", (0, 0, 255))
```

## 🎯 Example Games

### Simple Platformer Player
```python
player = GameObject("Player", "rectangle")
player.position = (100, 300)
player.set_property("width", 40)
player.set_property("height", 60)
player.script_code = """
var speed = 300;
var jumpPower = 500;
var gravity = 981;
var velocityY = 0;
var onGround = false;

function update() {
    // Horizontal movement
    if (keyPressed("ArrowLeft")) {
        move(-speed * 0.016, 0);
    }
    if (keyPressed("ArrowRight")) {
        move(speed * 0.016, 0);
    }
    
    // Jumping
    if (keyJustPressed(" ") && onGround) {
        velocityY = -jumpPower;
        onGround = false;
    }
    
    // Apply gravity
    velocityY += gravity * 0.016;
    move(0, velocityY * 0.016);
    
    // Simple ground collision
    var pos = getProperty("position");
    if (pos.y > 500) {
        setProperty("position", {x: pos.x, y: 500});
        velocityY = 0;
        onGround = true;
    }
}
"""
```

### Spinning Enemy
```python
enemy = GameObject("Enemy", "circle")
enemy.position = (400, 200)
enemy.script_code = """
var angle = 0;
var centerX = 400;
var centerY = 200;

function update() {
    angle += 0.05;
    var x = centerX + cos(angle) * 100;
    var y = centerY + sin(angle) * 50;
    setProperty("position", {x: x, y: y});
    
    // Change color
    var red = (sin(angle) + 1) * 127;
    setProperty("color", red + ",100,100");
}
"""
```

## 🏗️ Engine Architecture

- `engine/core.py` - Main engine class
- `engine/game_object.py` - Game object system
- `engine/scene.py` - Scene management
- `engine/renderer.py` - Graphics rendering
- `engine/input_system.py` - Input handling
- `engine/physics.py` - Physics simulation
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

Run `python main.py` to see the sample game, then edit `create_your_game()` to build your masterpiece!

Happy coding! 🎮✨
