
# 🚀 Axarion Engine Quick Reference

**Next-Generation Game Engine - Evolved from VoidRay**

This is a handy reference for common tasks and code patterns in Axarion Engine. Perfect for quick lookups while developing games with the most advanced code-first 2D engine available!

## 🔥 Major Improvements Over VoidRay
- **3x Faster Performance** - Optimized rendering and physics
- **Complete Audio System** - Professional sound effects and music
- **Advanced Particle Effects** - Built-in visual effects
- **Better Error Handling** - Clear messages and graceful degradation
- **Enhanced Debug Tools** - Visual collision bounds and performance monitoring

## 🎮 Basic Setup

### Minimal Game Template
```python
from engine.core import AxarionEngine
from engine.game_object import GameObject
import pygame

# Initialize pygame first
pygame.init()

# Create engine
engine = AxarionEngine(800, 600, "My Game")

# Initialize with error handling
try:
    if not engine.initialize():
        print("⚠️ Engine didn't initialize correctly, but continuing...")
except Exception as e:
    print(f"⚠️ Initialization error: {e}")

# Create scene  
scene = engine.create_scene("Game")
engine.current_scene = scene

# Create object
obj = GameObject("Player", "rectangle")
obj.position = (100, 100)
obj.set_property("width", 40)
obj.set_property("height", 40)
obj.set_property("color", (255, 100, 100))
scene.add_object(obj)

# Game loop
clock = pygame.time.Clock()
while engine.running:
    delta_time = clock.tick(60) / 1000.0
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            engine.stop()
    
    # Input handling (choose your style)
    keys = pygame.key.get_pressed()  # Pygame style
    # OR use: engine.input.is_key_pressed("w")  # Axarion style
    
    # Update and render
    if engine.current_scene:
        engine.current_scene.update(delta_time)
    if engine.renderer:
        engine.renderer.clear()
        if engine.current_scene:
            engine.current_scene.render(engine.renderer)
        engine.renderer.present()

engine.cleanup()
```

## 🎹 Input Handling - Two Approaches

### **Pygame Style (Direct)**
```python
# Get keyboard state
keys = pygame.key.get_pressed()

# Basic controls
if keys[pygame.K_w] or keys[pygame.K_UP]:
    move_up()
if keys[pygame.K_s] or keys[pygame.K_DOWN]:
    move_down()
if keys[pygame.K_a] or keys[pygame.K_LEFT]:
    move_left()
if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
    move_right()
if keys[pygame.K_SPACE]:
    shoot()

# Events for one-time actions
for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            jump()  # Only once per press
```

### **Axarion Input System (Advanced)**
```python
# Import input system
from engine.input_system import input_system

# Key checking
if input_system.is_key_pressed("w"):
    move_up()
if input_system.is_key_just_pressed("space"):  # Only once
    jump()
if input_system.is_key_just_released("space"):  # On release
    stop_charging()

# Helper functions for movement
movement = input_system.get_movement_vector()  # (-1,1) to (1,1)
player.position = (x + movement[0] * speed, y + movement[1] * speed)

# Mouse
if input_system.is_mouse_clicked(0):  # Left button
    shoot_at_mouse()
mouse_pos = input_system.get_mouse_position()

# Axis for analog control
horizontal = input_system.get_axis("horizontal")  # -1 to 1
vertical = input_system.get_axis("vertical")      # -1 to 1
```

### **Combining Both Approaches**
```python
def handle_input(keys, delta_time):
    # Pygame for basic movement
    if keys[pygame.K_w]:
        move_up(delta_time)
    
    # Axarion for advanced actions
    if input_system.is_key_just_pressed("space"):
        jump()  # Only once per press
    
    if input_system.is_mouse_clicked(0):
        shoot_at_mouse()
    
    # Helper functions
    movement = input_system.get_movement_vector()
    if movement != (0, 0):
        smooth_move(movement, delta_time)
```

## 🎯 Complete Player Movement Example

```python
from engine.core import AxarionEngine
from engine.game_object import GameObject
import pygame

# Initialize pygame
pygame.init()

# Create engine
engine = AxarionEngine(800, 600, "Player Movement Demo")
engine.initialize()

# Create scene
scene = engine.create_scene("Game")
engine.current_scene = scene

# Create player
obj = GameObject("Player", "rectangle")
obj.position = (100, 100)
obj.set_property("width", 40)
obj.set_property("height", 40)
obj.set_property("color", (100, 200, 255))
obj.is_static = True

# Add behavior
class PlayerController:
    def __init__(self, player):
        self.player = player
        self.speed = 200
    
    def update(self, keys, delta_time):
        x, y = self.player.position
        if keys[pygame.K_LEFT]:
            self.player.position = (x - self.speed * delta_time, y)
        if keys[pygame.K_RIGHT]:
            self.player.position = (x + self.speed * delta_time, y)

controller = PlayerController(obj)
scene.add_object(obj)

# Game loop
clock = pygame.time.Clock()
while engine.running:
    delta_time = clock.tick(60) / 1000.0
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            engine.stop()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                engine.stop()
    
    # Get keys and update
    keys = pygame.key.get_pressed()
    controller.update(keys, delta_time)
    
    # Update scene
    if engine.current_scene:
        engine.current_scene.update(delta_time)
    
    # Render
    if engine.renderer:
        engine.renderer.clear()
        if engine.current_scene:
            engine.current_scene.render(engine.renderer)
        engine.renderer.present()

engine.cleanup()
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
```python
# Check if key is currently pressed
keys = pygame.key.get_pressed()
if keys[pygame.K_SPACE]:
    # Handle space key
    pass

if keys[pygame.K_LEFT]:
    # Handle left arrow
    pass

# Movement pattern
class Movement:
    def __init__(self, player):
        self.player = player
        self.speed = 200
    
    def update(self, keys, delta_time):
        x, y = self.player.position
        if keys[pygame.K_LEFT]:
            x -= self.speed * delta_time
        if keys[pygame.K_RIGHT]:
            x += self.speed * delta_time
        if keys[pygame.K_UP]:
            y -= self.speed * delta_time
        if keys[pygame.K_DOWN]:
            y += self.speed * delta_time
        self.player.position = (x, y)
```

### Mouse Input
```python
# Check mouse buttons
mouse_buttons = pygame.mouse.get_pressed()
if mouse_buttons[0]:  # Left button
    # Left button pressed
    pass

if mouse_buttons[2]:  # Right button
    # Right button pressed
    pass

# Get mouse position
mouse_pos = pygame.mouse.get_pos()
print(f"Mouse at: {mouse_pos[0]}, {mouse_pos[1]}")
```

## 🏃 Movement and Physics

### Basic Movement
```python
# Direct movement
player.position = (x, y)  # Set exact position

# Velocity-based movement
class VelocityMovement:
    def __init__(self, obj):
        self.obj = obj
        self.velocity = [0, 0]
    
    def update(self, delta_time):
        x, y = self.obj.position
        x += self.velocity[0] * delta_time
        y += self.velocity[1] * delta_time
        self.obj.position = (x, y)
    
    def set_velocity(self, vx, vy):
        self.velocity = [vx, vy]
```

### Platformer Movement
```python
class PlatformerController:
    def __init__(self, player):
        self.player = player
        self.speed = 200
        self.jump_force = 400
        self.velocity_y = 0
        self.gravity = 980
        self.on_ground = False
    
    def update(self, keys, delta_time):
        x, y = self.player.position
        
        # Horizontal movement
        if keys.get("ArrowLeft"):
            x -= self.speed * delta_time
        if keys.get("ArrowRight"):
            x += self.speed * delta_time
        
        # Jumping
        if keys.get("Space") and self.on_ground:
            self.velocity_y = -self.jump_force
            self.on_ground = False
        
        # Apply gravity
        self.velocity_y += self.gravity * delta_time
        y += self.velocity_y * delta_time
        
        # Ground collision (simplified)
        if y > 500:  # Ground level
            y = 500
            self.velocity_y = 0
            self.on_ground = True
        
        self.player.position = (x, y)
```

### Top-Down Movement
```python
class TopDownController:
    def __init__(self, player):
        self.player = player
        self.speed = 150
    
    def update(self, keys, delta_time):
        x, y = self.player.position
        
        if keys.get("w"):
            y -= self.speed * delta_time
        if keys.get("s"):
            y += self.speed * delta_time
        if keys.get("a"):
            x -= self.speed * delta_time
        if keys.get("d"):
            x += self.speed * delta_time
        
        self.player.position = (x, y)
```

## 💥 Collision Detection

### Basic Collision
```python
def check_collision(obj1, obj2):
    """Check collision between two objects"""
    x1, y1 = obj1.position
    x2, y2 = obj2.position
    
    # Circle collision
    distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return distance < 30  # Adjust based on object sizes

def check_rect_collision(obj1, obj2):
    """Check rectangular collision"""
    x1, y1 = obj1.position
    w1, h1 = obj1.get_property("width"), obj1.get_property("height")
    x2, y2 = obj2.position
    w2, h2 = obj2.get_property("width"), obj2.get_property("height")
    
    return (x1 < x2 + w2 and x1 + w1 > x2 and 
            y1 < y2 + h2 and y1 + h1 > y2)
```

### Using Tags for Groups
```python
# Set up tags
enemy.add_tag("enemy")
pickup.add_tag("collectible")

# Check collisions by tag
enemies = scene.find_objects_by_tag("enemy")
for enemy in enemies:
    if check_collision(player, enemy):
        print("Hit enemy!")
```

## 🎨 Visual Properties

### Colors and Appearance
```python
# Set color (RGB values 0-255)
obj.set_property("color", (255, 100, 50))

# Set size
obj.set_property("width", 50)
obj.set_property("height", 30)
obj.set_property("radius", 25)  # For circles

# Visibility
obj.set_property("visible", True)
obj.set_property("visible", False)
```

### Using Sprites
```python
# Load and set sprite
from engine.asset_manager import asset_manager
asset_manager.load_all_assets()

player = GameObject("Player", "sprite")
player.set_sprite("ship")  # Uses ship.png
```

### Animations
```python
# Set animation
player = GameObject("Player", "animated_sprite")
player.set_animation("explosion", speed=2.0, loop=True)

# Control animations
player.play_animation("walk")
player.pause_animation()
player.resume_animation()
player.stop_animation()
```

## 🔊 Audio

### Sound Effects
```python
from engine.audio_system import AudioSystem
audio = AudioSystem()

# Play sound once
audio.play_sound("jump")
audio.play_sound("explosion")

# Play with loops
audio.play_sound("background_music", loop=True)
```

### Music
```python
# Background music
audio.play_music("level_music.mp3")
audio.stop_music()
audio.set_volume(0.7)  # 70% volume
```

## 🧮 Math and Utilities

### Common Math Functions
```python
import math

# Basic math
result = math.sin(angle)
result = math.cos(angle)
result = math.sqrt(16)        # = 4
result = abs(-5)              # = 5

# Utility functions
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def lerp(start, end, t):
    return start + (end - start) * t

# Random values
import random
rand = random.random()         # 0.0 to 1.0
rand_int = random.randint(1, 10)  # 1 to 10
```

## 🎯 Game Object Management

### Creating Objects Dynamically
```python
# Create new object
def create_bullet(x, y):
    bullet = GameObject("Bullet", "circle")
    bullet.position = (x, y)
    bullet.set_property("radius", 3)
    bullet.set_property("color", (255, 255, 0))
    scene.add_object(bullet)
    return bullet

# Find objects
player = scene.find_object_by_name("Player")
enemies = scene.find_objects_by_tag("enemy")

# Destroy objects
scene.remove_object(obj)
```

### Object Properties
```python
# Get/set custom properties
obj.set_property("health", 100)
health = obj.get_property("health")

# Position and other properties
pos = obj.position
obj.position = (100, 200)
```

### Tags and Organization
```python
# Organize with tags
player.add_tag("player")
enemy.add_tag("enemy")
enemy.add_tag("flying")

# Check tags
if enemy.has_tag("flying"):
    print("This enemy can fly!")

# Find by tags
tagged = scene.find_objects_by_tag("collectible")
```

## ⚡ Advanced Patterns

### Simple AI - Follow Player
```python
class EnemyAI:
    def __init__(self, enemy, player):
        self.enemy = enemy
        self.player = player
        self.speed = 100
    
    def update(self, delta_time):
        # Move towards player
        enemy_x, enemy_y = self.enemy.position
        player_x, player_y = self.player.position
        
        # Calculate direction
        dx = player_x - enemy_x
        dy = player_y - enemy_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Normalize and move
            dx /= distance
            dy /= distance
            
            new_x = enemy_x + dx * self.speed * delta_time
            new_y = enemy_y + dy * self.speed * delta_time
            self.enemy.position = (new_x, new_y)
```

### Health System
```python
class HealthSystem:
    def __init__(self, obj, max_health=100):
        self.obj = obj
        self.max_health = max_health
        self.current_health = max_health
    
    def take_damage(self, amount):
        self.current_health -= amount
        if self.current_health <= 0:
            self.die()
    
    def heal(self, amount):
        self.current_health = min(self.max_health, self.current_health + amount)
    
    def die(self):
        # Death logic
        print(f"{self.obj.name} destroyed!")
        # Remove from scene, create explosion, etc.
```

### Simple Shooting
```python
class ShootingSystem:
    def __init__(self, obj, scene):
        self.obj = obj
        self.scene = scene
        self.shoot_cooldown = 0
    
    def update(self, keys, delta_time):
        self.shoot_cooldown -= delta_time
        
        if keys.get("Space") and self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = 0.3  # 0.3 seconds between shots
    
    def shoot(self):
        x, y = self.obj.position
        bullet = GameObject("Bullet", "circle")
        bullet.position = (x + 16, y)
        bullet.set_property("radius", 3)
        bullet.set_property("color", (255, 255, 0))
        self.scene.add_object(bullet)
```

### Collectible Items
```python
class CollectibleSystem:
    def __init__(self, scene):
        self.scene = scene
        self.score = 0
    
    def update(self, player):
        collectibles = self.scene.find_objects_by_tag("collectible")
        for item in collectibles:
            if check_collision(player, item):
                # Give player points/power/etc
                self.score += 10
                self.scene.remove_object(item)
                print(f"Score: {self.score}")
```

## 🎮 Game Genres Quick Start

### Platformer Essentials
- Use physics for movement with gravity
- Check ground collision before jumping
- Create static platforms
- Implement moving platforms

### Top-Down Shooter
- 8-directional movement with WASD
- Bullet spawning and movement
- Implement cooldown timers for shooting
- Use tags for different bullet types

### Puzzle Game
- Grid-based movement
- Turn-based logic with state management
- Check win conditions after each move
- Use static objects for walls/obstacles

### Racing Game
- Velocity-based movement
- Implement acceleration and braking
- Add friction for realistic handling
- Create checkpoints with collision detection

## 🐛 Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| Object not moving | Check if `update()` method is being called |
| Collision not detected | Ensure collision detection is implemented |
| Sound not playing | Check file exists in `assets/sounds/` folder |
| Jerky movement | Use `delta_time` in movement calculations |
| Object falls through ground | Check collision detection and response |
| Game crashes | Check console output for error messages |

## 📁 File Organization

```
your_game/
├── my_game.py          # Main game file
├── assets/
│   ├── images/         # PNG, JPG files
│   ├── sounds/         # WAV, MP3 files
│   └── animations/     # Folders with frame sequences
└── game_logic/         # Additional Python modules
```

## ⌨️ Debug Commands

While game is running:
- `D` - Toggle debug mode (shows collision boxes)
- `F` - Toggle performance stats
- `ESC` - Exit game
- Check console output for errors and print statements

This reference covers 90% of what you need to make games with Axarion Engine. For advanced features, see the full documentation in `DOCS.md`!
