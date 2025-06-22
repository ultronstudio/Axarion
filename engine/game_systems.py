"""
Axarion Engine Game Systems
Specialized systems for different game genres
"""

import math
import random
from typing import Dict, List, Tuple, Any, Optional
from .game_object import GameObject

class PlatformerSystem:
    """System for platformer games with gravity, jumping, and collisions"""
    
    def __init__(self):
        self.gravity = 980.0  # pixels/second^2
        self.jump_force = -400.0  # negative for upward
        self.ground_friction = 0.8
        self.air_friction = 0.95
        self.max_fall_speed = 600.0
        
    def apply_platformer_physics(self, player: GameObject, platforms: List[GameObject], delta_time: float):
        """Apply platformer physics to player"""
        # Apply gravity
        vel_x, vel_y = player.velocity
        vel_y += self.gravity * delta_time
        
        # Limit fall speed
        if vel_y > self.max_fall_speed:
            vel_y = self.max_fall_speed
        
        # Apply friction
        if self.is_on_ground(player, platforms):
            vel_x *= self.ground_friction
        else:
            vel_x *= self.air_friction
        
        # Update position
        pos_x, pos_y = player.position
        new_x = pos_x + vel_x * delta_time
        new_y = pos_y + vel_y * delta_time
        
        # Check collisions
        player.velocity = (vel_x, vel_y)
        player.position = (new_x, new_y)
        
        self.handle_platform_collisions(player, platforms)
    
    def jump(self, player: GameObject, platforms: List[GameObject]):
        """Make player jump if on ground"""
        if self.is_on_ground(player, platforms):
            vel_x, vel_y = player.velocity
            player.velocity = (vel_x, self.jump_force)
    
    def is_on_ground(self, player: GameObject, platforms: List[GameObject]) -> bool:
        """Check if player is on ground"""
        player_bounds = player.get_bounds()
        
        for platform in platforms:
            platform_bounds = platform.get_bounds()
            
            # Check if player is standing on platform
            if (player_bounds[0] < platform_bounds[2] and 
                player_bounds[2] > platform_bounds[0] and
                abs(player_bounds[3] - platform_bounds[1]) < 5):
                return True
        
        return False
    
    def handle_platform_collisions(self, player: GameObject, platforms: List[GameObject]):
        """Handle collisions with platforms"""
        player_bounds = player.get_bounds()
        
        for platform in platforms:
            platform_bounds = platform.get_bounds()
            
            # Check collision
            if (player_bounds[0] < platform_bounds[2] and 
                player_bounds[2] > platform_bounds[0] and
                player_bounds[1] < platform_bounds[3] and 
                player_bounds[3] > platform_bounds[1]):
                
                # Resolve collision
                vel_x, vel_y = player.velocity
                
                # Top collision (landing on platform)
                if vel_y > 0 and player_bounds[3] - platform_bounds[1] < 10:
                    player.position = (player.position[0], platform_bounds[1] - (player_bounds[3] - player_bounds[1]))
                    player.velocity = (vel_x, 0)
                
                # Bottom collision (hitting platform from below)
                elif vel_y < 0 and platform_bounds[3] - player_bounds[1] < 10:
                    player.position = (player.position[0], platform_bounds[3])
                    player.velocity = (vel_x, 0)

class RPGSystem:
    """System for RPG games with stats, inventory, and turn-based combat"""
    
    def __init__(self):
        self.characters = {}
        self.items = {}
        self.dialogs = {}
        
    def create_character(self, name: str, stats: Dict[str, int]) -> Dict[str, Any]:
        """Create RPG character with stats"""
        character = {
            "name": name,
            "level": 1,
            "exp": 0,
            "hp": stats.get("hp", 100),
            "max_hp": stats.get("hp", 100),
            "mp": stats.get("mp", 50),
            "max_mp": stats.get("mp", 50),
            "attack": stats.get("attack", 10),
            "defense": stats.get("defense", 5),
            "speed": stats.get("speed", 10),
            "inventory": [],
            "equipment": {},
            "skills": []
        }
        self.characters[name] = character
        return character
    
    def add_item(self, character_name: str, item_name: str, quantity: int = 1):
        """Add item to character inventory"""
        if character_name in self.characters:
            inventory = self.characters[character_name]["inventory"]
            
            # Check if item already exists
            for item in inventory:
                if item["name"] == item_name:
                    item["quantity"] += quantity
                    return
            
            # Add new item
            inventory.append({"name": item_name, "quantity": quantity})
    
    def calculate_damage(self, attacker: Dict[str, Any], defender: Dict[str, Any]) -> int:
        """Calculate damage in combat"""
        base_damage = attacker["attack"]
        defense = defender["defense"]
        
        # Add some randomness
        damage = max(1, base_damage - defense + random.randint(-5, 5))
        return damage
    
    def gain_exp(self, character_name: str, exp: int):
        """Give experience to character"""
        if character_name in self.characters:
            char = self.characters[character_name]
            char["exp"] += exp
            
            # Check for level up
            exp_needed = char["level"] * 100
            if char["exp"] >= exp_needed:
                char["level"] += 1
                char["exp"] -= exp_needed
                
                # Increase stats
                char["max_hp"] += 10
                char["max_mp"] += 5
                char["attack"] += 2
                char["defense"] += 1
                char["hp"] = char["max_hp"]  # Full heal on level up

class ShooterSystem:
    """System for shooter games with bullets, enemies, and weapons"""
    
    def __init__(self):
        self.bullets = []
        self.enemies = []
        self.weapons = {
            "pistol": {"damage": 10, "fire_rate": 0.5, "bullet_speed": 400},
            "rifle": {"damage": 15, "fire_rate": 0.3, "bullet_speed": 600},
            "shotgun": {"damage": 25, "fire_rate": 1.0, "bullet_speed": 300}
        }
        
    def create_bullet(self, start_x: float, start_y: float, 
                     target_x: float, target_y: float, weapon: str) -> GameObject:
        """Create bullet object"""
        bullet = GameObject("Bullet", "circle")
        bullet.position = (start_x, start_y)
        bullet.set_property("radius", 3)
        bullet.set_property("color", (255, 255, 0))
        
        # Calculate velocity
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            speed = self.weapons[weapon]["bullet_speed"]
            bullet.velocity = ((dx / distance) * speed, (dy / distance) * speed)
        
        bullet.set_property("damage", self.weapons[weapon]["damage"])
        bullet.set_property("weapon", weapon)
        
        self.bullets.append(bullet)
        return bullet
    
    def update_bullets(self, delta_time: float, scene_bounds: Tuple[float, float, float, float]):
        """Update all bullets"""
        bullets_to_remove = []
        
        for bullet in self.bullets:
            bullet.update(delta_time)
            
            # Remove bullets that are out of bounds
            x, y = bullet.position
            if (x < scene_bounds[0] or x > scene_bounds[2] or 
                y < scene_bounds[1] or y > scene_bounds[3]):
                bullets_to_remove.append(bullet)
        
        for bullet in bullets_to_remove:
            self.bullets.remove(bullet)
    
    def check_bullet_hits(self, targets: List[GameObject]) -> List[Tuple[GameObject, GameObject]]:
        """Check bullet collisions with targets"""
        hits = []
        bullets_to_remove = []
        
        for bullet in self.bullets:
            bullet_bounds = bullet.get_bounds()
            
            for target in targets:
                target_bounds = target.get_bounds()
                
                # Check collision
                if (bullet_bounds[0] < target_bounds[2] and 
                    bullet_bounds[2] > target_bounds[0] and
                    bullet_bounds[1] < target_bounds[3] and 
                    bullet_bounds[3] > target_bounds[1]):
                    
                    hits.append((bullet, target))
                    bullets_to_remove.append(bullet)
                    break
        
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)
        
        return hits

class PuzzleSystem:
    """System for puzzle games with grid-based mechanics"""
    
    def __init__(self, grid_width: int, grid_height: int):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid = [[None for _ in range(grid_width)] for _ in range(grid_height)]
        self.cell_size = 32
        
    def world_to_grid(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to grid coordinates"""
        grid_x = int(world_x // self.cell_size)
        grid_y = int(world_y // self.cell_size)
        return (grid_x, grid_y)
    
    def grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """Convert grid coordinates to world coordinates"""
        world_x = grid_x * self.cell_size
        world_y = grid_y * self.cell_size
        return (world_x, world_y)
    
    def place_object(self, obj: GameObject, grid_x: int, grid_y: int) -> bool:
        """Place object on grid"""
        if (0 <= grid_x < self.grid_width and 
            0 <= grid_y < self.grid_height and 
            self.grid[grid_y][grid_x] is None):
            
            self.grid[grid_y][grid_x] = obj
            world_x, world_y = self.grid_to_world(grid_x, grid_y)
            obj.position = (world_x, world_y)
            return True
        
        return False
    
    def move_object(self, grid_x: int, grid_y: int, new_x: int, new_y: int) -> bool:
        """Move object on grid"""
        if (0 <= grid_x < self.grid_width and 
            0 <= grid_y < self.grid_height and
            0 <= new_x < self.grid_width and 
            0 <= new_y < self.grid_height and
            self.grid[grid_y][grid_x] is not None and
            self.grid[new_y][new_x] is None):
            
            obj = self.grid[grid_y][grid_x]
            self.grid[grid_y][grid_x] = None
            self.grid[new_y][new_x] = obj
            
            world_x, world_y = self.grid_to_world(new_x, new_y)
            obj.position = (world_x, world_y)
            return True
        
        return False
    
    def check_match_three(self) -> List[Tuple[int, int]]:
        """Check for match-3 patterns"""
        matches = []
        
        # Check horizontal matches
        for y in range(self.grid_height):
            count = 1
            current_type = None
            
            for x in range(self.grid_width):
                obj = self.grid[y][x]
                obj_type = obj.object_type if obj else None
                
                if obj_type == current_type and obj_type is not None:
                    count += 1
                else:
                    if count >= 3 and current_type is not None:
                        for i in range(count):
                            matches.append((x - 1 - i, y))
                    count = 1
                    current_type = obj_type
            
            # Check end of row
            if count >= 3 and current_type is not None:
                for i in range(count):
                    matches.append((self.grid_width - 1 - i, y))
        
        # Check vertical matches
        for x in range(self.grid_width):
            count = 1
            current_type = None
            
            for y in range(self.grid_height):
                obj = self.grid[y][x]
                obj_type = obj.object_type if obj else None
                
                if obj_type == current_type and obj_type is not None:
                    count += 1
                else:
                    if count >= 3 and current_type is not None:
                        for i in range(count):
                            matches.append((x, y - 1 - i))
                    count = 1
                    current_type = obj_type
            
            # Check end of column
            if count >= 3 and current_type is not None:
                for i in range(count):
                    matches.append((x, self.grid_height - 1 - i))
        
        return list(set(matches))  # Remove duplicates

class RacingSystem:
    """System for racing games with tracks and lap timing"""
    
    def __init__(self):
        self.checkpoints = []
        self.lap_times = {}
        self.current_laps = {}
        
    def add_checkpoint(self, x: float, y: float, radius: float = 50):
        """Add checkpoint to track"""
        checkpoint = {
            "position": (x, y),
            "radius": radius,
            "id": len(self.checkpoints)
        }
        self.checkpoints.append(checkpoint)
    
    def check_checkpoint(self, car: GameObject, car_id: str) -> Optional[int]:
        """Check if car passed through checkpoint"""
        car_x, car_y = car.position
        
        if car_id not in self.current_laps:
            self.current_laps[car_id] = {"current_checkpoint": 0, "start_time": 0, "lap_count": 0}
        
        current_checkpoint = self.current_laps[car_id]["current_checkpoint"]
        
        if current_checkpoint < len(self.checkpoints):
            checkpoint = self.checkpoints[current_checkpoint]
            cp_x, cp_y = checkpoint["position"]
            
            # Check distance to checkpoint
            distance = math.sqrt((car_x - cp_x) ** 2 + (car_y - cp_y) ** 2)
            
            if distance <= checkpoint["radius"]:
                self.current_laps[car_id]["current_checkpoint"] += 1
                
                # Check if completed lap
                if current_checkpoint == len(self.checkpoints) - 1:
                    self.current_laps[car_id]["current_checkpoint"] = 0
                    self.current_laps[car_id]["lap_count"] += 1
                    return self.current_laps[car_id]["lap_count"]
                
                return current_checkpoint + 1
        
        return None
    
    def apply_car_physics(self, car: GameObject, input_throttle: float, input_steering: float, delta_time: float):
        """Apply realistic car physics"""
        # Get current velocity
        vel_x, vel_y = car.velocity
        current_speed = math.sqrt(vel_x * vel_x + vel_y * vel_y)
        
        # Car properties
        max_speed = car.get_property("max_speed", 300)
        acceleration = car.get_property("acceleration", 200)
        turn_speed = car.get_property("turn_speed", 180)
        friction = car.get_property("friction", 0.95)
        
        # Apply throttle
        if input_throttle != 0:
            # Calculate forward direction
            rotation = car.rotation
            forward_x = math.cos(math.radians(rotation))
            forward_y = math.sin(math.radians(rotation))
            
            # Apply acceleration
            accel_force = acceleration * input_throttle * delta_time
            vel_x += forward_x * accel_force
            vel_y += forward_y * accel_force
            
            # Limit max speed
            speed = math.sqrt(vel_x * vel_x + vel_y * vel_y)
            if speed > max_speed:
                vel_x = (vel_x / speed) * max_speed
                vel_y = (vel_y / speed) * max_speed
        
        # Apply steering (only when moving)
        if current_speed > 10 and input_steering != 0:
            rotation_change = turn_speed * input_steering * (current_speed / max_speed) * delta_time
            car.rotation += rotation_change
        
        # Apply friction
        vel_x *= friction
        vel_y *= friction
        
        # Update velocity and position
        car.velocity = (vel_x, vel_y)
        car.update(delta_time)