
"""
Axarion Engine Genre Examples
Complete game examples for different genres
"""

from engine.core import AxarionEngine
from engine.game_object import GameObject
from engine.scene import Scene

def create_platformer_game():
    """Create a complete platformer game"""
    engine = AxarionEngine(800, 600)
    engine.initialize()
    
    # Create main scene
    scene = engine.create_scene("Platformer")
    engine.current_scene = scene
    
    # Create player
    player = GameObject("Player", "rectangle")
    player.position = (100, 400)
    player.set_property("width", 32)
    player.set_property("height", 48)
    player.set_property("color", (100, 150, 255))
    player.add_tag("player")
    
    player.script_code = """
var speed = 200;
var jumpPower = 400;
var onGround = false;
var coyoteTime = 0.1;
var coyoteTimer = 0;

function update() {
    // Horizontal movement
    var movement = getMovement();
    if (movement.x != 0) {
        move(movement.x * speed * 0.016, 0);
    }
    
    // Coyote time for better jumping
    if (isOnGround()) {
        onGround = true;
        coyoteTimer = coyoteTime;
    } else {
        onGround = false;
        coyoteTimer -= 0.016;
    }
    
    // Jumping with coyote time
    if (keyJustPressed("Space") && coyoteTimer > 0) {
        jump(jumpPower);
        coyoteTimer = 0;
    }
    
    // Collect coins
    var colliding = getCollidingObjects();
    for (var i = 0; i < colliding.length; i++) {
        var obj = findObjectByName(colliding[i]);
        if (obj && hasTag("coin", obj)) {
            destroy(obj);
            setGlobal("score", getGlobal("score", 0) + 10);
            playSound("coin_collect");
        }
    }
}
"""
    
    # Create platforms
    platforms = [
        (0, 550, 800, 50),      # Ground
        (200, 450, 150, 20),    # Platform 1
        (400, 350, 150, 20),    # Platform 2
        (600, 250, 150, 20),    # Platform 3
    ]
    
    for i, (x, y, w, h) in enumerate(platforms):
        platform = GameObject(f"Platform_{i}", "rectangle")
        platform.position = (x, y)
        platform.set_property("width", w)
        platform.set_property("height", h)
        platform.set_property("color", (100, 100, 100))
        platform.add_tag("platform")
        platform.is_static = True
        scene.add_object(platform)
    
    # Create collectible coins
    coin_positions = [(250, 400), (450, 300), (650, 200), (750, 500)]
    
    for i, (x, y) in enumerate(coin_positions):
        coin = GameObject(f"Coin_{i}", "circle")
        coin.position = (x, y)
        coin.set_property("radius", 15)
        coin.set_property("color", (255, 255, 0))
        coin.add_tag("coin")
        
        coin.script_code = """
var rotationSpeed = 2;
var bobHeight = 5;
var time = 0;

function update() {
    time += 0.016;
    
    // Rotate coin
    rotate(rotationSpeed);
    
    // Bob up and down
    var pos = getProperty("position");
    var baseY = 400; // Original Y position
    var newY = baseY + sin(time * 3) * bobHeight;
    setProperty("position", {x: pos.x, y: newY});
}
"""
        scene.add_object(coin)
    
    scene.add_object(player)
    return engine

def create_rpg_game():
    """Create RPG game with stats, inventory, and quests"""
    engine = AxarionEngine(800, 600)
    engine.initialize()
    
    scene = engine.create_scene("RPG_Town")
    engine.current_scene = scene
    
    # Create player character
    player = GameObject("Hero", "rectangle")
    player.position = (400, 300)
    player.set_property("width", 32)
    player.set_property("height", 32)
    player.set_property("color", (0, 120, 255))
    player.add_tag("player")
    
    # Set RPG stats
    player.health = 100
    player.max_health = 100
    player.level = 1
    player.experience = 0
    player.stats = {"strength": 10, "defense": 5, "magic": 8}
    
    player.script_code = """
var speed = 150;
var inCombat = false;

function update() {
    if (!inCombat) {
        // Movement
        var movement = getMovement();
        move(movement.x * speed * 0.016, movement.y * speed * 0.016);
        
        // Check for NPCs
        if (keyJustPressed("e")) {
            var npcs = findObjectsByTag("npc");
            for (var i = 0; i < npcs.length; i++) {
                var npc = npcs[i];
                if (distance(getProperty("position").x, getProperty("position").y,
                           npc.position.x, npc.position.y) < 50) {
                    // Start dialogue
                    emitEvent("start_dialogue", npc.name);
                }
            }
        }
    }
}

function takeDamage(amount) {
    var actualDamage = max(1, amount - getStat("defense"));
    setProperty("health", getProperty("health") - actualDamage);
    
    if (getProperty("health") <= 0) {
        // Game over
        emitEvent("player_died");
    }
}
"""
    
    # Create NPCs
    npc_data = [
        ("Merchant", (200, 200), "Hello traveler! I have wares for sale."),
        ("Guard", (600, 400), "Keep the peace, citizen."),
        ("Quest_Giver", (100, 500), "I need your help with the goblins!")
    ]
    
    for name, pos, dialogue in npc_data:
        npc = GameObject(name, "rectangle")
        npc.position = pos
        npc.set_property("width", 32)
        npc.set_property("height", 32)
        npc.set_property("color", (150, 100, 50))
        npc.add_tag("npc")
        npc.set_property("dialogue", dialogue)
        
        npc.script_code = f"""
var originalPos = getProperty("position");
var time = 0;

function update() {{
    time += 0.016;
    
    // Idle animation
    var bobAmount = sin(time * 2) * 2;
    setProperty("position", {{x: originalPos.x, y: originalPos.y + bobAmount}});
    
    // Face player when nearby
    var player = findObjectByName("Hero");
    if (player) {{
        var dist = distance(getProperty("position").x, getProperty("position").y,
                          player.position.x, player.position.y);
        if (dist < 80) {{
            lookAt(player.position.x, player.position.y);
        }}
    }}
}}
"""
        scene.add_object(npc)
    
    # Create enemies
    enemy_positions = [(300, 100), (500, 150), (700, 300)]
    
    for i, pos in enumerate(enemy_positions):
        enemy = GameObject(f"Goblin_{i}", "triangle")
        enemy.position = pos
        enemy.set_property("size", 25)
        enemy.set_property("color", (150, 0, 0))
        enemy.add_tag("enemy")
        enemy.health = 30
        enemy.damage = 15
        
        enemy.script_code = """
var speed = 50;
var attackRange = 40;
var detectionRange = 100;
var lastAttackTime = 0;
var attackCooldown = 2.0;

function update() {
    var player = findObjectByName("Hero");
    if (!player) return;
    
    var dist = distance(getProperty("position").x, getProperty("position").y,
                       player.position.x, player.position.y);
    
    if (dist <= detectionRange) {
        if (dist <= attackRange) {
            // Attack player
            if (time() - lastAttackTime >= attackCooldown) {
                player.takeDamage(getProperty("damage"));
                lastAttackTime = time();
            }
        } else {
            // Move towards player
            moveTowards(player.position.x, player.position.y, speed);
        }
    }
}
"""
        scene.add_object(enemy)
    
    scene.add_object(player)
    return engine

def create_shooter_game():
    """Create top-down shooter game"""
    engine = AxarionEngine(800, 600)
    engine.initialize()
    
    scene = engine.create_scene("Shooter_Arena")
    engine.current_scene = scene
    
    # Create player
    player = GameObject("Player", "triangle")
    player.position = (400, 300)
    player.set_property("size", 20)
    player.set_property("color", (0, 255, 0))
    player.add_tag("player")
    player.health = 100
    
    player.script_code = """
var speed = 200;
var fireRate = 0.2;
var lastShotTime = 0;

function update() {
    // Movement
    var movement = getMovement();
    move(movement.x * speed * 0.016, movement.y * speed * 0.016);
    
    // Rotation based on mouse
    var mouse = getMousePos();
    lookAt(mouse.x, mouse.y);
    
    // Shooting
    if (mousePressed(0) && time() - lastShotTime >= fireRate) {
        var pos = getProperty("position");
        createBullet(mouse.x, mouse.y, 500);
        lastShotTime = time();
        playSound("shoot");
    }
    
    // Check bullet collisions
    var bullets = findObjectsByTag("bullet");
    for (var i = 0; i < bullets.length; i++) {
        var bullet = bullets[i];
        var enemies = findObjectsByTag("enemy");
        
        for (var j = 0; j < enemies.length; j++) {
            var enemy = enemies[j];
            if (isCollidingWith(bullet, enemy)) {
                enemy.takeDamage(25);
                destroy(bullet);
                break;
            }
        }
    }
}
"""
    
    # Create enemies that spawn periodically
    enemy_spawner = GameObject("EnemySpawner", "rectangle")
    enemy_spawner.position = (0, 0)
    enemy_spawner.visible = False
    
    enemy_spawner.script_code = """
var spawnRate = 2.0;
var lastSpawnTime = 0;
var enemyCount = 0;

function update() {
    if (time() - lastSpawnTime >= spawnRate) {
        spawnEnemy();
        lastSpawnTime = time();
    }
}

function spawnEnemy() {
    // Spawn at random edge position
    var side = floor(random() * 4);
    var x, y;
    
    switch(side) {
        case 0: // Top
            x = random() * 800;
            y = -20;
            break;
        case 1: // Right
            x = 820;
            y = random() * 600;
            break;
        case 2: // Bottom
            x = random() * 800;
            y = 620;
            break;
        case 3: // Left
            x = -20;
            y = random() * 600;
            break;
    }
    
    var enemy = instantiate("circle", x, y);
    enemy.addTag("enemy");
    enemy.setProperty("radius", 15);
    enemy.setProperty("color", "255,0,0");
    enemy.setProperty("health", 50);
    enemy.setProperty("speed", 80);
    
    // Simple AI: move towards player
    enemy.script_code = `
var speed = getProperty("speed");
var health = getProperty("health");

function update() {
    var player = findObjectByName("Player");
    if (player) {
        moveTowards(player.position.x, player.position.y, speed);
        
        // Damage player on contact
        if (isCollidingWith("Player")) {
            player.takeDamage(10);
            destroy();
        }
    }
}

function takeDamage(amount) {
    health -= amount;
    setProperty("health", health);
    
    if (health <= 0) {
        createExplosion(getProperty("position").x, getProperty("position").y);
        setGlobal("score", getGlobal("score", 0) + 100);
        destroy();
    }
}
`;
}
"""
    
    scene.add_object(enemy_spawner)
    scene.add_object(player)
    return engine

def create_puzzle_game():
    """Create match-3 puzzle game"""
    engine = AxarionEngine(800, 600)
    engine.initialize()
    
    scene = engine.create_scene("Puzzle_Game")
    engine.current_scene = scene
    
    # Create game manager
    game_manager = GameObject("GameManager", "rectangle")
    game_manager.position = (0, 0)
    game_manager.visible = False
    
    game_manager.script_code = """
var gridWidth = 8;
var gridHeight = 8;
var tileSize = 60;
var colors = ["255,0,0", "0,255,0", "0,0,255", "255,255,0", "255,0,255"];
var selectedTile = null;
var score = 0;

function start() {
    createGrid();
    setGlobal("score", 0);
}

function createGrid() {
    for (var x = 0; x < gridWidth; x++) {
        for (var y = 0; y < gridHeight; y++) {
            createTile(x, y);
        }
    }
}

function createTile(gridX, gridY) {
    var worldX = 100 + gridX * tileSize;
    var worldY = 100 + gridY * tileSize;
    
    var tile = instantiate("rectangle", worldX, worldY);
    tile.setProperty("width", tileSize - 2);
    tile.setProperty("height", tileSize - 2);
    tile.addTag("tile");
    tile.setProperty("gridX", gridX);
    tile.setProperty("gridY", gridY);
    
    // Random color
    var colorIndex = floor(random() * colors.length);
    tile.setProperty("color", colors[colorIndex]);
    tile.setProperty("colorIndex", colorIndex);
    
    tile.script_code = `
function onMouseClick() {
    var manager = findObjectByName("GameManager");
    if (manager.selectedTile == null) {
        // Select this tile
        manager.selectedTile = this;
        setProperty("color", "255,255,255"); // Highlight
    } else {
        // Try to swap with selected tile
        if (manager.canSwap(manager.selectedTile, this)) {
            manager.swapTiles(manager.selectedTile, this);
            manager.checkMatches();
        }
        
        // Deselect
        manager.selectedTile.setProperty("color", manager.colors[manager.selectedTile.getProperty("colorIndex")]);
        manager.selectedTile = null;
    }
}
`;
}

function canSwap(tile1, tile2) {
    var dx = abs(tile1.getProperty("gridX") - tile2.getProperty("gridX"));
    var dy = abs(tile1.getProperty("gridY") - tile2.getProperty("gridY"));
    
    return (dx == 1 && dy == 0) || (dx == 0 && dy == 1);
}

function swapTiles(tile1, tile2) {
    var color1 = tile1.getProperty("colorIndex");
    var color2 = tile2.getProperty("colorIndex");
    
    tile1.setProperty("colorIndex", color2);
    tile1.setProperty("color", colors[color2]);
    
    tile2.setProperty("colorIndex", color1);
    tile2.setProperty("color", colors[color1]);
}

function checkMatches() {
    // Simple match-3 detection (horizontal only for demo)
    var tiles = findObjectsByTag("tile");
    var matches = [];
    
    for (var y = 0; y < gridHeight; y++) {
        var count = 1;
        var currentColor = -1;
        
        for (var x = 0; x < gridWidth; x++) {
            var tile = getTileAt(x, y);
            if (tile) {
                var color = tile.getProperty("colorIndex");
                
                if (color == currentColor) {
                    count++;
                } else {
                    if (count >= 3) {
                        // Mark previous tiles for removal
                        for (var i = 0; i < count; i++) {
                            var matchTile = getTileAt(x - 1 - i, y);
                            if (matchTile) matches.push(matchTile);
                        }
                    }
                    count = 1;
                    currentColor = color;
                }
            }
        }
        
        // Check end of row
        if (count >= 3) {
            for (var i = 0; i < count; i++) {
                var matchTile = getTileAt(gridWidth - 1 - i, y);
                if (matchTile) matches.push(matchTile);
            }
        }
    }
    
    // Remove matches and add score
    for (var i = 0; i < matches.length; i++) {
        destroy(matches[i]);
        score += 10;
        setGlobal("score", score);
    }
    
    if (matches.length > 0) {
        // Trigger gravity and refill
        setTimeout(function() { refillGrid(); }, 0.5);
    }
}

function getTileAt(gridX, gridY) {
    var tiles = findObjectsByTag("tile");
    for (var i = 0; i < tiles.length; i++) {
        var tile = tiles[i];
        if (tile.getProperty("gridX") == gridX && tile.getProperty("gridY") == gridY) {
            return tile;
        }
    }
    return null;
}

function refillGrid() {
    // Simple refill - just create new tiles where missing
    for (var x = 0; x < gridWidth; x++) {
        for (var y = 0; y < gridHeight; y++) {
            if (!getTileAt(x, y)) {
                createTile(x, y);
            }
        }
    }
}

// Start the game
start();
"""
    
    scene.add_object(game_manager)
    return engine

def create_racing_game():
    """Create simple racing game"""
    engine = AxarionEngine(800, 600)
    engine.initialize()
    
    scene = engine.create_scene("Racing_Track")
    engine.current_scene = scene
    
    # Create player car
    car = GameObject("PlayerCar", "rectangle")
    car.position = (100, 300)
    car.set_property("width", 40)
    car.set_property("height", 20)
    car.set_property("color", (255, 0, 0))
    car.add_tag("player")
    
    car.script_code = """
var maxSpeed = 300;
var acceleration = 200;
var turnSpeed = 120;
var friction = 0.95;
var currentSpeed = 0;

function update() {
    // Get input
    var throttle = 0;
    var steering = 0;
    
    if (keyPressed("ArrowUp") || keyPressed("w")) throttle = 1;
    if (keyPressed("ArrowDown") || keyPressed("s")) throttle = -0.5;
    if (keyPressed("ArrowLeft") || keyPressed("a")) steering = -1;
    if (keyPressed("ArrowRight") || keyPressed("d")) steering = 1;
    
    // Apply throttle
    if (throttle != 0) {
        currentSpeed += throttle * acceleration * 0.016;
        currentSpeed = clamp(currentSpeed, -maxSpeed * 0.5, maxSpeed);
    }
    
    // Apply friction
    currentSpeed *= friction;
    
    // Apply steering (only when moving)
    if (abs(currentSpeed) > 10 && steering != 0) {
        var turnAmount = steering * turnSpeed * (abs(currentSpeed) / maxSpeed) * 0.016;
        rotate(turnAmount);
    }
    
    // Move forward based on rotation
    var radians = getProperty("rotation") * PI / 180;
    var moveX = cos(radians) * currentSpeed * 0.016;
    var moveY = sin(radians) * currentSpeed * 0.016;
    
    move(moveX, moveY);
    
    // Keep in bounds
    var pos = getProperty("position");
    if (pos.x < 0 || pos.x > 800 || pos.y < 0 || pos.y > 600) {
        currentSpeed *= 0.5; // Bounce off walls
    }
}
"""
    
    # Create AI cars
    ai_positions = [(200, 200), (300, 400), (500, 150)]
    
    for i, pos in enumerate(ai_positions):
        ai_car = GameObject(f"AICar_{i}", "rectangle")
        ai_car.position = pos
        ai_car.set_property("width", 40)
        ai_car.set_property("height", 20)
        ai_car.set_property("color", (0, 0, 255))
        ai_car.add_tag("ai_car")
        
        ai_car.script_code = f"""
var speed = 150;
var waypoints = [
    {{x: 100, y: 100}}, {{x: 700, y: 100}},
    {{x: 700, y: 500}}, {{x: 100, y: 500}}
];
var currentWaypoint = {i % 4};
var waypointRadius = 50;

function update() {{
    var target = waypoints[currentWaypoint];
    var pos = getProperty("position");
    
    // Calculate distance to waypoint
    var dist = distance(pos.x, pos.y, target.x, target.y);
    
    if (dist < waypointRadius) {{
        // Move to next waypoint
        currentWaypoint = (currentWaypoint + 1) % waypoints.length;
        target = waypoints[currentWaypoint];
    }}
    
    // Look at target and move
    lookAt(target.x, target.y);
    moveTowards(target.x, target.y, speed);
}}
"""
        scene.add_object(ai_car)
    
    scene.add_object(car)
    return engine

# Export functions for easy access
GENRE_EXAMPLES = {
    "platformer": create_platformer_game,
    "rpg": create_rpg_game,
    "shooter": create_shooter_game,
    "puzzle": create_puzzle_game,
    "racing": create_racing_game
}
