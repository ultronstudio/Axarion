
"""
Axarion Engine Advanced Collision System
Implements pixel-perfect, SAT, continuous collision detection and trigger zones
"""

import math
import pygame
from typing import List, Tuple, Optional, Dict, Any
from .game_object import GameObject

class CollisionResult:
    """Result of collision detection"""
    
    def __init__(self, colliding: bool = False, penetration: Tuple[float, float] = (0, 0),
                 contact_point: Tuple[float, float] = (0, 0), normal: Tuple[float, float] = (0, 0)):
        self.colliding = colliding
        self.penetration = penetration  # How much objects are overlapping
        self.contact_point = contact_point  # Point of contact
        self.normal = normal  # Collision normal vector

class TriggerZone:
    """Trigger zone for area-based detection"""
    
    def __init__(self, x: float, y: float, width: float, height: float, 
                 trigger_id: str, layer: str = "default"):
        self.position = (x, y)
        self.size = (width, height)
        self.trigger_id = trigger_id
        self.layer = layer
        self.active = True
        self.objects_inside: List[GameObject] = []
        self.on_enter: Optional[callable] = None
        self.on_exit: Optional[callable] = None
        self.on_stay: Optional[callable] = None
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get trigger zone bounds"""
        x, y = self.position
        w, h = self.size
        return (x, y, x + w, y + h)
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside trigger"""
        bounds = self.get_bounds()
        return (bounds[0] <= x <= bounds[2] and 
                bounds[1] <= y <= bounds[3])
    
    def check_object(self, obj: GameObject) -> bool:
        """Check if object is in trigger zone"""
        obj_bounds = obj.get_bounds()
        trigger_bounds = self.get_bounds()
        
        return (obj_bounds[0] < trigger_bounds[2] and obj_bounds[2] > trigger_bounds[0] and
                obj_bounds[1] < trigger_bounds[3] and obj_bounds[3] > trigger_bounds[1])

class AdvancedCollisionSystem:
    """Advanced collision detection system"""
    
    def __init__(self):
        self.pixel_perfect_cache: Dict[str, pygame.mask.Mask] = {}
        self.trigger_zones: List[TriggerZone] = []
        self.collision_layers: Dict[str, List[GameObject]] = {}
        
        # Continuous collision detection
        self.ccd_enabled = True
        self.max_ccd_iterations = 5
        
        # Performance settings
        self.use_spatial_hashing = True
        self.spatial_hash: Dict[Tuple[int, int], List[GameObject]] = {}
        self.spatial_cell_size = 64
    
    def pixel_perfect_collision(self, obj1: GameObject, obj2: GameObject) -> CollisionResult:
        """Pixel-perfect collision detection using masks"""
        # Get or create masks
        mask1 = self._get_or_create_mask(obj1)
        mask2 = self._get_or_create_mask(obj2)
        
        if not mask1 or not mask2:
            return CollisionResult(False)
        
        # Calculate offset between objects
        x1, y1 = obj1.position
        x2, y2 = obj2.position
        offset = (int(x2 - x1), int(y2 - y1))
        
        # Check overlap
        overlap = mask1.overlap(mask2, offset)
        
        if overlap:
            # Calculate contact point and normal
            contact_x = x1 + overlap[0]
            contact_y = y1 + overlap[1]
            
            # Simple normal calculation
            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx * dx + dy * dy)
            
            if length > 0:
                normal = (dx / length, dy / length)
            else:
                normal = (1, 0)
            
            return CollisionResult(
                colliding=True,
                contact_point=(contact_x, contact_y),
                normal=normal
            )
        
        return CollisionResult(False)
    
    def sat_collision(self, obj1: GameObject, obj2: GameObject) -> CollisionResult:
        """Separating Axis Theorem collision detection for polygons"""
        # Get polygon points
        points1 = self._get_polygon_points(obj1)
        points2 = self._get_polygon_points(obj2)
        
        if not points1 or not points2:
            return CollisionResult(False)
        
        # Get all axes to test
        axes = []
        axes.extend(self._get_polygon_axes(points1))
        axes.extend(self._get_polygon_axes(points2))
        
        min_overlap = float('inf')
        min_axis = (1, 0)
        
        # Test each axis
        for axis in axes:
            proj1 = self._project_polygon(points1, axis)
            proj2 = self._project_polygon(points2, axis)
            
            # Check for separation
            if proj1[1] < proj2[0] or proj2[1] < proj1[0]:
                return CollisionResult(False)  # Separated
            
            # Calculate overlap
            overlap = min(proj1[1] - proj2[0], proj2[1] - proj1[0])
            if overlap < min_overlap:
                min_overlap = overlap
                min_axis = axis
        
        # Calculate penetration vector
        penetration = (min_axis[0] * min_overlap, min_axis[1] * min_overlap)
        
        return CollisionResult(
            colliding=True,
            penetration=penetration,
            normal=min_axis
        )
    
    def continuous_collision_detection(self, obj: GameObject, delta_time: float) -> List[CollisionResult]:
        """Continuous collision detection for fast-moving objects"""
        if not self.ccd_enabled:
            return []
        
        results = []
        vx, vy = obj.velocity
        
        # Only use CCD for fast-moving objects
        speed = math.sqrt(vx * vx + vy * vy)
        if speed < 100:  # Threshold for CCD
            return results
        
        # Calculate movement trajectory
        start_pos = obj.position
        end_pos = (start_pos[0] + vx * delta_time, start_pos[1] + vy * delta_time)
        
        # Sample points along trajectory
        steps = min(self.max_ccd_iterations, int(speed * delta_time / 32) + 1)
        
        for i in range(1, steps + 1):
            t = i / steps
            test_x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
            test_y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
            
            # Temporarily move object to test position
            original_pos = obj.position
            obj.position = (test_x, test_y)
            
            # Check collisions at this position
            nearby_objects = self._get_nearby_objects(obj)
            for other_obj in nearby_objects:
                if other_obj != obj and other_obj.collision_enabled:
                    if obj.is_colliding_with(other_obj):
                        result = CollisionResult(
                            colliding=True,
                            contact_point=(test_x, test_y)
                        )
                        results.append(result)
                        break
            
            # Restore position
            obj.position = original_pos
            
            if results:  # Stop at first collision
                break
        
        return results
    
    def add_trigger_zone(self, x: float, y: float, width: float, height: float, 
                        trigger_id: str, layer: str = "default") -> TriggerZone:
        """Add trigger zone"""
        trigger = TriggerZone(x, y, width, height, trigger_id, layer)
        self.trigger_zones.append(trigger)
        return trigger
    
    def remove_trigger_zone(self, trigger_id: str):
        """Remove trigger zone"""
        self.trigger_zones = [t for t in self.trigger_zones if t.trigger_id != trigger_id]
    
    def update_trigger_zones(self, objects: List[GameObject]):
        """Update trigger zone states"""
        for trigger in self.trigger_zones:
            if not trigger.active:
                continue
            
            # Check which objects are currently in the zone
            current_objects = []
            for obj in objects:
                if obj.active and not obj.destroyed and trigger.check_object(obj):
                    current_objects.append(obj)
            
            # Find new entries and exits
            new_entries = [obj for obj in current_objects if obj not in trigger.objects_inside]
            exits = [obj for obj in trigger.objects_inside if obj not in current_objects]
            staying = [obj for obj in current_objects if obj in trigger.objects_inside]
            
            # Trigger events
            for obj in new_entries:
                if trigger.on_enter:
                    trigger.on_enter(trigger, obj)
            
            for obj in exits:
                if trigger.on_exit:
                    trigger.on_exit(trigger, obj)
            
            for obj in staying:
                if trigger.on_stay:
                    trigger.on_stay(trigger, obj)
            
            # Update objects list
            trigger.objects_inside = current_objects
    
    def update_spatial_hash(self, objects: List[GameObject]):
        """Update spatial hash for performance"""
        if not self.use_spatial_hashing:
            return
        
        self.spatial_hash.clear()
        
        for obj in objects:
            if not obj.active or obj.destroyed:
                continue
            
            bounds = obj.get_bounds()
            
            # Calculate which cells this object occupies
            min_cell_x = int(bounds[0] // self.spatial_cell_size)
            max_cell_x = int(bounds[2] // self.spatial_cell_size)
            min_cell_y = int(bounds[1] // self.spatial_cell_size)
            max_cell_y = int(bounds[3] // self.spatial_cell_size)
            
            # Add object to relevant cells
            for cell_x in range(min_cell_x, max_cell_x + 1):
                for cell_y in range(min_cell_y, max_cell_y + 1):
                    cell = (cell_x, cell_y)
                    if cell not in self.spatial_hash:
                        self.spatial_hash[cell] = []
                    self.spatial_hash[cell].append(obj)
    
    def get_collision_candidates(self, obj: GameObject) -> List[GameObject]:
        """Get potential collision candidates using spatial hashing"""
        if not self.use_spatial_hashing:
            return []
        
        candidates = set()
        bounds = obj.get_bounds()
        
        # Get cells that this object occupies
        min_cell_x = int(bounds[0] // self.spatial_cell_size)
        max_cell_x = int(bounds[2] // self.spatial_cell_size)
        min_cell_y = int(bounds[1] // self.spatial_cell_size)
        max_cell_y = int(bounds[3] // self.spatial_cell_size)
        
        # Collect candidates from relevant cells
        for cell_x in range(min_cell_x, max_cell_x + 1):
            for cell_y in range(min_cell_y, max_cell_y + 1):
                cell = (cell_x, cell_y)
                if cell in self.spatial_hash:
                    candidates.update(self.spatial_hash[cell])
        
        # Remove self and return list
        candidates.discard(obj)
        return list(candidates)
    
    def _get_or_create_mask(self, obj: GameObject) -> Optional[pygame.mask.Mask]:
        """Get or create collision mask for object"""
        cache_key = f"{obj.name}_{obj.object_type}"
        
        if cache_key in self.pixel_perfect_cache:
            return self.pixel_perfect_cache[cache_key]
        
        # Create mask based on object type
        mask = None
        
        if obj.object_type == "sprite":
            sprite_surface = obj.get_current_sprite()
            if sprite_surface:
                mask = pygame.mask.from_surface(sprite_surface)
        
        elif obj.object_type == "rectangle":
            width = obj.properties.get("width", 50)
            height = obj.properties.get("height", 50)
            surface = pygame.Surface((width, height))
            surface.fill((255, 255, 255))
            mask = pygame.mask.from_surface(surface)
        
        elif obj.object_type == "circle":
            radius = obj.properties.get("radius", 25)
            size = int(radius * 2)
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 255, 255), (radius, radius), radius)
            mask = pygame.mask.from_surface(surface)
        
        if mask:
            self.pixel_perfect_cache[cache_key] = mask
        
        return mask
    
    def _get_polygon_points(self, obj: GameObject) -> List[Tuple[float, float]]:
        """Get polygon points for SAT collision"""
        if obj.object_type == "polygon":
            return obj.properties.get("points", [])
        
        elif obj.object_type == "rectangle":
            x, y = obj.position
            width = obj.properties.get("width", 50)
            height = obj.properties.get("height", 50)
            
            # Apply rotation if needed
            if obj.rotation != 0:
                return self._rotate_rectangle_points(x, y, width, height, obj.rotation)
            else:
                return [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]
        
        return []
    
    def _rotate_rectangle_points(self, x: float, y: float, width: float, height: float, 
                                rotation: float) -> List[Tuple[float, float]]:
        """Rotate rectangle points"""
        rad = math.radians(rotation)
        cos_r = math.cos(rad)
        sin_r = math.sin(rad)
        
        # Center of rectangle
        cx = x + width / 2
        cy = y + height / 2
        
        # Original points relative to center
        points = [
            (-width/2, -height/2), (width/2, -height/2),
            (width/2, height/2), (-width/2, height/2)
        ]
        
        # Rotate and translate back
        rotated_points = []
        for px, py in points:
            rx = px * cos_r - py * sin_r + cx
            ry = px * sin_r + py * cos_r + cy
            rotated_points.append((rx, ry))
        
        return rotated_points
    
    def _get_polygon_axes(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Get axes for SAT collision detection"""
        axes = []
        
        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            
            # Edge vector
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            
            # Normal vector (perpendicular)
            normal = (-edge[1], edge[0])
            
            # Normalize
            length = math.sqrt(normal[0] * normal[0] + normal[1] * normal[1])
            if length > 0:
                axes.append((normal[0] / length, normal[1] / length))
        
        return axes
    
    def _project_polygon(self, points: List[Tuple[float, float]], 
                        axis: Tuple[float, float]) -> Tuple[float, float]:
        """Project polygon onto axis"""
        projections = []
        
        for point in points:
            dot_product = point[0] * axis[0] + point[1] * axis[1]
            projections.append(dot_product)
        
        return (min(projections), max(projections))
    
    def _get_nearby_objects(self, obj: GameObject) -> List[GameObject]:
        """Get nearby objects for collision testing"""
        if self.use_spatial_hashing:
            return self.get_collision_candidates(obj)
        else:
            # Fallback to checking layer objects
            layer = obj.collision_layer or "default"
            return self.collision_layers.get(layer, [])

# Global instance
advanced_collision_system = AdvancedCollisionSystem()
