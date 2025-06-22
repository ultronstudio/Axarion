"""
Axarion Engine Game Templates
Pre-built templates for different game genres
"""

from typing import Dict, List, Any
from .game_object import GameObject
from .scene import Scene

class GameTemplate:
    """Base class for game templates"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.required_objects = []
        self.default_scripts = {}
        self.settings = {}

    def create_scene(self, scene_name: str = "Main") -> Scene:
        """Create a scene with template objects"""
        scene = Scene(scene_name)

        # Add template objects
        for obj_data in self.required_objects:
            obj = GameObject(obj_data["name"], obj_data["type"])
            obj.position = obj_data["position"]

            # Set properties
            for key, value in obj_data.get("properties", {}).items():
                obj.set_property(key, value)

            # Set script
            if "script" in obj_data:
                obj.script_code = obj_data["script"]

            scene.add_object(obj)

        return scene

class PlatformerTemplate(GameTemplate):
    """Template for platformer games"""

    def __init__(self):
        super().__init__(
            "Platformer Game", 
            "Jumping and running game with gravity and platforms"
        )

        self.required_objects = [
            {
                "name": "Player",
                "type": "rectangle",
                "position": (100, 400),
                "properties": {
                    "width": 32,
                    "height": 48,
                    "color": (100, 150, 255),
                    "max_speed": 200,
                    "jump_force": 400
                },
                "script": """// Player movement with gravity
var speed = 200;
var jumpPower = 300;
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
    if (keyPressed("Space") && onGround) {
        var vel = getProperty("velocity");
        setProperty("velocity", vel);
        onGround = false;
    }

    // Simple ground detection
    var pos = getProperty("position");
    if (pos.y > 450) {
        var newPos = pos;
        newPos.y = 450;
        setProperty("position", newPos);
        onGround = true;
    }
}

function onCollision(other) {
    var otherName = getProperty("name");
    if (otherName == "Platform") {
        onGround = true;
    }
}"""
            },
            {
                "name": "Platform1",
                "type": "rectangle",
                "position": (200, 450),
                "properties": {
                    "width": 150,
                    "height": 20,
                    "color": (100, 100, 100)
                }
            },
            {
                "name": "Platform2",
                "type": "rectangle",
                "position": (400, 350),
                "properties": {
                    "width": 150,
                    "height": 20,
                    "color": (100, 100, 100)
                }
            },
            {
                "name": "Enemy",
                "type": "circle",
                "position": (300, 420),
                "properties": {
                    "radius": 16,
                    "color": (255, 100, 100)
                },
                "script": """// Simple enemy AI
var speed = 50;
var direction = 1;

function update() {
    // Simple back and forth movement
    move(speed * direction * 0.016, 0);

    // Bounce off edges
    var pos = getProperty("position");
    if (pos.x > 600 || pos.x < 200) {
        direction = -direction;
        setProperty("color", "255,150,150");
    }
}"""
            }
        ]

class ShooterTemplate(GameTemplate):
    """Template for shooter games"""

    def __init__(self):
        super().__init__(
            "Top-Down Shooter", 
            "Shoot enemies while avoiding their attacks"
        )

        self.required_objects = [
            {
                "name": "Player",
                "type": "rectangle",
                "position": (400, 500),
                "properties": {
                    "width": 24,
                    "height": 24,
                    "color": (100, 255, 100),
                    "health": 100,
                    "speed": 150
                },
                "script": """// Shooter Player Controller
var speed = 150;
var health = 100;
var shootTimer = 0;

function update() {
    // Movement
    var moveX = 0;
    var moveY = 0;

    if (keyPressed("left")) moveX = -1;
    if (keyPressed("right")) moveX = 1;
    if (keyPressed("up")) moveY = -1;
    if (keyPressed("down")) moveY = 1;

    move(moveX * speed * 0.016, moveY * speed * 0.016);

    // Shooting
    shootTimer -= 0.016;
    if (keyPressed("space") && shootTimer <= 0) {
        shoot();
        shootTimer = 0.2; // fire rate
    }

    // Keep player on screen
    var pos = this.position;
    if (pos.x < 0) setProperty("position", {x: 0, y: pos.y});
    if (pos.x > 800) setProperty("position", {x: 800, y: pos.y});
    if (pos.y < 0) setProperty("position", {x: pos.x, y: 0});
    if (pos.y > 600) setProperty("position", {x: pos.x, y: 600});
}

function shoot() {
    createBullet(this.position.x, this.position.y, 0, -1);
}

function createBullet(x, y, dirX, dirY) {
    // Placeholder for bullet creation
    print("Shooting bullet from " + x + ", " + y);
}

function keyPressed(key) {
    // Placeholder for input system
    return false;
}"""
            },
            {
                "name": "Enemy1",
                "type": "circle",
                "position": (200, 100),
                "properties": {
                    "radius": 15,
                    "color": (255, 100, 100),
                    "health": 50,
                    "speed": 80
                },
                "script": """// Enemy AI
var health = 50;
var speed = 80;
var shootTimer = 0;

function update() {
    // Move toward player (simple AI)
    var playerPos = findPlayer();
    if (playerPos) {
        var dx = playerPos.x - this.position.x;
        var dy = playerPos.y - this.position.y;
        var distance = sqrt(dx * dx + dy * dy);

        if (distance > 0) {
            move((dx / distance) * speed * 0.016, (dy / distance) * speed * 0.016);
        }

        // Shoot at player
        shootTimer -= 0.016;
        if (shootTimer <= 0) {
            shootAtPlayer(playerPos);
            shootTimer = 1.0;
        }
    }
}

function findPlayer() {
    // Placeholder - would find player object
    return {x: 400, y: 500};
}

function shootAtPlayer(playerPos) {
    print("Enemy shooting at player");
}"""
            }
        ]

class PuzzleTemplate(GameTemplate):
    """Template for puzzle games"""

    def __init__(self):
        super().__init__(
            "Match-3 Puzzle", 
            "Match three or more similar objects to clear them"
        )

        self.required_objects = [
            {
                "name": "GameBoard",
                "type": "rectangle",
                "position": (300, 200),
                "properties": {
                    "width": 200,
                    "height": 200,
                    "color": (50, 50, 50)
                },
                "script": """// Puzzle Game Manager
var gridSize = 8;
var cellSize = 25;
var selectedPiece = null;
var score = 0;

function update() {
    // Handle mouse input for piece selection
    if (mouseClicked()) {
        var mousePos = getMousePosition();
        handlePieceSelection(mousePos);
    }

    // Check for matches
    checkMatches();
}

function handlePieceSelection(mousePos) {
    var gridX = floor((mousePos.x - this.position.x) / cellSize);
    var gridY = floor((mousePos.y - this.position.y) / cellSize);

    if (gridX >= 0 && gridX < gridSize && gridY >= 0 && gridY < gridSize) {
        if (selectedPiece == null) {
            selectedPiece = {x: gridX, y: gridY};
            print("Selected piece at " + gridX + ", " + gridY);
        } else {
            // Try to swap pieces
            swapPieces(selectedPiece, {x: gridX, y: gridY});
            selectedPiece = null;
        }
    }
}

function swapPieces(piece1, piece2) {
    // Swap logic would go here
    print("Swapping pieces");
}

function checkMatches() {
    // Match detection logic would go here
}

function mouseClicked() {
    // Placeholder for mouse input
    return false;
}

function getMousePosition() {
    // Placeholder for mouse position
    return {x: 0, y: 0};
}"""
            },
            {
                "name": "PuzzlePiece",
                "type": "circle",
                "position": (350, 250),
                "properties": {
                    "radius": 12,
                    "color": (100, 100, 255)
                },
                "script": """// Puzzle piece logic
var color = "blue";
var matched = false;

function init() {
    print("Puzzle piece initialized");
    setProperty("color", "100,100,255");
}

function update() {
    // Simple color changing logic
    var pos = getProperty("position");
    if (pos.x > 300) {
        color = "green";
        setProperty("color", "100,255,100");
    }
}

function onClick() {
    matched = !matched;
    if (matched) {
        setProperty("color", "255,255,100");
        print("Piece matched!");
    } else {
        setProperty("color", "100,100,255");
    }
}"""
            }
        ]

class RPGTemplate(GameTemplate):
    """Template for RPG games"""

    def __init__(self):
        super().__init__(
            "RPG Adventure", 
            "Role-playing game with stats, inventory, and quests"
        )

        self.required_objects = [
            {
                "name": "Player",
                "type": "rectangle",
                "position": (400, 300),
                "properties": {
                    "width": 32,
                    "height": 32,
                    "color": (100, 150, 255),
                    "level": 1,
                    "hp": 100,
                    "mp": 50,
                    "exp": 0
                },
                "script": """// RPG Player Controller
var level = 1;
var hp = 100;
var maxHp = 100;
var mp = 50;
var maxMp = 50;
var exp = 0;
var speed = 100;

function update() {
    // Movement
    var moveX = 0;
    var moveY = 0;

    if (keyPressed("left")) moveX = -1;
    if (keyPressed("right")) moveX = 1;
    if (keyPressed("up")) moveY = -1;
    if (keyPressed("down")) moveY = 1;

    move(moveX * speed * 0.016, moveY * speed * 0.016);

    // Check for interactions
    if (keyPressed("space")) {
        interact();
    }

    // Update UI
    updateUI();
}

function interact() {
    // Check for nearby NPCs or objects
    print("Player interacting");
}

function gainExp(amount) {
    exp += amount;
    var expNeeded = level * 100;

    if (exp >= expNeeded) {
        levelUp();
    }
}

function levelUp() {
    level += 1;
    exp = 0;
    maxHp += 10;
    maxMp += 5;
    hp = maxHp; // full heal
    mp = maxMp;

    print("Level up! Now level " + level);
}

function updateUI() {
    // Update health/mana bars
}

function keyPressed(key) {
    // Placeholder for input system
    return false;
}"""
            },
            {
                "name": "NPC",
                "type": "circle",
                "position": (200, 200),
                "properties": {
                    "radius": 20,
                    "color": (255, 255, 100)
                },
                "script": """// NPC with dialog
var hasQuest = true;
var questCompleted = false;

function update() {
    // Check if player is nearby
    var player = findPlayer();
    if (player && distanceToPlayer(player) < 50) {
        showInteractionPrompt();
    }
}

function interact() {
    if (hasQuest && !questCompleted) {
        giveQuest();
    } else {
        showDialog("Hello, adventurer!");
    }
}

function giveQuest() {
    showDialog("Please collect 5 magic crystals for me!");
    hasQuest = false;
}

function showDialog(text) {
    print("NPC: " + text);
}

function findPlayer() {
    // Placeholder - would find player object
    return null;
}

function distanceToPlayer(player) {
    var dx = player.position.x - this.position.x;
    var dy = player.position.y - this.position.y;
    return sqrt(dx * dx + dy * dy);
}

function showInteractionPrompt() {
    // Show press E to interact
}"""
            }
        ]

class RacingTemplate(GameTemplate):
    """Template for racing games"""

    def __init__(self):
        super().__init__(
            "Racing Game", 
            "Race around tracks with realistic car physics"
        )

        self.required_objects = [
            {
                "name": "PlayerCar",
                "type": "rectangle",
                "position": (100, 300),
                "properties": {
                    "width": 40,
                    "height": 20,
                    "color": (255, 100, 100),
                    "max_speed": 300,
                    "acceleration": 200,
                    "turn_speed": 180
                },
                "script": """// Racing Car Controller
var maxSpeed = 300;
var acceleration = 200;
var turnSpeed = 180;
var currentLap = 0;
var lapTime = 0;

function update() {
    lapTime += 0.016;

    // Get input
    var throttle = 0;
    var steering = 0;

    if (keyPressed("up")) throttle = 1;
    if (keyPressed("down")) throttle = -0.5;
    if (keyPressed("left")) steering = -1;
    if (keyPressed("right")) steering = 1;

    // Apply car physics
    applyCarpysics(throttle, steering);

    // Check checkpoints
    checkCheckpoints();
}

function applyCarpysics(throttle, steering) {
    var vel = this.velocity;
    var speed = sqrt(vel.x * vel.x + vel.y * vel.y);

    // Apply throttle
    if (throttle != 0) {
        var forwardX = cos(this.rotation * PI / 180);
        var forwardY = sin(this.rotation * PI / 180);

        vel.x += forwardX * acceleration * throttle * 0.016;
        vel.y += forwardY * acceleration * throttle * 0.016;

        // Limit speed
        var newSpeed = sqrt(vel.x * vel.x + vel.y * vel.y);
        if (newSpeed > maxSpeed) {
            vel.x = (vel.x / newSpeed) * maxSpeed;
            vel.y = (vel.y / newSpeed) * maxSpeed;
        }
    }

    // Apply steering
    if (speed > 10 && steering != 0) {
        this.rotation += turnSpeed * steering * (speed / maxSpeed) * 0.016;
    }

    // Apply friction
    vel.x *= 0.98;
    vel.y *= 0.98;

    setProperty("velocity", vel);
    move(vel.x * 0.016, vel.y * 0.016);
}

function checkCheckpoints() {
    // Check if passed through checkpoint
    // Implementation would check distance to checkpoint markers
}

function completeLap() {
    currentLap += 1;
    print("Lap " + currentLap + " completed in " + lapTime + " seconds");
    lapTime = 0;
}

function keyPressed(key) {
    // Placeholder for input system
    return false;
}"""
            },
            {
                "name": "Checkpoint1",
                "type": "circle",
                "position": (400, 100),
                "properties": {
                    "radius": 30,
                    "color": (255, 255, 0),
                    "checkpoint_id": 1
                }
            },
            {
                "name": "Checkpoint2",
                "type": "circle",
                "position": (700, 300),
                "properties": {
                    "radius": 30,
                    "color": (255, 255, 0),
                    "checkpoint_id": 2
                }
            },
            {
                "name": "Finish",
                "type": "rectangle",
                "position": (50, 250),
                "properties": {
                    "width": 100,
                    "height": 10,
                    "color": (0, 255, 0)
                }
            }
        ]

# Template registry
GAME_TEMPLATES = {
    "platformer": PlatformerTemplate(),
    "shooter": ShooterTemplate(),
    "puzzle": PuzzleTemplate(),
    "rpg": RPGTemplate(),
    "racing": RacingTemplate()
}

def get_template(template_name: str) -> GameTemplate:
    """Get a game template by name"""
    return GAME_TEMPLATES.get(template_name)

def get_available_templates() -> List[str]:
    """Get list of available template names"""
    return list(GAME_TEMPLATES.keys())

def create_template_scene(template_name: str, scene_name: str = "Main") -> Scene:
    """Create a scene from a template"""
    template = get_template(template_name)
    if template:
        return template.create_scene(scene_name)
    return None