
# 🚀 Axarion Engine Quick Reference

This is a handy reference for common tasks and code patterns. Perfect for quick lookups while developing!

## 🎮 Basic Setup

### Minimal Game Template
```python
from engine.core import AxarionEngine
from engine.game_object import GameObject

# Create engine
engine = AxarionEngine(800, 600)
engine.initialize()

# Create scene  
scene = engine.create_scene("Game")
engine.current_scene = scene

# Create object
obj = GameObject("Player", "rectangle")
obj.position = (100, 100)
obj.set_property("color", (255, 100, 100))

# Add script
obj.script_code = """
function update() {
    // Your game logic here
}
"""

scene.add_object(obj)
engine.run()
```

## 🎯 GameObject Types

| Type | Description | Properties |
|------|-------------|------------|
| `"rectangle"` | Colored rectangle | `width`, `height`, `color` |
| `"circle"` | Colored circle | `radius`, `color` |
| `"sprite"` | Image/texture | Uses image files |
| `"animated_sprite"` | Animated frames | Uses animation folders |

## 🕹️ Input Controls

### Keyboard Input
```javascript
// Check if key is currently pressed
if (keyPressed("Space")) { /* ... */ }
if (keyPressed("ArrowLeft")) { /* ... */ }
if (keyPressed("w")) { /* ... */ }

// Check if key was just pressed this frame
if (keyJustPressed("Enter")) { /* ... */ }

// Movement pattern
var speed = 200;
if (keyPressed("ArrowLeft")) move(-speed * 0.016, 0);
if (keyPressed("ArrowRight")) move(speed * 0.016, 0);
if (keyPressed("ArrowUp")) move(0, -speed * 0.016);
if (keyPressed("ArrowDown")) move(0, speed * 0.016);
```

### Mouse Input
```javascript
// Check mouse buttons
if (mousePressed(0)) { /* left button */ }
if (mousePressed(1)) { /* right button */ }
if (mouseClicked(0)) { /* just clicked */ }

// Get mouse position
var mouse = getMousePos();
print("Mouse at: " + mouse.x + ", " + mouse.y);
```

## 🏃 Movement and Physics

### Basic Movement
```javascript
// Direct movement
move(x, y);                    // Move by offset
setProperty("position", {x: 100, y: 200});  // Set exact position

// Velocity-based
setProperty("velocity", {x: 100, y: 0});     // Set velocity
applyForce(200, 0);            // Apply force (physics)
```

### Platformer Movement
```javascript
var speed = 200;
var jumpForce = 400;

function update() {
    // Horizontal movement
    if (keyPressed("ArrowLeft")) {
        applyForce(-speed * 2, 0);
    }
    if (keyPressed("ArrowRight")) {
        applyForce(speed * 2, 0);
    }
    
    // Jumping
    if (keyPressed("Space") && isOnGround()) {
        var vel = getProperty("velocity");
        setProperty("velocity", {x: vel.x, y: -jumpForce});
    }
}
```

### Top-Down Movement
```javascript
var speed = 150;

function update() {
    var dx = 0, dy = 0;
    
    if (keyPressed("w")) dy = -1;
    if (keyPressed("s")) dy = 1;
    if (keyPressed("a")) dx = -1;
    if (keyPressed("d")) dx = 1;
    
    move(dx * speed * 0.016, dy * speed * 0.016);
}
```

## 💥 Collision Detection

### Basic Collision
```javascript
// Check collision with specific object
if (isCollidingWith("Enemy")) {
    print("Hit enemy!");
}

// Get all colliding objects
var colliding = getCollidingObjects();
for (var i = 0; i < colliding.length; i++) {
    print("Colliding with: " + colliding[i]);
}
```

### Using Tags for Groups
```python
# Python - set up tags
enemy.add_tag("enemy")
pickup.add_tag("collectible")
```

```javascript
// AXScript - check collisions by tag
var enemies = findObjectsByTag("enemy");
for (var i = 0; i < enemies.length; i++) {
    if (isCollidingWith(enemies[i].name)) {
        print("Hit enemy!");
    }
}
```

## 🎨 Visual Properties

### Colors and Appearance
```javascript
// Set color (RGB values 0-255)
setProperty("color", {r: 255, g: 100, b: 50});

// Set size
setProperty("width", 50);
setProperty("height", 30);
setProperty("radius", 25);  // For circles

// Visibility
setProperty("visible", true);
setProperty("visible", false);
```

### Using Sprites
```python
# Python - load and set sprite
from engine.asset_manager import asset_manager
asset_manager.load_all_assets()

player = GameObject("Player", "sprite")
player.set_sprite("ship")  # Uses ship.png
```

### Animations
```python
# Python - set animation
player = GameObject("Player", "animated_sprite")
player.set_animation("explosion", speed=2.0, loop=True)
```

```javascript
// AXScript - control animations
playAnimation("walk");
pauseAnimation();
resumeAnimation();
stopAnimation();
```

## 🔊 Audio

### Sound Effects
```javascript
// Play sound once
playSound("jump");
playSound("explosion");

// Play with loops (-1 = infinite)
playSound("background_music", -1);
```

### Music
```javascript
// Background music
playMusic("level_music.mp3");
stopMusic();
setVolume(0.7, 0.5);  // music, sound effects
```

## 🧮 Math and Utilities

### Common Math Functions
```javascript
// Basic math
var result = sin(angle);
var result = cos(angle);
var result = sqrt(16);        // = 4
var result = abs(-5);         // = 5

// Utility functions
var dist = distance(x1, y1, x2, y2);
var clamped = clamp(value, 0, 100);
var mixed = lerp(start, end, 0.5);  // 50% between start and end
var rand = random();           // 0.0 to 1.0

// Rounding
var down = floor(3.7);        // = 3
var up = ceil(3.2);           // = 4
var nearest = round(3.6);     // = 4
```

### Random Values
```javascript
// Random float 0-1
var rand = random();

// Random integer range
var randInt = floor(random() * 10);  // 0-9
var randRange = floor(random() * 5) + 10;  // 10-14
```

## 🎯 Game Object Management

### Creating Objects Dynamically
```javascript
// Create new object from script
var bulletId = instantiate("circle", x, y);

// Find objects
var player = findObjectByName("Player");
var enemies = findObjectsByTag("enemy");

// Destroy objects
destroy();  // Destroy current object
```

### Object Properties
```javascript
// Get/set custom properties
setProperty("health", 100);
var health = getProperty("health");

// Position and velocity
var pos = getProperty("position");
var vel = getProperty("velocity");
setProperty("position", {x: 100, y: 200});
```

### Tags and Organization
```python
# Python - organize with tags
player.add_tag("player")
enemy.add_tag("enemy")
enemy.add_tag("flying")

# Check tags
if enemy.has_tag("flying"):
    print("This enemy can fly!")
```

```javascript
// AXScript - work with tags
addTag("powerup");
var hasTag = hasTag("enemy");
var tagged = findObjectsByTag("collectible");
```

## ⚡ Advanced Patterns

### Simple AI - Follow Player
```javascript
function update() {
    var player = findObjectByName("Player");
    if (player) {
        var playerPos = player.getProperty("position");
        var myPos = getProperty("position");
        
        // Move towards player
        moveTowards(playerPos.x, playerPos.y, 100);
    }
}
```

### Health System
```javascript
var maxHealth = 100;
var currentHealth = maxHealth;

function takeDamage(amount) {
    currentHealth -= amount;
    if (currentHealth <= 0) {
        die();
    }
}

function die() {
    // Death logic
    createExplosion(pos.x, pos.y);
    destroy();
}
```

### Simple Shooting
```javascript
var shootCooldown = 0;

function update() {
    shootCooldown -= 0.016;  // Decrease by delta time
    
    if (keyPressed("Space") && shootCooldown <= 0) {
        shoot();
        shootCooldown = 0.3;  // 0.3 seconds between shots
    }
}

function shoot() {
    var pos = getProperty("position");
    var bulletId = instantiate("circle", pos.x + 16, pos.y);
    // Set bullet properties via engine
}
```

### Collectible Items
```javascript
// For collectible objects
function update() {
    if (isCollidingWith("Player")) {
        // Give player points/power/etc
        playSound("pickup");
        destroy();
    }
}
```

## 🎮 Game Genres Quick Start

### Platformer Essentials
- Use `applyForce()` for movement
- Check `isOnGround()` before jumping
- Set gravity: `scene.set_gravity(0, 400)`
- Create static platforms with `is_static = True`

### Top-Down Shooter
- 8-directional movement with WASD
- Use `createBullet(targetX, targetY)` for projectiles
- Implement cooldown timers for shooting
- Use tags for different bullet types

### Puzzle Game
- Use `snapToGrid()` for grid-based movement
- Implement turn-based logic with flags
- Check win conditions after each move
- Use static objects for walls/obstacles

### Racing Game
- Use `applyForce()` for acceleration
- Implement `setBrake()` for stopping
- Add friction for realistic handling
- Create checkpoints with collision detection

## 🐛 Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| Object not moving | Check if `update()` function exists and script is attached |
| Collision not detected | Ensure both objects have `collision_enabled = True` |
| Sound not playing | Check file exists in `assets/sounds/` folder |
| Jerky movement | Use `* 0.016` for delta-time in movement |
| Object falls through ground | Check platform has `is_static = True` |
| Script errors | Check console output for error messages |

## 📁 File Organization

```
your_game/
├── my_game.py          # Main game file
├── assets/
│   ├── images/         # PNG, JPG files
│   ├── sounds/         # WAV, MP3 files
│   └── animations/     # Folders with frame sequences
└── scripts/            # Additional AXScript files
```

## ⌨️ Debug Commands

While game is running:
- `D` - Toggle debug mode (shows collision boxes)
- `F` - Toggle performance stats
- `ESC` - Exit game
- Check console output for script errors and print statements

This reference covers 90% of what you need to make games with Axarion Engine. For advanced features, see the full documentation in `DOCS.md`!
