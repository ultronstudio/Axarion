"""
Axarion Engine Scene System
Manages game objects and scene hierarchy
"""

import json
from typing import Dict, List, Optional, Any
from .game_object import GameObject
from .renderer import Renderer

class Scene:
    """Represents a game scene with objects and properties"""
    
    def __init__(self, name: str = "Unnamed Scene"):
        self.name = name
        self.game_objects: Dict[str, GameObject] = {}
        self.object_order: List[str] = []  # Render order
        self.properties: Dict[str, Any] = {}
        
        # Scene settings
        self.background_color = (50, 50, 50)
        self.camera_x = 0
        self.camera_y = 0
        
        # Internal state
        self._next_object_id = 1
    
    def add_object(self, game_object: GameObject) -> str:
        """Add a game object to the scene"""
        # Generate unique ID if not set
        if not game_object.id:
            game_object.id = f"object_{self._next_object_id}"
            self._next_object_id += 1
        
        # Ensure unique ID
        while game_object.id in self.game_objects:
            game_object.id = f"object_{self._next_object_id}"
            self._next_object_id += 1
        
        self.game_objects[game_object.id] = game_object
        self.object_order.append(game_object.id)
        game_object.scene = self
        
        return game_object.id
    
    def remove_object(self, object_id: str) -> bool:
        """Remove a game object from the scene"""
        if object_id in self.game_objects:
            del self.game_objects[object_id]
            if object_id in self.object_order:
                self.object_order.remove(object_id)
            return True
        return False
    
    def get_object(self, object_id: str) -> Optional[GameObject]:
        """Get a game object by ID"""
        return self.game_objects.get(object_id)
    
    def get_objects_by_name(self, name: str) -> List[GameObject]:
        """Get all game objects with a specific name"""
        return [obj for obj in self.game_objects.values() if obj.name == name]
    
    def get_objects_by_type(self, object_type: str) -> List[GameObject]:
        """Get all game objects of a specific type"""
        return [obj for obj in self.game_objects.values() if obj.object_type == object_type]
    
    def get_all_objects(self) -> List[GameObject]:
        """Get all game objects in render order"""
        return [self.game_objects[obj_id] for obj_id in self.object_order 
                if obj_id in self.game_objects]
    
    def move_object_to_front(self, object_id: str):
        """Move object to front of render order"""
        if object_id in self.object_order:
            self.object_order.remove(object_id)
            self.object_order.append(object_id)
    
    def move_object_to_back(self, object_id: str):
        """Move object to back of render order"""
        if object_id in self.object_order:
            self.object_order.remove(object_id)
            self.object_order.insert(0, object_id)
    
    def update(self, delta_time: float):
        """Update all objects in the scene"""
        for game_object in self.get_all_objects():
            if game_object.active:
                game_object.update(delta_time)
    
    def render(self, renderer: Renderer):
        """Render all objects in the scene"""
        # Set camera position
        renderer.set_camera(self.camera_x, self.camera_y)
        
        # Render objects in order
        for game_object in self.get_all_objects():
            if game_object.visible:
                renderer.draw_game_object(game_object)
    
    def find_object_at_position(self, x: float, y: float) -> Optional[GameObject]:
        """Find the topmost object at a given position"""
        # Check objects in reverse render order (front to back)
        for obj_id in reversed(self.object_order):
            if obj_id in self.game_objects:
                obj = self.game_objects[obj_id]
                if obj.contains_point(x, y):
                    return obj
        return None
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize scene to dictionary"""
        return {
            "name": self.name,
            "background_color": self.background_color,
            "camera_x": self.camera_x,
            "camera_y": self.camera_y,
            "properties": self.properties,
            "objects": {
                obj_id: obj.serialize() 
                for obj_id, obj in self.game_objects.items()
            },
            "object_order": self.object_order
        }
    
    def deserialize(self, data: Dict[str, Any]):
        """Deserialize scene from dictionary"""
        self.name = data.get("name", "Unnamed Scene")
        self.background_color = tuple(data.get("background_color", (50, 50, 50)))
        self.camera_x = data.get("camera_x", 0)
        self.camera_y = data.get("camera_y", 0)
        self.properties = data.get("properties", {})
        
        # Clear existing objects
        self.game_objects.clear()
        self.object_order.clear()
        
        # Load objects
        objects_data = data.get("objects", {})
        for obj_id, obj_data in objects_data.items():
            game_object = GameObject()
            game_object.deserialize(obj_data)
            game_object.id = obj_id
            self.game_objects[obj_id] = game_object
            game_object.scene = self
        
        # Restore object order
        self.object_order = data.get("object_order", list(self.game_objects.keys()))
        
        # Update next object ID
        if self.game_objects:
            max_id = max([int(obj_id.split('_')[-1]) for obj_id in self.game_objects.keys() 
                         if obj_id.startswith('object_')], default=0)
            self._next_object_id = max_id + 1
    
    def clear(self):
        """Clear all objects from the scene"""
        self.game_objects.clear()
        self.object_order.clear()
        self._next_object_id = 1
    
    def get_bounds(self) -> tuple:
        """Get the bounding box of all objects in the scene"""
        if not self.game_objects:
            return (0, 0, 0, 0)
        
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for obj in self.game_objects.values():
            bounds = obj.get_bounds()
            min_x = min(min_x, bounds[0])
            min_y = min(min_y, bounds[1])
            max_x = max(max_x, bounds[2])
            max_y = max(max_y, bounds[3])
        
        return (min_x, min_y, max_x, max_y)
