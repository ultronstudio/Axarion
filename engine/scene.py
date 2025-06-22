"""
Axarion Engine Scene
Manages game objects and scene rendering
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from .game_object import GameObject
from .physics import PhysicsSystem

class Scene:
    """Scene class that manages game objects"""

    def __init__(self, name: str):
        self.name = name
        self.objects: Dict[str, GameObject] = {}
        self.object_counter = 0

        # Scene properties
        self.background_color = (30, 30, 40)
        self.gravity = (0.0, 500.0)  # Default gravity

        # Physics system
        self.physics = PhysicsSystem()
        self.physics.set_gravity(self.gravity[0], self.gravity[1])

        # Scene bounds
        self.bounds = (0, 0, 800, 600)  # left, top, right, bottom
        self.physics.set_world_bounds(*self.bounds)

        # Collision layers
        self.collision_layers: Dict[str, List[str]] = {
            "default": [],
            "player": [],
            "enemy": [],
            "projectile": [],
            "platform": [],
            "collectible": []
        }

        # Scene state
        self.active = True
        self.paused = False

        # Performance optimization
        self.cull_objects = True
        self.render_distance = 1000.0

        # Event callbacks
        self.on_object_added = None
        self.on_object_removed = None

    def add_object(self, game_object: GameObject) -> str:
        """Add object to scene and return its ID"""
        # Generate unique ID if needed
        if not game_object.name or game_object.name in self.objects:
            self.object_counter += 1
            object_id = f"{game_object.object_type}_{self.object_counter}"
            game_object.name = object_id
        else:
            object_id = game_object.name

        # Add to scene
        self.objects[object_id] = game_object
        game_object.scene = self

        # Add to collision layer
        layer = game_object.collision_layer
        if layer not in self.collision_layers:
            self.collision_layers[layer] = []

        if object_id not in self.collision_layers[layer]:
            self.collision_layers[layer].append(object_id)

        # Add to physics system
        self.physics.add_to_collision_layer(layer, game_object)

        # Call event callback
        if self.on_object_added:
            self.on_object_added(game_object)

        return object_id

    def remove_object(self, object_id: str) -> bool:
        """Remove object from scene"""
        if object_id not in self.objects:
            return False

        game_object = self.objects[object_id]

        # Remove from collision layers
        for layer_name, layer_objects in self.collision_layers.items():
            if object_id in layer_objects:
                layer_objects.remove(object_id)

        # Remove from physics system
        self.physics.remove_from_collision_layer(game_object.collision_layer, game_object)

        # Call event callback
        if self.on_object_removed:
            self.on_object_removed(game_object)

        # Remove from scene
        game_object.scene = None
        del self.objects[object_id]

        return True

    def get_object(self, object_id: str) -> Optional[GameObject]:
        """Get object by ID"""
        return self.objects.get(object_id)

    def get_objects_by_name(self, name: str) -> List[GameObject]:
        """Get all objects with matching name"""
        return [obj for obj in self.objects.values() if obj.name == name]

    def get_objects_by_type(self, object_type: str) -> List[GameObject]:
        """Get all objects of specific type"""
        return [obj for obj in self.objects.values() if obj.object_type == object_type]

    def get_objects_by_tag(self, tag: str) -> List[GameObject]:
        """Get all objects with specific tag"""
        return [obj for obj in self.objects.values() if obj.has_tag(tag)]

    def get_objects_in_layer(self, layer: str) -> List[GameObject]:
        """Get all objects in collision layer"""
        if layer not in self.collision_layers:
            return []

        return [self.objects[obj_id] for obj_id in self.collision_layers[layer] 
                if obj_id in self.objects]

    def get_all_objects(self) -> List[GameObject]:
        """Get all objects in scene"""
        return list(self.objects.values())

    def get_active_objects(self) -> List[GameObject]:
        """Get all active objects"""
        return [obj for obj in self.objects.values() if obj.active and not obj.destroyed]

    def update(self, delta_time: float):
        """Update the scene"""
        if not self.active:
            return

        # Get active objects
        active_objects = [obj for obj in self.objects.values() 
                         if obj.active and not obj.destroyed]

        # Update all objects first
        for obj in active_objects:
            obj.update(delta_time)

        # Handle physics collisions
        if self.physics and self.physics.collision_enabled:
            self.physics.check_all_collisions(active_objects, delta_time)

        # Apply physics constraints (world bounds, etc.)
        if self.physics:
            for obj in active_objects:
                if not obj.is_static:
                    self.physics.constrain_to_bounds(obj)

        # Remove destroyed objects
        self.objects = {name: obj for name, obj in self.objects.items() 
                       if not obj.destroyed}

    def render(self, renderer):
        """Render scene and all objects"""
        if not self.active:
            return

        # Set background color
        renderer.set_background_color(self.background_color)

        # Get camera position for culling
        camera_x, camera_y = renderer.get_camera()

        # Render objects
        rendered_count = 0
        for obj in self.objects.values():
            if not obj.visible or obj.destroyed:
                continue

            # Cull objects outside render distance (optimization)
            if self.cull_objects:
                obj_x, obj_y = obj.position
                distance = ((obj_x - camera_x) ** 2 + (obj_y - camera_y) ** 2) ** 0.5
                if distance > self.render_distance:
                    continue

                # Also check if object is roughly on screen
                if not renderer.is_on_screen(obj):
                    continue

            # Render object
            renderer.draw_game_object(obj)
            rendered_count += 1

        # Draw scene debug info if needed
        if renderer.debug_mode:
            self._render_debug_info(renderer)

    def _render_debug_info(self, renderer):
        """Render debug information"""
        debug_info = [
            f"Scene: {self.name}",
            f"Objects: {len(self.objects)}",
            f"Active: {len(self.get_active_objects())}",
            f"Gravity: ({self.gravity[0]}, {self.gravity[1]})",
        ]

        y_offset = 80
        for info in debug_info:
            renderer.draw_text(info, 10, y_offset, (255, 255, 0), renderer.small_font)
            y_offset += 16

    def _cleanup_collision_layers(self):
        """Clean up collision layers by removing non-existent objects"""
        for layer_name, layer_objects in self.collision_layers.items():
            self.collision_layers[layer_name] = [
                obj_id for obj_id in layer_objects if obj_id in self.objects
            ]

    def find_objects_near(self, x: float, y: float, radius: float) -> List[GameObject]:
        """Find objects within radius of point"""
        return self.physics.get_objects_in_range(x, y, radius, self.get_active_objects())

    def find_object_at_point(self, x: float, y: float) -> Optional[GameObject]:
        """Find object at specific point"""
        for obj in self.get_active_objects():
            if obj.contains_point(x, y):
                return obj
        return None

    def raycast(self, start_x: float, start_y: float, end_x: float, end_y: float) -> Optional[GameObject]:
        """Cast a ray and return first object hit"""
        return self.physics.raycast(start_x, start_y, end_x, end_y, self.get_active_objects())

    def set_gravity(self, gx: float, gy: float):
        """Set scene gravity"""
        self.gravity = (gx, gy)
        self.physics.set_gravity(gx, gy)

    def set_bounds(self, left: float, top: float, right: float, bottom: float):
        """Set scene bounds"""
        self.bounds = (left, top, right, bottom)
        self.physics.set_world_bounds(left, top, right, bottom)

    def enable_physics(self, enabled: bool):
        """Enable or disable physics"""
        self.physics.enable_physics(enabled)

    def enable_collision(self, enabled: bool):
        """Enable or disable collision detection"""
        self.physics.enable_collision(enabled)

    def pause(self):
        """Pause scene updates"""
        self.paused = True

    def resume(self):
        """Resume scene updates"""
        self.paused = False

    def clear(self):
        """Remove all objects from scene"""
        object_ids = list(self.objects.keys())
        for obj_id in object_ids:
            self.remove_object(obj_id)

    def move_object_to_layer(self, object_id: str, new_layer: str):
        """Move object to different collision layer"""
        if object_id not in self.objects:
            return False

        game_object = self.objects[object_id]
        old_layer = game_object.collision_layer

        # Remove from old layer
        if old_layer in self.collision_layers:
            if object_id in self.collision_layers[old_layer]:
                self.collision_layers[old_layer].remove(object_id)

        self.physics.remove_from_collision_layer(old_layer, game_object)

        # Add to new layer
        if new_layer not in self.collision_layers:
            self.collision_layers[new_layer] = []

        self.collision_layers[new_layer].append(object_id)
        self.physics.add_to_collision_layer(new_layer, game_object)

        return True

    def serialize(self) -> Dict[str, Any]:
        """Serialize scene to dictionary"""
        objects_data = {}
        for obj_id, obj in self.objects.items():
            objects_data[obj_id] = obj.serialize()

        return {
            "name": self.name,
            "background_color": self.background_color,
            "gravity": self.gravity,
            "bounds": self.bounds,
            "objects": objects_data,
            "collision_layers": self.collision_layers
        }

    def deserialize(self, data: Dict[str, Any]):
        """Deserialize scene from dictionary"""
        self.name = data.get("name", "Unknown")
        self.background_color = tuple(data.get("background_color", (30, 30, 40)))
        self.gravity = tuple(data.get("gravity", (0.0, 500.0)))
        self.bounds = tuple(data.get("bounds", (0, 0, 800, 600)))

        # Set physics properties
        self.set_gravity(self.gravity[0], self.gravity[1])
        self.set_bounds(*self.bounds)

        # Clear existing objects
        self.clear()

        # Load objects
        objects_data = data.get("objects", {})
        for obj_id, obj_data in objects_data.items():
            obj = GameObject("temp", "rectangle")
            obj.deserialize(obj_data)
            obj.name = obj_id
            self.add_object(obj)

        # Restore collision layers
        self.collision_layers = data.get("collision_layers", {"default": []})

    def save_to_file(self, file_path: str) -> bool:
        """Save scene to file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.serialize(), f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save scene: {e}")
            return False

    def load_from_file(self, file_path: str) -> bool:
        """Load scene from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            self.deserialize(data)
            return True
        except Exception as e:
            print(f"Failed to load scene: {e}")
            return False