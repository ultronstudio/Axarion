#!/usr/bin/env python3
"""
Axarion Engif (pos.x < 0) setProperty("position", {x: 0, y: pos.y});ine Physics Test
Demonstrates physics system, collision detection, and player movement
"""

import pygame
import sys
import os
import random

# Add engine to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.core import AxarionEngine
from engine.game_object import GameObject
from engine.scene import Scene


def create_physics_test():
    """Create test scene with physics objects"""

    # Create engine
    engine = AxarionEngine(1000, 700)
    if not engine.initialize():
        print("Failed to initialize engine")
        return None

    # Create scene
    scene = Scene("Physics Test")
    engine.current_scene = scene

    # Set scene properties
    scene.set_gravity(0, 400)  # Gravity
    scene.set_bounds(0, 0, 1000, 700)

    # Create player
    player = GameObject("Player", "rectangle")
    player.position = (100, 200)
    player.set_property("width", 30)
    player.set_property("height", 40)
    player.set_property("color", (100, 150, 255))
    player.mass = 1.2
    player.bounce = 0.1
    player.friction = 0.8
    player.add_tag("player")

    # Player script with simplified movement and debugging
    player.script_code = """
// Check all movement keys
if (keyPressed("a") || keyPressed("left")) {
    print("LEFT movement detected!");
    applyForce(-300, 0);
}

if (keyPressed("d") || keyPressed("right")) {
    print("RIGHT movement detected!");
    applyForce(300, 0);
}

if (keyPressed("w") || keyPressed("up")) {
    print("UP key detected!");
    if (isOnGround()) {
        print("Jumping!");
        applyForce(0, -500);
    }
}

if (keyPressed("space")) {
    print("SPACE detected!");
    if (isOnGround()) {
        print("Space jump!");
        applyForce(0, -500);
    }
}
"""
    scene.add_object(player)
    
    # Add scene reference to player for AXScript
    player.scene = scene
    
    # Enable AXScript mode by default
    player.use_axscript = True

    # Create ground platforms
    platforms = [
        {
            "pos": (0, 650),
            "size": (300, 50)
        },
        {
            "pos": (400, 650),
            "size": (600, 50)
        },
        {
            "pos": (300, 500),
            "size": (150, 20)
        },
        {
            "pos": (600, 400),
            "size": (120, 20)
        },
        {
            "pos": (800, 300),
            "size": (100, 20)
        },
        {
            "pos": (150, 350),
            "size": (100, 20)
        },
    ]

    for i, platform_data in enumerate(platforms):
        platform = GameObject(f"Platform_{i}", "rectangle")
        platform.position = platform_data["pos"]
        platform.set_property("width", platform_data["size"][0])
        platform.set_property("height", platform_data["size"][1])
        platform.set_property("color", (80, 120, 80))
        platform.is_static = True
        platform.add_tag("platform")
        scene.add_object(platform)

    # Create bouncing balls
    ball_colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255),
                   (255, 255, 100)]
    for i in range(6):
        ball = GameObject(f"Ball_{i}", "circle")
        ball.position = (200 + i * 120, 100)
        ball.set_property("radius", 12 + (i % 3) * 3)
        ball.set_property("color", ball_colors[i % len(ball_colors)])
        ball.mass = 0.5 + (i % 3) * 0.3
        ball.bounce = 0.7 + (i % 2) * 0.2
        ball.friction = 0.1
        ball.velocity = (random.randint(-50, 50), random.randint(-100, 50))
        ball.add_tag("ball")
        scene.add_object(ball)

    # Create movable boxes
    for i in range(4):
        box = GameObject(f"Box_{i}", "rectangle")
        box.position = (500 + i * 80, 300 + i * 50)
        box.set_property("width", 25 + (i % 2) * 10)
        box.set_property("height", 25 + (i % 2) * 10)
        box.set_property("color", (150, 100 + i * 20, 50))
        box.mass = 1.0 + i * 0.3
        box.bounce = 0.3
        box.friction = 0.5
        box.add_tag("box")
        scene.add_object(box)

    # Set up renderer
    engine.renderer.enable_debug(True)
    engine.renderer.show_object_bounds(False)

    return engine


def main():
    """Main test function"""
    print("🎮 Testing Fixed Axarion Engine")
    print("=" * 50)

    # Create test scene
    engine = create_physics_test()
    if not engine:
        return

    print("✅ Engine initialized successfully")
    print("✅ Scene created with physics objects")
    print("✅ Objects: Player, Platforms, Balls, Boxes")
    print("\n🎯 Controls:")
    print("   Arrow Keys - Move player")
    print("   Space - Jump")
    print("   ESC - Exit")
    print("   D - Toggle debug mode")
    print("\n🚀 Starting simulation...")

    # Game loop
    clock = pygame.time.Clock()
    running = True

    try:
        while running:
            delta_time = clock.tick(60) / 1000.0

            # Handle events
            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            # Update input system with events
            from engine.input_system import input_system
            input_system.update(events)

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_d:
                        # Toggle debug mode
                        engine.renderer.debug_mode = not engine.renderer.debug_mode
                        engine.renderer.show_object_bounds(
                            engine.renderer.debug_mode)
                        print(
                            f"Debug mode: {'ON' if engine.renderer.debug_mode else 'OFF'}"
                        )
                    elif event.key == pygame.K_x:
                        # Toggle between basic controls and AXScript
                        player = engine.current_scene.get_object("Player")
                        if player:
                            use_axscript = getattr(player, 'use_axscript', False)
                            player.use_axscript = not use_axscript
                            mode = "AXScript" if player.use_axscript else "Basic"
                            print(f"Control mode: {mode}")

            # Handle player movement - toggle between basic and AXScript
            player = engine.current_scene.get_object("Player")
            if player:
                # Check if we should use AXScript (press X to toggle)
                use_axscript = getattr(player, 'use_axscript', True)  # Default to True
                
                if use_axscript and hasattr(player, 'script_code') and player.script_code:
                    # Use AXScript for movement
                    try:
                        from scripting.axscript_interpreter import AXScriptInterpreter
                        interpreter = AXScriptInterpreter()
                        result = interpreter.execute(player.script_code, player)

                        if not result["success"]:
                            print(f"❌ AXScript error: {result['error']}")
                            if result.get('output'):
                                print(f"🔍 AXScript debug: {result['output']}")
                        else:
                            # Only show output if there's actual output (not just successful execution)
                            if result.get('output') and result['output'].strip():
                                print(f"🟢 AXScript: {result['output']}")

                    except Exception as e:
                        print(f"❌ AXScript execution error: {e}")

                else:
                    # Use basic direct controls
                    if input_system.is_key_pressed("left") or input_system.is_key_pressed("a"):
                        player.apply_force(-300, 0)
                        print("🎮 Basic: LEFT")
                    if input_system.is_key_pressed("right") or input_system.is_key_pressed("d"):
                        player.apply_force(300, 0)
                        print("🎮 Basic: RIGHT")
                    if (input_system.is_key_pressed("up") or input_system.is_key_pressed("w") or 
                        input_system.is_key_pressed("space")):
                        # Jump only if on ground
                        platforms = [obj for obj in engine.current_scene.objects.values() 
                                   if obj.has_tag("platform") or obj.is_static]
                        if player.is_on_ground(platforms):
                            player.velocity = (player.velocity[0], -400)
                            print("🎮 Basic: JUMP")

            # Update engine with error handling
            try:
                engine.current_scene.update(delta_time)
            except Exception as e:
                print(f"Scene update error: {e}")

            # Follow player with camera
            if player:
                engine.renderer.follow_object(player, 0, -100)

            # Render
            engine.renderer.clear()
            engine.current_scene.render(engine.renderer)

            # Draw UI
            engine.renderer.draw_text("Axarion Engine - Physics Test", 10, 10,
                                      (255, 255, 255))
            engine.renderer.draw_text(
                "WASD/Arrows: Move | Space: Jump | D: Debug | X: Toggle Controls | ESC: Exit", 10,
                30, (200, 200, 200))

            # Show physics and input info
            if player:
                vel = player.velocity
                on_ground = player.is_on_ground([
                    obj for obj in engine.current_scene.objects.values()
                    if obj.is_static
                ])
                engine.renderer.draw_text(
                    f"Velocity: ({vel[0]:.1f}, {vel[1]:.1f})", 10, 50,
                    (150, 200, 255))
                engine.renderer.draw_text(f"On Ground: {on_ground}", 10, 70,
                                          (150, 200, 255))
                
                # Debug input state
                input_debug = f"Keys: "
                if input_system.is_key_pressed("left") or input_system.is_key_pressed("a"):
                    input_debug += "LEFT "
                if input_system.is_key_pressed("right") or input_system.is_key_pressed("d"):
                    input_debug += "RIGHT "
                if input_system.is_key_pressed("up") or input_system.is_key_pressed("w"):
                    input_debug += "UP "
                if input_system.is_key_pressed("space"):
                    input_debug += "SPACE "
                engine.renderer.draw_text(input_debug, 10, 90, (255, 255, 100))
                
                # Show control mode
                use_axscript = getattr(player, 'use_axscript', False)
                control_mode = "AXScript" if use_axscript else "Basic"
                engine.renderer.draw_text(f"Control Mode: {control_mode}", 10, 110, (100, 255, 100))

            engine.renderer.present()

    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🧹 Cleaning up...")
        engine.cleanup()
        pygame.quit()
        print("✅ Test completed")


if __name__ == "__main__":
    main()