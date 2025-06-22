
# 🚀 Getting Started with Axarion Engine

Welcome to Axarion Engine! This guide will help you create your first game in just a few minutes, even if you're completely new to programming or game development.

## 🎯 What is Axarion Engine?

Axarion Engine is a **code-first 2D game engine** that lets you create games by writing simple scripts instead of clicking through complex visual editors. It's perfect for:

- **Beginners** learning game programming
- **Programmers** who prefer code over visual tools
- **Educators** teaching game development concepts
- **Rapid prototyping** of game ideas

## ⚡ Quick Start (5 Minutes to Your First Game!)

### Step 1: Run Your First Demo

Let's see the engine in action! Click the **Run** button or type:

```bash
python test_fixed_engine.py
```

You'll see a physics demo with:
- A blue player character you can control
- Bouncing balls with realistic physics
- Platforms to jump on
- Smooth collision detection

**Controls:**
- `WASD` or `Arrow Keys` - Move the player
- `Space` - Jump
- `D` - Toggle debug mode
- `ESC` - Exit

### Step 2: Try the Assets Demo

See sprites and animations in action:

```bash
python test_assets_demo.py
```

This shows how to use images, animations, and visual effects in your games.

### Step 3: Create Your First Game

Now let's make your own game! Create a new file called `my_first_game.py`:

```python
from engine.core import AxarionEngine
from engine.game_object import GameObject

# Create the game engine
engine = AxarionEngine(800, 600)
engine.initialize()

# Create a scene
scene = engine.create_scene("My First Game")
engine.current_scene = scene

# Create a player character
player = GameObject("Player", "rectangle")
player.position = (100, 100)
player.set_property("width", 40)
player.set_property("height", 40)
player.set_property("color", (100, 200, 255))

# Add simple movement with AXScript
player.script_code = """
var speed = 200;

function update() {
    // Move with arrow keys
    if (keyPressed("ArrowLeft")) {
        move(-speed * 0.016, 0);
    }
    if (keyPressed("ArrowRight")) {
        move(speed * 0.016, 0);
    }
    if (keyPressed("ArrowUp")) {
        move(0, -speed * 0.016);
    }
    if (keyPressed("ArrowDown")) {
        move(0, speed * 0.016);
    }
}
"""

# Add player to scene
scene.add_object(player)

# Run the game!
engine.run()
```

Save and run it:
```bash
python my_first_game.py
```

Congratulations! You just created your first game with a controllable character! 🎉

## 🎮 Understanding the Basics

### Game Objects

Everything in your game is a **GameObject**. Think of them as LEGO blocks you can combine:

```python
# Create different types of objects
player = GameObject("Player", "rectangle")    # Rectangle shape
enemy = GameObject("Enemy", "circle")         # Circle shape
background = GameObject("BG", "sprite")       # Image/sprite
```

### AXScript - Your Game Logic

AXScript is our simple scripting language that makes objects interactive:

```javascript
// This goes in your object's script_code
var speed = 150;

function update() {
    // This runs every frame
    if (keyPressed("Space")) {
        print("Jump!");
    }
}
```

**Common AXScript functions:**
- `move(x, y)` - Move the object
- `keyPressed("key")` - Check if key is pressed
- `setProperty("name", value)` - Change object properties
- `print("text")` - Show messages in console

### Scenes

Scenes are like levels or rooms in your game:

```python
# Create different scenes
menu_scene = engine.create_scene("Main Menu")
game_scene = engine.create_scene("Level 1")
boss_scene = engine.create_scene("Boss Fight")

# Switch between scenes
engine.current_scene = game_scene
```

## 🎯 Your First Real Game - Collect the Coins!

Let's make a simple but complete game where you collect coins:

```python
from engine.core import AxarionEngine
from engine.game_object import GameObject
import random

# Setup
engine = AxarionEngine(800, 600)
engine.initialize()
scene = engine.create_scene("Coin Collector")
engine.current_scene = scene

# Create player
player = GameObject("Player", "rectangle")
player.position = (50, 50)
player.set_property("width", 30)
player.set_property("height", 30)
player.set_property("color", (100, 200, 100))
player.add_tag("player")

player.script_code = """
var speed = 200;
var score = 0;

function update() {
    // Movement
    if (keyPressed("ArrowLeft")) move(-speed * 0.016, 0);
    if (keyPressed("ArrowRight")) move(speed * 0.016, 0);
    if (keyPressed("ArrowUp")) move(0, -speed * 0.016);
    if (keyPressed("ArrowDown")) move(0, speed * 0.016);
    
    // Check coin collection
    var coins = findObjectsByTag("coin");
    for (var i = 0; i < coins.length; i++) {
        if (isCollidingWith(coins[i].name)) {
            // Collect coin!
            score += 10;
            print("Score: " + score);
            // Coin will be destroyed automatically
        }
    }
}
"""

scene.add_object(player)

# Create coins randomly
for i in range(10):
    coin = GameObject(f"Coin_{i}", "circle")
    coin.position = (random.randint(100, 700), random.randint(100, 500))
    coin.set_property("radius", 15)
    coin.set_property("color", (255, 255, 0))
    coin.add_tag("coin")
    
    # Make coin disappear when collected
    coin.script_code = """
    function update() {
        if (isCollidingWith("Player")) {
            destroy();
        }
    }
    """
    
    scene.add_object(coin)

# Run the game
engine.run()
```

## 🎨 Making It Look Better

### Using Sprites (Images)

Replace colored rectangles with actual images:

```python
# First, create sample assets
from assets.create_sample_assets import create_sample_assets
create_sample_assets()

# Load assets
from engine.asset_manager import asset_manager
asset_manager.load_all_assets()

# Use sprite instead of rectangle
player = GameObject("Player", "sprite")
player.set_sprite("ship")  # Uses ship.png from assets
```

### Adding Sound Effects

```python
# In your AXScript
function update() {
    if (keyPressed("Space")) {
        playSound("jump");  # Plays jump.wav
    }
}
```

### Simple Animations

```python
# Create animated object
explosion = GameObject("Boom", "animated_sprite")
explosion.set_animation("explosion", speed=2.0, loop=False)
```

## 🏗️ Game Architecture Made Simple

### 1. **Engine** = The foundation
- Handles graphics, input, sound
- Manages scenes and objects
- Runs the game loop

### 2. **Scenes** = Levels or screens
- Main menu scene
- Game level scenes  
- Game over scene

### 3. **GameObjects** = Everything you see
- Player, enemies, platforms, pickups
- Each has position, appearance, behavior

### 4. **AXScript** = The behavior
- Makes objects interactive
- Handles movement, collisions, logic

## 🎯 Game Ideas for Beginners

Start with these simple concepts and build up:

### 1. **Moving Square** (5 minutes)
- Rectangle that moves with arrow keys
- Good for learning basic controls

### 2. **Collector Game** (15 minutes)  
- Player collects items for points
- Learn collision detection and scoring

### 3. **Simple Platformer** (30 minutes)
- Player jumps on platforms
- Add gravity and jumping mechanics

### 4. **Top-Down Shooter** (45 minutes)
- Player shoots at targets
- Learn projectiles and enemy AI

### 5. **Puzzle Game** (60 minutes)
- Move objects to solve puzzles
- Learn game state and win conditions

## 🔧 Common Patterns and Recipes

### Player Movement
```javascript
// Basic 4-direction movement
var speed = 200;
if (keyPressed("ArrowLeft")) move(-speed * 0.016, 0);
if (keyPressed("ArrowRight")) move(speed * 0.016, 0);
if (keyPressed("ArrowUp")) move(0, -speed * 0.016);
if (keyPressed("ArrowDown")) move(0, speed * 0.016);
```

### Platformer Jumping
```javascript
var jumpForce = 400;
if (keyPressed("Space") && isOnGround()) {
    var vel = getProperty("velocity");
    setProperty("velocity", {x: vel.x, y: -jumpForce});
}
```

### Simple Enemy AI
```javascript
// Follow player
var player_pos = findObjectByName("Player").position;
var my_pos = getProperty("position");
moveTowards(player_pos.x, player_pos.y, 100);
```

### Collision Detection
```javascript
// Check collision with specific object
if (isCollidingWith("Player")) {
    print("Hit player!");
    takeDamage(10);
}

// Check collision with any object with tag
var enemies = getCollidingObjects();
for (var i = 0; i < enemies.length; i++) {
    if (hasTag(enemies[i], "enemy")) {
        print("Hit enemy!");
    }
}
```

## 🚨 Common Beginner Mistakes

### 1. **Forgetting Delta Time**
```javascript
// ❌ Wrong - frame rate dependent
move(5, 0);

// ✅ Right - smooth movement
move(speed * 0.016, 0);
```

### 2. **Not Using Tags**
```python
# ❌ Hard to manage many objects
enemy1 = GameObject("Enemy1", "circle")
enemy2 = GameObject("Enemy2", "circle")

# ✅ Use tags for groups
enemy1.add_tag("enemy")
enemy2.add_tag("enemy")
# Then: findObjectsByTag("enemy")
```

### 3. **Complex Logic in Scripts**
```javascript
// ❌ Don't put everything in update()
function update() {
    // 100 lines of code...
}

// ✅ Break into smaller functions
function update() {
    handleMovement();
    checkCollisions();
    updateAnimation();
}
```

## 📚 What's Next?

Once you're comfortable with the basics:

1. **Read the full documentation** - `DOCS.md` has advanced features
2. **Study example games** - Look in the `examples/` folder
3. **Experiment with physics** - Try different mass, friction, bounce values
4. **Add visual effects** - Learn particle systems and animations
5. **Create your own assets** - Make custom sprites and sounds

## 🆘 Getting Help

### Built-in Help
- All AXScript functions are documented in `DOCS.md`
- Run demos to see working examples
- Use debug mode (`D` key) to visualize collisions

### Understanding Error Messages
```
Runtime error at line 5: Undefined variable: speeed
```
This means you have a typo in your variable name (should be "speed").

```
move() can only be called in object context
```
This means you're trying to use `move()` outside of an object's script.

### Common Solutions
- **Object not moving?** Check if the script is attached and has `update()` function
- **Collision not working?** Make sure both objects have collision enabled
- **Sound not playing?** Check if the sound file exists in `assets/sounds/`

## 🎉 Congratulations!

You now know enough to start creating games with Axarion Engine! Remember:

- **Start simple** - Build complexity gradually
- **Experiment** - Try changing values to see what happens  
- **Don't be afraid to break things** - That's how you learn!
- **Have fun** - Game development should be enjoyable!

Happy game making! 🎮✨
