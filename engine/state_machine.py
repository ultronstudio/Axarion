
"""
State Machine System for Axarion Engine
Provides finite state machine functionality for AI and game logic
"""

from typing import Dict, Callable, Any, Optional
from enum import Enum

class StateTransition:
    """Represents a transition between states"""
    
    def __init__(self, from_state: str, to_state: str, condition: Callable, action: Callable = None):
        self.from_state = from_state
        self.to_state = to_state
        self.condition = condition
        self.action = action  # Optional action to execute during transition

class StateMachine:
    """Finite State Machine implementation"""
    
    def __init__(self, initial_state: str = "idle"):
        self.current_state = initial_state
        self.states: Dict[str, Callable] = {}
        self.transitions: Dict[str, list] = {}
        self.state_data: Dict[str, Any] = {}
        self.global_data: Dict[str, Any] = {}
        
    def add_state(self, state_name: str, update_function: Callable):
        """Add a state with its update function"""
        self.states[state_name] = update_function
        if state_name not in self.transitions:
            self.transitions[state_name] = []
    
    def add_transition(self, transition: StateTransition):
        """Add a transition rule"""
        if transition.from_state not in self.transitions:
            self.transitions[transition.from_state] = []
        
        self.transitions[transition.from_state].append(transition)
    
    def set_state_data(self, state_name: str, key: str, value: Any):
        """Set data specific to a state"""
        if state_name not in self.state_data:
            self.state_data[state_name] = {}
        self.state_data[state_name][key] = value
    
    def get_state_data(self, state_name: str, key: str, default=None):
        """Get data specific to a state"""
        return self.state_data.get(state_name, {}).get(key, default)
    
    def update(self, game_object, delta_time: float):
        """Update the state machine"""
        # Execute current state
        if self.current_state in self.states:
            self.states[self.current_state](game_object, delta_time, self)
        
        # Check for transitions
        self.check_transitions(game_object)
    
    def check_transitions(self, game_object):
        """Check if any transitions should be triggered"""
        if self.current_state not in self.transitions:
            return
        
        for transition in self.transitions[self.current_state]:
            if transition.condition(game_object, self):
                self.change_state(transition.to_state, game_object)
                
                # Execute transition action if present
                if transition.action:
                    transition.action(game_object, self)
                break
    
    def change_state(self, new_state: str, game_object = None):
        """Manually change state"""
        if new_state in self.states:
            old_state = self.current_state
            self.current_state = new_state
            
            # Call exit and enter functions if they exist
            exit_func_name = f"exit_{old_state}"
            enter_func_name = f"enter_{new_state}"
            
            if hasattr(game_object, exit_func_name):
                getattr(game_object, exit_func_name)(self)
            
            if hasattr(game_object, enter_func_name):
                getattr(game_object, enter_func_name)(self)

# Predefined AI states for common game objects

def idle_state(game_object, delta_time, state_machine):
    """Default idle state - do nothing"""
    pass

def patrol_state(game_object, delta_time, state_machine):
    """Patrol between points"""
    if not hasattr(game_object, 'patrol_points') or not game_object.patrol_points:
        return
    
    speed = state_machine.get_state_data("patrol", "speed", 100)
    arrival_distance = state_machine.get_state_data("patrol", "arrival_distance", 20)
    
    if not hasattr(game_object, 'current_patrol_index'):
        game_object.current_patrol_index = 0
    
    target_point = game_object.patrol_points[game_object.current_patrol_index]
    x, y = game_object.position
    tx, ty = target_point
    
    distance = ((tx - x) ** 2 + (ty - y) ** 2) ** 0.5
    
    if distance <= arrival_distance:
        game_object.current_patrol_index = (game_object.current_patrol_index + 1) % len(game_object.patrol_points)
    else:
        game_object.move_towards(target_point, speed)

def chase_state(game_object, delta_time, state_machine):
    """Chase a target"""
    target = state_machine.global_data.get("chase_target")
    if not target:
        return
    
    speed = state_machine.get_state_data("chase", "speed", 150)
    target_pos = getattr(target, 'position', target)
    game_object.move_towards(target_pos, speed)

def attack_state(game_object, delta_time, state_machine):
    """Attack state behavior"""
    target = state_machine.global_data.get("attack_target")
    if not target:
        return
    
    attack_timer = state_machine.get_state_data("attack", "timer", 0)
    attack_cooldown = state_machine.get_state_data("attack", "cooldown", 1.0)
    
    attack_timer -= delta_time
    state_machine.set_state_data("attack", "timer", attack_timer)
    
    if attack_timer <= 0:
        # Perform attack
        if hasattr(game_object, 'perform_attack'):
            game_object.perform_attack(target)
        
        # Reset timer
        state_machine.set_state_data("attack", "timer", attack_cooldown)

# Condition functions for transitions

def target_in_sight(game_object, state_machine) -> bool:
    """Check if target is within sight range"""
    target = state_machine.global_data.get("chase_target")
    if not target:
        return False
    
    sight_range = state_machine.global_data.get("sight_range", 200)
    target_pos = getattr(target, 'position', target)
    x, y = game_object.position
    tx, ty = target_pos
    
    distance = ((tx - x) ** 2 + (ty - y) ** 2) ** 0.5
    return distance <= sight_range

def target_in_attack_range(game_object, state_machine) -> bool:
    """Check if target is within attack range"""
    target = state_machine.global_data.get("attack_target") or state_machine.global_data.get("chase_target")
    if not target:
        return False
    
    attack_range = state_machine.global_data.get("attack_range", 50)
    target_pos = getattr(target, 'position', target)
    x, y = game_object.position
    tx, ty = target_pos
    
    distance = ((tx - x) ** 2 + (ty - y) ** 2) ** 0.5
    return distance <= attack_range

def target_lost(game_object, state_machine) -> bool:
    """Check if target is lost (out of sight)"""
    return not target_in_sight(game_object, state_machine)

def create_basic_enemy_ai() -> StateMachine:
    """Create a basic enemy AI state machine"""
    ai = StateMachine("patrol")
    
    # Add states
    ai.add_state("idle", idle_state)
    ai.add_state("patrol", patrol_state)
    ai.add_state("chase", chase_state)
    ai.add_state("attack", attack_state)
    
    # Add transitions
    ai.add_transition(StateTransition("patrol", "chase", target_in_sight))
    ai.add_transition(StateTransition("chase", "attack", target_in_attack_range))
    ai.add_transition(StateTransition("attack", "chase", lambda obj, sm: not target_in_attack_range(obj, sm)))
    ai.add_transition(StateTransition("chase", "patrol", target_lost))
    
    # Set default parameters
    ai.set_state_data("patrol", "speed", 50)
    ai.set_state_data("chase", "speed", 120)
    ai.set_state_data("attack", "cooldown", 1.5)
    ai.global_data["sight_range"] = 150
    ai.global_data["attack_range"] = 40
    
    return ai
