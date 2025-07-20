
# 🎮 Create Your First Complete Game in Axarion Studio: Cosmic Defender

In this tutorial, you'll create a complete space shooter from scratch using Axarion Studio! By the end, you'll have a fully playable game with:

- Modern UI created in Axarion Studio
- Enemy system with AI
- Particle effects and sound effects
- Scoring system and power-ups
- Professional build ready for distribution

**Estimated Time:** 45-60 minutes  
**Difficulty:** Beginner with Axarion Studio

## 🚀 What You'll Learn

- Working with Axarion Studio interface
- Asset Management and import workflow
- Modern component-based game development
- Build and deployment process
- Professional game architecture

## 📋 Prerequisites

- Axarion Studio installed and working
- Basic knowledge of programming (variables, functions)
- Knowledge of Axarion Studio controls (see Getting Started)

## 🎯 Step 1: Create Project in Axarion Studio

### Launch Studio and New Project

1. **Start Axarion Studio:**
```bash
python axarion_studio.py
```

2. **Create new project:**
   - Click "New Project"
   - Name: "Cosmic Defender"
   - Studio creates complete project structure

### Understanding Project Structure

Studio automatically creates:

```
Cosmic_Defender/
├── game.js              # Main file (Studio template)
├── project.json         # Project configuration
├── assets/              # Managed by Asset Manager
│   ├── images/
│   ├── sounds/
│   ├── music/
│   └── fonts/
├── scenes/              # Game scenes
├── scripts/             # Script files
└── build/               # Build outputs
```

## 🎨 Step 2: Import Assets using Asset Manager

### Open Asset Manager

1. **Launch Asset Manager:** `Ctrl+Shift+A` or folder icon
2. **Discover modern interface** with two main sections:
   - **Local Assets** - your imported files
   - **Asset Store** - thousands of free assets

### Import from Asset Store

1. **Go to Asset Store tab**
2. **Search for "Space Game Pack"**
3. **Download these packages:**
   - "Space Ships Collection"
   - "Laser Sound Effects"
   - "Explosion Animations"
   - "UI Elements Pack"

### Custom Assets (drag & drop)

If you have your own files:
1. **Drag PNG images** into "Images" section
2. **Drag WAV/MP3 files** into "Sounds" section
3. **Studio automatically** creates previews and optimizes files

### Verify Import

In Studio console you'll see:
```
✅ Downloaded: space_ship_pack (12 assets)
✅ Import: player_ship.png (64x48)
✅ Import: enemy_fighter.png (48x32)
✅ Import: laser_shoot.wav (0.2s)
✅ Asset Manager: 25 assets ready
```

## 🎮 Step 3: Create Basic Game

### Studio Template Analysis

Studio created basic `game.js`:

```javascript
/*
Cosmic Defender - Axarion Engine Game

Created in Axarion Studio with modern workflow
*/

// Studio automatically includes necessary modules
var engine = createEngine(1024, 768);
engine.initialize();

// Main scene
var gameScene = engine.createScene("SpaceArena");
engine.currentScene = gameScene;

// Game state management
var score = 0;
var gameOver = false;
var wave = 1;

// Asset Manager integration
setupAssets();

// Create game objects
createPlayer();
setupUI();

function setupAssets() {
    // Studio Asset Manager automatically loads everything
    loadAssets();
    
    console.log("🚀 Assets loaded via Axarion Studio Asset Manager");
}
```

### Create Player with Asset Manager

```javascript
function createPlayer() {
    // Create player ship using Studio assets
    var player = createGameObject("Player", "sprite");
    player.position = {x: 512, y: 600}; // Center bottom
    
    // Asset Manager integration - sprite found automatically
    if (!player.setSprite("player_ship")) {
        // Fallback if asset not available
        player.type = "rectangle";
        player.width = 60;
        player.height = 40;
        player.color = {r: 100, g: 150, b: 255};
    }
    
    player.addTag("player");
    player.health = 100;
    player.maxHealth = 100;
    
    // Modern controls with Studio IntelliSense
    player.update = function() {
        var speed = 350;
        var health = 100;
        var invulnerable = 0;
        var shootCooldown = 0;
        var powerLevel = 1;

        handleMovement();
        handleShooting();
        handleInvulnerability();
        updatePowerups();

        function handleMovement() {
            var pos = getProperty("position");
            var newPos = pos;
            
            // Smooth movement with diagonal capability
            var moveX = 0, moveY = 0;
            
            if (keyPressed("a") || keyPressed("ArrowLeft")) moveX = -1;
            if (keyPressed("d") || keyPressed("ArrowRight")) moveX = 1;
            if (keyPressed("w") || keyPressed("ArrowUp")) moveY = -1;
            if (keyPressed("s") || keyPressed("ArrowDown")) moveY = 1;
            
            // Normalize diagonal movement
            if (moveX != 0 && moveY != 0) {
                moveX *= 0.707; // sqrt(2)/2
                moveY *= 0.707;
            }
            
            newPos.x += moveX * speed * deltaTime();
            newPos.y += moveY * speed * deltaTime();
            
            // Bounds checking with padding
            if (newPos.x < 30) newPos.x = 30;
            if (newPos.x > 994) newPos.x = 994;
            if (newPos.y < 30) newPos.y = 30;
            if (newPos.y > 738) newPos.y = 738;
            
            setProperty("position", newPos);
        }

        function handleShooting() {
            shootCooldown -= deltaTime();
            
            if ((keyPressed("Space") || keyPressed("x")) && shootCooldown <= 0) {
                createPlayerBullets();
                playSound("laser_shoot"); // Asset Manager automatically finds
                shootCooldown = 0.15; // Faster shooting
            }
        }

        function createPlayerBullets() {
            var pos = getProperty("position");
            
            if (powerLevel == 1) {
                // Single shot
                createBullet(pos.x, pos.y - 20, 0, -600, "player_bullet");
            } else if (powerLevel == 2) {
                // Double shot
                createBullet(pos.x - 15, pos.y - 20, 0, -600, "player_bullet");
                createBullet(pos.x + 15, pos.y - 20, 0, -600, "player_bullet");
            } else {
                // Triple shot
                createBullet(pos.x, pos.y - 20, 0, -600, "player_bullet");
                createBullet(pos.x - 20, pos.y - 10, -100, -600, "player_bullet");
                createBullet(pos.x + 20, pos.y - 10, 100, -600, "player_bullet");
            }
        }

        function takeDamage(amount) {
            if (invulnerable > 0) return;
            
            health -= amount;
            setProperty("health", health);
            
            if (health <= 0) {
                explode();
                // Game over will be handled in main game loop
            } else {
                invulnerable = 1.5; // 1.5 seconds invincibility
                playSound("player_hit");
            }
        }

        function handleInvulnerability() {
            if (invulnerable > 0) {
                invulnerable -= deltaTime();
                // Blinking effect
                var alpha = (Math.sin(time() * 10) + 1) * 0.5;
                setProperty("alpha", alpha);
            } else {
                setProperty("alpha", 1.0);
            }
        }

        function explode() {
            var pos = getProperty("position");
            createExplosion(pos.x, pos.y, "large");
            playSound("player_death");
        }
    };
    
    gameScene.addObject(player);
}
```

### Bullet System with Asset Manager

```javascript
function createBullet(x, y, velX, velY, tag, color) {
    // Create bullet with improved graphics from Asset Manager
    var bullet = createGameObject("Bullet_" + getUniqueId(), "sprite");
    
    // Try to use sprite from Asset Manager
    if (!bullet.setSprite("laser_bullet")) {
        // Fallback to basic circle
        bullet.type = "circle";
        bullet.radius = 4;
        bullet.color = color || {r: 255, g: 255, b: 100};
    }
    
    bullet.position = {x: x, y: y};
    bullet.velocity = {x: velX, y: velY};
    bullet.addTag(tag);
    bullet.collisionEnabled = true;
    
    // Script for bullets with better lifecycle
    bullet.update = function() {
        var lifetime = 3.0; // Bullets disappear after 3 seconds
        
        lifetime -= deltaTime();
        
        // Remove if lifetime expired or off screen
        var pos = getProperty("position");
        if (lifetime <= 0 || pos.y < -50 || pos.y > 820 || 
            pos.x < -50 || pos.x > 1074) {
            destroy();
            return;
        }
        
        // Enhanced collision detection
        checkCollisions();
        
        function checkCollisions() {
            var colliding = getCollidingObjects();
            
            for (var i = 0; i < colliding.length; i++) {
                var other = findObjectByName(colliding[i]);
                
                if (hasTag("player_bullet") && other.hasTag("enemy")) {
                    // Player bullet hit enemy
                    var pos = getProperty("position");
                    createHitEffect(pos.x, pos.y);
                    other.takeDamage(25);
                    destroy();
                    return;
                }
                
                if (hasTag("enemy_bullet") && other.hasTag("player")) {
                    // Enemy bullet hit player
                    other.takeDamage(20);
                    destroy();
                    return;
                }
            }
        }
    };
    
    return gameScene.addObject(bullet);
}

function getUniqueId() {
    // Generate unique ID for objects
    return Math.floor(Date.now() % 100000);
}
```

## 👾 Step 4: Enemies with Advanced AI

### Enemy Spawning System

```javascript
function spawnEnemy(enemyType) {
    // Spawn enemy with AI from Asset Manager sprites
    var enemy = createGameObject("Enemy_" + getUniqueId(), "sprite");
    
    // Different enemy types with different sprites
    if (enemyType == "basic") {
        enemy.setSprite("enemy_fighter");
        enemy.health = 50;
        enemy.speed = 120;
        enemy.scoreValue = 100;
    } else if (enemyType == "fast") {
        enemy.setSprite("enemy_interceptor");
        enemy.health = 25;
        enemy.speed = 200;
        enemy.scoreValue = 150;
    } else if (enemyType == "tank") {
        enemy.setSprite("enemy_destroyer");
        enemy.health = 150;
        enemy.speed = 60;
        enemy.scoreValue = 300;
    }
    
    // Fallback if sprites not available
    if (!enemy.sprite) {
        enemy.type = "rectangle";
        enemy.width = 40;
        enemy.height = 30;
        enemy.color = {r: 255, g: 100, b: 100};
    }
    
    // Spawn position
    enemy.position = {x: Math.random() * 924 + 50, y: -50};
    enemy.addTag("enemy");
    enemy.collisionEnabled = true;
    
    // Enhanced AI script
    enemy.update = function() {
        var health = getProperty("health");
        var maxHealth = health;
        var speed = getProperty("speed");
        var shootTimer = Math.random() * 3; // Random initial delay
        var movementPattern = Math.floor(Math.random() * 3); // 0, 1, or 2
        var phaseOffset = Math.random() * 6.28; // Random phase for sine wave
        
        updateMovement();
        updateCombat();
        updateVisuals();
        
        function updateMovement() {
            var pos = getProperty("position");
            
            // Remove if too far off screen
            if (pos.y > 820) {
                destroy();
                return;
            }
            
            // Different movement patterns
            if (movementPattern == 0) {
                // Straight down
                move(0, speed * deltaTime());
            } else if (movementPattern == 1) {
                // Sine wave pattern
                move(Math.sin(time() * 2 + phaseOffset) * 50 * deltaTime(), speed * deltaTime());
            } else {
                // Zigzag pattern
                var zigzag = Math.sin(time() * 4) * 30;
                move(zigzag * deltaTime(), speed * deltaTime());
            }
            
            // Bounds checking
            if (pos.x < 20) move(20, 0);
            if (pos.x > 1004) move(-20, 0);
        }
        
        function updateCombat() {
            shootTimer -= deltaTime();
            
            if (shootTimer <= 0) {
                var pos = getProperty("position");
                var player = findObjectByName("Player");
                
                if (player) {
                    var playerPos = player.getProperty("position");
                    
                    // Aim at player with some inaccuracy
                    var dx = playerPos.x - pos.x;
                    var dy = playerPos.y - pos.y;
                    var distance = Math.sqrt(dx*dx + dy*dy);
                    
                    var inaccuracy = 50; // Pixels of inaccuracy
                    dx += (Math.random() - 0.5) * inaccuracy;
                    dy += (Math.random() - 0.5) * inaccuracy;
                    
                    // Normalize and scale
                    var length = Math.sqrt(dx*dx + dy*dy);
                    var bulletSpeed = 300;
                    var velX = (dx / length) * bulletSpeed;
                    var velY = (dy / length) * bulletSpeed;
                    
                    createEnemyBullet(pos.x, pos.y + 15, velX, velY);
                    playSound("enemy_shoot");
                }
                
                shootTimer = 2 + Math.random() * 2; // 2-4 seconds
            }
        }
        
        function updateVisuals() {
            // Health-based color tinting
            var healthPercent = health / maxHealth;
            if (healthPercent < 0.5) {
                // Red tint when damaged
                var tintAmount = (1 - healthPercent) * 2;
                setProperty("colorTint", {r: 255, g: 255 * (1-tintAmount), b: 255 * (1-tintAmount)});
            }
        }
        
        function takeDamage(amount) {
            health -= amount;
            
            // Hit feedback
            playSound("enemy_hit");
            createHitEffect(getProperty("position").x, getProperty("position").y);
            
            if (health <= 0) {
                die();
            }
        }
        
        function die() {
            var pos = getProperty("position");
            var scoreValue = getProperty("scoreValue");
            
            // Death effects
            createExplosion(pos.x, pos.y, "medium");
            playSound("enemy_death");
            
            // Chance to drop power-up
            if (Math.random() < 0.2) { // 20% chance
                createPowerUp(pos.x, pos.y);
            }
            
            // Award score
            addScore(scoreValue);
            
            destroy();
        }
    };
    
    gameScene.addObject(enemy);
}
```

### Enemy Wave Management

```javascript
function updateEnemySpawning(dt) {
    // Advanced enemy spawning with waves
    if (!spawnTimer) {
        spawnTimer = 0;
        enemiesThisWave = 0;
        maxEnemiesPerWave = 10;
    }
    
    spawnTimer += dt;
    
    // Current wave difficulty scaling
    var spawnDelay = Math.max(0.5, 2.0 - (wave * 0.1)); // Faster spawning each wave
    
    if (spawnTimer >= spawnDelay && enemiesThisWave < maxEnemiesPerWave) {
        
        // Choose enemy type based on wave
        var enemyType = "basic";
        if (wave >= 3) {
            var enemyChoices = ["basic", "fast"];
            if (wave >= 5) {
                enemyChoices.push("tank");
            }
            enemyType = enemyChoices[Math.floor(Math.random() * enemyChoices.length)];
        }
        
        spawnEnemy(enemyType);
        spawnTimer = 0;
        enemiesThisWave++;
    }
    
    // Check for wave completion
    if (enemiesThisWave >= maxEnemiesPerWave && 
        getObjectsByTag("enemy").length == 0) {
        startNextWave();
    }
}

function startNextWave() {
    // Start the next wave with increased difficulty
    wave++;
    enemiesThisWave = 0;
    maxEnemiesPerWave += 2; // More enemies each wave
    
    console.log("🌊 Wave " + wave + " starts!");
    // Here could be wave announcement UI
}
```

## 🎨 Step 5: Visual Effects using Asset Manager

### Particle Systems

```javascript
function createExplosion(x, y, size) {
    // Create explosion effect using Asset Manager
    var explosion = createGameObject("Explosion_" + getUniqueId(), "particle_system");
    explosion.position = {x: x, y: y};
    
    // Different explosion sizes
    var particleCount, particleSize, lifetime;
    if (size == "small") {
        particleCount = 20;
        particleSize = 3;
        lifetime = 0.8;
    } else if (size == "large") {
        particleCount = 80;
        particleSize = 6;
        lifetime = 2.0;
    } else { // medium
        particleCount = 50;
        particleSize = 4;
        lifetime = 1.2;
    }
    
    explosion.setParticleConfig({
        count: particleCount,
        lifetime: lifetime,
        speedMin: 50,
        speedMax: 200,
        directionMin: 0,
        directionMax: 360,
        sizeStart: particleSize,
        sizeEnd: 0,
        colorStart: {r: 255, g: 255, b: 100},
        colorEnd: {r: 255, g: 0, b: 0},
        alphaStart: 1.0,
        alphaEnd: 0.0
    });
    
    // Auto-destroy after completion
    explosion.update = function() {
        var timer = lifetime;
        
        timer -= deltaTime();
        if (timer <= 0) {
            destroy();
        }
    };
    
    gameScene.addObject(explosion);
}

function createHitEffect(x, y) {
    // Small impact effect
    var impact = createGameObject("Impact_" + getUniqueId(), "particle_system");
    impact.position = {x: x, y: y};
    
    impact.setParticleConfig({
        count: 10,
        lifetime: 0.3,
        speedMin: 20,
        speedMax: 80,
        directionMin: 0,
        directionMax: 360,
        sizeStart: 2,
        sizeEnd: 0,
        colorStart: {r: 255, g: 255, b: 255},
        colorEnd: {r: 255, g: 255, b: 0},
    });
    
    // Quick cleanup
    impact.update = function() {
        var timer = 0.3;
        timer -= deltaTime();
        if (timer <= 0) destroy();
    };
    
    gameScene.addObject(impact);
}
```

### Power-up System

```javascript
function createPowerUp(x, y) {
    // Create power-up pickup
    var powerup = createGameObject("PowerUp_" + getUniqueId(), "sprite");
    
    if (!powerup.setSprite("power_orb")) {
        powerup.type = "circle";
        powerup.radius = 12;
        powerup.color = {r: 100, g: 255, b: 100};
    }
    
    powerup.position = {x: x, y: y};
    powerup.addTag("powerup");
    powerup.collisionEnabled = true;
    
    // Random power-up type
    var powerupTypes = ["weapon_upgrade", "health", "shield", "speed"];
    powerup.powerType = powerupTypes[Math.floor(Math.random() * powerupTypes.length)];
    
    powerup.update = function() {
        var bobTimer = 0;
        var lifetime = 8.0; // Disappears after 8 seconds
        
        // Bobbing animation
        bobTimer += deltaTime() * 3;
        var offset = Math.sin(bobTimer) * 3;
        var pos = getProperty("position");
        setProperty("visualOffsetY", offset);
        
        // Lifetime
        lifetime -= deltaTime();
        if (lifetime <= 0) {
            destroy();
            return;
        }
        
        // Collection detection
        var player = findObjectByName("Player");
        if (player && isCollidingWith("Player")) {
            collectPowerUp();
        }
        
        function collectPowerUp() {
            var type = getProperty("powerType");
            var player = findObjectByName("Player");
            
            playSound("powerup_collect");
            createCollectEffect(getProperty("position").x, getProperty("position").y);
            
            // Apply power-up effect (handled by player or game manager)
            applyPowerUpEffect(type);
            
            destroy();
        }
    };
    
    gameScene.addObject(powerup);
}
```

## 🎵 Step 6: Audio System with Asset Manager

### Setup Audio Environment

```javascript
function setupAudio() {
    // Background music
    if (getSound("space_theme")) {
        playMusic("space_theme", {loop: true, volume: 0.6});
    }
    
    // Pre-load all sound effects for better performance
    var soundEffects = {
        laserShoot: getSound("laser_shoot"),
        enemyShoot: getSound("enemy_shoot"),
        explosion: getSound("explosion"),
        powerup: getSound("powerup_collect"),
        playerHit: getSound("player_damage"),
    };
    
    // Dynamic audio settings
    var audioSettings = {
        masterVolume: 1.0,
        musicVolume: 0.6,
        sfxVolume: 0.8
    };
}

function playPositionalAudio(soundName, x, y, volume) {
    // Play sound with 3D positioning
    volume = volume || 1.0;
    
    // Calculate distance from player for volume adjustment
    var playerPos = player.position;
    var distance = Math.sqrt((x - playerPos.x) * (x - playerPos.x) + 
                           (y - playerPos.y) * (y - playerPos.y));
    
    // Volume falloff based on distance
    var maxDistance = 400;
    var distanceFactor = Math.max(0, 1 - (distance / maxDistance));
    var adjustedVolume = volume * distanceFactor * audioSettings.sfxVolume;
    
    if (soundEffects[soundName] && adjustedVolume > 0.1) {
        playSound(soundName, {volume: adjustedVolume});
    }
}
```

## 🎯 Step 7: UI System in Studio

### Modern UI with Asset Manager

```javascript
function setupUI() {
    // Score display
    var scoreText = createGameObject("ScoreUI", "text");
    scoreText.position = {x: 50, y: 50};
    
    // Font from Asset Manager
    if (!scoreText.setFont("game_font", 24)) {
        // Fallback system font
        scoreText.setFont("Arial", 24);
    }
    
    scoreText.text = "Score: 0";
    scoreText.color = {r: 255, g: 255, b: 255};
    scoreText.shadow = true;
    scoreText.shadowColor = {r: 0, g: 0, b: 0};
    
    // Health bar
    createHealthBar();
    
    // Wave indicator
    var waveText = createGameObject("WaveUI", "text");
    waveText.position = {x: 50, y: 100};
    waveText.setFont("game_font", 18);
    waveText.text = "Wave: 1";
    waveText.color = {r: 100, g: 255, b: 100};
    
    // Add to scene
    gameScene.addObject(scoreText);
    gameScene.addObject(waveText);
}

function createHealthBar() {
    // Background
    var healthBG = createGameObject("HealthBG", "rectangle");
    healthBG.position = {x: 50, y: 150};
    healthBG.width = 200;
    healthBG.height = 20;
    healthBG.color = {r: 100, g: 0, b: 0};
    
    // Foreground (actual health)
    var healthFG = createGameObject("HealthFG", "rectangle");
    healthFG.position = {x: 50, y: 150};
    healthFG.width = 200;
    healthFG.height = 20;
    healthFG.color = {r: 0, g: 255, b: 0};
    
    gameScene.addObject(healthBG);
    gameScene.addObject(healthFG);
}

function updateUI() {
    // Update UI elements each frame
    // Update score
    var scoreText = findObjectByName("ScoreUI");
    if (scoreText) {
        scoreText.text = "Score: " + score;
    }
    
    // Update wave
    var waveText = findObjectByName("WaveUI");
    if (waveText) {
        waveText.text = "Wave: " + wave;
    }
    
    // Update health bar
    var healthFG = findObjectByName("HealthFG");
    if (healthFG && player) {
        var currentHealth = player.health;
        var maxHealth = player.maxHealth;
        var healthPercent = Math.max(0, currentHealth / maxHealth);
        
        // Width based on health percentage
        healthFG.width = Math.floor(200 * healthPercent);
        
        // Color changes based on health
        if (healthPercent > 0.6) {
            healthFG.color = {r: 0, g: 255, b: 0}; // Green
        } else if (healthPercent > 0.3) {
            healthFG.color = {r: 255, g: 255, b: 0}; // Yellow
        } else {
            healthFG.color = {r: 255, g: 0, b: 0}; // Red
        }
    }
}
```

## 🎮 Step 8: Game Loop and Logic

### Main Game Loop

```javascript
function run() {
    // Main game loop with Studio optimizations
    console.log("🚀 Cosmic Defender started in Axarion Studio!");
    console.log("Controls: WASD/Arrows - move, Space/X - shoot");
    
    // Setup audio
    setupAudio();
    
    var lastTime = 0;
    
    function gameLoop(currentTime) {
        var dt = (currentTime - lastTime) / 1000.0; // Delta time in seconds
        lastTime = currentTime;
        
        // Handle events
        handleEvents();
        
        // Update game systems
        updateGameLogic(dt);
        
        // Update UI
        updateUI();
        
        // Render frame
        engine.runFrame();
        
        // Check win/lose conditions
        checkGameState();
        
        if (!gameOver) {
            requestAnimationFrame(gameLoop);
        } else {
            handleGameOver();
        }
    }
    
    requestAnimationFrame(gameLoop);
}

function updateGameLogic(dt) {
    // Update all game systems
    // Enemy spawning
    updateEnemySpawning(dt);
    
    // Collision detection
    handleCollisions();
    
    // Clean up dead objects
    cleanupObjects();
    
    // Power-up effects
    updatePowerEffects(dt);
}

function handleCollisions() {
    // Advanced collision handling
    // Player vs enemies (direct collision)
    var playerPos = player.position;
    var enemies = getObjectsByTag("enemy");
    
    for (var i = 0; i < enemies.length; i++) {
        var enemy = enemies[i];
        var enemyPos = enemy.position;
        var distance = Math.sqrt((playerPos.x - enemyPos.x) * (playerPos.x - enemyPos.x) + 
                               (playerPos.y - enemyPos.y) * (playerPos.y - enemyPos.y));
        
        if (distance < 40) { // Collision threshold
            // Damage both
            player.takeDamage(30);
            enemy.takeDamage(100);
        }
    }
}

function checkGameState() {
    // Check for win/lose conditions
    // Game over if player health <= 0
    if (player.health <= 0) {
        gameOver = true;
        return;
    }
    
    // Wave completion check handled in updateEnemySpawning
    
    // High score tracking
    if (score > getHighScore()) {
        setHighScore(score);
    }
}

function handleGameOver() {
    // Handle game over state
    console.log("🎮 Game Over! Final Score: " + score + ", Wave: " + wave);
    
    // Stop music
    stopMusic();
    
    // Play game over sound
    playSound("game_over");
    
    // Show game over screen (in full version this would be UI)
    alert("Game Over! Final Score: " + score);
}
```

## 🔨 Step 9: Build and Deployment in Studio

### Build Preparation

1. **Check assets:** Make sure all assets are properly imported
2. **Test game:** Run the game several times to verify stability
3. **Optimization:** Studio automatically optimizes during build

### Build Process

```bash
# Studio contains build_studio.py script
# Run from console or use Studio GUI

# Command line:
python build_studio.py --project "Cosmic_Defender"

# Studio GUI:
# Menu -> Build -> Create Executable
# Or Shift+F5
```

### Build Configuration

Studio creates `build_config.json`:

```json
{
    "project_name": "Cosmic Defender",
    "version": "1.0.0",
    "description": "Space shooter created in Axarion Studio",
    "icon": "favicon.png",
    "include_assets": true,
    "optimize_assets": true,
    "target_platforms": ["windows"],
    "executable_name": "CosmicDefender.exe",
    "build_settings": {
        "compression": true,
        "debug_info": false,
        "console_window": false
    }
}
```

### Automatic Optimizations

Studio during build:
- **Compresses assets** - PNG optimization, audio compression
- **Bundles dependencies** - includes only necessary libraries
- **Code minification** - removes unnecessary debug code
- **Asset atlas** - merges small textures for better performance

## 🚀 Step 10: Publishing and Sharing

### Deployment on Replit

```bash
# In Studio terminal or through deployment GUI
python build_studio.py --deploy replit

# Studio creates:
# - Optimized web version
# - Automatic deployment URL
# - Share link for community
```

### Local Distribution

Studio creates in `build/` folder:
```
build/
├── windows/
│   ├── CosmicDefender.exe      # Standalone executable
│   ├── assets/                 # Optimized assets
│   └── README.txt              # Instructions for users
├── web/
│   ├── index.html             # Web version
│   ├── game.js                # JavaScript port
│   └── assets/                # Web-optimized assets
└── source/
    ├── CosmicDefender.zip     # Source code package
    └── project_info.json     # Metadata
```

### Community Sharing

1. **GitHub integration:** Studio can push project to GitHub
2. **Axarion Gallery:** Publishing to Studio gallery
3. **Export template:** Creating template for other developers

## 🎉 Completion and Extensions

### What You Created

✅ **Complete space shooter** with professional effects  
✅ **Asset Management workflow** with drag & drop import  
✅ **Modern component system** with scripts  
✅ **Build system** for distribution  
✅ **Studio workflow** for rapid development  

### Possible Extensions

#### Easy Extensions (15-30 minutes):
- More power-up types (triple shot, shield, speed boost)
- Boss enemies with complex attack patterns
- Multiple levels with different backgrounds
- Achievement system

#### Medium Advanced (1-2 hours):
- Multiplayer cooperation
- Upgrade system between waves
- Custom soundtrack integration
- Mobile controls support

#### Advanced Projects (several hours):
- Level editor integrated in Studio
- Mod support for community
- AI-generated enemies
- Procedural level generation

### Professional Tips for Further Development

1. **Asset Organization:** Maintain clean Asset Manager structure
2. **Version Control:** Use Studio integration with Git
3. **Performance:** Monitor performance tools in Studio
4. **Community:** Share your projects in Axarion community
5. **Documentation:** Studio automatically generates documentation

---

**Congratulations! You've created a complete game in Axarion Studio!** 🎊

This tutorial demonstrated the power of modern game development workflow in Axarion Studio. The combination of visual tools with code flexibility makes game development fun and efficient.

**Axarion Studio - Where ideas become games!** 🎮✨
