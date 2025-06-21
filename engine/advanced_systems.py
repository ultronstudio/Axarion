
"""
Axarion Engine Advanced Systems
Specialized systems for different game genres and advanced features
"""

import math
import random
from typing import Dict, List, Tuple, Any, Optional, Callable
from .game_object import GameObject

class SaveSystem:
    """Save/Load game system"""
    
    def __init__(self):
        self.save_slots = {}
        self.auto_save_enabled = True
        self.auto_save_interval = 60.0  # seconds
        self.last_auto_save = 0.0
    
    def save_game(self, slot_name: str, data: Dict[str, Any]) -> bool:
        """Save game data to slot"""
        try:
            import json
            import os
            
            save_dir = "saves"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            file_path = os.path.join(save_dir, f"{slot_name}.json")
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.save_slots[slot_name] = data
            return True
        except Exception as e:
            print(f"Save failed: {e}")
            return False
    
    def load_game(self, slot_name: str) -> Optional[Dict[str, Any]]:
        """Load game data from slot"""
        try:
            import json
            import os
            
            file_path = os.path.join("saves", f"{slot_name}.json")
            
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                self.save_slots[slot_name] = data
                return data
        except Exception as e:
            print(f"Load failed: {e}")
        
        return None
    
    def auto_save(self, engine, current_time: float):
        """Automatic save system"""
        if (self.auto_save_enabled and 
            current_time - self.last_auto_save >= self.auto_save_interval):
            
            # Create auto-save data
            save_data = {
                "timestamp": current_time,
                "current_scene": engine.current_scene.name if engine.current_scene else "",
                "global_variables": engine.global_variables,
                "scenes": {name: scene.serialize() for name, scene in engine.scenes.items()}
            }
            
            self.save_game("auto_save", save_data)
            self.last_auto_save = current_time

class DialogueSystem:
    """Dialogue system for narrative games"""
    
    def __init__(self):
        self.conversations = {}
        self.current_conversation = None
        self.current_node = None
        self.dialogue_history = []
        self.character_portraits = {}
    
    def add_conversation(self, conv_id: str, dialogue_tree: Dict):
        """Add dialogue conversation"""
        self.conversations[conv_id] = dialogue_tree
    
    def start_conversation(self, conv_id: str, start_node: str = "start"):
        """Start dialogue conversation"""
        if conv_id in self.conversations:
            self.current_conversation = conv_id
            self.current_node = start_node
            return self.get_current_dialogue()
        return None
    
    def get_current_dialogue(self) -> Optional[Dict]:
        """Get current dialogue node"""
        if (self.current_conversation and 
            self.current_conversation in self.conversations and
            self.current_node):
            
            tree = self.conversations[self.current_conversation]
            return tree.get(self.current_node)
        return None
    
    def choose_option(self, option_index: int) -> Optional[Dict]:
        """Choose dialogue option"""
        current = self.get_current_dialogue()
        if current and "options" in current and option_index < len(current["options"]):
            option = current["options"][option_index]
            
            # Add to history
            self.dialogue_history.append({
                "speaker": current.get("speaker", ""),
                "text": current.get("text", ""),
                "choice": option["text"]
            })
            
            # Move to next node
            self.current_node = option.get("next", None)
            
            # Execute any actions
            if "action" in option:
                self.execute_dialogue_action(option["action"])
            
            return self.get_current_dialogue()
        return None
    
    def execute_dialogue_action(self, action: Dict):
        """Execute dialogue action (set flag, give item, etc.)"""
        action_type = action.get("type")
        
        if action_type == "set_flag":
            # Set global flag
            pass
        elif action_type == "give_item":
            # Give item to player
            pass
        elif action_type == "change_scene":
            # Change scene
            pass

class QuestSystem:
    """Quest and mission system"""
    
    def __init__(self):
        self.quests = {}
        self.active_quests = []
        self.completed_quests = []
        self.quest_progress = {}
    
    def create_quest(self, quest_id: str, title: str, description: str, objectives: List[Dict]):
        """Create new quest"""
        quest = {
            "id": quest_id,
            "title": title,
            "description": description,
            "objectives": objectives,  # [{"type": "kill", "target": "enemy", "count": 5}]
            "status": "available",
            "reward": {},
            "progress": {}
        }
        
        self.quests[quest_id] = quest
        return quest
    
    def start_quest(self, quest_id: str) -> bool:
        """Start quest"""
        if quest_id in self.quests and quest_id not in self.active_quests:
            self.active_quests.append(quest_id)
            self.quests[quest_id]["status"] = "active"
            
            # Initialize progress
            for i, objective in enumerate(self.quests[quest_id]["objectives"]):
                self.quest_progress[f"{quest_id}_{i}"] = 0
            
            return True
        return False
    
    def update_quest_progress(self, event_type: str, target: str = "", amount: int = 1):
        """Update quest progress based on game events"""
        for quest_id in self.active_quests:
            quest = self.quests[quest_id]
            
            for i, objective in enumerate(quest["objectives"]):
                if objective["type"] == event_type:
                    if "target" not in objective or objective["target"] == target:
                        progress_key = f"{quest_id}_{i}"
                        self.quest_progress[progress_key] += amount
                        
                        # Check if objective completed
                        if self.quest_progress[progress_key] >= objective.get("count", 1):
                            self.check_quest_completion(quest_id)
    
    def check_quest_completion(self, quest_id: str):
        """Check if quest is completed"""
        quest = self.quests[quest_id]
        all_completed = True
        
        for i, objective in enumerate(quest["objectives"]):
            progress_key = f"{quest_id}_{i}"
            if self.quest_progress.get(progress_key, 0) < objective.get("count", 1):
                all_completed = False
                break
        
        if all_completed:
            self.complete_quest(quest_id)
    
    def complete_quest(self, quest_id: str):
        """Complete quest"""
        if quest_id in self.active_quests:
            self.active_quests.remove(quest_id)
            self.completed_quests.append(quest_id)
            self.quests[quest_id]["status"] = "completed"
            
            # Give rewards
            reward = self.quests[quest_id].get("reward", {})
            if "experience" in reward:
                # Give experience
                pass
            if "items" in reward:
                # Give items
                pass

class InventorySystem:
    """Advanced inventory management"""
    
    def __init__(self, max_slots: int = 20):
        self.max_slots = max_slots
        self.items = []
        self.equipped_items = {}
        self.item_templates = {}
    
    def register_item_template(self, item_id: str, template: Dict):
        """Register item template"""
        self.item_templates[item_id] = template
    
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """Add item to inventory"""
        if item_id not in self.item_templates:
            return False
        
        template = self.item_templates[item_id]
        
        # Check if item is stackable
        if template.get("stackable", False):
            # Find existing stack
            for item in self.items:
                if item["id"] == item_id:
                    item["quantity"] += quantity
                    return True
        
        # Add new item stack
        if len(self.items) < self.max_slots:
            self.items.append({
                "id": item_id,
                "quantity": quantity,
                "template": template
            })
            return True
        
        return False  # Inventory full
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Remove item from inventory"""
        for i, item in enumerate(self.items):
            if item["id"] == item_id:
                if item["quantity"] >= quantity:
                    item["quantity"] -= quantity
                    if item["quantity"] <= 0:
                        del self.items[i]
                    return True
        return False
    
    def equip_item(self, item_id: str, slot: str) -> bool:
        """Equip item in slot"""
        # Find item in inventory
        for item in self.items:
            if item["id"] == item_id:
                template = item["template"]
                if template.get("equippable", False) and template.get("slot") == slot:
                    # Unequip current item
                    if slot in self.equipped_items:
                        self.unequip_item(slot)
                    
                    # Equip new item
                    self.equipped_items[slot] = {
                        "id": item_id,
                        "template": template
                    }
                    
                    # Remove from inventory if not stackable
                    if not template.get("stackable", False):
                        self.remove_item(item_id, 1)
                    
                    return True
        return False
    
    def unequip_item(self, slot: str) -> bool:
        """Unequip item from slot"""
        if slot in self.equipped_items:
            item = self.equipped_items[slot]
            
            # Add back to inventory
            self.add_item(item["id"], 1)
            
            # Remove from equipment
            del self.equipped_items[slot]
            return True
        return False

class CraftingSystem:
    """Crafting system"""
    
    def __init__(self):
        self.recipes = {}
        self.workbenches = {}
    
    def add_recipe(self, recipe_id: str, ingredients: List[Dict], result: Dict, workbench: str = "none"):
        """Add crafting recipe"""
        self.recipes[recipe_id] = {
            "ingredients": ingredients,  # [{"item": "wood", "quantity": 2}]
            "result": result,  # {"item": "stick", "quantity": 1}
            "workbench": workbench
        }
    
    def can_craft(self, recipe_id: str, inventory: InventorySystem, workbench: str = "none") -> bool:
        """Check if recipe can be crafted"""
        if recipe_id not in self.recipes:
            return False
        
        recipe = self.recipes[recipe_id]
        
        # Check workbench requirement
        if recipe["workbench"] != "none" and recipe["workbench"] != workbench:
            return False
        
        # Check ingredients
        for ingredient in recipe["ingredients"]:
            if not self.has_ingredient(inventory, ingredient["item"], ingredient["quantity"]):
                return False
        
        return True
    
    def craft_item(self, recipe_id: str, inventory: InventorySystem, workbench: str = "none") -> bool:
        """Craft item using recipe"""
        if not self.can_craft(recipe_id, inventory, workbench):
            return False
        
        recipe = self.recipes[recipe_id]
        
        # Remove ingredients
        for ingredient in recipe["ingredients"]:
            inventory.remove_item(ingredient["item"], ingredient["quantity"])
        
        # Add result
        result = recipe["result"]
        inventory.add_item(result["item"], result["quantity"])
        
        return True
    
    def has_ingredient(self, inventory: InventorySystem, item_id: str, quantity: int) -> bool:
        """Check if inventory has enough of ingredient"""
        total_quantity = 0
        for item in inventory.items:
            if item["id"] == item_id:
                total_quantity += item["quantity"]
        
        return total_quantity >= quantity

class AchievementSystem:
    """Achievement system"""
    
    def __init__(self):
        self.achievements = {}
        self.unlocked_achievements = []
        self.progress = {}
    
    def register_achievement(self, achievement_id: str, title: str, description: str, requirements: Dict):
        """Register achievement"""
        self.achievements[achievement_id] = {
            "title": title,
            "description": description,
            "requirements": requirements,  # {"type": "kill_enemies", "count": 100}
            "unlocked": False,
            "unlock_time": None
        }
        
        # Initialize progress
        self.progress[achievement_id] = 0
    
    def update_progress(self, event_type: str, amount: int = 1):
        """Update achievement progress"""
        for achievement_id, achievement in self.achievements.items():
            if achievement["unlocked"]:
                continue
            
            requirements = achievement["requirements"]
            if requirements["type"] == event_type:
                self.progress[achievement_id] += amount
                
                # Check if unlocked
                if self.progress[achievement_id] >= requirements.get("count", 1):
                    self.unlock_achievement(achievement_id)
    
    def unlock_achievement(self, achievement_id: str):
        """Unlock achievement"""
        if achievement_id in self.achievements and not self.achievements[achievement_id]["unlocked"]:
            import time
            
            self.achievements[achievement_id]["unlocked"] = True
            self.achievements[achievement_id]["unlock_time"] = time.time()
            self.unlocked_achievements.append(achievement_id)
            
            # Notify player
            print(f"🏆 Achievement Unlocked: {self.achievements[achievement_id]['title']}")

# Global system instances
save_system = SaveSystem()
dialogue_system = DialogueSystem()
quest_system = QuestSystem()
achievement_system = AchievementSystem()
