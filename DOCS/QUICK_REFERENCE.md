
# 🚀 Axarion Studio - Quick Reference

**Professional Development Environment for 2D Games**

This is a practical reference for common tasks and code patterns in Axarion Studio. Perfect for quick lookup during development in the most modern 2D game studio!

## 🎯 Axarion Studio - Controls

### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New project |
| `Ctrl+O` | Open project |
| `Ctrl+S` | Save file |
| `F5` | Run game |
| `Shift+F5` | Build EXE |
| `Ctrl+Shift+A` | Open Asset Manager |
| `Ctrl+F` | Find in code |
| `Ctrl+/` | Comment/uncomment |
| `F11` | Editor fullscreen |

### Panels and Windows
- **Project Explorer** - file and folder management
- **Asset Manager** - asset import and management
- **Properties Panel** - object properties
- **Console Output** - debug and error messages
- **Code Editor** - main editor with IntelliSense

## 🎮 Basic Game Setup

### Minimal Template in Axarion Studio
```javascript
// Engine with automatic configuration
var engine = createEngine(800, 600);
engine.initialize();

// Create scene through Studio API
var scene = engine.createScene("GameScene");
engine.currentScene = scene;

// Object with Asset Manager integration
var player = createGameObject("Player", "sprite");
player.position = {x: 100, y: 100};
player.sprite = "player_sprite"; // Automatically found in Asset Manager

// Controls with IntelliSense support
player.update = function() {
    var speed = 200;
    
    handleInput();
    updateAnimation();
    
    function handleInput() {
        if (keyPressed("ArrowLeft")) move(-speed * deltaTime(), 0);
        if (keyPressed("ArrowRight")) move(speed * deltaTime(), 0);
        if (keyPressed("ArrowUp")) move(0, -speed * deltaTime());
        if (keyPressed("ArrowDown")) move(0, speed * deltaTime());
    }
};

scene.addObject(player);
engine.run();
```

## 🎨 Asset Manager - New Features

### Asset Import
```javascript
// Automatic loading of all assets
loadAssets();

// Access assets from Studio
var sprite = getImage("hero_walk");
var sound = getSound("sword_hit");
var animation = getAnimation("explosion");
```

### Asset Store Integration
```javascript
// Direct download from Store (in Asset Manager)
downloadPack("Pixel Adventure Pack");
player.sprite = "pixel_hero"; // Immediately available
```

### Drag & Drop Workflow
```javascript
// After dragging into Asset Manager:
// 1. Files are automatically copied
// 2. Previews are created
// 3. Available in code under filename

// Example: dragging "spaceship.png"
var ship = createGameObject("Ship", "sprite");
ship.sprite = "spaceship"; // Automatically found
```

## 🕹️ Modern Input System

### Enhanced Controls
```javascript
// Better input handling
function update() {
    // Classic keys
    if (keyPressed("Space")) shoot();
    if (keyJustPressed("Enter")) interact();
    if (keyReleased("Shift")) stopRunning();
    
    // Key combinations
    if (keyPressed("Ctrl") && keyJustPressed("z")) undo();
    
    // Gamepad support
    if (gamepadPressed(0, "A")) jump();
    if (gamepadAxis(0, "leftStick") > 0.5) moveRight();
}

// Advanced mouse handling
function handleMouse() {
    var mousePos = getMousePosition();
    var worldPos = screenToWorld(mousePos.x, mousePos.y);
    
    if (mouseJustPressed("left")) {
        shootAt(worldPos.x, worldPos.y);
    }
    
    if (mouseDragged()) {
        var drag = getMouseDelta();
        moveCamera(drag.x, drag.y);
    }
}
```

## 🎯 GameObject Types in Studio

### Supported Types
| Type | Description | Studio Features |
|------|-------------|-----------------|
| `"sprite"` | Image/texture | Live preview, auto-resize |
| `"animated_sprite"` | Animated frames | Timeline editor, loop control |
| `"rectangle"` | Colored rectangle | Color picker, gradient fill |
| `"circle"` | Colored circle | Radius slider, outline options |
| `"text"` | Text object | Font selector, rich formatting |
| `"particle_system"` | Particle system | Visual particle editor |

### Advanced Objects
```javascript
// Particle system through Studio
var particles = createGameObject("Explosion", "particle_system");
particles.position = {x: 200, y: 200};
particles.setParticleConfig({
    count: 100,
    lifetime: 2.0,
    speed: 200,
    colorStart: {r: 255, g: 255, b: 0},
    colorEnd: {r: 255, g: 0, b: 0},
    sizeStart: 5,
    sizeEnd: 1
});

// Text objects with fonts from Asset Manager
var text = createGameObject("ScoreText", "text");
text.setFont("pixel_font", 24); // From Asset Manager
text.text = "Score: 1000";
text.color = {r: 255, g: 255, b: 255};
```

## 🏃 Movement and Physics

### Physics System
```javascript
// Modern physics
function initPhysics() {
    setProperty("mass", 1.0);
    setProperty("friction", 0.8);
    setProperty("bounce", 0.3);
    setProperty("gravityScale", 1.0);
}

function update() {
    // Force-based movement
    var moveForce = 500;
    if (keyPressed("a")) applyForce(-moveForce, 0);
    if (keyPressed("d")) applyForce(moveForce, 0);
    
    // Impulse jump
    if (keyJustPressed("w") && isGrounded()) {
        applyImpulse(0, -800);
        playSound("jump");
    }
    
    // Air control
    if (!isGrounded()) {
        var airControl = 0.2;
        if (keyPressed("a")) applyForce(-moveForce * airControl, 0);
        if (keyPressed("d")) applyForce(moveForce * airControl, 0);
    }
}
```

### Advanced Platformer
```javascript
var playerController = {
    speed: 300,
    jumpForce: 600,
    airControl: 0.3,
    coyoteTime: 0.1,
    jumpBuffer: 0.1
};

function update() {
    handleMovement();
    handleJumping();
    updateAnimations();
}

function handleMovement() {
    var input = getHorizontalInput(); // -1, 0, or 1
    var targetSpeed = input * playerController.speed;
    var speedDiff = targetSpeed - getVelocity().x;
    
    var acceleration = isGrounded() ? 10 : 5; // Faster acceleration on ground
    applyForce(speedDiff * acceleration, 0);
}

function handleJumping() {
    if (keyJustPressed("Space")) {
        if (canJump()) {
            jump();
        } else {
            bufferJump(); // Jump buffering
        }
    }
    
    // Variable jump height
    if (keyReleased("Space") && getVelocity().y < 0) {
        var vel = getVelocity();
        setVelocity(vel.x, vel.y * 0.5); // Shorter jump
    }
}
```

## 💥 Collision Detection in Studio

### Modern Collisions
```javascript
// Collision layers (set in Studio)
function setupCollisions() {
    setCollisionLayer("player");
    setCollisionMask(["enemies", "pickups", "platforms"]);
}

function update() {
    // Advanced collision detection
    var collisions = getDetailedCollisions();
    
    for (var i = 0; i < collisions.length; i++) {
        var collision = collisions[i];
        handleCollision(collision.object, collision.normal, collision.point);
    }
}

function handleCollision(other, normal, point) {
    if (other.hasTag("enemy")) {
        takeDamage(other.getDamage());
        createHitEffect(point.x, point.y);
        playSound("hurt");
        
        // Knockback
        var knockback = 300;
        applyImpulse(normal.x * knockback, normal.y * knockback);
    }
    
    if (other.hasTag("pickup")) {
        other.collect();
        playSound("coin");
        addScore(100);
    }
}
```

### Trigger Zones
```javascript
// Invisible trigger objects
function onTriggerEnter(other) {
    if (other.hasTag("player")) {
        showDialog("Welcome to new area!");
        playMusic("area_theme");
    }
}

function onTriggerExit(other) {
    if (other.hasTag("player")) {
        hideDialog();
        stopMusic();
    }
}
```

## 🔊 Audio System in Studio

### Advanced Sound
```javascript
// 3D positional audio
function playPositionalSound(soundName, x, y, volume, pitch) {
    var distance = distanceToPlayer(x, y);
    var adjustedVolume = volume * (1.0 - distance / 500.0); // Fade with distance
    
    playSound(soundName, {
        volume: adjustedVolume,
        pitch: pitch,
        position: {x: x, y: y}
    });
}

// Audio mixing
function setupAudio() {
    setMasterVolume(1.0);
    setMusicVolume(0.7);
    setSFXVolume(0.8);
    setVoiceVolume(1.0);
}

// Dynamic music
function updateMusic() {
    var playerHealth = getProperty("health");
    
    if (playerHealth < 30) {
        playMusic("tension_theme", 0.5); // Fade in over 0.5s
    } else {
        playMusic("normal_theme", 1.0);
    }
}
```

## 🎨 Visual Effects

### Particle Systems
```javascript
// Create effect in Studio
var explosionEffect = createGameObject("Explosion", "particle_system");
explosionEffect.setParticleConfig({
    texture: "spark", // From Asset Manager
    count: 50,
    lifetime: 1.5,
    spawnRate: 100,
    speedMin: 100,
    speedMax: 300,
    directionMin: 0,
    directionMax: 360,
    sizeStart: 3,
    sizeEnd: 0,
    colorStart: {r: 255, g: 255, b: 100},
    colorEnd: {r: 255, g: 0, b: 0},
    alphaStart: 1.0,
    alphaEnd: 0.0
});
```

### Screen Effects
```javascript
// Camera shake
function createExplosion(x, y) {
    // Particles
    createParticleEffect("explosion", x, y);
    
    // Screen shake
    shakeCamera(0.5, 10); // 0.5s duration, 10 pixel intensity
    
    // Flash effect
    flashScreen(255, 255, 255, 0.1); // White flash for 0.1s
    
    // Slow motion
    setTimeScale(0.3, 0.2); // 30% speed for 0.2s
}

// Post-processing effects
function applyVisualEffects() {
    if (playerInWater()) {
        setScreenTint(100, 150, 255, 0.3); // Blue tint
        setScreenBlur(2.0);
    } else {
        clearScreenEffects();
    }
}
```

## 🧮 Utility Functions in Studio

### Extended Mathematical Functions
```javascript
// Vector operations
function vectorAdd(v1, v2) {
    return {x: v1.x + v2.x, y: v1.y + v2.y};
}

function vectorLength(v) {
    return Math.sqrt(v.x * v.x + v.y * v.y);
}

function vectorNormalize(v) {
    var len = vectorLength(v);
    return {x: v.x / len, y: v.y / len};
}

// Smoothing functions
function smoothStep(edge0, edge1, x) {
    var t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
    return t * t * (3.0 - 2.0 * t);
}

function easeInOut(t) {
    return t < 0.5 ? 2*t*t : -1+(4-2*t)*t;
}
```

### Time and Tweening
```javascript
// Tween system
var tween = createTween();
tween.to({x: 300, y: 200}, 2.0)  // 2 seconds
     .ease("easeInOutQuad")
     .onComplete(function() {
         playSound("arrival");
     });

// Timer system
var timer = createTimer(3.0, function() {
    spawnEnemy();
}, true); // true = repeat

// Coroutine system
function* moveSequence() {
    yield moveTo(100, 100, 1.0);
    yield wait(0.5);
    yield moveTo(200, 100, 1.0);
    yield playAnimation("victory");
}
```

## 🎯 Design Patterns for Studio

### Component System
```javascript
// Components for game objects
function HealthComponent(maxHealth) {
    this.maxHealth = maxHealth || 100;
    this.currentHealth = this.maxHealth;
    
    this.takeDamage = function(amount) {
        this.currentHealth -= amount;
        if (this.currentHealth <= 0) {
            this.die();
        }
    };
    
    this.die = function() {
        // Trigger death sequence
    };
}

function MovementComponent(speed) {
    this.speed = speed || 100;
    this.velocity = {x: 0, y: 0};
    
    this.update = function(dt) {
        // Apply movement logic
    };
}

// Usage in GameObject
var player = createGameObject("Player", "sprite");
player.addComponent(new HealthComponent(100));
player.addComponent(new MovementComponent(200));
```

### State Machine
```javascript
// Finite State Machine
var stateMachine = {
    currentState: "idle",
    states: {
        "idle": {
            enter: function() { playAnimation("idle"); },
            update: function() { 
                if (keyPressed("ArrowRight")) {
                    stateMachine.changeState("walking");
                }
                if (keyJustPressed("Space")) {
                    stateMachine.changeState("jumping");
                }
            },
            exit: function() { }
        },
        "walking": {
            enter: function() { playAnimation("walk"); },
            update: function() {
                move(200 * deltaTime(), 0);
                if (!keyPressed("ArrowRight")) {
                    stateMachine.changeState("idle");
                }
            },
            exit: function() { }
        }
    },
    
    changeState: function(newState) {
        this.states[this.currentState].exit();
        this.currentState = newState;
        this.states[this.currentState].enter();
    }
};
```

## 🔧 Studio Optimization

### Performance Tips
```javascript
// Object pooling for bullets
function BulletPool(size) {
    this.bullets = [];
    this.size = size || 50;
    
    for (var i = 0; i < this.size; i++) {
        var bullet = createGameObject("Bullet_" + i, "sprite");
        bullet.active = false;
        this.bullets.push(bullet);
    }
    
    this.getBullet = function() {
        for (var i = 0; i < this.bullets.length; i++) {
            if (!this.bullets[i].active) {
                this.bullets[i].active = true;
                return this.bullets[i];
            }
        }
        return null;
    };
    
    this.returnBullet = function(bullet) {
        bullet.active = false;
        bullet.position = {x: -100, y: -100}; // Off screen
    };
}
```

### Batch Rendering
```javascript
// Group draw calls
function optimizeRendering() {
    // Sort objects by texture
    sortObjectsByTexture();
    
    // Batch draw similar objects
    drawBatch("enemy_sprites");
    drawBatch("particle_effects");
    
    // Cull off-screen objects
    cullOffscreenObjects();
}
```

## 📁 Project Structure in Studio

### Modern Organization
```
MyGame/
├── game.js                 # Entry point
├── project.json           # Studio configuration
├── scenes/                # Game scenes
│   ├── menu.js           # Main menu
│   ├── level1.js         # First level
│   └── boss_fight.js     # Boss scene
├── scripts/              # Script files
│   ├── player.js         # Player logic
│   ├── enemy_ai.js       # Enemy AI
│   └── ui_manager.js     # UI handling
├── components/           # Reusable components
│   ├── health.js
│   ├── movement.js
│   └── inventory.js
├── assets/              # Asset Manager folders
│   ├── images/          # Automatically managed
│   ├── sounds/          # Drag & drop import
│   ├── music/           # Background tracks
│   └── fonts/           # Fonts
└── build/              # Built outputs
    ├── windows/        # EXE for Windows
    ├── web/           # HTML5 export
    └── mobile/        # Mobile builds
```

## ⚡ Studio Workflow Tips

### Rapid Development
1. **Live Coding** - changes appear immediately
2. **Asset Hot-reload** - drag new asset → immediately available
3. **Quick Play** - F5 runs game without compilation
4. **Error Highlights** - errors highlighted in editor
5. **IntelliSense** - automatic code completion

### Debugging Workflow
```javascript
// Studio debug functions
if (engine.debugMode) {
    // Show collision bounds
    scene.showCollisionBounds = true;
    
    // FPS counter
    engine.showPerformance = true;
    
    // Object inspector
    engine.showObjectInfo = true;
    
    // Console commands
    console.registerCommand("teleport", teleportPlayer);
    console.registerCommand("giveItem", giveItem);
    console.registerCommand("killAll", killAllEnemies);
}
```

## 🎉 Export and Distribution

### Build System
```bash
# Build through Studio GUI or command line
python build_studio.py

# Build options:
# --windows      - Windows EXE
# --web          - HTML5/WebGL
# --steam        - Steam package
# --mobile       - Android APK (coming soon)
```

### Automatic Build Optimizations
- **Asset compression** - automatic file reduction
- **Code minification** - code size reduction
- **Texture atlas** - merge small textures
- **Audio compression** - optimize audio files
- **Dependency bundling** - package all dependencies

---

**This reference covers 95% of what you need to know for developing in Axarion Studio!**

*For advanced features, check the full documentation or use the built-in help system in Studio (F1).*

**Axarion Studio - The future of 2D game development is here!** 🎮✨
