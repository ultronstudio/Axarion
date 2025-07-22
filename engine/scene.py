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
        
        # Prefab system
        self.prefabs = {}
        self.prefab_instances = {}

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
        """Enhanced scene update with optimizations"""
        if not self.active or self.paused:
            return

        # Get active objects with caching
        active_objects = self._get_active_objects_cached()

        # Update physics system first
        if self.physics:
            self.physics.update(delta_time)

        # Update objects in optimized order
        self._update_objects_optimized(active_objects, delta_time)

        # Handle physics collisions with enhanced system
        if self.physics and self.physics.collision_enabled:
            self.physics.check_all_collisions(active_objects, delta_time)

        # Apply physics constraints
        if self.physics:
            self._apply_physics_constraints(active_objects)

        # Update object layers and spatial data
        self._update_spatial_data()

        # Clean up destroyed objects
        self._cleanup_destroyed_objects()

        # Update scene statistics
        self._update_scene_stats()

    def render(self, renderer):
        """Render scene and all objects, return count of rendered objects"""
        if not self.active:
            return 0

        # Set background color
        renderer.set_background_color(self.background_color)

        # Get camera position for culling
        camera_x, camera_y = renderer.get_camera()

        # Render objects with optimized culling
        rendered_count = 0
        visible_objects = [obj for obj in self.objects.values() 
                          if obj.visible and not obj.destroyed]
        
        for obj in visible_objects:
            # Cull objects outside render distance (optimization)
            if self.cull_objects:
                obj_x, obj_y = obj.position
                distance_sq = (obj_x - camera_x) ** 2 + (obj_y - camera_y) ** 2
                if distance_sq > self.render_distance * self.render_distance:
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
        
        return rendered_count

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
    
    # PREFAB SYSTEM
    def create_prefab(self, name: str, template_object: GameObject):
        """Create a prefab from a game object"""
        prefab_data = template_object.serialize()
        self.prefabs[name] = prefab_data
        return prefab_data
    
    def instantiate_prefab(self, prefab_name: str, x: float = 0, y: float = 0):
        """Create an instance of a prefab"""
        if prefab_name not in self.prefabs:
            print(f"Prefab '{prefab_name}' not found")
            return None
        
        # Create new object from prefab data
        prefab_data = self.prefabs[prefab_name].copy()
        obj = GameObject("temp", "rectangle")
        obj.deserialize(prefab_data)
        
        # Set position and generate unique name
        obj.position = (x, y)
        instance_id = len(self.prefab_instances.get(prefab_name, []))
        obj.name = f"{prefab_name}_{instance_id}"
        
        # Track instance
        if prefab_name not in self.prefab_instances:
            self.prefab_instances[prefab_name] = []
        self.prefab_instances[prefab_name].append(obj)
        
        # Add to scene
        self.add_object(obj)
        return obj
    
    def save_prefab(self, prefab_name: str, file_path: str):
        """Save prefab to file"""
        if prefab_name not in self.prefabs:
            return False
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.prefabs[prefab_name], f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save prefab: {e}")
            return False
    
    def load_prefab(self, prefab_name: str, file_path: str):
        """Load prefab from file"""
        try:
            with open(file_path, 'r') as f:
                prefab_data = json.load(f)
            self.prefabs[prefab_name] = prefab_data
            return True
        except Exception as e:
            print(f"Failed to load prefab: {e}")
            return False

    def _get_active_objects_cached(self) -> List[GameObject]:
        """Get active objects with caching for performance"""
        if not hasattr(self, '_active_objects_cache') or not hasattr(self, '_cache_timestamp'):
            self._active_objects_cache = []
            self._cache_timestamp = 0
        
        # Update cache every few frames
        current_time = getattr(self, '_frame_count', 0)
        if current_time - self._cache_timestamp > 5:  # Update every 5 frames
            self._active_objects_cache = [obj for obj in self.objects.values() 
                                        if obj.active and not obj.destroyed]
            self._cache_timestamp = current_time
        
        return self._active_objects_cache

    def _update_objects_optimized(self, active_objects: List[GameObject], delta_time: float):
        """Update objects with optimization strategies"""
        # Sort objects by update priority
        high_priority = []
        normal_priority = []
        low_priority = []
        
        for obj in active_objects:
            priority = obj.get_property("update_priority", "normal")
            if priority == "high":
                high_priority.append(obj)
            elif priority == "low":
                low_priority.append(obj)
            else:
                normal_priority.append(obj)
        
        # Update in priority order
        for obj in high_priority:
            self._update_single_object(obj, delta_time)
        
        for obj in normal_priority:
            self._update_single_object(obj, delta_time)
        
        # Low priority objects updated less frequently
        if not hasattr(self, '_low_priority_counter'):
            self._low_priority_counter = 0
        
        self._low_priority_counter += 1
        if self._low_priority_counter % 3 == 0:  # Every 3rd frame
            for obj in low_priority:
                self._update_single_object(obj, delta_time)

    def _update_single_object(self, obj: GameObject, delta_time: float):
        """Update single object with error handling"""
        try:
            obj.update(delta_time)
            
            # Update continuous forces if present
            if hasattr(obj, 'update_continuous_forces'):
                obj.update_continuous_forces(delta_time)
                
        except Exception as e:
            print(f"Error updating object {obj.name}: {e}")

    def _apply_physics_constraints(self, active_objects: List[GameObject]):
        """Apply physics constraints to objects"""
        for obj in active_objects:
            if not obj.is_static:
                # World bounds constraint
                self.physics.constrain_to_bounds(obj)
                
                # Apply custom constraints
                self._apply_custom_constraints(obj)

    def _apply_custom_constraints(self, obj: GameObject):
        """Apply custom physics constraints"""
        # Platform constraints
        if obj.has_tag("platform_constraint"):
            self._constrain_to_platforms(obj)
        
        # Rope/chain constraints
        if obj.has_tag("rope_segment"):
            self._apply_rope_constraint(obj)

    def _constrain_to_platforms(self, obj: GameObject):
        """Constrain object to stay on platforms"""
        platforms = self.get_objects_by_tag("platform")
        if not platforms:
            return
            
        obj_bounds = obj.get_bounds()
        on_platform = False
        
        for platform in platforms:
            platform_bounds = platform.get_bounds()
            
            # Check if object is above platform
            if (obj_bounds[0] < platform_bounds[2] and obj_bounds[2] > platform_bounds[0] and
                obj_bounds[3] <= platform_bounds[1] + 5):
                on_platform = True
                break
        
        # If not on any platform, apply corrective force
        if not on_platform:
            obj.apply_force(0, -200)  # Upward force to prevent falling

    def _apply_rope_constraint(self, obj: GameObject):
        """Apply rope/chain physics constraint"""
        rope_length = obj.get_property("rope_length", 100)
        anchor_point = obj.get_property("anchor_point")
        
        if not anchor_point:
            return
            
        ax, ay = anchor_point
        ox, oy = obj.position
        
        # Calculate current distance
        distance = math.sqrt((ox - ax) ** 2 + (oy - ay) ** 2)
        
        if distance > rope_length:
            # Constrain to rope length
            ratio = rope_length / distance
            new_x = ax + (ox - ax) * ratio
            new_y = ay + (oy - ay) * ratio
            obj.position = (new_x, new_y)
            
            # Apply tension force
            tension_force = (distance - rope_length) * 10
            force_x = -(ox - ax) / distance * tension_force
            force_y = -(oy - ay) / distance * tension_force
            obj.apply_force(force_x, force_y)

    def _update_spatial_data(self):
        """Update spatial partitioning data"""
        if not hasattr(self, '_frame_count'):
            self._frame_count = 0
        self._frame_count += 1
        
        # Update spatial grid in physics system
        if self.physics and hasattr(self.physics, '_update_spatial_grid'):
            if self._frame_count % 5 == 0:  # Update every 5 frames
                self.physics._update_spatial_grid()

    def _cleanup_destroyed_objects(self):
        """Efficiently clean up destroyed objects"""
        destroyed_ids = []
        
        for obj_id, obj in self.objects.items():
            if obj.destroyed:
                destroyed_ids.append(obj_id)
        
        # Remove destroyed objects
        for obj_id in destroyed_ids:
            self.remove_object(obj_id)
        
        # Clear caches if objects were removed
        if destroyed_ids and hasattr(self, '_active_objects_cache'):
            self._active_objects_cache = []

    def _update_scene_stats(self):
        """Update scene performance statistics"""
        if not hasattr(self, 'scene_stats'):
            self.scene_stats = {
                'total_objects': 0,
                'active_objects': 0,
                'static_objects': 0,
                'collision_objects': 0
            }
        
        self.scene_stats['total_objects'] = len(self.objects)
        self.scene_stats['active_objects'] = len([obj for obj in self.objects.values() if obj.active])
        self.scene_stats['static_objects'] = len([obj for obj in self.objects.values() if obj.is_static])
        self.scene_stats['collision_objects'] = len([obj for obj in self.objects.values() if obj.collision_enabled])

    def get_scene_stats(self) -> Dict:
        """Get scene performance statistics"""
        return getattr(self, 'scene_stats', {})

    def optimize_for_performance(self):
        """Optimize scene for better performance"""
        # Enable spatial partitioning
        if self.physics:
            self.physics.use_spatial_partitioning = True
            self.physics.use_broad_phase = True
        
        # Set render distance based on scene size
        scene_width = self.bounds[2] - self.bounds[0]
        scene_height = self.bounds[3] - self.bounds[1]
        self.render_distance = max(scene_width, scene_height) * 1.5
        
        # Enable object culling
        self.cull_objects = True
        
        print(f"Scene '{self.name}' optimized for performance")

    def create_spatial_region(self, name: str, bounds: Tuple[float, float, float, float], 
                            properties: Dict = None):
        """Create spatial region with special properties"""
        if not hasattr(self, 'spatial_regions'):
            self.spatial_regions = {}
        
        self.spatial_regions[name] = {
            'bounds': bounds,
            'properties': properties or {}
        }

    def get_objects_in_region(self, region_name: str) -> List[GameObject]:
        """Get objects within spatial region"""
        if not hasattr(self, 'spatial_regions') or region_name not in self.spatial_regions:
            return []
        
        region = self.spatial_regions[region_name]
        region_bounds = region['bounds']
        
        objects_in_region = []
        for obj in self.get_active_objects():
            obj_bounds = obj.get_bounds()
            
            # Check overlap with region
            if (obj_bounds[2] > region_bounds[0] and obj_bounds[0] < region_bounds[2] and
                obj_bounds[3] > region_bounds[1] and obj_bounds[1] < region_bounds[3]):
                objects_in_region.append(obj)
        
        return objects_in_region

    def apply_region_effects(self, delta_time: float):
        """Apply effects from spatial regions"""
        if not hasattr(self, 'spatial_regions'):
            return
        
        for region_name, region in self.spatial_regions.items():
            objects_in_region = self.get_objects_in_region(region_name)
            properties = region['properties']
            
            for obj in objects_in_region:
                # Apply gravity modifier
                if 'gravity_modifier' in properties:
                    modifier = properties['gravity_modifier']
                    obj.gravity_scale *= modifier
                
                # Apply fluid effects
                if 'fluid' in properties:
                    obj._in_fluid = True
                    obj._fluid_density = properties['fluid'].get('density', 1.0)
                
                # Apply force field
                if 'force_field' in properties:
                    field = properties['force_field']
                    obj.apply_force(field.get('x', 0), field.get('y', 0))