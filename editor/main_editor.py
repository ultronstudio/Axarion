"""
Axarion Engine Main Editor
Primary editor interface for the game engine
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu
import pygame
import sys
import os
import threading
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.core import AxarionEngine
from engine.game_object import GameObject
from engine.game_templates import get_available_templates, create_template_scene
from .scene_editor import SceneEditor
from .script_editor import ScriptEditor
from .project_manager import ProjectManager

class AxarionEditor:
    """Main editor window for Axarion Engine"""

    def __init__(self, root):
        self.root = root
        self.root.title("Axarion Engine Editor")
        self.root.geometry("1200x800")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialize engine
        self.engine = AxarionEngine(800, 600)
        self.engine_running = False
        self.engine_thread = None

        # Project management
        self.project_manager = ProjectManager(self)
        self.current_project_path = None
        self.project_modified = False

        # Editor components
        self.scene_editor = None
        self.script_editor = None

        # UI components
        self.setup_ui()
        self.setup_menu()

        # Initialize engine
        self.init_engine()

        print("Axarion Editor initialized")

    def setup_ui(self):
        """Setup the main UI layout"""
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create paned window for main layout
        self.main_paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        # Left panel (hierarchy and properties)
        self.left_panel = ttk.Frame(self.main_paned)
        self.main_paned.add(self.left_panel, weight=1)

        # Center panel (scene view)
        self.center_panel = ttk.Frame(self.main_paned)
        self.main_paned.add(self.center_panel, weight=3)

        # Right panel (script editor)
        self.right_panel = ttk.Frame(self.main_paned)
        self.main_paned.add(self.right_panel, weight=2)

        # Setup left panel
        self.setup_left_panel()

        # Setup center panel (scene editor)
        self.scene_editor = SceneEditor(self.center_panel, self)

        # Setup right panel (script editor)
        self.script_editor = ScriptEditor(self.right_panel, self)

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_left_panel(self):
        """Setup the left panel with hierarchy and properties"""
        # Hierarchy section
        hierarchy_frame = ttk.LabelFrame(self.left_panel, text="Scene Hierarchy")
        hierarchy_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Hierarchy tree
        self.hierarchy_tree = ttk.Treeview(hierarchy_frame, height=10)
        self.hierarchy_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.hierarchy_tree.bind("<<TreeviewSelect>>", self.on_object_selected)

        # Quick Game Templates
        template_frame = ttk.LabelFrame(hierarchy_frame, text="Quick Start")
        template_frame.pack(fill=tk.X, padx=5, pady=5)

        # Template buttons in grid
        templates = get_available_templates()
        template_info = {
            'platformer': ('🎮 Platformer', '#4CAF50'),
            'shooter': ('🔫 Shooter', '#FF5722'), 
            'puzzle': ('🧩 Puzzle', '#9C27B0'),
            'rpg': ('⚔️ RPG', '#2196F3'),
            'racing': ('🏎️ Racing', '#FF9800')
        }

        for i, template in enumerate(templates):
            text, color = template_info.get(template, (template.title(), '#607D8B'))
            btn = tk.Button(
                template_frame, 
                text=text,
                command=lambda t=template: self.create_from_template(t),
                bg=color,
                fg='white',
                font=('Arial', 8, 'bold'),
                relief=tk.RAISED,
                bd=1,
                width=12
            )
            row = i // 2
            col = i % 2
            btn.grid(row=row, column=col, padx=2, pady=2, sticky='ew')

        template_frame.grid_columnconfigure(0, weight=1)
        template_frame.grid_columnconfigure(1, weight=1)

        # Hierarchy buttons
        hierarchy_buttons = ttk.Frame(hierarchy_frame)
        hierarchy_buttons.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(hierarchy_buttons, text="Add Rectangle", 
                  command=lambda: self.add_object("rectangle")).pack(side=tk.LEFT, padx=2)
        ttk.Button(hierarchy_buttons, text="Add Circle", 
                  command=lambda: self.add_object("circle")).pack(side=tk.LEFT, padx=2)
        ttk.Button(hierarchy_buttons, text="Delete", 
                  command=self.delete_selected_object).pack(side=tk.LEFT, padx=2)

        # Properties section
        properties_frame = ttk.LabelFrame(self.left_panel, text="Properties")
        properties_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Properties notebook
        self.properties_notebook = ttk.Notebook(properties_frame)
        self.properties_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Transform tab
        self.transform_frame = ttk.Frame(self.properties_notebook)
        self.properties_notebook.add(self.transform_frame, text="Transform")
        self.setup_transform_properties()

        # Object tab
        self.object_frame = ttk.Frame(self.properties_notebook)
        self.properties_notebook.add(self.object_frame, text="Object")
        self.setup_object_properties()

        # Current selected object
        self.selected_object = None

    def setup_transform_properties(self):
        """Setup transform properties UI"""
        # Position
        ttk.Label(self.transform_frame, text="Position:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)

        ttk.Label(self.transform_frame, text="X:").grid(row=1, column=0, sticky=tk.W, padx=10)
        self.pos_x_var = tk.StringVar()
        self.pos_x_entry = ttk.Entry(self.transform_frame, textvariable=self.pos_x_var, width=10)
        self.pos_x_entry.grid(row=1, column=1, padx=5, pady=2)
        self.pos_x_var.trace('w', self.on_property_changed)

        ttk.Label(self.transform_frame, text="Y:").grid(row=2, column=0, sticky=tk.W, padx=10)
        self.pos_y_var = tk.StringVar()
        self.pos_y_entry = ttk.Entry(self.transform_frame, textvariable=self.pos_y_var, width=10)
        self.pos_y_entry.grid(row=2, column=1, padx=5, pady=2)
        self.pos_y_var.trace('w', self.on_property_changed)

        # Size (for applicable objects)
        ttk.Label(self.transform_frame, text="Size:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)

        ttk.Label(self.transform_frame, text="Width:").grid(row=4, column=0, sticky=tk.W, padx=10)
        self.width_var = tk.StringVar()
        self.width_entry = ttk.Entry(self.transform_frame, textvariable=self.width_var, width=10)
        self.width_entry.grid(row=4, column=1, padx=5, pady=2)
        self.width_var.trace('w', self.on_property_changed)

        ttk.Label(self.transform_frame, text="Height:").grid(row=5, column=0, sticky=tk.W, padx=10)
        self.height_var = tk.StringVar()
        self.height_entry = ttk.Entry(self.transform_frame, textvariable=self.height_var, width=10)
        self.height_entry.grid(row=5, column=1, padx=5, pady=2)
        self.height_var.trace('w', self.on_property_changed)

    def setup_object_properties(self):
        """Setup object properties UI"""
        # Name
        ttk.Label(self.object_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(self.object_frame, textvariable=self.name_var, width=20)
        self.name_entry.grid(row=0, column=1, padx=5, pady=2)
        self.name_var.trace('w', self.on_property_changed)

        # Type
        ttk.Label(self.object_frame, text="Type:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.type_var = tk.StringVar()
        self.type_label = ttk.Label(self.object_frame, textvariable=self.type_var)
        self.type_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        # Visibility
        self.visible_var = tk.BooleanVar()
        self.visible_check = ttk.Checkbutton(self.object_frame, text="Visible", 
                                           variable=self.visible_var,
                                           command=self.on_property_changed)
        self.visible_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)

        # Active
        self.active_var = tk.BooleanVar()
        self.active_check = ttk.Checkbutton(self.object_frame, text="Active", 
                                          variable=self.active_var,
                                          command=self.on_property_changed)
        self.active_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)

    def setup_menu(self):
        """Setup the application menu"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)

        # Template submenu
        template_menu = Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="New from Template", menu=template_menu)
        for template_name in get_available_templates():
            template_menu.add_command(
                label=template_name.title(), 
                command=lambda t=template_name: self.create_from_template(t)
            )

        file_menu.add_separator()
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_command(label="Save Project", command=self.save_project)
        file_menu.add_command(label="Save As...", command=self.save_project_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        # Edit menu
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)

        # Engine menu
        engine_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Engine", menu=engine_menu)
        engine_menu.add_command(label="Engine Status", command=self.show_engine_status)
        engine_menu.add_command(label="Performance Monitor", command=self.show_performance)
        engine_menu.add_separator()
        engine_menu.add_command(label="Restart Engine", command=self.restart_engine)
        engine_menu.add_command(label="Engine Settings", command=self.show_engine_settings)
        
        # Scene menu
        scene_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Scene", menu=scene_menu)
        scene_menu.add_command(label="▶️ Run Scene", command=self.run_scene)
        scene_menu.add_command(label="⏹️ Stop Scene", command=self.stop_scene)
        scene_menu.add_command(label="🔄 Reset Scene", command=self.reset_scene)
        scene_menu.add_separator()
        scene_menu.add_command(label="Clear Scene", command=self.clear_scene)
        scene_menu.add_command(label="Scene Properties", command=self.show_scene_properties)

        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def init_engine(self):
        """Initialize the game engine"""
        try:
            pygame.init()
            self.engine.initialize()
            self.update_status("Engine initialized")
        except Exception as e:
            messagebox.showerror("Engine Error", f"Failed to initialize engine: {e}")

    def run(self):
        """Run the editor"""
        self.root.deiconify()  # Show the window
        self.root.mainloop()

    def add_object(self, object_type):
        """Add a new object to the scene"""
        if not self.engine.current_scene:
            return

        # Create new object
        obj = GameObject(f"New {object_type.capitalize()}", object_type)
        obj.position = (100, 100)  # Default position

        # Add to scene
        obj_id = self.engine.current_scene.add_object(obj)

        # Update hierarchy
        self.refresh_hierarchy()

        # Select the new object
        self.select_object(obj)

        self.project_modified = True
        self.update_status(f"Added {object_type}")

    def delete_selected_object(self):
        """Delete the currently selected object"""
        if not self.selected_object:
            return

        # Remove from scene
        self.engine.current_scene.remove_object(self.selected_object.id)

        # Clear selection
        self.selected_object = None
        self.clear_properties()

        # Update hierarchy
        self.refresh_hierarchy()

        self.project_modified = True
        self.update_status("Object deleted")

    def on_object_selected(self, event):
        """Handle object selection in hierarchy"""
        selection = self.hierarchy_tree.selection()
        if not selection:
            return

        item_id = selection[0]
        object_id = self.hierarchy_tree.item(item_id, "text")

        # Find object in scene
        obj = self.engine.current_scene.get_object(object_id)
        if obj:
            self.select_object(obj)

    def select_object(self, obj):
        """Select an object and update properties"""
        self.selected_object = obj
        self.update_properties()

        # Update scene editor selection
        if self.scene_editor:
            self.scene_editor.set_selected_object(obj)
            self.scene_editor.update_scene_info()  # Refresh scene info
        
        # Update script editor with object's script
        if self.script_editor:
            self.script_editor.set_object(obj)

    def update_properties(self):
        """Update property panel with selected object data"""
        if not self.selected_object:
            self.clear_properties()
            return

        obj = self.selected_object

        # Update transform properties
        self.pos_x_var.set(str(obj.position[0]))
        self.pos_y_var.set(str(obj.position[1]))

        if obj.object_type in ["rectangle", "sprite"]:
            self.width_var.set(str(obj.get_property("width", 50)))
            self.height_var.set(str(obj.get_property("height", 50)))
        elif obj.object_type == "circle":
            radius = obj.get_property("radius", 25)
            self.width_var.set(str(radius * 2))
            self.height_var.set(str(radius * 2))

        # Update object properties
        self.name_var.set(obj.name)
        self.type_var.set(obj.object_type)
        self.visible_var.set(obj.visible)
        self.active_var.set(obj.active)

    def clear_properties(self):
        """Clear all property fields"""
        self.pos_x_var.set("")
        self.pos_y_var.set("")
        self.width_var.set("")
        self.height_var.set("")
        self.name_var.set("")
        self.type_var.set("")
        self.visible_var.set(False)
        self.active_var.set(False)

    def on_property_changed(self, *args):
        """Handle property changes"""
        if not self.selected_object:
            return

        try:
            obj = self.selected_object

            # Update position
            if self.pos_x_var.get() and self.pos_y_var.get():
                x = float(self.pos_x_var.get())
                y = float(self.pos_y_var.get())
                obj.position = (x, y)

            # Update size
            if obj.object_type in ["rectangle", "sprite"]:
                if self.width_var.get():
                    obj.set_property("width", float(self.width_var.get()))
                if self.height_var.get():
                    obj.set_property("height", float(self.height_var.get()))
            elif obj.object_type == "circle":
                if self.width_var.get():
                    radius = float(self.width_var.get()) / 2
                    obj.set_property("radius", radius)

            # Update object properties
            if self.name_var.get():
                obj.name = self.name_var.get()

            obj.visible = self.visible_var.get()
            obj.active = self.active_var.get()

            # Refresh hierarchy
            self.refresh_hierarchy()

            self.project_modified = True

        except ValueError:
            pass  # Ignore invalid input

    def refresh_hierarchy(self):
        """Refresh the hierarchy tree"""
        # Clear tree
        for item in self.hierarchy_tree.get_children():
            self.hierarchy_tree.delete(item)

        # Add objects
        if self.engine.current_scene:
            for obj in self.engine.current_scene.get_all_objects():
                self.hierarchy_tree.insert("", tk.END, text=obj.id, 
                                         values=(obj.name, obj.object_type))

    def new_project(self):
        """Create a new project"""
        if self.project_modified:
            result = messagebox.askyesnocancel("Save Project", 
                                             "Save current project before creating new one?")
            if result is True:
                self.save_project()
            elif result is None:
                return

        # Clear current project
        self.engine.scenes.clear()
        self.engine.current_scene = self.engine.create_scene("Main")
        self.current_project_path = None
        self.project_modified = False

        # Refresh UI
        self.refresh_hierarchy()
        self.clear_properties()

        self.update_status("New project created")

    def create_from_template(self, template_name: str):
        """Create a new project from template"""
        try:
            # Create new scene from template
            scene = create_template_scene(template_name, "Main")
            if scene:
                # Clear current scene
                if self.engine.current_scene:
                    self.engine.current_scene.clear()

                # Load template scene
                self.engine.current_scene = scene
                self.engine.scenes["Main"] = scene

                # Refresh UI
                self.refresh_hierarchy()
                self.update_status(f"Created {template_name.title()} game template")

                # Show template info
                self.show_template_info(template_name)
            else:
                self.update_status(f"Failed to create template: {template_name}")
        except Exception as e:
            self.update_status(f"Error creating template: {str(e)}")

    def show_template_info(self, template_name: str):
        """Show information about the created template"""
        info_messages = {
            "platformer": "Platformer template created!\n\nControls:\n- Arrow keys to move\n- Space to jump\n\nFeatures:\n- Gravity physics\n- Platform collisions\n- Enemy AI",
            "shooter": "Shooter template created!\n\nControls:\n- Arrow keys to move\n- Space to shoot\n\nFeatures:\n- Top-down movement\n- Bullet system\n- Enemy AI",
            "puzzle": "Puzzle template created!\n\nControls:\n- Mouse to select pieces\n\nFeatures:\n- Grid-based gameplay\n- Match-3 mechanics\n- Score system",
            "rpg": "RPG template created!\n\nControls:\n- Arrow keys to move\n- Space to interact\n\nFeatures:\n- Character stats\n- Level system\n- NPC dialogs",
            "racing": "Racing template created!\n\nControls:\n- Arrow keys to drive\n\nFeatures:\n- Car physics\n- Checkpoints\n- Lap timing"
        }

        message = info_messages.get(template_name, f"{template_name.title()} template created!")
        messagebox.showinfo("Template Created", message)

    def open_project(self):
        """Open an existing project"""
        file_path = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("Axarion Project", "*.axp"), ("JSON files", "*.json")]
        )

        if file_path:
            if self.engine.load_project(file_path):
                self.current_project_path = file_path
                self.project_modified = False
                self.refresh_hierarchy()
                self.update_status(f"Project loaded: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("Error", "Failed to load project")

    def save_project(self):
        """Save the current project"""
        if self.current_project_path:
            if self.engine.save_project(self.current_project_path):
                self.project_modified = False
                self.update_status(f"Project saved: {os.path.basename(self.current_project_path)}")
            else:
                messagebox.showerror("Error", "Failed to save project")
        else:
            self.save_project_as()

    def save_project_as(self):
        """Save the project with a new name"""
        file_path = filedialog.asksaveasfilename(
            title="Save Project As",
            defaultextension=".axp",
            filetypes=[("Axarion Project", "*.axp"), ("JSON files", "*.json")]
        )

        if file_path:
            if self.engine.save_project(file_path):
                self.current_project_path = file_path
                self.project_modified = False
                self.update_status(f"Project saved: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("Error", "Failed to save project")

    def run_scene(self):
        """Run the current scene with AXScript execution"""
        if not self.engine.current_scene:
            messagebox.showwarning("No Scene", "No scene selected to run")
            return

        try:
            # Start engine if not running
            if not self.engine_running:
                self.engine_running = True
                self.engine.running = True

            # Execute scripts for all objects in scene
            scene = self.engine.current_scene
            script_count = 0

            for obj in scene.get_all_objects():
                if obj.script_code.strip():
                    print(f"Executing script for object: {obj.name}")

                    # Import and use AXScript interpreter
                    from scripting.axscript_interpreter import AXScriptInterpreter
                    interpreter = AXScriptInterpreter()

                    # Execute the script with object context
                    result = interpreter.execute(obj.script_code, obj)

                    if result["success"]:
                        if result["output"]:
                            print(f"Output from {obj.name}: {result['output']}")
                        script_count += 1
                    else:
                        print(f"Script error in {obj.name}: {result['error']}")
                        messagebox.showerror("Script Error", 
                                           f"Error in {obj.name}:\n{result['error']}")

            if script_count > 0:
                self.update_status(f"Scene running - {script_count} scripts executed")
                print(f"Scene '{scene.name}' is now running with {script_count} active scripts")
            else:
                self.update_status("Scene running - no scripts found")
                print("Scene is running but no objects have scripts")

        except Exception as e:
            messagebox.showerror("Run Error", f"Failed to run scene: {e}")
            print(f"Error running scene: {e}")

    def stop_scene(self):
        """Stop the current scene"""
        self.engine_running = False
        self.engine.running = False
        print("Scene stopped")
        self.update_status("Scene stopped")

    def reset_scene(self):
        """Reset the current scene to initial state"""
        if self.engine.current_scene:
            # Reload scene from template or reset positions
            scene_name = self.engine.current_scene.name
            self.update_status(f"Scene '{scene_name}' reset")
            print(f"Scene '{scene_name}' reset to initial state")

    def engine_loop(self):
        """Engine update loop"""
        while self.engine_running:
            try:
                self.engine.run_frame()
                time.sleep(1/60)  # 60 FPS
            except Exception as e:
                print(f"Engine error: {e}")
                break

    def clear_scene(self):
        """Clear the current scene"""
        if messagebox.askyesno("Clear Scene", "Clear all objects from the scene?"):
            self.engine.current_scene.clear()
            self.selected_object = None
            self.refresh_hierarchy()
            self.clear_properties()
            self.project_modified = True
            self.update_status("Scene cleared")

    def undo(self):
        """Undo last action"""
        # TODO: Implement undo system
        pass

    def redo(self):
        """Redo last undone action"""
        # TODO: Implement redo system
        pass

    def show_about(self):
        """Show about dialog with comprehensive engine information"""
        about_text = """Axarion Engine v1.0
        
🎮 2D GAME ENGINE
════════════════════════════════════

ENGINE COMPONENTS:
• 2D Renderer - Pygame rendering system
• Physics Engine - Collision and gravity  
• Scene Manager - Object hierarchy
• Asset Manager - Game resource management
• Input System - Keyboard and mouse

AXSCRIPT LANGUAGE:
• Custom scripting language for games
• Lexer, Parser and Interpreter
• Built-in game functions
• Real-time code execution

EDITOR FEATURES:
• Visual Scene Editor with drag & drop
• Object Hierarchy panel
• Properties Editor
• Script Editor with syntax highlighting
• Project Management system

SUPPORTED GAME TYPES:
🏃 Platformers - Jump games
🔫 Shooters - Action games  
🧩 Puzzle - Logic games
⚔️ RPG - Role-playing games
🏎️ Racing - Racing games

SYSTEM:
Python 3.11+ | Pygame 2.6.1+ | Tkinter GUI
JSON projects | Cross-platform support

© 2025 Axarion Engine - Professional 2D Game Engine"""
        
        # Create custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("About Axarion Engine")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"500x600+{x}+{y}")
        
        # Content frame with scrolling
        canvas = tk.Canvas(dialog, bg='#2b2b2b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # About text
        text_label = tk.Label(
            scrollable_frame, 
            text=about_text,
            font=("Consolas", 10),
            bg="#2b2b2b",
            fg="#ffffff",
            justify=tk.LEFT,
            padx=20,
            pady=20
        )
        text_label.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(buttons_frame, text="Documentation", 
                  command=lambda: self.show_documentation()).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Engine Status", 
                  command=lambda: self.show_engine_status()).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Close", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_documentation(self):
        """Show engine documentation"""
        doc_text = """AXARION ENGINE - DOCUMENTATION
        
BASIC USAGE:
1. Create a new project (File -> New Project)
2. Add objects to scene (Add Rectangle/Circle)
3. Set object properties in Properties panel
4. Write AXScript code for object behavior
5. Run the scene (Scene -> Run Scene)

AXSCRIPT EXAMPLES:
// Object movement
function update() {
    move(100 * deltaTime, 0);
}

// Keyboard input
if (keyPressed("SPACE")) {
    jump();
}

// Collision detection
var nearObjects = findNearObjects(50);

GAME OBJECTS:
• Rectangle - Rectangular objects
• Circle - Circular objects  
• Sprite - Textures and images

PHYSICS SYSTEM:
• Gravity - gravity, setGravity()
• Movement - move(), setVelocity()
• Collision - checkCollision()"""
        
        messagebox.showinfo("Axarion Engine - Documentation", doc_text)
    
    def show_engine_status(self):
        """Show current engine status"""
        if not self.engine:
            messagebox.showwarning("Engine Status", "Engine is not initialized!")
            return
            
        # Collect engine statistics
        scene_count = len(self.engine.scenes)
        current_scene_name = self.engine.current_scene.name if self.engine.current_scene else "None"
        object_count = len(self.engine.current_scene.game_objects) if self.engine.current_scene else 0
        physics_enabled = hasattr(self.engine, 'physics') and self.engine.physics
        
        status_text = f"""AXARION ENGINE STATUS
        
🔧 ENGINE STATE:
• Initialization: {'✓ Complete' if self.engine else '✗ Error'}
• Pygame: {'✓ Active' if pygame.get_init() else '✗ Inactive'}
• Renderer: {'✓ Ready' if self.engine.renderer else '✗ Unavailable'}
• Physics: {'✓ Active' if physics_enabled else '✗ Inactive'}

📦 PROJECT INFO:
• Total scenes: {scene_count}
• Current scene: {current_scene_name}
• Objects in scene: {object_count}
• Project status: {'✓ Saved' if not self.project_modified else '⚠ Unsaved changes'}

🎮 ENGINE RUNTIME:
• FPS Target: 60
• Engine running: {'✓ Yes' if self.engine_running else '✗ No'}
• Active scripts: {self.count_active_scripts()}

🖥️ SYSTEM INFO:
• Python: {sys.version.split()[0]}
• Pygame: {pygame.version.ver}
• Platform: {sys.platform}"""
        
        messagebox.showinfo("Engine Status", status_text)
    
    def count_active_scripts(self):
        """Count objects with scripts in current scene"""
        if not self.engine.current_scene:
            return 0
        return len([obj for obj in self.engine.current_scene.get_all_objects() 
                   if obj.script_code.strip()])

    def update_status(self, message):
        """Update status bar with engine information"""
        # Add engine runtime info to status
        engine_info = ""
        if self.engine and self.engine.current_scene:
            obj_count = len(self.engine.current_scene.game_objects)
            script_count = self.count_active_scripts()
            engine_info = f" | Objects: {obj_count} | Scripts: {script_count}"
            
        if self.engine_running:
            engine_info += " | 🎮 ENGINE RUNNING"
        
        full_message = f"{message}{engine_info}"
        self.status_bar.config(text=full_message)
        self.root.update_idletasks()

    def show_performance(self):
        """Show engine performance monitor"""
        try:
            import psutil
        except ImportError:
            messagebox.showerror("Missing Package", "psutil package is required for performance monitoring.\nInstalling psutil...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
            import psutil
        
        import threading
        
        # Create performance window
        perf_window = tk.Toplevel(self.root)
        perf_window.title("Engine Performance Monitor")
        perf_window.geometry("400x300")
        
        # Performance text
        perf_text = tk.Text(perf_window, font=("Consolas", 10))
        perf_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        def update_performance():
            try:
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                
                perf_info = f"""AXARION ENGINE PERFORMANCE
                
🖥️ SYSTEM RESOURCES:
CPU Usage: {cpu_percent:.1f}%
Memory: {memory.percent:.1f}% ({memory.used//1024//1024} MB)
Available: {memory.available//1024//1024} MB

🎮 ENGINE METRICS:
Target FPS: 60
Engine Status: {'Running' if self.engine_running else 'Stopped'}
Scene Objects: {len(self.engine.current_scene.game_objects) if self.engine.current_scene else 0}
Active Scripts: {self.count_active_scripts()}

🖼️ RENDERER:
Resolution: {self.engine.width}x{self.engine.height}
Pygame Version: {pygame.version.ver}
SDL Version: {pygame.version.SDL}

⚡ PHYSICS:
Physics Enabled: {hasattr(self.engine, 'physics') and self.engine.physics}
Delta Time: Variable (60 FPS target)"""
                
                perf_text.delete(1.0, tk.END)
                perf_text.insert(1.0, perf_info)
                
                if perf_window.winfo_exists():
                    perf_window.after(1000, update_performance)
            except:
                pass
        
        update_performance()
    
    def restart_engine(self):
        """Restart the engine"""
        if messagebox.askyesno("Restart Engine", "Restart Axarion Engine? Unsaved changes will be lost."):
            self.stop_scene()
            self.engine.cleanup()
            self.init_engine()
            self.update_status("Engine restarted")
    
    def show_engine_settings(self):
        """Show engine configuration settings"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Engine Settings")
        settings_window.geometry("350x400")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Resolution settings
        res_frame = ttk.LabelFrame(settings_window, text="Resolution")
        res_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(res_frame, text="Width:").grid(row=0, column=0, padx=5, pady=5)
        width_var = tk.StringVar(value=str(self.engine.width))
        ttk.Entry(res_frame, textvariable=width_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(res_frame, text="Height:").grid(row=1, column=0, padx=5, pady=5)
        height_var = tk.StringVar(value=str(self.engine.height))
        ttk.Entry(res_frame, textvariable=height_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        # Performance settings
        perf_frame = ttk.LabelFrame(settings_window, text="Performance")
        perf_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(perf_frame, text="Target FPS:").grid(row=0, column=0, padx=5, pady=5)
        fps_var = tk.StringVar(value="60")
        ttk.Entry(perf_frame, textvariable=fps_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        # Physics settings
        physics_frame = ttk.LabelFrame(settings_window, text="Physics")
        physics_frame.pack(fill=tk.X, padx=10, pady=5)
        
        physics_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(physics_frame, text="Enable Physics", 
                       variable=physics_enabled).pack(anchor=tk.W, padx=5, pady=5)
        
        def apply_settings():
            try:
                # Apply resolution (requires restart)
                new_width = int(width_var.get())
                new_height = int(height_var.get())
                new_fps = int(fps_var.get())
                
                if new_width != self.engine.width or new_height != self.engine.height:
                    messagebox.showinfo("Settings", "Resolution change requires engine restart.")
                
                self.engine.fps = new_fps
                self.update_status(f"Engine settings updated (FPS: {new_fps})")
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid values in settings!")
        
        # Buttons
        btn_frame = ttk.Frame(settings_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Apply", command=apply_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def show_scene_properties(self):
        """Show current scene properties"""
        if not self.engine.current_scene:
            messagebox.showwarning("No Scene", "No scene is loaded!")
            return
        
        scene = self.engine.current_scene
        props_text = f"""SCENE PROPERTIES: {scene.name}
        
📦 OBJECTS:
• Total objects: {len(scene.game_objects)}
• Visible objects: {len([obj for obj in scene.get_all_objects() if obj.visible])}
• Active objects: {len([obj for obj in scene.get_all_objects() if obj.active])}

🎨 APPEARANCE:
• Background Color: {scene.background_color}
• Camera Position: ({scene.camera_x}, {scene.camera_y})

📝 SCRIPTING:
• Objects with scripts: {self.count_active_scripts()}
• Total code: {sum(len(obj.script_code) for obj in scene.get_all_objects())} characters

📊 RENDER ORDER:
{chr(10).join([f"{i+1}. {scene.game_objects[obj_id].name} ({obj_id})" for i, obj_id in enumerate(scene.object_order)])}"""
        
        messagebox.showinfo("Scene Properties", props_text)

    def on_closing(self):
        """Handle application closing"""
        if self.project_modified:
            result = messagebox.askyesnocancel("Exit", "Save project before exiting?")
            if result is True:
                self.save_project()
            elif result is None:
                return

        # Stop engine
        self.stop_scene()

        # Cleanup
        if self.engine:
            self.engine.cleanup()

        self.root.quit()
        self.root.destroy()

    def create_platformer_scene(self):
        """Create a platformer game template"""
        if messagebox.askyesno("Create Template", "Create a new platformer scene? This will replace current scene."):
            try:
                scene = create_template_scene("platformer")
                self.engine.scenes["Platformer"] = scene
                self.engine.current_scene = scene
                self.refresh_hierarchy()
                self.update_status("Platformer scene created with player, platforms and scripts")
                print("Platformer template created with scripted objects")
            except Exception as e:
                messagebox.showerror("Template Error", f"Failed to create platformer: {e}")

    def create_puzzle_scene(self):
        """Create a puzzle game template"""
        if messagebox.askyesno("Create Template", "Create a new puzzle scene? This will replace current scene."):
            try:
                scene = create_template_scene("puzzle")
                self.engine.scenes["Puzzle"] = scene
                self.engine.current_scene = scene
                self.refresh_hierarchy()
                self.update_status("Puzzle scene created with interactive objects and scripts")
                print("Puzzle template created with scripted objects")
            except Exception as e:
                messagebox.showerror("Template Error", f"Failed to create puzzle: {e}")

    def create_shooter_scene(self):
        """Create a shooter game template"""
        if messagebox.askyesno("Create Template", "Create a new shooter scene? This will replace current scene."):
            try:
                scene = create_template_scene("shooter")
                self.engine.scenes["Shooter"] = scene
                self.engine.current_scene = scene
                self.refresh_hierarchy()
                self.update_status("Shooter scene created with player, enemies and scripts")
                print("Shooter template created with scripted objects")
            except Exception as e:
                messagebox.showerror("Template Error", f"Failed to create shooter: {e}")

    def edit_script(self):
        """Open script editor for selected object"""
        if self.selected_object:
            if self.script_editor:
                self.script_editor.set_object(self.selected_object)
                self.script_editor.show()
            else:
                messagebox.showinfo("Script Editor", "Script editor not initialized")

    def test_script(self):
        """Test the script of selected object"""
        if not self.selected_object:
            messagebox.showwarning("No Object", "No object selected")
            return

        if not self.selected_object.script_code.strip():
            messagebox.showinfo("No Script", "Object has no script to test")
            return

        try:
            from scripting.axscript_interpreter import AXScriptInterpreter
            interpreter = AXScriptInterpreter()

            result = interpreter.execute(self.selected_object.script_code, self.selected_object)

            if result["success"]:
                message = f"Script executed successfully!\n"
                if result["output"]:
                    message += f"\nOutput:\n{result['output']}"
                else:
                    message += "\nNo output produced."
                messagebox.showinfo("Script Test", message)
            else:
                messagebox.showerror("Script Error", f"Script failed:\n{result['error']}")

        except Exception as e:
            messagebox.showerror("Test Error", f"Failed to test script: {e}")

    # Update properties display if needed
    def setup_properties(self):
        """Setup object properties UI"""
        # Clear existing properties
        properties_frame = ttk.LabelFrame(self.left_panel, text="Properties")
        properties_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.properties_frame = properties_frame

        if not self.selected_object:
            ttk.Label(self.properties_frame, text="No object selected").pack(pady=10)
            return

        # Transform properties
        transform_frame = ttk.LabelFrame(self.properties_frame, text="Transform")
        transform_frame.pack(fill=tk.BOTH, expand=True, pady=2)

        ttk.Label(transform_frame, text="Position X:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.pos_x_var = tk.StringVar()
        self.pos_x_entry = ttk.Entry(transform_frame, textvariable=self.pos_x_var, width=10)
        self.pos_x_entry.grid(row=0, column=1, padx=5, pady=2)
        self.pos_x_var.trace('w', self.on_property_changed)

        ttk.Label(transform_frame, text="Position Y:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.pos_y_var = tk.StringVar()
        self.pos_y_entry = ttk.Entry(transform_frame, textvariable=self.pos_y_var, width=10)
        self.pos_y_entry.grid(row=1, column=1, padx=5, pady=2)
        self.pos_y_var.trace('w', self.on_property_changed)

        # Object properties
        object_frame = ttk.LabelFrame(self.properties_frame, text="Object")
        object_frame.pack(fill=tk.BOTH, expand=True, pady=2)

        ttk.Label(object_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(object_frame, textvariable=self.name_var, width=20)
        self.name_entry.grid(row=0, column=1, padx=5, pady=2)
        self.name_var.trace('w', self.on_property_changed)

        # Script section
        script_frame = ttk.LabelFrame(self.properties_frame, text="Script")
        script_frame.pack(fill=tk.BOTH, expand=True, pady=2)

        # Script preview
        self.script_preview = tk.Text(script_frame, height=8, width=40, 
                                     font=("Consolas", 9), wrap=tk.WORD)
        self.script_preview.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        script_buttons = ttk.Frame(script_frame)
        script_buttons.pack(fill=tk.X, padx=2, pady=2)

        ttk.Button(script_buttons, text="Edit Script", 
                  command=self.edit_script).pack(side=tk.LEFT, padx=2)
        ttk.Button(script_buttons, text="Test Script", 
                  command=self.test_script).pack(side=tk.LEFT, padx=2)

    def update_properties(self):
        """Update property panel with selected object data"""
        self.setup_properties()

        if not self.selected_object:
            return

        obj = self.selected_object

        # Update transform properties
        self.pos_x_var.set(str(obj.position[0]))
        self.pos_y_var.set(str(obj.position[1]))

        # Update object properties
        self.name_var.set(obj.name)

        # Update script preview if it exists
        if hasattr(self, 'script_preview') and self.selected_object:
            self.script_preview.delete(1.0, tk.END)
            if self.selected_object.script_code:
                self.script_preview.insert(1.0, self.selected_object.script_code)
            else:
                self.script_preview.insert(1.0, "// No script code\n// Click 'Edit Script' to add code")