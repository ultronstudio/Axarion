# 🎮 Build Your First Complete Game: Space Defender

In this tutorial, you'll create a complete space shooter game from scratch! By the end, you'll have a fully playable game with:

- Player spaceship with smooth controls
- Enemy ships that move and attack
- Projectiles and collision detection
- Score system and game over screen
- Sound effects and visual feedback

**Estimated time:** 45-60 minutes  
**Difficulty:** Beginner

## 🚀 What You'll Learn

- Complete game structure and flow
- Managing multiple object types
- Game states (playing, game over)
- Score and health systems
- Polish and juice effects

## 📋 Prerequisites

- Basic understanding of Python (variables, functions, classes)
- Completed the "Getting Started" guide
- Axarion Engine running on your system

## 🎯 Step 1: Project Setup

Create a new file called `space_defender.py`:

```python
from engine.core import AxarionEngine
from engine.game_object import GameObject
from engine.asset_manager import asset_manager
import random
import pygame
import math

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 250
BULLET_SPEED = 400
ENEMY_SPEED = 100

class SpaceDefender:
    def __init__(self):
        # Initialize engine
        self.engine = AxarionEngine(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.engine.initialize()

        # Create main scene
        self.game_scene = self.engine.create_scene("Space Defender")
        self.engine.current_scene = self.game_scene

        # Game state
        self.score = 0
        self.game_over = False

        # Load assets
        self.setup_assets()

        # Create game objects
        self.create_player()
        self.create_enemies()
        self.create_ui()

    def setup_assets(self):
        """Load or create game assets"""
        # Create sample assets if they don't exist
        from assets.create_sample_assets import create_sample_assets
        create_sample_assets()

        # Load all assets
        asset_manager.load_all_assets()

    def create_player(self):
        """Create the player spaceship"""
        pass  # We'll implement this next

    def create_enemies(self):
        """Create enemy ships"""
        pass  # We'll implement this later

    def create_ui(self):
        """Create UI elements"""
        pass  # We'll implement this later

    def run(self):
        """Start the game"""
        self.engine.run()

# Create and run the game
if __name__ == "__main__":
    game = SpaceDefender()
    game.run()
```

Run this to make sure everything works:
```bash
python space_defender.py
```

You should see an empty black window. Perfect! Now let's add the player.

## 🚀 Step 2: Create the Player Ship

Replace the `create_player` method:

```python
def create_player(self):
    """Create the player spaceship"""
    self.player = GameObject("Player", "sprite")
    self.player.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)

    # Try to use sprite, fallback to colored rectangle
    if not self.player.set_sprite("ship"):
        self.player.object_type = "rectangle"
        self.player.set_property("width", 40)
        self.player.set_property("height", 30)
        self.player.set_property("color", (100, 200, 255))

    # Player properties
    self.player.add_tag("player")
    self.player.set_property("health", 100)
    self.player.set_property("max_health", 100)

    # Create player controller
    self.player_controller = PlayerController(self.player)

    self.game_scene.add_object(self.player)

class PlayerController:
    def __init__(self, player):
        self.player = player
        self.speed = PLAYER_SPEED
        self.shoot_cooldown = 0
        self.health = 100

    def update(self, keys, delta_time):
        # Decrease cooldown
        self.shoot_cooldown -= delta_time

        # Movement
        x, y = self.player.position

        if keys.get("ArrowLeft") or keys.get("a"):
            x -= self.speed * delta_time
        if keys.get("ArrowRight") or keys.get("d"):
            x += self.speed * delta_time
        if keys.get("ArrowUp") or keys.get("w"):
            y -= self.speed * delta_time
        if keys.get("ArrowDown") or keys.get("s"):
            y += self.speed * delta_time

        # Keep player on screen
        x = max(0, min(x, SCREEN_WIDTH - 40))
        y = max(0, min(y, SCREEN_HEIGHT - 30))

        self.player.position = (x, y)

        # Shooting
        if keys.get("Space") and self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = 0.2  # 5 shots per second

    def shoot(self):
        # This will be handled by the main game class
        pass

    def take_damage(self, amount):
        self.health -= amount
        self.player.set_property("health", self.health)

        if self.health <= 0:
            print("Player destroyed!")
```

Update the `run` method to handle the game loop:

```python
def run(self):
    """Start the game"""
    clock = pygame.time.Clock()

    while self.engine.running:
        delta_time = clock.tick(60) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.engine.running = False

        # Get input
        keys = self.engine.get_keys()

        # Update player
        self.player_controller.update(keys, delta_time)

        # Update engine
        self.engine.update(delta_time)
        self.engine.render()

    self.engine.cleanup()
```

Run the game now and you should be able to move your blue rectangle (or ship sprite) around with WASD or arrow keys!

## 💥 Step 3: Add Bullets

Now let's make the shooting work. Add this to your `SpaceDefender` class:

```python
def __init__(self):
    # ... existing code ...

    # Game objects
    self.bullets = []
    self.enemies = []

def create_bullet(self, x, y, velocity_y, tag, color):
    """Create a bullet object"""
    bullet = GameObject(f"Bullet_{random.randint(1000, 9999)}", "circle")
    bullet.position = (x, y)
    bullet.set_property("radius", 3)
    bullet.set_property("color", color)
    bullet.add_tag(tag)

    # Create bullet controller
    bullet_controller = BulletController(bullet, velocity_y)

    self.bullets.append({'object': bullet, 'controller': bullet_controller})
    self.game_scene.add_object(bullet)

    return bullet

class BulletController:
    def __init__(self, bullet, velocity_y):
        self.bullet = bullet
        self.velocity_y = velocity_y
        self.destroyed = False

    def update(self, delta_time):
        if self.destroyed:
            return

        # Move bullet
        x, y = self.bullet.position
        y += self.velocity_y * delta_time
        self.bullet.position = (x, y)

        # Remove if off screen
        if y < -10 or y > SCREEN_HEIGHT + 10:
            self.destroyed = True
```

Update the `PlayerController.shoot` method:

```python
def shoot(self):
    # Signal to create bullet - handled by main game
    self.should_shoot = True
```

And add this to the `PlayerController.__init__`:

```python
def __init__(self, player):
    # ... existing code ...
    self.should_shoot = False
```

Update the main game loop to handle shooting:

```python
def run(self):
    """Start the game"""
    clock = pygame.time.Clock()

    while self.engine.running:
        delta_time = clock.tick(60) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.engine.running = False

        # Get input
        keys = self.engine.get_keys()

        # Update player
        self.player_controller.update(keys, delta_time)

        # Handle player shooting
        if self.player_controller.should_shoot:
            x, y = self.player.position
            self.create_bullet(x + 20, y, -BULLET_SPEED, "player_bullet", (255, 255, 100))
            self.player_controller.should_shoot = False

        # Update bullets
        for bullet_data in self.bullets[:]:
            bullet_data['controller'].update(delta_time)
            if bullet_data['controller'].destroyed:
                self.game_scene.remove_object(bullet_data['object'])
                self.bullets.remove(bullet_data)

        # Update engine
        self.engine.update(delta_time)
        self.engine.render()

    self.engine.cleanup()
```

Test it out! You should now be able to shoot yellow bullets by pressing Space.

## 👾 Step 4: Add Enemies

Now for the fun part - enemies! Add this to your `SpaceDefender` class:

```python
def create_enemies(self):
    """Create enemy ships"""
    self.enemy_spawn_timer = 0
    self.enemies_created = 0

def spawn_enemy(self):
    """Spawn a single enemy"""
    enemy = GameObject(f"Enemy_{self.enemies_created}", "sprite")

    # Try to use enemy sprite, fallback to rectangle
    if not enemy.set_sprite("enemy"):
        enemy.object_type = "rectangle"
        enemy.set_property("width", 35)
        enemy.set_property("height", 25)
        enemy.set_property("color", (255, 100, 100))

    # Random spawn position at top of screen
    enemy.position = (random.randint(50, SCREEN_WIDTH - 50), -30)
    enemy.add_tag("enemy")

    # Create enemy controller
    enemy_controller = EnemyController(enemy)

    self.enemies.append({'object': enemy, 'controller': enemy_controller})
    self.game_scene.add_object(enemy)
    self.enemies_created += 1

class EnemyController:
    def __init__(self, enemy):
        self.enemy = enemy
        self.speed = ENEMY_SPEED
        self.velocity_x = random.randint(-50, 50)
        self.shoot_timer = random.uniform(1, 3)
        self.health = 50
        self.destroyed = False

    def update(self, delta_time):
        if self.destroyed:
            return

        # Move down and slightly side to side
        x, y = self.enemy.position
        x += self.velocity_x * delta_time
        y += self.speed * delta_time

        self.enemy.position = (x, y)

        # Remove if off screen
        if y > SCREEN_HEIGHT + 50:
            self.destroyed = True
            return

        # Shooting
        self.shoot_timer -= delta_time
        if self.shoot_timer <= 0:
            self.should_shoot = True
            self.shoot_timer = random.uniform(2, 4)  # Shoot every 2-4 seconds

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            print("Enemy destroyed!")
            self.destroyed = True
```

Update the game loop to spawn and update enemies:

```python
def run(self):
    """Start the game"""
    clock = pygame.time.Clock()

    while self.engine.running:
        delta_time = clock.tick(60) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.engine.running = False

        # Get input
        keys = self.engine.get_keys()

        # Update player
        self.player_controller.update(keys, delta_time)

        # Handle player shooting
        if self.player_controller.should_shoot:
            x, y = self.player.position
            self.create_bullet(x + 20, y, -BULLET_SPEED, "player_bullet", (255, 255, 100))
            self.player_controller.should_shoot = False

        # Spawn enemies
        self.enemy_spawn_timer += delta_time
        if self.enemy_spawn_timer > 2:  # Spawn every 2 seconds
            self.spawn_enemy()
            self.enemy_spawn_timer = 0

        # Update enemies
        for enemy_data in self.enemies[:]:
            enemy_data['controller'].update(delta_time)

            # Handle enemy shooting
            if hasattr(enemy_data['controller'], 'should_shoot') and enemy_data['controller'].should_shoot:
                x, y = enemy_data['object'].position
                self.create_bullet(x + 17, y + 25, 200, "enemy_bullet", (255, 100, 100))
                enemy_data['controller'].should_shoot = False

            # Remove destroyed enemies
            if enemy_data['controller'].destroyed:
                self.game_scene.remove_object(enemy_data['object'])
                self.enemies.remove(enemy_data)

        # Update bullets
        for bullet_data in self.bullets[:]:
            bullet_data['controller'].update(delta_time)
            if bullet_data['controller'].destroyed:
                self.game_scene.remove_object(bullet_data['object'])
                self.bullets.remove(bullet_data)

        # Update engine
        self.engine.update(delta_time)
        self.engine.render()

    self.engine.cleanup()
```

Run the game! You should now see red enemy ships spawning at the top and moving down. They'll occasionally shoot red bullets.

## 📊 Step 5: Add Collision Detection

Let's add collision detection between bullets and ships:

```python
def check_collision(self, obj1, obj2):
    """Check collision between two objects"""
    x1, y1 = obj1.position
    x2, y2 = obj2.position

    # Simple circle collision
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance < 30  # Adjust based on object sizes

def handle_collisions(self):
    """Handle all collision detection"""
    # Player bullets vs enemies
    for bullet_data in self.bullets[:]:
        if bullet_data['object'].has_tag("player_bullet"):
            for enemy_data in self.enemies[:]:
                if self.check_collision(bullet_data['object'], enemy_data['object']):
                    # Hit!
                    bullet_data['controller'].destroyed = True
                    enemy_data['controller'].take_damage(50)
                    self.score += 100
                    self.create_explosion(enemy_data['object'].position[0], enemy_data['object'].position[1])
                    break

    # Enemy bullets vs player
    for bullet_data in self.bullets[:]:
        if bullet_data['object'].has_tag("enemy_bullet"):
            if self.check_collision(bullet_data['object'], self.player):
                bullet_data['controller'].destroyed = True
                self.player_controller.take_damage(20)

    # Enemies vs player
    for enemy_data in self.enemies[:]:
        if self.check_collision(enemy_data['object'], self.player):
            enemy_data['controller'].destroyed = True
            self.player_controller.take_damage(30)
```

Add this to the game loop:

```python
def run(self):
    """Start the game"""
    clock = pygame.time.Clock()

    while self.engine.running:
        # ... existing code ...

        # Handle collisions
        self.handle_collisions()

        # ... rest of game loop ...
```

## 🎨 Step 6: Add Visual Polish

Let's make the game feel more alive with explosion effects:

```python
def create_explosion(self, x, y):
    """Create explosion effect"""
    explosion = GameObject(f"Explosion_{random.randint(1000, 9999)}", "circle")
    explosion.position = (x, y)
    explosion.set_property("radius", 10)
    explosion.set_property("color", (255, 150, 0))

    # Create explosion controller
    explosion_controller = ExplosionController(explosion)

    self.explosions = getattr(self, 'explosions', [])
    self.explosions.append({'object': explosion, 'controller': explosion_controller})
    self.game_scene.add_object(explosion)

class ExplosionController:
    def __init__(self, explosion):
        self.explosion = explosion
        self.timer = 0.5
        self.start_radius = 10
        self.destroyed = False

    def update(self, delta_time):
        if self.destroyed:
            return

        self.timer -= delta_time

        # Expand and fade
        progress = 1 - (self.timer / 0.5)
        radius = self.start_radius * (1 + progress * 3)
        self.explosion.set_property("radius", radius)

        if self.timer <= 0:
            self.destroyed = True
```

Update the game loop to handle explosions:

```python
def run(self):
    """Start the game"""
    clock = pygame.time.Clock()

    while self.engine.running:
        # ... existing code ...

        # Update explosions
        if hasattr(self, 'explosions'):
            for explosion_data in self.explosions[:]:
                explosion_data['controller'].update(delta_time)
                if explosion_data['controller'].destroyed:
                    self.game_scene.remove_object(explosion_data['object'])
                    self.explosions.remove(explosion_data)

        # ... rest of game loop ...
```

## 🎮 Step 7: Add Game Over and UI

Let's add a proper game over screen and score display:

```python
def create_ui(self):
    """Create UI elements"""
    # Score will be printed to console for now
    print("🚀 Space Defender Started!")
    print("Controls: WASD/Arrows to move, Space to shoot")
    print("Press ESC to quit")

def check_game_over(self):
    """Check if game should end"""
    if self.player_controller.health <= 0:
        self.game_over = True
        print(f"GAME OVER! Final Score: {self.score}")
        print("Press R to restart or ESC to quit")

def restart_game(self):
    """Restart the game"""
    # Clear all objects
    self.bullets.clear()
    self.enemies.clear()
    if hasattr(self, 'explosions'):
        self.explosions.clear()

    # Reset game state
    self.score = 0
    self.game_over = False
    self.enemy_spawn_timer = 0
    self.enemies_created = 0

    # Reset player
    self.player_controller.health = 100
    self.player.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)

    print("Game restarted!")
```

Update the game loop to handle game over:

```python
def run(self):
    """Start the game"""
    clock = pygame.time.Clock()

    while self.engine.running:
        delta_time = clock.tick(60) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.engine.running = False
                elif event.key == pygame.K_r and self.game_over:
                    self.restart_game()

        # Skip game logic if game over
        if self.game_over:
            self.engine.update(delta_time)
            self.engine.render()
            continue

        # Get input
        keys = self.engine.get_keys()

        # ... rest of game logic ...

        # Check game over
        self.check_game_over()

        # Display score periodically
        if hasattr(self, 'score_timer'):
            self.score_timer += delta_time
        else:
            self.score_timer = 0

        if self.score_timer > 1:  # Every second
            print(f"Score: {self.score} | Health: {self.player_controller.health}")
            self.score_timer = 0

        # Update engine
        self.engine.update(delta_time)
        self.engine.render()

    self.engine.cleanup()
```

## 🏁 Final Complete Code

Here's the complete `space_defender.py` file:

```python
from engine.core import AxarionEngine
from engine.game_object import GameObject
from engine.asset_manager import asset_manager
import random
import pygame
import math

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 250
BULLET_SPEED = 400
ENEMY_SPEED = 100

class PlayerController:
    def __init__(self, player):
        self.player = player
        self.speed = PLAYER_SPEED
        self.shoot_cooldown = 0
        self.health = 100
        self.should_shoot = False

    def update(self, keys, delta_time):
        self.shoot_cooldown -= delta_time

        # Movement
        x, y = self.player.position

        if keys.get("ArrowLeft") or keys.get("a"):
            x -= self.speed * delta_time
        if keys.get("ArrowRight") or keys.get("d"):
            x += self.speed * delta_time
        if keys.get("ArrowUp") or keys.get("w"):
            y -= self.speed * delta_time
        if keys.get("ArrowDown") or keys.get("s"):
            y += self.speed * delta_time

        # Keep player on screen
        x = max(0, min(x, SCREEN_WIDTH - 40))
        y = max(0, min(y, SCREEN_HEIGHT - 30))

        self.player.position = (x, y)

        # Shooting
        if keys.get("Space") and self.shoot_cooldown <= 0:
            self.should_shoot = True
            self.shoot_cooldown = 0.2

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            print("Player destroyed!")

class BulletController:
    def __init__(self, bullet, velocity_y):
        self.bullet = bullet
        self.velocity_y = velocity_y
        self.destroyed = False

    def update(self, delta_time):
        if self.destroyed:
            return

        x, y = self.bullet.position
        y += self.velocity_y * delta_time
        self.bullet.position = (x, y)

        if y < -10 or y > SCREEN_HEIGHT + 10:
            self.destroyed = True

class EnemyController:
    def __init__(self, enemy):
        self.enemy = enemy
        self.speed = ENEMY_SPEED
        self.velocity_x = random.randint(-50, 50)
        self.shoot_timer = random.uniform(1, 3)
        self.health = 50
        self.destroyed = False
        self.should_shoot = False

    def update(self, delta_time):
        if self.destroyed:
            return

        x, y = self.enemy.position
        x += self.velocity_x * delta_time
        y += self.speed * delta_time

        self.enemy.position = (x, y)

        if y > SCREEN_HEIGHT + 50:
            self.destroyed = True
            return

        self.shoot_timer -= delta_time
        if self.shoot_timer <= 0:
            self.should_shoot = True
            self.shoot_timer = random.uniform(2, 4)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.destroyed = True

class ExplosionController:
    def __init__(self, explosion):
        self.explosion = explosion
        self.timer = 0.5
        self.start_radius = 10
        self.destroyed = False

    def update(self, delta_time):
        if self.destroyed:
            return

        self.timer -= delta_time
        progress = 1 - (self.timer / 0.5)
        radius = self.start_radius * (1 + progress * 3)
        self.explosion.set_property("radius", radius)

        if self.timer <= 0:
            self.destroyed = True

class SpaceDefender:
    def __init__(self):
        self.engine = AxarionEngine(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.engine.initialize()

        self.game_scene = self.engine.create_scene("Space Defender")
        self.engine.current_scene = self.game_scene

        self.score = 0
        self.game_over = False
        self.enemy_spawn_timer = 0
        self.enemies_created = 0

        self.bullets = []
        self.enemies = []
        self.explosions = []

        self.setup_assets()
        self.create_player()
        self.create_ui()

    def setup_assets(self):
        from assets.create_sample_assets import create_sample_assets
        create_sample_assets()
        asset_manager.load_all_assets()

    def create_player(self):
        self.player = GameObject("Player", "sprite")
        self.player.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)

        if not self.player.set_sprite("ship"):
            self.player.object_type = "rectangle"
            self.player.set_property("width", 40)
            self.player.set_property("height", 30)
            self.player.set_property("color", (100, 200, 255))

        self.player.add_tag("player")
        self.player_controller = PlayerController(self.player)
        self.game_scene.add_object(self.player)

    def create_ui(self):
        print("🚀 Space Defender Started!")
        print("Controls: WASD/Arrows to move, Space to shoot")
        print("Press ESC to quit")

    def create_bullet(self, x, y, velocity_y, tag, color):
        bullet = GameObject(f"Bullet_{random.randint(1000, 9999)}", "circle")
        bullet.position = (x, y)
        bullet.set_property("radius", 3)
        bullet.set_property("color", color)
        bullet.add_tag(tag)

        bullet_controller = BulletController(bullet, velocity_y)
        self.bullets.append({'object': bullet, 'controller': bullet_controller})
        self.game_scene.add_object(bullet)

        return bullet

    def spawn_enemy(self):
        enemy = GameObject(f"Enemy_{self.enemies_created}", "sprite")

        if not enemy.set_sprite("enemy"):
            enemy.object_type = "rectangle"
            enemy.set_property("width", 35)
            enemy.set_property("height", 25)
            enemy.set_property("color", (255, 100, 100))

        enemy.position = (random.randint(50, SCREEN_WIDTH - 50), -30)
        enemy.add_tag("enemy")

        enemy_controller = EnemyController(enemy)
        self.enemies.append({'object': enemy, 'controller': enemy_controller})
        self.game_scene.add_object(enemy)
        self.enemies_created += 1

    def create_explosion(self, x, y):
        explosion = GameObject(f"Explosion_{random.randint(1000, 9999)}", "circle")
        explosion.position = (x, y)
        explosion.set_property("radius", 10)
        explosion.set_property("color", (255, 150, 0))

        explosion_controller = ExplosionController(explosion)
        self.explosions.append({'object': explosion, 'controller': explosion_controller})
        self.game_scene.add_object(explosion)

    def check_collision(self, obj1, obj2):
        x1, y1 = obj1.position
        x2, y2 = obj2.position
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance < 30

    def handle_collisions(self):
        # Player bullets vs enemies
        for bullet_data in self.bullets[:]:
            if bullet_data['object'].has_tag("player_bullet"):
                for enemy_data in self.enemies[:]:
                    if self.check_collision(bullet_data['object'], enemy_data['object']):
                        bullet_data['controller'].destroyed = True
                        enemy_data['controller'].take_damage(50)
                        self.score += 100
                        self.create_explosion(enemy_data['object'].position[0], enemy_data['object'].position[1])
                        break

        # Enemy bullets vs player
        for bullet_data in self.bullets[:]:
            if bullet_data['object'].has_tag("enemy_bullet"):
                if self.check_collision(bullet_data['object'], self.player):
                    bullet_data['controller'].destroyed = True
                    self.player_controller.take_damage(20)

        # Enemies vs player
        for enemy_data in self.enemies[:]:
            if self.check_collision(enemy_data['object'], self.player):
                enemy_data['controller'].destroyed = True
                self.player_controller.take_damage(30)

    def check_game_over(self):
        if self.player_controller.health <= 0:
            self.game_over = True
            print(f"GAME OVER! Final Score: {self.score}")
            print("Press R to restart or ESC to quit")

    def restart_game(self):
        self.bullets.clear()
        self.enemies.clear()
        self.explosions.clear()

        self.score = 0
        self.game_over = False
        self.enemy_spawn_timer = 0
        self.enemies_created = 0

        self.player_controller.health = 100
        self.player.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)

        print("Game restarted!")

    def run(self):
        clock = pygame.time.Clock()

        while self.engine.running:
            delta_time = clock.tick(60) / 1000.0

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.engine.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.engine.running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.restart_game()

            if self.game_over:
                self.engine.update(delta_time)
                self.engine.render()
                continue

            keys = self.engine.get_keys()

            # Update player
            self.player_controller.update(keys, delta_time)

            # Handle player shooting
            if self.player_controller.should_shoot:
                x, y = self.player.position
                self.create_bullet(x + 20, y, -BULLET_SPEED, "player_bullet", (255, 255, 100))
                self.player_controller.should_shoot = False

            # Spawn enemies
            self.enemy_spawn_timer += delta_time
            if self.enemy_spawn_timer > 2:
                self.spawn_enemy()
                self.enemy_spawn_timer = 0

            # Update enemies
            for enemy_data in self.enemies[:]:
                enemy_data['controller'].update(delta_time)

                if enemy_data['controller'].should_shoot:
                    x, y = enemy_data['object'].position
                    self.create_bullet(x + 17, y + 25, 200, "enemy_bullet", (255, 100, 100))
                    enemy_data['controller'].should_shoot = False

                if enemy_data['controller'].destroyed:
                    self.game_scene.remove_object(enemy_data['object'])
                    self.enemies.remove(enemy_data)

            # Update bullets
            for bullet_data in self.bullets[:]:
                bullet_data['controller'].update(delta_time)
                if bullet_data['controller'].destroyed:
                    self.game_scene.remove_object(bullet_data['object'])
                    self.bullets.remove(bullet_data)

            # Update explosions
            for explosion_data in self.explosions[:]:
                explosion_data['controller'].update(delta_time)
                if explosion_data['controller'].destroyed:
                    self.game_scene.remove_object(explosion_data['object'])
                    self.explosions.remove(explosion_data)

            # Handle collisions
            self.handle_collisions()

            # Check game over
            self.check_game_over()

            # Display score periodically
            if hasattr(self, 'score_timer'):
                self.score_timer += delta_time
            else:
                self.score_timer = 0

            if self.score_timer > 1:
                print(f"Score: {self.score} | Health: {self.player_controller.health}")
                self.score_timer = 0

            # Update engine
            self.engine.update(delta_time)
            self.engine.render()

        self.engine.cleanup()

if __name__ == "__main__":
    game = SpaceDefender()
    game.run()
```

## 🎉 Congratulations!

You've just built a complete space shooter game! Here's what you've accomplished:

- ✅ Player ship with smooth movement
- ✅ Shooting mechanics with cooldown
- ✅ Enemy spawning and AI
- ✅ Collision detection between all objects
- ✅ Health and scoring systems
- ✅ Visual effects (explosions)
- ✅ Game over and restart functionality

## 🚀 What's Next?

Now that you have a working game, try adding these features:

### Easy Improvements:
- Different enemy types with different behaviors
- Power-ups (faster shooting, multi-shot, shield)
- Background graphics and scrolling
- Sound effects for shooting and explosions

### Intermediate Features:
- Boss enemies with multiple phases
- Different levels with increasing difficulty
- Player ship upgrades and customization
- Particle effects for more visual polish

### Advanced Features:
- High score saving and loading
- Multiple weapon types
- Multiplayer support
- Level editor for custom content

## 💡 Key Learning Points

From this tutorial, you learned:

1. **Game Architecture** - How to structure a complete game
2. **Object Management** - Creating, updating, and destroying game objects
3. **Collision Systems** - Detecting and responding to object interactions
4. **Game State** - Managing different states (playing, game over)
5. **Polish and Juice** - Adding effects that make the game feel good

You now have all the skills needed to create your own games with Axarion Engine! 🎮✨