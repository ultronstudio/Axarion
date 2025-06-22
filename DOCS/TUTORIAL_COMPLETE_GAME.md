
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

- Basic understanding of Python (variables, functions)
- Completed the "Getting Started" guide
- Axarion Engine running on your system

## 🎯 Step 1: Project Setup

Create a new file called `space_defender.py`:

```python
from engine.core import AxarionEngine
from engine.game_object import GameObject
from engine.asset_manager import asset_manager
import random

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
    
    # Player controls script
    self.player.script_code = f"""
var speed = {PLAYER_SPEED};
var shootCooldown = 0;
var health = 100;

function update() {{
    // Decrease cooldown
    shootCooldown -= 0.016;
    
    // Movement
    var pos = getProperty("position");
    
    if (keyPressed("ArrowLeft") || keyPressed("a")) {{
        pos.x -= speed * 0.016;
    }}
    if (keyPressed("ArrowRight") || keyPressed("d")) {{
        pos.x += speed * 0.016;
    }}
    if (keyPressed("ArrowUp") || keyPressed("w")) {{
        pos.y -= speed * 0.016;
    }}
    if (keyPressed("ArrowDown") || keyPressed("s")) {{
        pos.y += speed * 0.016;
    }}
    
    // Keep player on screen
    if (pos.x < 0) pos.x = 0;
    if (pos.x > {SCREEN_WIDTH - 40}) pos.x = {SCREEN_WIDTH - 40};
    if (pos.y < 0) pos.y = 0;
    if (pos.y > {SCREEN_HEIGHT - 30}) pos.y = {SCREEN_HEIGHT - 30};
    
    setProperty("position", pos);
    
    // Shooting
    if (keyPressed("Space") && shootCooldown <= 0) {{
        createPlayerBullet();
        shootCooldown = 0.2;  // 5 shots per second
    }}
    
    // Check collisions with enemies
    var enemies = getCollidingObjects();
    for (var i = 0; i < enemies.length; i++) {{
        if (findObjectByName(enemies[i]).hasTag("enemy")) {{
            takeDamage(20);
            break;
        }}
    }}
}}

function createPlayerBullet() {{
    var pos = getProperty("position");
    var bullet = instantiate("circle", pos.x + 20, pos.y);
    // Bullet will be configured by Python
}}

function takeDamage(amount) {{
    health -= amount;
    setProperty("health", health);
    
    if (health <= 0) {{
        // Game over logic will be handled by engine
        print("Player destroyed!");
    }}
}}
"""
    
    self.game_scene.add_object(self.player)
```

Run the game now and you should be able to move your blue rectangle (or ship sprite) around with WASD or arrow keys!

## 💥 Step 3: Add Bullets

Now let's make the shooting work. Add this method to your `SpaceDefender` class:

```python
def create_bullet(self, x, y, velocity_y, tag, color):
    """Create a bullet object"""
    bullet = GameObject(f"Bullet_{random.randint(1000, 9999)}", "circle")
    bullet.position = (x, y)
    bullet.set_property("radius", 3)
    bullet.set_property("color", color)
    bullet.velocity = (0, velocity_y)
    bullet.add_tag(tag)
    
    # Bullet behavior
    bullet.script_code = f"""
function update() {{
    var pos = getProperty("position");
    
    // Remove if off screen
    if (pos.y < -10 || pos.y > {SCREEN_HEIGHT + 10}) {{
        destroy();
        return;
    }}
    
    // Check collisions
    var colliding = getCollidingObjects();
    for (var i = 0; i < colliding.length; i++) {{
        var other = findObjectByName(colliding[i]);
        
        if (hasTag("player_bullet") && other.hasTag("enemy")) {{
            // Player bullet hit enemy
            print("Enemy hit!");
            destroy();
            other.takeDamage(50);
            break;
        }}
        else if (hasTag("enemy_bullet") && other.hasTag("player")) {{
            // Enemy bullet hit player
            print("Player hit!");
            destroy();
            other.takeDamage(20);
            break;
        }}
    }}
}}
"""
    
    return self.game_scene.add_object(bullet)
```

Now we need to handle bullet creation from the player script. Add this to your `SpaceDefender` class after `__init__`:

```python
def update_game(self):
    """Handle game logic each frame"""
    # Handle bullet creation requests
    # This is a simplified approach - in a real game you'd use a more robust system
    
    # Create player bullets when Space is pressed
    import pygame
    keys = pygame.key.get_pressed()
    if hasattr(self, 'last_shoot_time'):
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and current_time - self.last_shoot_time > 200:
            pos = self.player.position
            self.create_bullet(pos[0] + 20, pos[1], -BULLET_SPEED, "player_bullet", (255, 255, 100))
            self.last_shoot_time = current_time
    else:
        self.last_shoot_time = pygame.time.get_ticks()
```

And modify the `run` method to call our update:

```python
def run(self):
    """Start the game"""
    import pygame
    clock = pygame.time.Clock()
    
    while self.engine.running:
        # Update game logic
        self.update_game()
        
        # Run engine frame
        self.engine.run_frame()
        
        # Cap framerate
        clock.tick(60)
    
    self.engine.cleanup()
```

Test it out! You should now be able to shoot yellow bullets by pressing Space.

## 👾 Step 4: Add Enemies

Now for the fun part - enemies! Replace the `create_enemies` method:

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
    enemy.velocity = (random.randint(-50, 50), ENEMY_SPEED)
    enemy.add_tag("enemy")
    enemy.set_property("health", 50)
    
    # Enemy AI script
    enemy.script_code = f"""
var health = 50;
var shootTimer = random() * 2;  // Random initial shoot delay

function update() {{
    // Move down and slightly side to side
    var pos = getProperty("position");
    var vel = getProperty("velocity");
    
    // Remove if off screen
    if (pos.y > {SCREEN_HEIGHT + 50}) {{
        destroy();
        return;
    }}
    
    // Shooting
    shootTimer -= 0.016;
    if (shootTimer <= 0) {{
        shootAtPlayer();
        shootTimer = 2 + random() * 2;  // Shoot every 2-4 seconds
    }}
}}

function shootAtPlayer() {{
    var pos = getProperty("position");
    // Simple shooting - bullet creation handled by engine
    print("Enemy shooting from " + pos.x + ", " + pos.y);
}}

function takeDamage(amount) {{
    health -= amount;
    if (health <= 0) {{
        // Create explosion effect
        print("Enemy destroyed!");
        destroy();
    }}
}}
"""
    
    self.game_scene.add_object(enemy)
    self.enemies_created += 1
```

Update the `update_game` method to spawn enemies:

```python
def update_game(self):
    """Handle game logic each frame"""
    # Handle bullet creation requests
    import pygame
    keys = pygame.key.get_pressed()
    if hasattr(self, 'last_shoot_time'):
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and current_time - self.last_shoot_time > 200:
            pos = self.player.position
            self.create_bullet(pos[0] + 20, pos[1], -BULLET_SPEED, "player_bullet", (255, 255, 100))
            self.last_shoot_time = current_time
    else:
        self.last_shoot_time = pygame.time.get_ticks()
    
    # Spawn enemies
    self.enemy_spawn_timer += 1/60  # Assuming 60 FPS
    if self.enemy_spawn_timer > 2:  # Spawn every 2 seconds
        self.spawn_enemy()
        self.enemy_spawn_timer = 0
    
    # Enemy shooting
    self.handle_enemy_shooting()

def handle_enemy_shooting(self):
    """Handle enemy bullet creation"""
    # Find all enemies and let them shoot occasionally
    for obj_name, obj in self.game_scene.objects.items():
        if obj.has_tag("enemy") and random.random() < 0.01:  # 1% chance per frame
            pos = obj.position
            self.create_bullet(pos[0] + 17, pos[1] + 25, 200, "enemy_bullet", (255, 100, 100))
```

Run the game! You should now see red enemy ships spawning at the top and moving down. They'll occasionally shoot red bullets at you.

## 📊 Step 5: Add Score and UI

Let's add a score system and display it. First, update the bullet collision detection to award points:

```python
def award_points(self, points):
    """Award points to player"""
    self.score += points
    print(f"Score: {self.score}")

def update_game(self):
    """Handle game logic each frame"""
    # Previous code...
    
    # Check for destroyed enemies and award points
    # This is simplified - in a real game you'd use events
    current_enemies = len([obj for obj in self.game_scene.objects.values() if obj.has_tag("enemy")])
    if hasattr(self, 'last_enemy_count'):
        if current_enemies < self.last_enemy_count:
            # Enemy was destroyed
            self.award_points(100)
    self.last_enemy_count = current_enemies
    
    # Check game over
    if self.player.get_property("health") <= 0:
        self.game_over = True
        print(f"GAME OVER! Final Score: {self.score}")
```

## 🎨 Step 6: Add Visual Polish

Let's make the game feel more alive with some effects:

```python
def create_explosion(self, x, y):
    """Create explosion effect"""
    explosion = GameObject(f"Explosion_{random.randint(1000, 9999)}", "animated_sprite")
    explosion.position = (x, y)
    
    # Try to use explosion animation, fallback to particles
    if explosion.set_animation("explosion", speed=2.0, loop=False):
        explosion.script_code = """
var timer = 1.0;  // 1 second lifetime

function update() {
    timer -= 0.016;
    if (timer <= 0) {
        destroy();
    }
}
"""
    else:
        # Fallback: create simple expanding circle
        explosion.object_type = "circle"
        explosion.set_property("radius", 5)
        explosion.set_property("color", (255, 150, 0))
        explosion.script_code = """
var timer = 0.5;
var startRadius = 5;

function update() {
    timer -= 0.016;
    var radius = startRadius * (1 + (0.5 - timer) * 4);
    setProperty("radius", radius);
    
    if (timer <= 0) {
        destroy();
    }
}
"""
    
    self.game_scene.add_object(explosion)
```

Update the bullet collision detection to create explosions:

```python
def create_bullet(self, x, y, velocity_y, tag, color):
    """Create a bullet object"""
    bullet = GameObject(f"Bullet_{random.randint(1000, 9999)}", "circle")
    bullet.position = (x, y)
    bullet.set_property("radius", 3)
    bullet.set_property("color", color)
    bullet.velocity = (0, velocity_y)
    bullet.add_tag(tag)
    
    # Bullet behavior
    bullet.script_code = f"""
function update() {{
    var pos = getProperty("position");
    
    // Remove if off screen
    if (pos.y < -10 || pos.y > {SCREEN_HEIGHT + 10}) {{
        destroy();
        return;
    }}
    
    // Check collisions
    var colliding = getCollidingObjects();
    for (var i = 0; i < colliding.length; i++) {{
        var otherName = colliding[i];
        var other = findObjectByName(otherName);
        
        if (hasTag("player_bullet") && other.hasTag("enemy")) {{
            // Player bullet hit enemy
            print("Enemy hit!");
            // Create explosion at enemy position
            var enemyPos = other.getProperty("position");
            createExplosion(enemyPos.x, enemyPos.y);
            destroy();
            other.destroy();
            break;
        }}
        else if (hasTag("enemy_bullet") && other.hasTag("player")) {{
            // Enemy bullet hit player
            print("Player hit!");
            destroy();
            other.takeDamage(20);
            break;
        }}
    }}
}}
"""
    
    return self.game_scene.add_object(bullet)
```

## 🎵 Step 7: Add Sound Effects

If you have sound files, you can add them:

```python
def setup_assets(self):
    """Load or create game assets"""
    # Create sample assets if they don't exist
    from assets.create_sample_assets import create_sample_assets
    create_sample_assets()
    
    # Load all assets
    asset_manager.load_all_assets()
    
    # Load specific sounds if available
    self.has_sounds = True
    try:
        asset_manager.load_sound("shoot", "assets/sounds/shoot.wav")
        asset_manager.load_sound("explosion", "assets/sounds/explosion.wav")
        asset_manager.load_sound("hit", "assets/sounds/hit.wav")
    except:
        self.has_sounds = False
        print("Sound files not found - running without sound")
```

Add sound effects to actions by updating scripts:

```python
# In player script, add to shooting:
playSound("shoot");

# In bullet collision, add:
playSound("explosion");
```

## 🎮 Step 8: Complete Game Loop

Let's add a proper game over screen and restart functionality:

```python
def create_ui(self):
    """Create UI elements"""
    # Score display
    self.score_text = GameObject("ScoreText", "text")
    self.score_text.position = (10, 10)
    self.score_text.set_property("text", "Score: 0")
    self.score_text.set_property("color", (255, 255, 255))
    self.game_scene.add_object(self.score_text)
    
    # Health display
    self.health_text = GameObject("HealthText", "text")
    self.health_text.position = (10, 40)
    self.health_text.set_property("text", "Health: 100")
    self.health_text.set_property("color", (255, 255, 255))
    self.game_scene.add_object(self.health_text)

def update_ui(self):
    """Update UI elements"""
    if hasattr(self, 'score_text'):
        self.score_text.set_property("text", f"Score: {self.score}")
    
    if hasattr(self, 'health_text'):
        health = self.player.get_property("health")
        self.health_text.set_property("text", f"Health: {health}")

def update_game(self):
    """Handle game logic each frame"""
    if self.game_over:
        return
    
    # Previous update code...
    
    # Update UI
    self.update_ui()
    
    # Check game over condition
    if self.player.get_property("health") <= 0:
        self.show_game_over()

def show_game_over(self):
    """Display game over screen"""
    self.game_over = True
    
    # Create game over text
    game_over_text = GameObject("GameOverText", "text")
    game_over_text.position = (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
    game_over_text.set_property("text", f"GAME OVER! Score: {self.score}")
    game_over_text.set_property("color", (255, 255, 255))
    self.game_scene.add_object(game_over_text)
    
    restart_text = GameObject("RestartText", "text")
    restart_text.position = (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 30)
    restart_text.set_property("text", "Press R to restart or ESC to quit")
    restart_text.set_property("color", (200, 200, 200))
    self.game_scene.add_object(restart_text)
```

## 🏁 Final Complete Code

Here's the complete `space_defender.py` file:

```python
from engine.core import AxarionEngine
from engine.game_object import GameObject
from engine.asset_manager import asset_manager
import random
import pygame

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
        self.enemy_spawn_timer = 0
        self.enemies_created = 0
        self.last_enemy_count = 0
        
        # Load assets
        self.setup_assets()
        
        # Create game objects
        self.create_player()
        self.create_enemies()
        self.create_ui()
    
    def setup_assets(self):
        """Load or create game assets"""
        from assets.create_sample_assets import create_sample_assets
        create_sample_assets()
        asset_manager.load_all_assets()
    
    def create_player(self):
        """Create the player spaceship"""
        self.player = GameObject("Player", "sprite")
        self.player.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        
        if not self.player.set_sprite("ship"):
            self.player.object_type = "rectangle"
            self.player.set_property("width", 40)
            self.player.set_property("height", 30)
            self.player.set_property("color", (100, 200, 255))
        
        self.player.add_tag("player")
        self.player.set_property("health", 100)
        
        self.player.script_code = f"""
var speed = {PLAYER_SPEED};
var health = 100;

function update() {{
    var pos = getProperty("position");
    
    if (keyPressed("ArrowLeft") || keyPressed("a")) {{
        pos.x -= speed * 0.016;
    }}
    if (keyPressed("ArrowRight") || keyPressed("d")) {{
        pos.x += speed * 0.016;
    }}
    if (keyPressed("ArrowUp") || keyPressed("w")) {{
        pos.y -= speed * 0.016;
    }}
    if (keyPressed("ArrowDown") || keyPressed("s")) {{
        pos.y += speed * 0.016;
    }}
    
    if (pos.x < 0) pos.x = 0;
    if (pos.x > {SCREEN_WIDTH - 40}) pos.x = {SCREEN_WIDTH - 40};
    if (pos.y < 0) pos.y = 0;
    if (pos.y > {SCREEN_HEIGHT - 30}) pos.y = {SCREEN_HEIGHT - 30};
    
    setProperty("position", pos);
}}

function takeDamage(amount) {{
    health -= amount;
    setProperty("health", health);
}}
"""
        
        self.game_scene.add_object(self.player)
    
    def create_enemies(self):
        """Create enemy ships"""
        pass  # Enemies are spawned dynamically
    
    def create_ui(self):
        """Create UI elements"""
        pass  # UI updates are handled in update_ui()
    
    def create_bullet(self, x, y, velocity_y, tag, color):
        """Create a bullet object"""
        bullet = GameObject(f"Bullet_{random.randint(1000, 9999)}", "circle")
        bullet.position = (x, y)
        bullet.set_property("radius", 3)
        bullet.set_property("color", color)
        bullet.velocity = (0, velocity_y)
        bullet.add_tag(tag)
        bullet.collision_enabled = True
        
        self.game_scene.add_object(bullet)
        return bullet
    
    def spawn_enemy(self):
        """Spawn a single enemy"""
        enemy = GameObject(f"Enemy_{self.enemies_created}", "sprite")
        
        if not enemy.set_sprite("enemy"):
            enemy.object_type = "rectangle"
            enemy.set_property("width", 35)
            enemy.set_property("height", 25)
            enemy.set_property("color", (255, 100, 100))
        
        enemy.position = (random.randint(50, SCREEN_WIDTH - 50), -30)
        enemy.velocity = (random.randint(-50, 50), ENEMY_SPEED)
        enemy.add_tag("enemy")
        enemy.set_property("health", 50)
        enemy.collision_enabled = True
        
        self.game_scene.add_object(enemy)
        self.enemies_created += 1
    
    def update_game(self):
        """Handle game logic each frame"""
        if self.game_over:
            # Check for restart
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                self.restart_game()
            return
        
        # Handle shooting
        keys = pygame.key.get_pressed()
        if hasattr(self, 'last_shoot_time'):
            current_time = pygame.time.get_ticks()
            if keys[pygame.K_SPACE] and current_time - self.last_shoot_time > 200:
                pos = self.player.position
                self.create_bullet(pos[0] + 20, pos[1], -BULLET_SPEED, "player_bullet", (255, 255, 100))
                self.last_shoot_time = current_time
        else:
            self.last_shoot_time = pygame.time.get_ticks()
        
        # Spawn enemies
        self.enemy_spawn_timer += 1/60
        if self.enemy_spawn_timer > 2:
            self.spawn_enemy()
            self.enemy_spawn_timer = 0
        
        # Enemy shooting
        for obj_name, obj in list(self.game_scene.objects.items()):
            if obj.has_tag("enemy") and random.random() < 0.005:
                pos = obj.position
                self.create_bullet(pos[0] + 17, pos[1] + 25, 200, "enemy_bullet", (255, 100, 100))
        
        # Handle collisions
        self.handle_collisions()
        
        # Check game over
        if self.player.get_property("health") <= 0:
            self.show_game_over()
    
    def handle_collisions(self):
        """Handle all collision detection"""
        # Get all bullets
        player_bullets = [obj for obj in self.game_scene.objects.values() if obj.has_tag("player_bullet")]
        enemy_bullets = [obj for obj in self.game_scene.objects.values() if obj.has_tag("enemy_bullet")]
        enemies = [obj for obj in self.game_scene.objects.values() if obj.has_tag("enemy")]
        
        # Player bullets vs enemies
        for bullet in player_bullets:
            for enemy in enemies:
                if bullet.is_colliding_with(enemy):
                    bullet.destroyed = True
                    enemy.destroyed = True
                    self.score += 100
                    self.create_explosion(enemy.position[0], enemy.position[1])
                    break
        
        # Enemy bullets vs player
        for bullet in enemy_bullets:
            if bullet.is_colliding_with(self.player):
                bullet.destroyed = True
                current_health = self.player.get_property("health")
                self.player.set_property("health", current_health - 20)
        
        # Enemies vs player
        for enemy in enemies:
            if enemy.is_colliding_with(self.player):
                enemy.destroyed = True
                current_health = self.player.get_property("health")
                self.player.set_property("health", current_health - 30)
    
    def create_explosion(self, x, y):
        """Create explosion effect"""
        explosion = GameObject(f"Explosion_{random.randint(1000, 9999)}", "circle")
        explosion.position = (x, y)
        explosion.set_property("radius", 10)
        explosion.set_property("color", (255, 150, 0))
        
        explosion.script_code = """
var timer = 0.5;
var startRadius = 10;

function update() {
    timer -= 0.016;
    var radius = startRadius * (1 + (0.5 - timer) * 3);
    setProperty("radius", radius);
    
    if (timer <= 0) {
        destroy();
    }
}
"""
        self.game_scene.add_object(explosion)
    
    def show_game_over(self):
        """Display game over screen"""
        self.game_over = True
        print(f"GAME OVER! Final Score: {self.score}")
    
    def restart_game(self):
        """Restart the game"""
        # Clear scene
        self.game_scene.objects.clear()
        
        # Reset state
        self.score = 0
        self.game_over = False
        self.enemy_spawn_timer = 0
        self.enemies_created = 0
        
        # Recreate game objects
        self.create_player()
        self.create_enemies()
        self.create_ui()
    
    def run(self):
        """Start the game"""
        clock = pygame.time.Clock()
        
        print("🚀 Space Defender Started!")
        print("Controls: WASD/Arrows to move, Space to shoot")
        print("Press ESC to quit, R to restart when game over")
        
        while self.engine.running:
            # Handle quit
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.engine.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.engine.running = False
            
            # Update game
            self.update_game()
            
            # Run engine frame
            self.engine.run_frame()
            
            # Display info
            if hasattr(self, 'display_timer'):
                self.display_timer += 1/60
            else:
                self.display_timer = 0
            
            if self.display_timer > 1:  # Every second
                health = self.player.get_property("health") if not self.game_over else 0
                print(f"Score: {self.score} | Health: {health}")
                self.display_timer = 0
            
            clock.tick(60)
        
        self.engine.cleanup()

# Create and run the game
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
