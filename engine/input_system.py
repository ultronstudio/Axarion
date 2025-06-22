"""
Axarion Engine Input System
Handles keyboard and mouse input for games
"""

import pygame
from typing import Dict, Set, Tuple, Optional

class InputSystem:
    """Manages keyboard and mouse input"""

    def __init__(self):
        self.keys_pressed = set()
        self.keys_just_pressed = set()
        self.keys_just_released = set()
        self.previous_keys = set()

        self.mouse_position = (0, 0)
        self.mouse_buttons = set()
        self.mouse_just_clicked = set()
        self.mouse_just_released = set()
        self.previous_mouse_buttons = set()

        self.mouse_wheel = 0

        # Key mappings for easier access
        self.key_mappings = {
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'space': pygame.K_SPACE,
            'enter': pygame.K_RETURN,
            'escape': pygame.K_ESCAPE,
            'a': pygame.K_a,
            'b': pygame.K_b,
            'c': pygame.K_c,
            'd': pygame.K_d,
            'e': pygame.K_e,
            'f': pygame.K_f,
            'g': pygame.K_g,
            'h': pygame.K_h,
            'i': pygame.K_i,
            'j': pygame.K_j,
            'k': pygame.K_k,
            'l': pygame.K_l,
            'm': pygame.K_m,
            'n': pygame.K_n,
            'o': pygame.K_o,
            'p': pygame.K_p,
            'q': pygame.K_q,
            'r': pygame.K_r,
            's': pygame.K_s,
            't': pygame.K_t,
            'u': pygame.K_u,
            'v': pygame.K_v,
            'w': pygame.K_w,
            'x': pygame.K_x,
            'y': pygame.K_y,
            'z': pygame.K_z,
            '1': pygame.K_1,
            '2': pygame.K_2,
            '3': pygame.K_3,
            '4': pygame.K_4,
            '5': pygame.K_5,
            '6': pygame.K_6,
            '7': pygame.K_7,
            '8': pygame.K_8,
            '9': pygame.K_9,
            '0': pygame.K_0,
            'shift': pygame.K_LSHIFT,
            'ctrl': pygame.K_LCTRL,
            'alt': pygame.K_LALT,
            'tab': pygame.K_TAB
        }

    def update(self, events):
        """Update input state with pygame events"""
        # Store previous states
        self.previous_keys = self.keys_pressed.copy()
        self.previous_mouse_buttons = self.mouse_buttons.copy()

        # Clear frame-specific states
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.mouse_just_clicked.clear()
        self.mouse_just_released.clear()
        self.mouse_wheel = 0

        # Get current key state
        keys = pygame.key.get_pressed()
        current_keys = set()

        for key_code in range(len(keys)):
            if keys[key_code]:
                current_keys.add(key_code)

        # Calculate just pressed/released
        self.keys_just_pressed = current_keys - self.previous_keys
        self.keys_just_released = self.previous_keys - current_keys
        self.keys_pressed = current_keys

        # Get mouse state
        self.mouse_position = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        current_mouse = set()

        for i, pressed in enumerate(mouse_buttons):
            if pressed:
                current_mouse.add(i)

        # Calculate mouse just clicked/released
        self.mouse_just_clicked = current_mouse - self.previous_mouse_buttons
        self.mouse_just_released = self.previous_mouse_buttons - current_mouse
        self.mouse_buttons = current_mouse

        # Process events for additional input
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.mouse_wheel = event.y

    def is_key_pressed(self, key: str) -> bool:
        """Check if key is currently pressed"""
        key_code = self.key_mappings.get(key.lower())
        if key_code is None:
            return False
        return key_code in self.keys_pressed

    def is_key_just_pressed(self, key: str) -> bool:
        """Check if key was just pressed this frame"""
        key_code = self.key_mappings.get(key.lower())
        if key_code is None:
            return False
        return key_code in self.keys_just_pressed

    def is_key_just_released(self, key: str) -> bool:
        """Check if key was just released this frame"""
        key_code = self.key_mappings.get(key.lower())
        if key_code is None:
            return False
        return key_code in self.keys_just_released

    def is_mouse_button_pressed(self, button: int = 0) -> bool:
        """Check if mouse button is pressed (0=left, 1=middle, 2=right)"""
        return button in self.mouse_buttons

    def is_mouse_button_just_clicked(self, button: int = 0) -> bool:
        """Check if mouse button was just clicked this frame"""
        return button in self.mouse_just_clicked

    def is_mouse_button_just_released(self, button: int = 0) -> bool:
        """Check if mouse button was just released this frame"""
        return button in self.mouse_just_released

    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        return self.mouse_position

    def get_mouse_wheel(self) -> int:
        """Get mouse wheel movement this frame"""
        return self.mouse_wheel

    def get_axis(self, axis_name: str) -> float:
        """Get axis value (-1 to 1) for common input axes"""
        if axis_name == "horizontal":
            value = 0.0
            if self.is_key_pressed("left") or self.is_key_pressed("a"):
                value -= 1.0
            if self.is_key_pressed("right") or self.is_key_pressed("d"):
                value += 1.0
            return value

        elif axis_name == "vertical":
            value = 0.0
            if self.is_key_pressed("up") or self.is_key_pressed("w"):
                value -= 1.0
            if self.is_key_pressed("down") or self.is_key_pressed("s"):
                value += 1.0
            return value

        return 0.0

    def get_movement_vector(self) -> Tuple[float, float]:
        """Get normalized movement vector from WASD or arrow keys"""
        x = self.get_axis("horizontal")
        y = self.get_axis("vertical")

        # Normalize diagonal movement
        if x != 0 and y != 0:
            length = (x * x + y * y) ** 0.5
            x /= length
            y /= length

        return (x, y)

    def reset(self):
        """Reset all input states"""
        self.keys_pressed.clear()
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.previous_keys.clear()

        self.mouse_buttons.clear()
        self.mouse_just_clicked.clear()
        self.mouse_just_released.clear()
        self.previous_mouse_buttons.clear()

        self.mouse_wheel = 0
        self.mouse_position = (0, 0)

    def is_key_down(self, key_name: str) -> bool:
        """Check if key is currently pressed"""
        key_code = self.key_mappings.get(key_name.lower())
        if key_code is None:
            return False
        return key_code in self.keys_pressed

    def is_key_pressed(self, key_name: str) -> bool:
        """Alias for is_key_down for AXScript compatibility"""
        return self.is_key_down(key_name)

# Global input system instance
input_system = InputSystem()

# Convenience functions for scripts
def key_pressed(key: str) -> bool:
    """Check if key is currently pressed"""
    return input_system.is_key_pressed(key)

def key_just_pressed(key: str) -> bool:
    """Check if key was just pressed this frame"""
    return input_system.is_key_just_pressed(key)

def key_just_released(key: str) -> bool:
    """Check if key was just released this frame"""
    return input_system.is_key_just_released(key)

def mouse_clicked(button: int = 0) -> bool:
    """Check if mouse button was just clicked"""
    return input_system.is_mouse_button_just_clicked(button)

def mouse_pressed(button: int = 0) -> bool:
    """Check if mouse button is currently pressed"""
    return input_system.is_mouse_button_pressed(button)

def get_mouse_pos() -> Tuple[int, int]:
    """Get current mouse position"""
    return input_system.get_mouse_position()

def get_axis(axis_name: str) -> float:
    """Get axis value for movement"""
    return input_system.get_axis(axis_name)

def get_movement() -> Tuple[float, float]:
    """Get movement vector from input"""
    return input_system.get_movement_vector()