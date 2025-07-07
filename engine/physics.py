"""
SnowFox Engine Physics System
Basic 2D physics simulation
"""

import math
from typing import Dict, List, Tuple, Optional
from .game_object import GameObject

class PhysicsSystem:
    """Basic 2D physics system for the engine"""

    def __init__(self):
        self.gravity: Tuple[float, float] = (0.0, 800.0)  # pixels/second^2
        self.enabled = True
        self.collision_enabled = True

        # Physics constants
        self.min_velocity = 0.5  # Minimum velocity threshold
        self.restitution = 0.3  # Bounce factor
        self.air_resistance = 0.98  # Air resistance factor

        # Collision layers
        self.collision_layers: Dict[str, List[GameObject]] = {}

        # World bounds
        self.world_bounds = (0, 0, 800, 600)  # left, top, right, bottom
        self.constrain_to_world = True

        # UNLIMITED PHYSICS FEATURES
        self.unlimited_mode = True
        self.advanced_collision = True
        self.fluid_dynamics = False
        self.soft_body_physics = False
        self.cloth_simulation = False
        self.particle_physics = True

        # Genre-specific physics
        self.platformer_physics = {"coyote_time": 0.1, "jump_buffer": 0.1}
        self.racing_physics = {"friction_curves": True, "aerodynamics": True}
        self.shooter_physics = {"bullet_physics": True, "ballistics": True}
        self.rpg_physics = {"turn_based_mode": False, "grid_movement": False}

        # Advanced features
        self.physics_materials = {}
        self.joint_systems = []
        self.force_fields = []
        self.magnetic_fields = []
        self.gravity_wells = []

    def update(self, delta_time: float):
        """Update physics simulation"""
        if not self.enabled:
            return

        # Physics updates are handled in GameObject.update_physics()
        # This method handles global physics effects and cleanup

        # Clean up collision layers
        for layer_name in self.collision_layers:
            self.collision_layers[layer_name] = [
                obj for obj in self.collision_layers[layer_name] 
                if obj.active and not obj.destroyed
            ]

    def apply_gravity(self, game_object: GameObject, delta_time: float):
        """Apply gravity to a game object"""
        if not self.enabled or game_object.is_static or game_object.gravity_scale <= 0:
            return

        gx, gy = self.gravity
        ax, ay = game_object.acceleration

        # Add gravity to acceleration
        game_object.acceleration = (
            ax + gx * game_object.gravity_scale,
            ay + gy * game_object.gravity_scale
        )

    def check_collision(self, obj1: GameObject, obj2: GameObject) -> bool:
        """Check if two objects are colliding"""
        if not self.collision_enabled:
            return False

        if not obj1.collision_enabled or not obj2.collision_enabled:
            return False

        if obj1 == obj2:
            return False

        return obj1.is_colliding_with(obj2)

    def resolve_collision(self, obj1: GameObject, obj2: GameObject, delta_time: float):
        """Resolve collision between two objects"""
        if not self.check_collision(obj1, obj2):
            return

        bounds1 = obj1.get_bounds()
        bounds2 = obj2.get_bounds()

        # Calculate overlap
        overlap_x = min(bounds1[2], bounds2[2]) - max(bounds1[0], bounds2[0])
        overlap_y = min(bounds1[3], bounds2[3]) - max(bounds1[1], bounds2[1])

        if overlap_x <= 0 or overlap_y <= 0:
            return

        # Calculate centers
        center1_x = (bounds1[0] + bounds1[2]) / 2
        center1_y = (bounds1[1] + bounds1[3]) / 2
        center2_x = (bounds2[0] + bounds2[2]) / 2
        center2_y = (bounds2[1] + bounds2[3]) / 2

        # Determine collision direction and separate objects
        if overlap_x < overlap_y:
            # Horizontal collision
            separation = overlap_x / 2
            if center1_x < center2_x:
                # obj1 is left of obj2
                if not obj1.is_static:
                    obj1.position = (obj1.position[0] - separation, obj1.position[1])
                    obj1.velocity = (-abs(obj1.velocity[0]) * obj1.bounce * 0.5, obj1.velocity[1])
                if not obj2.is_static:
                    obj2.position = (obj2.position[0] + separation, obj2.position[1])
                    obj2.velocity = (abs(obj2.velocity[0]) * obj2.bounce * 0.5, obj2.velocity[1])
            else:
                # obj1 is right of obj2
                if not obj1.is_static:
                    obj1.position = (obj1.position[0] + separation, obj1.position[1])
                    obj1.velocity = (abs(obj1.velocity[0]) * obj1.bounce * 0.5, obj1.velocity[1])
                if not obj2.is_static:
                    obj2.position = (obj2.position[0] - separation, obj2.position[1])
                    obj2.velocity = (-abs(obj2.velocity[0]) * obj2.bounce * 0.5, obj2.velocity[1])
        else:
            # Vertical collision
            separation = overlap_y / 2
            if center1_y < center2_y:
                # obj1 is above obj2 (landing on platform)
                if not obj1.is_static:
                    obj1.position = (obj1.position[0], obj1.position[1] - separation)
                    # Stop falling completely and enable ground flag
                    if obj1.velocity[1] > 10:  # Only if falling with significant speed
                        obj1.velocity = (obj1.velocity[0] * 0.8, 0)  # Stop vertical movement
                        obj1._on_ground = True
                    else:
                        obj1.velocity = (obj1.velocity[0], min(0, obj1.velocity[1]))
                if not obj2.is_static:
                    obj2.position = (obj2.position[0], obj2.position[1] + separation)
                    obj2.velocity = (obj2.velocity[0], abs(obj2.velocity[1]) * obj2.bounce * 0.3)
            else:
                # obj1 is below obj2 (hitting from below)
                if not obj1.is_static:
                    obj1.position = (obj1.position[0], obj1.position[1] + separation)
                    obj1.velocity = (obj1.velocity[0], abs(obj1.velocity[1]) * obj1.bounce * 0.5)
                if not obj2.is_static:
                    obj2.position = (obj2.position[0], obj2.position[1] - separation)
                    obj2.velocity = (obj2.velocity[0], -abs(obj2.velocity[1]) * obj2.bounce * 0.5)

    def check_all_collisions(self, objects: List[GameObject], delta_time: float):
        """Optimalized collision detection using spatial partitioning"""
        if not self.collision_enabled:
            return

        active_objects = [obj for obj in objects if obj.active and not obj.destroyed and obj.collision_enabled]

        # NOVÁ OPTIMALIZACE: Použij spatial grid pro kolize
        if hasattr(self, 'spatial_grid') and len(active_objects) > 20:
            self._check_collisions_spatial_grid(active_objects, delta_time)
        else:
            # Původní metoda pro menší počet objektů
            for i, obj1 in enumerate(active_objects):
                for j, obj2 in enumerate(active_objects[i+1:], i+1):
                    if self.check_collision(obj1, obj2):
                        self.resolve_collision(obj1, obj2, delta_time)

    def _check_collisions_spatial_grid(self, objects: List[GameObject], delta_time: float):
        """Rychlá detekce kolizí pomocí prostorové mřížky"""
        grid_size = 64
        grid = {}

        # Rozděl objekty do grid
        for obj in objects:
            bounds = obj.get_bounds()
            grid_x = int(bounds[0] // grid_size)
            grid_y = int(bounds[1] // grid_size)

            # Objekt může být ve více cells
            for gx in range(grid_x, int(bounds[2] // grid_size) + 1):
                for gy in range(grid_y, int(bounds[3] // grid_size) + 1):
                    key = f"{gx},{gy}"
                    if key not in grid:
                        grid[key] = []
                    grid[key].append(obj)

        # Zkontroluj kolize pouze v rámci stejných cells
        checked_pairs = set()
        for cell_objects in grid.values():
            for i, obj1 in enumerate(cell_objects):
                for j, obj2 in enumerate(cell_objects[i+1:], i+1):
                    pair = (id(obj1), id(obj2))
                    if pair not in checked_pairs:
                        checked_pairs.add(pair)
                        if self.check_collision(obj1, obj2):
                            self.resolve_collision(obj1, obj2, delta_time)

    def check_bounds_collision(self, game_object: GameObject, 
                              bounds: Tuple[float, float, float, float] = None) -> bool:
        """Check if object is colliding with bounds"""
        if bounds is None:
            bounds = self.world_bounds

        obj_bounds = game_object.get_bounds()
        min_x, min_y, max_x, max_y = bounds

        return (obj_bounds[0] < min_x or obj_bounds[2] > max_x or
                obj_bounds[1] < min_y or obj_bounds[3] > max_y)

    def constrain_to_bounds(self, game_object: GameObject, 
                           bounds: Tuple[float, float, float, float] = None):
        """Constrain object to bounds"""
        if not self.constrain_to_world:
            return

        if bounds is None:
            bounds = self.world_bounds

        obj_bounds = game_object.get_bounds()
        min_x, min_y, max_x, max_y = bounds
        x, y = game_object.position

        obj_width = obj_bounds[2] - obj_bounds[0]
        obj_height = obj_bounds[3] - obj_bounds[1]

        # Calculate new position
        new_x = x
        new_y = y

        # Check horizontal bounds
        if obj_bounds[0] < min_x:
            new_x = min_x
        elif obj_bounds[2] > max_x:
            new_x = max_x - obj_width

        # Check vertical bounds
        if obj_bounds[1] < min_y:
            new_y = min_y
        elif obj_bounds[3] > max_y:
            new_y = max_y - obj_height

        # Apply position changes and velocity corrections
        vx, vy = game_object.velocity

        if new_x != x:
            game_object.velocity = (-vx * self.restitution, vy)
        if new_y != y:
            game_object.velocity = (vx, -vy * self.restitution)

        game_object.position = (new_x, new_y)

    def apply_force(self, game_object: GameObject, force_x: float, force_y: float):
        """Apply force to game object"""
        if game_object.mass <= 0 or game_object.is_static:
            return

        # F = ma, so a = F/m
        ax, ay = game_object.acceleration
        game_object.acceleration = (ax + force_x / game_object.mass,
                                   ay + force_y / game_object.mass)

    def apply_impulse(self, game_object: GameObject, impulse_x: float, impulse_y: float):
        """Apply impulse to game object (immediate velocity change)"""
        if game_object.mass <= 0 or game_object.is_static:
            return

        # J = mv, so v = J/m
        vx, vy = game_object.velocity
        game_object.velocity = (vx + impulse_x / game_object.mass,
                               vy + impulse_y / game_object.mass)

    def set_gravity(self, gx: float, gy: float):
        """Set gravity vector"""
        self.gravity = (gx, gy)

    def set_world_bounds(self, left: float, top: float, right: float, bottom: float):
        """Set world bounds"""
        self.world_bounds = (left, top, right, bottom)

    def enable_physics(self, enabled: bool):
        """Enable or disable physics"""
        self.enabled = enabled

    def enable_collision(self, enabled: bool):
        """Enable or disable collision detection"""
        self.collision_enabled = enabled

    def enable_world_bounds(self, enabled: bool):
        """Enable or disable world bounds constraint"""
        self.constrain_to_world = enabled

    def add_to_collision_layer(self, layer_name: str, game_object: GameObject):
        """Add object to collision layer"""
        if layer_name not in self.collision_layers:
            self.collision_layers[layer_name] = []

        if game_object not in self.collision_layers[layer_name]:
            self.collision_layers[layer_name].append(game_object)

        game_object.collision_layer = layer_name

    def remove_from_collision_layer(self, layer_name: str, game_object: GameObject):
        """Remove object from collision layer"""
        if layer_name in self.collision_layers:
            if game_object in self.collision_layers[layer_name]:
                self.collision_layers[layer_name].remove(game_object)

    def get_objects_in_layer(self, layer_name: str) -> List[GameObject]:
        """Get all objects in collision layer"""
        return self.collision_layers.get(layer_name, [])

    def check_layer_collisions(self, layer1: str, layer2: str, delta_time: float):
        """Check collisions between two layers"""
        objects1 = self.get_objects_in_layer(layer1)
        objects2 = self.get_objects_in_layer(layer2)

        for obj1 in objects1:
            for obj2 in objects2:
                if self.check_collision(obj1, obj2):
                    self.resolve_collision(obj1, obj2, delta_time)

    def get_objects_in_range(self, center_x: float, center_y: float, 
                            radius: float, objects: List[GameObject]) -> List[GameObject]:
        """Get all objects within a certain range"""
        result = []
        for obj in objects:
            if not obj.active or obj.destroyed:
                continue

            x, y = obj.position
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            if distance <= radius:
                result.append(obj)
        return result

    def raycast(self, start_x: float, start_y: float, 
                end_x: float, end_y: float, 
                objects: List[GameObject]) -> Optional[GameObject]:
        """Simple raycast to find first object hit"""
        # This is a simplified raycast implementation
        steps = 100
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps

        for i in range(steps):
            x = start_x + dx * i
            y = start_y + dy * i

            for obj in objects:
                if obj.active and not obj.destroyed and obj.contains_point(x, y):
                    return obj

        return None

    def circle_cast(self, start_x: float, start_y: float, 
                   end_x: float, end_y: float, radius: float,
                   objects: List[GameObject]) -> List[GameObject]:
        """Cast a circle along a path and return all hit objects"""
        hits = []
        steps = int(math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2) / 5) + 1
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps

        for i in range(steps):
            x = start_x + dx * i
            y = start_y + dy * i

            nearby = self.get_objects_in_range(x, y, radius, objects)
            for obj in nearby:
                if obj not in hits:
                    hits.append(obj)

        return hits

    def apply_explosion_force(self, center_x: float, center_y: float, 
                            force: float, radius: float, objects: List[GameObject]):
        """Apply explosion force to objects in range"""
        affected_objects = self.get_objects_in_range(center_x, center_y, radius, objects)

        for obj in affected_objects:
            if obj.is_static:
                continue

            x, y = obj.position
            dx = x - center_x
            dy = y - center_y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance == 0:
                continue

            # Calculate force based on distance (inverse square law)
            force_magnitude = force * (1.0 - distance / radius)
            if force_magnitude <= 0:
                continue

            # Normalize direction and apply force
            nx = dx / distance
            ny = dy / distance

            self.apply_impulse(obj, nx * force_magnitude, ny * force_magnitude)

    def step_simulation(self, objects: List[GameObject], delta_time: float):
        """Step the physics simulation for all objects"""
        if not self.enabled:
            return

        # Apply physics to all objects
        for obj in objects:
            if obj.active and not obj.destroyed and not obj.is_static:
                # Apply gravity
                self.apply_gravity(obj, delta_time)

                # Apply air resistance
                vx, vy = obj.velocity
                obj.velocity = (vx * self.air_resistance, vy * self.air_resistance)

                # Apply unlimited physics features
                self.apply_unlimited_physics(obj, delta_time)

                # Constrain to world bounds
                self.constrain_to_bounds(obj)

        # Check all collisions
        self.check_all_collisions(objects, delta_time)

        # Update advanced physics
        self.update_force_fields(objects, delta_time)
        self.update_joints(delta_time)

    # UNLIMITED PHYSICS METHODS

    def enable_unlimited_physics(self):
        """Enable unlimited physics capabilities"""
        self.unlimited_mode = True
        self.advanced_collision = True
        self.particle_physics = True

    def apply_unlimited_physics(self, obj: GameObject, delta_time: float):
        """Apply unlimited physics features to object"""
        # Apply force fields
        for field in self.force_fields:
            self.apply_force_field(obj, field, delta_time)

        # Apply magnetic fields
        for field in self.magnetic_fields:
            self.apply_magnetic_field(obj, field, delta_time)

        # Apply gravity wells
        for well in self.gravity_wells:
            self.apply_gravity_well(obj, well, delta_time)

    def create_force_field(self, center_x: float, center_y: float, 
                          radius: float, force: float, field_type: str = "radial"):
        """Create force field for unlimited physics interactions"""
        field = {
            "center": (center_x, center_y),
            "radius": radius,
            "force": force,
            "type": field_type,
            "active": True
        }
        self.force_fields.append(field)
        return field

    def apply_force_field(self, obj: GameObject, field: Dict, delta_time: float):
        """Apply force field to object"""
        if not field["active"]:
            return

        x, y = obj.position
        fx, fy = field["center"]
        dx = x - fx
        dy = y - fy
        distance = math.sqrt(dx * dx + dy * dy)

        if distance <= field["radius"] and distance > 0:
            if field["type"] == "radial":
                # Radial force (push/pull)
                force_mag = field["force"] * (1.0 - distance / field["radius"])
                nx = dx / distance
                ny = dy / distance
                self.apply_force(obj, nx * force_mag, ny * force_mag)
            elif field["type"] == "vortex":
                # Vortex force (circular)
                force_mag = field["force"] * (1.0 - distance / field["radius"])
                nx = -dy / distance  # Perpendicular for rotation
                ny = dx / distance
                self.apply_force(obj, nx * force_mag, ny * force_mag)

    def create_magnetic_field(self, center_x: float, center_y: float, 
                             radius: float, strength: float):
        """Create magnetic field for metal objects"""
        field = {
            "center": (center_x, center_y),
            "radius": radius,
            "strength": strength,
            "active": True
        }
        self.magnetic_fields.append(field)
        return field

    def apply_magnetic_field(self, obj: GameObject, field: Dict, delta_time: float):
        """Apply magnetic field to magnetic objects"""
        if not field["active"] or not obj.get_property("magnetic", False):
            return

        x, y = obj.position
        fx, fy = field["center"]
        dx = fx - x
        dy = fy - y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance <= field["radius"] and distance > 0:
            # Magnetic attraction
            force_mag = field["strength"] / (distance * distance + 1)
            nx = dx / distance
            ny = dy / distance
            self.apply_force(obj, nx * force_mag, ny * force_mag)

    def create_gravity_well(self, center_x: float, center_y: float, 
                           radius: float, mass: float):
        """Create gravity well for space games"""
        well = {
            "center": (center_x, center_y),
            "radius": radius,
            "mass": mass,
            "active": True
        }
        self.gravity_wells.append(well)
        return well

    def apply_gravity_well(self, obj: GameObject, well: Dict, delta_time: float):
        """Apply gravity well to object"""
        if not well["active"]:
            return

        x, y = obj.position
        wx, wy = well["center"]
        dx = wx - x
        dy = wy - y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance <= well["radius"] and distance > 0:
            # Gravitational force: F = G * m1 * m2 / r²
            G = 100  # Gravitational constant (adjusted for game)
            force_mag = G * well["mass"] * obj.mass / (distance * distance)
            nx = dx / distance
            ny = dy / distance
            self.apply_force(obj, nx * force_mag, ny * force_mag)

    def create_physics_material(self, name: str, friction: float, 
                               restitution: float, density: float):
        """Create physics material for unlimited surface types"""
        material = {
            "friction": friction,
            "restitution": restitution,
            "density": density,
            "special_properties": {}
        }
        self.physics_materials[name] = material
        return material

    def apply_material_properties(self, obj: GameObject, material_name: str):
        """Apply material properties to object"""
        if material_name in self.physics_materials:
            material = self.physics_materials[material_name]
            obj.friction = material["friction"]
            obj.bounce = material["restitution"]
            obj.mass = material["density"] * obj.get_property("volume", 1.0)

    def enable_fluid_dynamics(self):
        """Enable fluid dynamics for water/air simulation"""
        self.fluid_dynamics = True
        self.fluid_grid = []
        self.fluid_particles = []

    def enable_soft_body_physics(self):
        """Enable soft body physics for deformable objects"""
        self.soft_body_physics = True
        self.soft_bodies = []

    def enable_cloth_simulation(self):
        """Enable cloth simulation"""
        self.cloth_simulation = True
        self.cloth_objects = []

    def create_joint(self, obj1: GameObject, obj2: GameObject, 
                    joint_type: str, anchor_point: Tuple[float, float]):
        """Create physics joint between objects"""
        joint = {
            "object1": obj1,
            "object2": obj2,
            "type": joint_type,
            "anchor": anchor_point,
            "active": True
        }
        self.joint_systems.append(joint)
        return joint

    def update_joints(self, delta_time: float):
        """Update all physics joints"""
        for joint in self.joint_systems:
            if joint["active"]:
                self.update_joint(joint, delta_time)

    def update_joint(self, joint: Dict, delta_time: float):
        """Update individual joint"""
        obj1 = joint["object1"]
        obj2 = joint["object2"]
        joint_type = joint["type"]

        if joint_type == "distance":
            self.update_distance_joint(obj1, obj2, joint, delta_time)
        elif joint_type == "revolute":
            self.update_revolute_joint(obj1, obj2, joint, delta_time)
        elif joint_type == "spring":
            self.update_spring_joint(obj1, obj2, joint, delta_time)

    def update_distance_joint(self, obj1: GameObject, obj2: GameObject, 
                             joint: Dict, delta_time: float):
        """Update distance joint (fixed distance between objects)"""
        x1, y1 = obj1.position
        x2, y2 = obj2.position
        target_distance = joint.get("distance", 100)

        dx = x2 - x1
        dy = y2 - y1
        current_distance = math.sqrt(dx * dx + dy * dy)

        if current_distance > 0:
            difference = target_distance - current_distance
            correction = difference * 0.5  # Split correction between objects

            nx = dx / current_distance
            ny = dy / current_distance

            if not obj1.is_static:
                obj1.position = (x1 - nx * correction, y1 - ny * correction)
            if not obj2.is_static:
                obj2.position = (x2 + nx * correction, y2 + ny * correction)

    def update_spring_joint(self, obj1: GameObject, obj2: GameObject, 
                           joint: Dict, delta_time: float):
        """Update spring joint (elastic connection)"""
        x1, y1 = obj1.position
        x2, y2 = obj2.position
        rest_length = joint.get("rest_length", 100)
        spring_k = joint.get("spring_constant", 1000)
        damping = joint.get("damping", 0.1)

        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            # Spring force: F = -k * (x - rest_length)
            force_magnitude = spring_k * (distance - rest_length)
            nx = dx / distance
            ny = dy / distance

            # Apply damping
            v1x, v1y = obj1.velocity
            v2x, v2y = obj2.velocity
            relative_velocity = ((v2x - v1x) * nx + (v2y - v1y) * ny)
            damping_force = damping * relative_velocity

            total_force = force_magnitude + damping_force

            if not obj1.is_static:
                self.apply_force(obj1, nx * total_force, ny * total_force)
            if not obj2.is_static:
                self.apply_force(obj2, -nx * total_force, -ny * total_force)

    def update_force_fields(self, objects: List[GameObject], delta_time: float):
        """Update all force fields"""
        for field in self.force_fields:
            if field["active"]:
                for obj in objects:
                    if obj.active and not obj.destroyed:
                        self.apply_force_field(obj, field, delta_time)
    def cleanup(self):
        """Clean up physics system"""
        self.collision_layers.clear()

    # PATHFINDING SYSTEM
    def create_pathfinding_grid(self, width, height, cell_size=32):
        """Create pathfinding grid"""
        self.pathfinding_grid = {
            'width': width,
            'height': height,
            'cell_size': cell_size,
            'obstacles': set()
        }

    def add_obstacle(self, x, y):
        """Add obstacle to pathfinding grid"""
        if hasattr(self, 'pathfinding_grid'):
            grid_x = int(x // self.pathfinding_grid['cell_size'])
            grid_y = int(y // self.pathfinding_grid['cell_size'])
            self.pathfinding_grid['obstacles'].add((grid_x, grid_y))

    def find_path(self, start_x, start_y, end_x, end_y):
        """Find path using A* algorithm"""
        if not hasattr(self, 'pathfinding_grid'):
            return []

        grid = self.pathfinding_grid
        cell_size = grid['cell_size']

        # Convert world coordinates to grid coordinates
        start_grid = (int(start_x // cell_size), int(start_y // cell_size))
        end_grid = (int(end_x // cell_size), int(end_y // cell_size))

        # Simple A* implementation
        from heapq import heappush, heappop

        open_set = [(0, start_grid)]
        came_from = {}
        g_score = {start_grid: 0}
        f_score = {start_grid: self._heuristic(start_grid, end_grid)}

        while open_set:
            current = heappop(open_set)[1]

            if current == end_grid:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append((current[0] * cell_size, current[1] * cell_size))
                    current = came_from[current]
                path.reverse()
                return path

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)

                # Check bounds and obstacles
                if (neighbor[0] < 0 or neighbor[0] >= grid['width'] or
                    neighbor[1] < 0 or neighbor[1] >= grid['height'] or
                    neighbor in grid['obstacles']):
                    continue

                tentative_g = g_score[current] + 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._heuristic(neighbor, end_grid)
                    heappush(open_set, (f_score[neighbor], neighbor))

        return []  # No path found

    def _heuristic(self, a, b):
        """Manhattan distance heuristic"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])