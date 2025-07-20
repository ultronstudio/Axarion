
# 🚀 Getting Started with Axarion Studio

Welcome to Axarion Studio - a professional development environment for creating 2D games! This guide will help you create your first game in just a few minutes, even if you're a complete beginner in programming or game development.

## 🎯 What is Axarion Studio?

Axarion Studio is a **complete development environment** combining an advanced code editor with a powerful 2D game engine. Unlike complex tools like Unity or Godot, Axarion Studio focuses on simplicity and rapid development.

### 🚀 Key Features of Axarion Studio:
- **Modern dark interface** with gradient effects and purple-blue theme
- **Integrated Asset Manager** with access to Asset Store
- **Syntax highlighting** with IntelliSense
- **Instant testing** - run your game with one click
- **Project management** with automatic saving
- **Drag & Drop import** of assets directly into projects
- **Automatic compilation** of games into standalone EXE files

## ⚡ Quick Start (5 minutes to your first game!)

### Step 1: Launch Axarion Studio

Start Axarion Studio:

```bash
python axarion_studio.py
```

You'll see a modern dark environment with a purple-blue theme. This is your new development environment!

### Step 2: Create a New Project

1. Click **"New Project"**
2. Enter project name (e.g., "My First Game")
3. Studio automatically creates project structure with:
   - Main game file
   - Asset folders (images, sounds)
   - Configuration files

### Step 3: Understanding the Studio Interface

**Main Areas:**
- **Code Editor** (center) - where you write code
- **Project Explorer** (left) - file management
- **Properties** (right) - object settings
- **Asset Manager** - image, sound, animation management
- **Console** (bottom) - output and errors

### Step 4: Your First Code

Studio creates a basic template:

```javascript
/*
My First Game - Axarion Engine

Created in Axarion Studio
*/

// Create game engine
var engine = createEngine(800, 600);
engine.initialize();

// Create scene
var scene = engine.createScene("My Scene");
engine.currentScene = scene;

// Create player
var player = createGameObject("Player", "rectangle");
player.position = {x: 100, y: 100};
player.width = 50;
player.height = 50;
player.color = {r: 100, g: 200, b: 255};

// Add movement controls
player.update = function() {
    var speed = 200;
    
    // Movement using arrow keys
    if (keyPressed("ArrowLeft")) {
        this.position.x -= speed * deltaTime();
    }
    if (keyPressed("ArrowRight")) {
        this.position.x += speed * deltaTime();
    }
    if (keyPressed("ArrowUp")) {
        this.position.y -= speed * deltaTime();
    }
    if (keyPressed("ArrowDown")) {
        this.position.y += speed * deltaTime();
    }
};

// Add player to scene
scene.addObject(player);

// Start the game!
engine.run();
```

### Step 5: Running the Game

Simply press **F5** or click the **"Run"** button. Your game will start immediately!

## 🎨 New Asset Manager

### Importing Assets

Axarion Studio has a revolutionary asset import system:

1. **Drag & Drop Import:**
   - Drag images directly into Asset Manager
   - Automatically copied to correct folders
   - Immediately available in code

2. **Asset Store Integration:**
   - Thousands of free assets
   - One-click downloads
   - Automatic categorization

3. **Smart Detection:**
   - Studio automatically recognizes file types
   - Creates image previews
   - Optimizes for game use

### Using Assets in Code

```javascript
// Load all assets
loadAssets();

// Use an image
player.sprite = "ship"; // Uses ship.png from Asset Manager

// Play sound
if (keyPressed("Space")) {
    playSound("laser"); // Plays laser.wav
}
```

## 🎮 New Coding Features

### IntelliSense and Code Completion

Studio provides:
- **Automatic completion** of functions and variables
- **Context help** for functions
- **Real-time error highlighting**
- **Code snippets** for common tasks

### Modern Debugging

```javascript
// Use print() for debug output
print("Player position: " + player.position.x + ", " + player.position.y);

// Check for errors in real-time
function update() {
    var pos = getProperty("position");
    print("X: " + pos.x + ", Y: " + pos.y);
}
```

### Live Reload

Studio automatically:
- **Saves changes** while typing
- **Detects errors** immediately
- **Reloads assets** when changed

## 🏗️ Project Structure in Axarion Studio

```
My_Game/
├── game.js              # Main game file
├── project.json         # Project configuration
├── assets/              # Assets
│   ├── images/          # Images, sprites
│   ├── sounds/          # Sound effects, music
│   ├── animations/      # Animations
│   └── fonts/           # Fonts
├── scenes/              # Game scenes
├── scripts/             # Script files
└── build/               # Built EXE files
```

## 🎯 Creating a Complete Game - Step by Step

### 1. Asset Preparation

**Importing Images:**
1. Open Asset Manager (folder icon)
2. Drag PNG files into "Images" section
3. Studio automatically optimizes them

**Adding Sounds:**
1. Drag WAV/MP3 files
2. Test sounds directly in Asset Manager
3. Use in code with one line

### 2. Creating Game Objects

```javascript
// Modern way of creating objects
var engine = createEngine(1024, 768);
engine.initialize();

// Scene with environment
var scene = engine.createScene("Level1");
scene.setBackgroundColor(20, 30, 80); // Dark blue
scene.setGravity(0, 400); // Gravity for platforms

// Player with sprite
var player = createGameObject("Player", "sprite");
player.position = {x: 100, y: 500};
player.sprite = "hero"; // Automatically finds hero.png
player.addTag("player");

// Modern controls with better functions
player.update = function() {
    var speed = 250;
    var jumpForce = 500;
    var health = 100;
    
    handleMovement();
    handleCombat();
    checkCollisions();
    
    function handleMovement() {
        // Smooth movement
        if (keyPressed("a") || keyPressed("ArrowLeft")) {
            applyForce(-speed, 0);
        }
        if (keyPressed("d") || keyPressed("ArrowRight")) {
            applyForce(speed, 0);
        }
        
        // Jump only on ground
        if (keyJustPressed("w") || keyJustPressed("Space")) {
            if (isOnGround()) {
                applyForce(0, -jumpForce);
                playSound("jump");
            }
        }
    }
    
    function handleCombat() {
        if (keyJustPressed("x")) {
            attack();
            playSound("sword");
        }
    }
    
    function checkCollisions() {
        var enemies = findObjectsByTag("enemy");
        for (var i = 0; i < enemies.length; i++) {
            if (isCollidingWith(enemies[i].name)) {
                takeDamage(10);
                createEffect("hit", getProperty("position"));
            }
        }
    }
};

scene.addObject(player);
```

### 3. Adding Enemies and Logic

```javascript
// Create enemy with AI
var enemy = createGameObject("Enemy1", "sprite");
enemy.position = {x: 400, y: 500};
enemy.sprite = "skeleton";
enemy.addTag("enemy");

enemy.update = function() {
    var speed = 100;
    var health = 50;
    var attackCooldown = 0;
    
    attackCooldown -= deltaTime();
    
    // AI - track player
    var player = findObjectByName("Player");
    if (player) {
        var playerPos = player.getProperty("position");
        var myPos = getProperty("position");
        
        // Move towards player
        if (distance(myPos.x, myPos.y, playerPos.x, playerPos.y) > 50) {
            moveTowards(playerPos.x, playerPos.y, speed);
        } else if (attackCooldown <= 0) {
            attack();
            attackCooldown = 2.0;
        }
    }
};

scene.addObject(enemy);
```

## 🎨 Advanced Studio Features

### Visual Scripting Support

Studio supports hybrid approach:
- **Game logic** code
- **Object behavior** scripts
- **Visual nodes** for complex interactions (coming soon)

### Asset Store Integration

```javascript
// Direct download from Store
downloadPack("Medieval Knight Pack");
downloadPack("8-bit Sound Effects");

// Automatically available in code
player.sprite = "knight_idle";
```

### Automatic Building

Studio can create standalone EXE:

1. **Menu → Build → Create Executable**
2. Studio automatically:
   - Packages all assets
   - Creates EXE file
   - Adds application icon
   - Optimizes file size

## 🔧 Tips for Efficient Development

### 1. Use Code Snippets

Studio contains pre-made blocks:
- `player_movement` - basic controls
- `collision_detection` - collision detection
- `sound_system` - sound effects
- `particle_effects` - visual effects

### 2. Real-time Preview

Changes appear immediately:
- Edit code → automatic save
- Change asset → instant reload
- Syntax error → immediate warning

### 3. Project Templates

Studio offers ready templates:
- **Platformer** - jumping game
- **Top-down Shooter** - bird's eye view shooter
- **Puzzle Game** - logic game
- **RPG Template** - RPG basics

## 🐛 Debugging and Troubleshooting

### Integrated Debugging Tools

```javascript
// Activate debug mode
engine.debugMode = true;

// Show collision boxes
scene.showCollisionBounds = true;

// Performance monitoring
engine.showFPS = true;
```

### Common Problems and Solutions

| Problem | Solution |
|---------|----------|
| Object doesn't move | Check if it has `update()` function |
| Image doesn't display | Verify path in Asset Manager |
| Sound doesn't play | Check file format (WAV recommended) |
| Game is slow | Reduce object count or use object pooling |

### Console Output

Studio shows detailed information:
```
✅ Engine initialized (800x600)
✅ Loaded sprite: hero (32x48)
✅ Scene created: Level1
🎵 Playing sound: background_music
⚠️ Warning: Object outside screen bounds
❌ Error: Sprite 'missing_image' not found
```

## 🎉 Completion and Sharing

### Project Export

Studio allows several export methods:

1. **Standalone EXE** - for Windows
2. **Web build** - for browsers
3. **Project package** - for sharing with others

### Publishing on Replit

```bash
# Automatic deployment
python build_studio.py --deploy
```

Studio creates:
- Optimized code
- Compressed assets
- Automatic deployment on Replit

## 🚀 What's Next?

### Advanced Features to Explore:

1. **Particle systems** - explosions, fire, smoke
2. **Animation system** - smooth transitions
3. **Physics system** - realistic physics
4. **Tile mapping** - level creation
5. **Save/Load system** - progress saving

### Examples of Advanced Games:

Check out completed projects in `Projects/` folder:
- **Space Defender** - complete shooter
- **Platform Adventure** - Mario-style platformer
- **Puzzle Quest** - logic game

## 🏆 Advantages of Axarion Studio

### Compared to Traditional Editors:
- **Faster learning** - intuitive interface
- **Immediate results** - no compilation
- **All-in-one** - editor + engine + assets
- **Modern workflow** - Git integration, cloud sync

### Compared to Large Engines:
- **Simpler** - no complex setup
- **Faster** - instant project startup
- **2D focused** - optimized for pixel art games
- **Beginner friendly** - ideal for learning

---

**Welcome to the future of 2D game development with Axarion Studio!** 🎮✨

*Axarion Studio - Professional tools for every developer*
