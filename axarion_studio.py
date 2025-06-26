
"""
Axarion Studio - Professional Game Development IDE
Advanced code editor for Axarion Engine with real-time error checking
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import subprocess
import threading
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys

# Import Axarion Engine components for error checking
try:
    from scripting.axscript_parser import AXScriptParser
    from scripting.axscript_interpreter import AXScriptInterpreter
    from engine.core import AxarionEngine
    from utils.file_manager import FileManager
except ImportError as e:
    print(f"Warning: Some Axarion components not available: {e}")

class SyntaxHighlighter:
    """Advanced syntax highlighter for Python and AXScript"""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.setup_tags()
    
    def setup_tags(self):
        """Configure syntax highlighting tags"""
        # Python keywords
        self.text_widget.tag_configure("python_keyword", foreground="#FF7F50")
        self.text_widget.tag_configure("python_string", foreground="#98FB98")
        self.text_widget.tag_configure("python_comment", foreground="#87CEEB")
        self.text_widget.tag_configure("python_function", foreground="#FFD700")
        self.text_widget.tag_configure("python_number", foreground="#DDA0DD")
        
        # AXScript keywords
        self.text_widget.tag_configure("axscript_keyword", foreground="#FFA500")
        self.text_widget.tag_configure("axscript_function", foreground="#40E0D0")
        self.text_widget.tag_configure("axscript_builtin", foreground="#FF69B4")
        
        # Error highlighting
        self.text_widget.tag_configure("error", background="#FF4444", foreground="white")
        self.text_widget.tag_configure("warning", background="#FFAA00", foreground="black")
    
    def highlight_python(self, content: str):
        """Highlight Python syntax"""
        python_keywords = [
            "def", "class", "if", "else", "elif", "for", "while", "try", "except",
            "finally", "with", "as", "import", "from", "return", "yield", "break",
            "continue", "pass", "lambda", "and", "or", "not", "in", "is", "True",
            "False", "None", "global", "nonlocal", "async", "await"
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines):
            # Keywords
            for keyword in python_keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                for match in re.finditer(pattern, line):
                    start = f"{line_num + 1}.{match.start()}"
                    end = f"{line_num + 1}.{match.end()}"
                    self.text_widget.tag_add("python_keyword", start, end)
            
            # Strings
            string_patterns = [r'"[^"]*"', r"'[^']*'", r'""".*?"""', r"'''.*?'''"]
            for pattern in string_patterns:
                for match in re.finditer(pattern, line):
                    start = f"{line_num + 1}.{match.start()}"
                    end = f"{line_num + 1}.{match.end()}"
                    self.text_widget.tag_add("python_string", start, end)
            
            # Comments
            comment_match = re.search(r'#.*$', line)
            if comment_match:
                start = f"{line_num + 1}.{comment_match.start()}"
                end = f"{line_num + 1}.{comment_match.end()}"
                self.text_widget.tag_add("python_comment", start, end)
            
            # Functions
            func_match = re.search(r'def\s+(\w+)', line)
            if func_match:
                start = f"{line_num + 1}.{func_match.start(1)}"
                end = f"{line_num + 1}.{func_match.end(1)}"
                self.text_widget.tag_add("python_function", start, end)
            
            # Numbers
            for match in re.finditer(r'\b\d+\.?\d*\b', line):
                start = f"{line_num + 1}.{match.start()}"
                end = f"{line_num + 1}.{match.end()}"
                self.text_widget.tag_add("python_number", start, end)
    
    def highlight_axscript(self, content: str):
        """Highlight AXScript syntax"""
        axscript_keywords = [
            "function", "var", "if", "else", "while", "for", "return",
            "true", "false", "null", "class"
        ]
        
        axscript_builtins = [
            "move", "rotate", "keyPressed", "print", "setProperty", "getProperty",
            "playSound", "createExplosion", "distance", "random", "time"
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines):
            # Keywords
            for keyword in axscript_keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                for match in re.finditer(pattern, line):
                    start = f"{line_num + 1}.{match.start()}"
                    end = f"{line_num + 1}.{match.end()}"
                    self.text_widget.tag_add("axscript_keyword", start, end)
            
            # Built-in functions
            for builtin in axscript_builtins:
                pattern = r'\b' + re.escape(builtin) + r'\b'
                for match in re.finditer(pattern, line):
                    start = f"{line_num + 1}.{match.start()}"
                    end = f"{line_num + 1}.{match.end()}"
                    self.text_widget.tag_add("axscript_builtin", start, end)
            
            # Functions
            func_match = re.search(r'function\s+(\w+)', line)
            if func_match:
                start = f"{line_num + 1}.{func_match.start(1)}"
                end = f"{line_num + 1}.{func_match.end(1)}"
                self.text_widget.tag_add("axscript_function", start, end)

class ErrorChecker:
    """Real-time error checking for Python and AXScript"""
    
    def __init__(self):
        self.axscript_parser = None
        try:
            self.axscript_parser = AXScriptParser()
        except:
            pass
    
    def check_python_syntax(self, code: str) -> List[Dict]:
        """Check Python syntax for errors"""
        errors = []
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            errors.append({
                'type': 'error',
                'line': e.lineno or 1,
                'message': f"Syntax Error: {e.msg}",
                'column': e.offset or 0
            })
        except Exception as e:
            errors.append({
                'type': 'error',
                'line': 1,
                'message': f"Error: {str(e)}",
                'column': 0
            })
        
        # Check for common game development issues
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for undefined Axarion components
            if 'GameObject' in line and 'from engine.game_object import GameObject' not in code:
                errors.append({
                    'type': 'warning',
                    'line': i,
                    'message': "GameObject used but not imported",
                    'column': line.find('GameObject')
                })
            
            if 'AxarionEngine' in line and 'from engine.core import AxarionEngine' not in code:
                errors.append({
                    'type': 'warning',
                    'line': i,
                    'message': "AxarionEngine used but not imported",
                    'column': line.find('AxarionEngine')
                })
        
        return errors
    
    def check_axscript_syntax(self, code: str) -> List[Dict]:
        """Check AXScript syntax for errors"""
        errors = []
        
        if not self.axscript_parser:
            return [{'type': 'warning', 'line': 1, 'message': 'AXScript parser not available', 'column': 0}]
        
        try:
            self.axscript_parser.parse(code)
        except Exception as e:
            error_msg = str(e)
            line_num = 1
            
            # Try to extract line number from error message
            line_match = re.search(r'line (\d+)', error_msg)
            if line_match:
                line_num = int(line_match.group(1))
            
            errors.append({
                'type': 'error',
                'line': line_num,
                'message': f"AXScript Error: {error_msg}",
                'column': 0
            })
        
        # Check for common AXScript issues
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for missing semicolons (common issue)
            stripped = line.strip()
            if (stripped and 
                not stripped.startswith('//') and 
                not stripped.startswith('function') and
                not stripped.startswith('if') and
                not stripped.startswith('while') and
                not stripped.startswith('}') and
                not stripped.endswith(';') and
                not stripped.endswith('{') and
                '=' in stripped):
                errors.append({
                    'type': 'warning',
                    'line': i,
                    'message': "Missing semicolon",
                    'column': len(line)
                })
        
        return errors

class FileExplorer:
    """File explorer panel for project management"""
    
    def __init__(self, parent, editor_callback):
        self.parent = parent
        self.editor_callback = editor_callback
        self.current_project = None
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup file explorer UI"""
        # Toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(toolbar, text="📁 Open Project", command=self.open_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📄 New File", command=self.new_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗂️ New Folder", command=self.new_folder).pack(side=tk.LEFT, padx=2)
        
        # Tree view
        self.tree = ttk.Treeview(self.frame)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind events
        self.tree.bind('<Double-1>', self.on_file_double_click)
        self.tree.bind('<Button-3>', self.on_right_click)
    
    def open_project(self):
        """Open project directory"""
        directory = filedialog.askdirectory(title="Select Project Directory")
        if directory:
            self.current_project = directory
            self.refresh_tree()
    
    def refresh_tree(self):
        """Refresh file tree"""
        if not self.current_project:
            return
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add files and folders
        self.add_directory_to_tree("", self.current_project)
    
    def add_directory_to_tree(self, parent, path):
        """Add directory contents to tree"""
        try:
            for item in sorted(os.listdir(path)):
                if item.startswith('.'):
                    continue
                
                item_path = os.path.join(path, item)
                
                if os.path.isdir(item_path):
                    # Folder
                    folder_id = self.tree.insert(parent, 'end', text=f"📁 {item}", 
                                               values=[item_path], open=False)
                    self.add_directory_to_tree(folder_id, item_path)
                else:
                    # File
                    icon = self.get_file_icon(item)
                    self.tree.insert(parent, 'end', text=f"{icon} {item}", 
                                   values=[item_path])
        except PermissionError:
            pass
    
    def get_file_icon(self, filename):
        """Get icon for file type"""
        ext = os.path.splitext(filename)[1].lower()
        icons = {
            '.py': '🐍',
            '.ax': '⚡',
            '.axs': '⚡',
            '.json': '📋',
            '.png': '🖼️',
            '.jpg': '🖼️',
            '.wav': '🔊',
            '.mp3': '🎵',
            '.txt': '📄',
            '.md': '📖'
        }
        return icons.get(ext, '📄')
    
    def on_file_double_click(self, event):
        """Handle file double click"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            file_path = self.tree.item(item, 'values')[0]
            
            if os.path.isfile(file_path):
                self.editor_callback(file_path)
    
    def new_file(self):
        """Create new file"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please open a project first")
            return
        
        filename = tk.simpledialog.askstring("New File", "Enter filename:")
        if filename:
            file_path = os.path.join(self.current_project, filename)
            try:
                with open(file_path, 'w') as f:
                    f.write("")
                self.refresh_tree()
                self.editor_callback(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create file: {e}")
    
    def new_folder(self):
        """Create new folder"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please open a project first")
            return
        
        foldername = tk.simpledialog.askstring("New Folder", "Enter folder name:")
        if foldername:
            folder_path = os.path.join(self.current_project, foldername)
            try:
                os.makedirs(folder_path, exist_ok=True)
                self.refresh_tree()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create folder: {e}")
    
    def on_right_click(self, event):
        """Handle right click context menu"""
        # TODO: Implement context menu
        pass

class ErrorPanel:
    """Error and warning display panel"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.errors = []
    
    def setup_ui(self):
        """Setup error panel UI"""
        # Header
        header = ttk.Frame(self.frame)
        header.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(header, text="🚨 Problems", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        self.error_count = ttk.Label(header, text="0 errors, 0 warnings")
        self.error_count.pack(side=tk.RIGHT)
        
        # Error list
        self.error_tree = ttk.Treeview(self.frame, columns=('type', 'line', 'message'), show='headings', height=6)
        self.error_tree.heading('type', text='Type')
        self.error_tree.heading('line', text='Line')
        self.error_tree.heading('message', text='Message')
        
        self.error_tree.column('type', width=80)
        self.error_tree.column('line', width=60)
        self.error_tree.column('message', width=400)
        
        self.error_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def update_errors(self, errors: List[Dict]):
        """Update error display"""
        self.errors = errors
        
        # Clear existing items
        for item in self.error_tree.get_children():
            self.error_tree.delete(item)
        
        # Add new errors
        error_count = 0
        warning_count = 0
        
        for error in errors:
            icon = "🔴" if error['type'] == 'error' else "🟡"
            self.error_tree.insert('', 'end', values=(
                f"{icon} {error['type'].title()}",
                error['line'],
                error['message']
            ))
            
            if error['type'] == 'error':
                error_count += 1
            else:
                warning_count += 1
        
        # Update count
        self.error_count.config(text=f"{error_count} errors, {warning_count} warnings")

class GameTemplateManager:
    """Manager for game templates and snippets"""
    
    def __init__(self):
        self.templates = {
            "Basic Game": '''from engine.core import AxarionEngine
from engine.game_object import GameObject

# Create engine
engine = AxarionEngine(800, 600, "My Game")
engine.initialize()

# Create scene
scene = engine.create_scene("Main")
engine.current_scene = scene

# Create player
player = GameObject("Player", "rectangle")
player.position = (100, 100)
player.set_property("color", (100, 200, 255))

# Add movement script
player.script_code = """
var speed = 200;

function update() {
    if (keyPressed("ArrowLeft")) {
        move(-speed * 0.016, 0);
    }
    if (keyPressed("ArrowRight")) {
        move(speed * 0.016, 0);
    }
}
"""

scene.add_object(player)
engine.run()''',
            
            "Platformer Game": '''from engine.core import AxarionEngine
from engine.game_object import GameObject

# Create platformer game
engine = AxarionEngine(800, 600, "Platformer")
engine.initialize()

scene = engine.create_scene("Level1")
engine.current_scene = scene

# Create player with physics
player = GameObject("Player", "rectangle")
player.position = (100, 400)
player.set_property("color", (100, 200, 255))
player.set_property("mass", 1.0)

# Platformer movement
player.script_code = """
var speed = 300;
var jumpForce = 400;

function update() {
    if (keyPressed("ArrowLeft")) {
        applyForce(-speed * 0.016, 0);
    }
    if (keyPressed("ArrowRight")) {
        applyForce(speed * 0.016, 0);
    }
    if (keyJustPressed("Space") && isOnGround()) {
        jump(jumpForce);
    }
}
"""

# Create platform
platform = GameObject("Platform", "rectangle")
platform.position = (400, 500)
platform.set_property("width", 200)
platform.set_property("height", 20)
platform.set_property("color", (100, 100, 100))

scene.add_object(player)
scene.add_object(platform)
engine.run()''',

            "AXScript Functions": '''// Common AXScript functions for game objects

var speed = 150;
var health = 100;

function update() {
    // Movement
    if (keyPressed("w")) move(0, -speed * 0.016);
    if (keyPressed("s")) move(0, speed * 0.016);
    if (keyPressed("a")) move(-speed * 0.016, 0);
    if (keyPressed("d")) move(speed * 0.016, 0);
    
    // Shooting
    if (keyJustPressed("Space")) {
        var mousePos = getMousePos();
        createBullet(mousePos.x, mousePos.y, 400);
    }
    
    // Health system
    if (health <= 0) {
        createExplosion(getProperty("position").x, getProperty("position").y);
        destroy();
    }
}

function takeDamage(amount) {
    health -= amount;
    print("Health: " + health);
}'''
        }
    
    def get_templates(self):
        """Get all available templates"""
        return list(self.templates.keys())
    
    def get_template_code(self, template_name):
        """Get code for specific template"""
        return self.templates.get(template_name, "")

class AxarionStudio:
    """Main Axarion Studio IDE class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Axarion Studio - Game Development IDE")
        self.root.geometry("1400x900")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Core components
        self.error_checker = ErrorChecker()
        self.template_manager = GameTemplateManager()
        self.file_manager = FileManager()
        
        # Current file info
        self.current_file = None
        self.current_file_type = None
        self.unsaved_changes = False
        
        # Setup UI
        self.setup_ui()
        self.setup_menu()
        
        # Start real-time error checking
        self.start_error_checking()
    
    def setup_ui(self):
        """Setup main UI layout"""
        # Main container
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (File Explorer)
        left_frame = ttk.Frame(main_paned, width=250)
        main_paned.add(left_frame, weight=0)
        
        self.file_explorer = FileExplorer(left_frame, self.open_file)
        self.file_explorer.frame.pack(fill=tk.BOTH, expand=True)
        
        # Right panel (Editor + Problems)
        right_paned = ttk.PanedWindow(main_paned, orient=tk.VERTICAL)
        main_paned.add(right_paned, weight=1)
        
        # Editor frame
        editor_frame = ttk.Frame(right_paned)
        right_paned.add(editor_frame, weight=1)
        
        # Editor toolbar
        self.setup_editor_toolbar(editor_frame)
        
        # Code editor
        self.setup_code_editor(editor_frame)
        
        # Problems panel
        problems_frame = ttk.Frame(right_paned, height=200)
        right_paned.add(problems_frame, weight=0)
        
        self.error_panel = ErrorPanel(problems_frame)
        self.error_panel.frame.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.setup_status_bar()
    
    def setup_editor_toolbar(self, parent):
        """Setup editor toolbar"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # File operations
        ttk.Button(toolbar, text="💾 Save", command=self.save_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄 Save As", command=self.save_file_as).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Templates
        ttk.Label(toolbar, text="Template:").pack(side=tk.LEFT, padx=5)
        self.template_var = tk.StringVar()
        template_combo = ttk.Combobox(toolbar, textvariable=self.template_var, 
                                    values=self.template_manager.get_templates(), 
                                    state="readonly", width=15)
        template_combo.pack(side=tk.LEFT, padx=2)
        template_combo.bind('<<ComboboxSelected>>', self.insert_template)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Game controls
        ttk.Button(toolbar, text="▶️ Run Game", command=self.run_game).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🛑 Stop Game", command=self.stop_game).pack(side=tk.LEFT, padx=2)
        
        # File info
        self.file_info = ttk.Label(toolbar, text="No file open")
        self.file_info.pack(side=tk.RIGHT, padx=5)
    
    def setup_code_editor(self, parent):
        """Setup code editor with syntax highlighting"""
        editor_container = ttk.Frame(parent)
        editor_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # Line numbers frame
        line_frame = tk.Frame(editor_container, width=50, bg='#f0f0f0')
        line_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.line_numbers = tk.Text(line_frame, width=4, bg='#f0f0f0', 
                                  state=tk.DISABLED, wrap=tk.NONE)
        self.line_numbers.pack(fill=tk.BOTH, expand=True)
        
        # Code editor
        self.code_editor = scrolledtext.ScrolledText(editor_container, 
                                                   wrap=tk.NONE,
                                                   bg='#1e1e1e',
                                                   fg='#ffffff',
                                                   insertbackground='white',
                                                   font=('Consolas', 11))
        self.code_editor.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Setup syntax highlighter
        self.highlighter = SyntaxHighlighter(self.code_editor)
        
        # Bind events
        self.code_editor.bind('<KeyRelease>', self.on_code_change)
        self.code_editor.bind('<Button-1>', self.on_code_change)
        self.code_editor.bind('<MouseWheel>', self.sync_scroll)
        self.code_editor.bind('<Configure>', self.update_line_numbers)
        
        # Auto-completion
        self.code_editor.bind('<KeyPress>', self.on_key_press)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_text = ttk.Label(self.status_bar, text="Ready")
        self.status_text.pack(side=tk.LEFT, padx=5)
        
        # Cursor position
        self.cursor_pos = ttk.Label(self.status_bar, text="Line 1, Col 1")
        self.cursor_pos.pack(side=tk.RIGHT, padx=5)
        
        # File type
        self.file_type_label = ttk.Label(self.status_bar, text="")
        self.file_type_label.pack(side=tk.RIGHT, padx=5)
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New File", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open File", command=self.open_file_dialog, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=lambda: self.code_editor.edit_undo(), accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=lambda: self.code_editor.edit_redo(), accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.code_editor.event_generate("<<Cut>>"), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=lambda: self.code_editor.event_generate("<<Copy>>"), accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=lambda: self.code_editor.event_generate("<<Paste>>"), accelerator="Ctrl+V")
        
        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="Run Game", command=self.run_game, accelerator="F5")
        game_menu.add_command(label="Stop Game", command=self.stop_game, accelerator="Shift+F5")
        game_menu.add_separator()
        game_menu.add_command(label="Create Asset Manager", command=self.create_asset_manager)
        game_menu.add_command(label="Game Templates", command=self.show_templates)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="AXScript Documentation", command=self.show_axscript_docs)
        help_menu.add_command(label="Axarion Engine Guide", command=self.show_engine_docs)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file_dialog())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-Shift-s>', lambda e: self.save_file_as())
        self.root.bind('<F5>', lambda e: self.run_game())
        self.root.bind('<Shift-F5>', lambda e: self.stop_game())
    
    def on_code_change(self, event=None):
        """Handle code changes"""
        self.unsaved_changes = True
        self.update_title()
        self.update_line_numbers()
        self.update_cursor_position()
        
        # Trigger syntax highlighting
        content = self.code_editor.get('1.0', tk.END)
        
        if self.current_file_type == 'python':
            self.highlighter.highlight_python(content)
        elif self.current_file_type == 'axscript':
            self.highlighter.highlight_axscript(content)
    
    def on_key_press(self, event):
        """Handle key press for auto-completion"""
        if event.keysym == 'Tab':
            # Auto-indent
            cursor_pos = self.code_editor.index(tk.INSERT)
            line_start = cursor_pos.split('.')[0] + '.0'
            line_content = self.code_editor.get(line_start, cursor_pos)
            
            if line_content.strip():
                return  # Don't auto-indent if there's content
            
            # Calculate indentation
            prev_line_num = int(cursor_pos.split('.')[0]) - 1
            if prev_line_num > 0:
                prev_line_start = f"{prev_line_num}.0"
                prev_line_end = f"{prev_line_num}.end"
                prev_line = self.code_editor.get(prev_line_start, prev_line_end)
                
                # Count leading spaces
                indent = len(prev_line) - len(prev_line.lstrip())
                
                # Add extra indent for certain keywords
                if any(keyword in prev_line for keyword in ['if', 'def', 'class', 'for', 'while', 'function', 'try']):
                    if prev_line.strip().endswith(':') or prev_line.strip().endswith('{'):
                        indent += 4
                
                self.code_editor.insert(tk.INSERT, ' ' * indent)
            return 'break'
    
    def update_line_numbers(self, event=None):
        """Update line numbers"""
        content = self.code_editor.get('1.0', tk.END)
        lines = content.split('\n')
        
        line_numbers_content = '\n'.join(str(i+1) for i in range(len(lines)-1))
        
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_content)
        self.line_numbers.config(state=tk.DISABLED)
    
    def update_cursor_position(self):
        """Update cursor position in status bar"""
        cursor_pos = self.code_editor.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        self.cursor_pos.config(text=f"Line {line}, Col {int(col)+1}")
    
    def sync_scroll(self, event):
        """Synchronize scrolling between editor and line numbers"""
        self.line_numbers.yview_moveto(self.code_editor.yview()[0])
    
    def update_title(self):
        """Update window title"""
        title = "Axarion Studio"
        if self.current_file:
            filename = os.path.basename(self.current_file)
            if self.unsaved_changes:
                filename += " *"
            title += f" - {filename}"
        self.root.title(title)
    
    def new_file(self):
        """Create new file"""
        if self.unsaved_changes:
            if not self.confirm_unsaved_changes():
                return
        
        self.code_editor.delete('1.0', tk.END)
        self.current_file = None
        self.current_file_type = None
        self.unsaved_changes = False
        self.update_title()
        self.file_info.config(text="New file")
        self.file_type_label.config(text="")
    
    def open_file_dialog(self):
        """Open file dialog"""
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("Python files", "*.py"),
                ("AXScript files", "*.ax *.axs"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.open_file(file_path)
    
    def open_file(self, file_path):
        """Open file in editor"""
        if self.unsaved_changes:
            if not self.confirm_unsaved_changes():
                return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.code_editor.delete('1.0', tk.END)
            self.code_editor.insert('1.0', content)
            
            self.current_file = file_path
            self.current_file_type = self.detect_file_type(file_path)
            self.unsaved_changes = False
            
            self.update_title()
            self.file_info.config(text=os.path.basename(file_path))
            self.file_type_label.config(text=self.current_file_type.upper())
            
            # Trigger syntax highlighting
            self.on_code_change()
            
            self.status_text.config(text=f"Opened: {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")
    
    def save_file(self):
        """Save current file"""
        if not self.current_file:
            self.save_file_as()
            return
        
        try:
            content = self.code_editor.get('1.0', tk.END)
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.unsaved_changes = False
            self.update_title()
            self.status_text.config(text=f"Saved: {self.current_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")
    
    def save_file_as(self):
        """Save file as new name"""
        file_path = filedialog.asksaveasfilename(
            title="Save File As",
            defaultextension=".py",
            filetypes=[
                ("Python files", "*.py"),
                ("AXScript files", "*.ax"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.current_file = file_path
            self.current_file_type = self.detect_file_type(file_path)
            self.save_file()
            self.file_info.config(text=os.path.basename(file_path))
            self.file_type_label.config(text=self.current_file_type.upper())
    
    def detect_file_type(self, file_path):
        """Detect file type from extension"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.py':
            return 'python'
        elif ext in ['.ax', '.axs']:
            return 'axscript'
        else:
            return 'text'
    
    def confirm_unsaved_changes(self):
        """Confirm unsaved changes dialog"""
        result = messagebox.askyesnocancel(
            "Unsaved Changes",
            "You have unsaved changes. Do you want to save them?"
        )
        
        if result is True:  # Yes - save
            self.save_file()
            return True
        elif result is False:  # No - don't save
            return True
        else:  # Cancel
            return False
    
    def start_error_checking(self):
        """Start real-time error checking thread"""
        def check_errors():
            while True:
                if self.current_file_type in ['python', 'axscript']:
                    content = self.code_editor.get('1.0', tk.END)
                    
                    if self.current_file_type == 'python':
                        errors = self.error_checker.check_python_syntax(content)
                    else:
                        errors = self.error_checker.check_axscript_syntax(content)
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self.error_panel.update_errors(errors))
                
                time.sleep(2)  # Check every 2 seconds
        
        error_thread = threading.Thread(target=check_errors, daemon=True)
        error_thread.start()
    
    def insert_template(self, event=None):
        """Insert selected template"""
        template_name = self.template_var.get()
        if template_name:
            template_code = self.template_manager.get_template_code(template_name)
            if template_code:
                # Insert at cursor position
                self.code_editor.insert(tk.INSERT, template_code)
                self.on_code_change()
    
    def run_game(self):
        """Run the current game"""
        if not self.current_file or self.current_file_type != 'python':
            messagebox.showwarning("Warning", "Please open a Python game file first")
            return
        
        if self.unsaved_changes:
            self.save_file()
        
        def run_in_thread():
            try:
                subprocess.run([sys.executable, self.current_file], 
                             cwd=os.path.dirname(self.current_file))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Could not run game: {e}"))
        
        threading.Thread(target=run_in_thread, daemon=True).start()
        self.status_text.config(text="Running game...")
    
    def stop_game(self):
        """Stop the running game"""
        # TODO: Implement game stopping
        self.status_text.config(text="Stopped game")
    
    def create_asset_manager(self):
        """Create asset manager code"""
        asset_code = '''# Asset Manager Setup
from assets.create_sample_assets import create_sample_assets
from engine.asset_manager import asset_manager

# Create sample assets
create_sample_assets()

# Load all assets
asset_manager.load_all_assets()

print("Assets loaded successfully!")
'''
        self.code_editor.insert(tk.INSERT, asset_code)
        self.on_code_change()
    
    def show_templates(self):
        """Show templates dialog"""
        template_window = tk.Toplevel(self.root)
        template_window.title("Game Templates")
        template_window.geometry("600x400")
        
        # Template list
        listbox = tk.Listbox(template_window)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for template in self.template_manager.get_templates():
            listbox.insert(tk.END, template)
        
        def insert_selected():
            selection = listbox.curselection()
            if selection:
                template_name = listbox.get(selection[0])
                template_code = self.template_manager.get_template_code(template_name)
                self.code_editor.insert(tk.INSERT, template_code)
                self.on_code_change()
                template_window.destroy()
        
        ttk.Button(template_window, text="Insert Template", command=insert_selected).pack(pady=5)
    
    def show_axscript_docs(self):
        """Show AXScript documentation"""
        docs = """AXScript Documentation

Basic Syntax:
- Variables: var name = value;
- Functions: function name() { }
- Comments: // single line

Built-in Functions:
- move(x, y) - Move object
- rotate(angle) - Rotate object
- keyPressed(key) - Check if key is pressed
- print(message) - Print to console
- playSound(name) - Play sound effect
- createExplosion(x, y) - Create explosion
- distance(x1, y1, x2, y2) - Calculate distance

Game Object Functions:
- setProperty(name, value) - Set object property
- getProperty(name) - Get object property
- addTag(tag) - Add tag to object
- hasTag(tag) - Check if object has tag

Physics Functions:
- applyForce(x, y) - Apply force to object
- jump(force) - Make object jump
- isOnGround() - Check if on ground
"""
        
        messagebox.showinfo("AXScript Documentation", docs)
    
    def show_engine_docs(self):
        """Show engine documentation"""
        docs = """Axarion Engine Guide

Basic Setup:
1. Create AxarionEngine instance
2. Initialize the engine
3. Create scenes and objects
4. Add scripts to objects
5. Run the game

Object Types:
- rectangle: Basic rectangle shape
- circle: Circular shape
- sprite: Image-based object
- animated_sprite: Animated frames

Common Patterns:
- Use scenes for different levels
- Add tags to group objects
- Use scripts for behavior
- Load assets with asset_manager
"""
        
        messagebox.showinfo("Axarion Engine Guide", docs)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Axarion Studio v1.0

Professional Game Development IDE for Axarion Engine

Features:
• Real-time error checking
• Syntax highlighting
• Code templates
• File explorer
• Game runner
• AXScript support

Created for game developers ❤️"""
        
        messagebox.showinfo("About Axarion Studio", about_text)
    
    def run(self):
        """Start the IDE"""
        self.status_text.config(text="Axarion Studio ready!")
        self.root.mainloop()

if __name__ == "__main__":
    # Create and run Axarion Studio
    studio = AxarionStudio()
    studio.run()

