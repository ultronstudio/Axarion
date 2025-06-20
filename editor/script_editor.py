"""
Axarion Engine Script Editor
AXScript code editor with syntax highlighting
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripting.axscript_interpreter import AXScriptInterpreter

class ScriptEditor:
    """Script editor for AXScript with syntax highlighting"""
    
    def __init__(self, parent, main_editor):
        self.parent = parent
        self.main_editor = main_editor
        self.interpreter = AXScriptInterpreter()
        self.current_object = None
        
        # Syntax highlighting patterns
        self.syntax_patterns = {
            'keyword': r'\b(var|if|else|while|for|function|return|true|false|null)\b',
            'string': r'"[^"]*"',
            'number': r'\b\d+(\.\d+)?\b',
            'comment': r'//.*$',
            'operator': r'[+\-*/=<>!&|]',
            'function_call': r'\b\w+\s*\(',
        }
        
        # Color scheme
        self.colors = {
            'keyword': '#569CD6',     # Blue
            'string': '#CE9178',      # Orange
            'number': '#B5CEA8',      # Light green
            'comment': '#6A9955',     # Green
            'operator': '#D4D4D4',    # Light gray
            'function_call': '#DCDCAA', # Yellow
            'default': '#D4D4D4'      # Default text color
        }
        
        self.setup_ui()
        # Don't load sample script automatically
    
    def setup_ui(self):
        """Setup the script editor UI"""
        # Script editor controls
        controls_frame = ttk.Frame(self.parent)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Run Script", 
                  command=self.run_script).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Validate", 
                  command=self.validate_script).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Clear", 
                  command=self.clear_script).pack(side=tk.LEFT, padx=2)
        
        # Script text area
        text_frame = ttk.Frame(self.parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create text widget with scrollbars
        self.text_widget = tk.Text(text_frame, bg='#1E1E1E', fg='#D4D4D4', 
                                  insertbackground='white', font=('Consolas', 10))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        h_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.text_widget.xview)
        
        self.text_widget.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack widgets
        self.text_widget.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Line numbers
        self.line_numbers = tk.Text(text_frame, width=4, bg='#252526', fg='#858585',
                                   font=('Consolas', 10), state=tk.DISABLED)
        self.line_numbers.grid(row=0, column=2, sticky='ns')
        
        # Configure syntax highlighting tags
        for token_type, color in self.colors.items():
            self.text_widget.tag_configure(token_type, foreground=color)
        
        # Bind events
        self.text_widget.bind('<KeyRelease>', self.on_text_change)
        self.text_widget.bind('<Button-1>', self.on_text_change)
        self.text_widget.bind('<Return>', self.on_return)
        self.text_widget.bind('<Tab>', self.on_tab)
        
        # Output area
        output_frame = ttk.LabelFrame(self.parent, text="Output")
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.output_text = tk.Text(output_frame, height=8, bg='#0C0C0C', fg='#CCCCCC',
                                  font=('Consolas', 9), state=tk.DISABLED)
        output_scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, 
                                       command=self.output_text.yview)
        self.output_text.config(yscrollcommand=output_scrollbar.set)
        
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # AXScript documentation
        docs_frame = ttk.LabelFrame(self.parent, text="AXScript Reference")
        docs_frame.pack(fill=tk.X, padx=5, pady=5)
        
        docs_text = """AXScript Quick Reference:
Variables: var name = value
Conditionals: if (condition) { ... } else { ... }
Loops: while (condition) { ... }
Functions: function name(param1, param2) { return value; }
Object access: object.property, object.method()
Built-in functions: print(), move(), rotate(), setProperty()"""
        
        docs_label = tk.Label(docs_frame, text=docs_text, justify=tk.LEFT, 
                            font=('Consolas', 8), bg='#F0F0F0')
        docs_label.pack(fill=tk.X, padx=5, pady=5)
    
    def load_sample_script(self):
        """Load a sample AXScript"""
        sample_script = '''// Sample AXScript - Bouncing Object
var speed = 150;
var direction = 1;
var bounceCount = 0;

function init() {
    print("Object initialized!");
    setProperty("color", "100,255,100");
}

function update() {
    var currentX = this.position.x;
    var currentY = this.position.y;
    
    // Move object horizontally
    move(speed * direction * 0.016, 0);
    
    // Check bounds and bounce
    if (currentX > 750) {
        direction = -1;
        bounceCount = bounceCount + 1;
        print("Bounced right! Count: " + bounceCount);
    } else if (currentX < 50) {
        direction = 1;
        bounceCount = bounceCount + 1;
        print("Bounced left! Count: " + bounceCount);
    }
    
    // Change color based on speed
    if (bounceCount > 10) {
        setProperty("color", "255,100,100");
    }
}

function onCollision(other) {
    print("Collided with: " + other.name);
    direction = -direction;
    setProperty("color", "255,255,0");
}

// Initialize the object
init();
'''
        self.text_widget.insert(tk.END, sample_script)
        self.highlight_syntax()
        self.update_line_numbers()
    
    def on_text_change(self, event=None):
        """Handle text changes"""
        self.highlight_syntax()
        self.update_line_numbers()
    
    def on_return(self, event):
        """Handle return key press for auto-indentation"""
        # Get current line
        current_line = self.text_widget.get("insert linestart", "insert lineend")
        
        # Count leading spaces
        indent_level = len(current_line) - len(current_line.lstrip())
        
        # Check if we should increase indentation
        if current_line.strip().endswith('{'):
            indent_level += 4
        
        # Insert newline with indentation
        self.text_widget.insert("insert", "\n" + " " * indent_level)
        return "break"  # Prevent default newline
    
    def on_tab(self, event):
        """Handle tab key press"""
        self.text_widget.insert("insert", "    ")  # 4 spaces
        return "break"  # Prevent default tab behavior
    
    def highlight_syntax(self):
        """Apply syntax highlighting"""
        # Clear existing tags
        for tag in self.syntax_patterns.keys():
            self.text_widget.tag_delete(tag)
        
        # Get all text
        content = self.text_widget.get("1.0", tk.END)
        
        # Apply highlighting for each pattern
        for token_type, pattern in self.syntax_patterns.items():
            for match in re.finditer(pattern, content, re.MULTILINE):
                start_pos = f"1.0+{match.start()}c"
                end_pos = f"1.0+{match.end()}c"
                self.text_widget.tag_add(token_type, start_pos, end_pos)
    
    def update_line_numbers(self):
        """Update line numbers"""
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        
        # Count lines
        line_count = int(self.text_widget.index(tk.END).split('.')[0]) - 1
        
        # Add line numbers
        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, f"{i:3}\n")
        
        self.line_numbers.config(state=tk.DISABLED)
    
    def run_script(self):
        """Run the current script"""
        script_content = self.text_widget.get("1.0", tk.END).strip()
        
        if not script_content:
            self.output("No script to run.")
            return
        
        # Save script to object first
        self.save_to_object()
        
        self.clear_output()
        self.output("Running AXScript...\n")
        
        try:
            # Get selected object as context
            context_object = self.main_editor.selected_object
            
            # Run script
            result = self.interpreter.execute(script_content, context_object)
            
            if result.get("success", False):
                self.output("Script executed successfully.")
                if result.get("output"):
                    self.output(f"Output: {result['output']}")
            else:
                self.output(f"Script error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.output(f"Runtime error: {str(e)}")
    
    def validate_script(self):
        """Validate the current script syntax"""
        script_content = self.text_widget.get("1.0", tk.END).strip()
        
        if not script_content:
            self.output("No script to validate.")
            return
        
        self.clear_output()
        self.output("Validating AXScript...\n")
        
        try:
            # Parse the script to check syntax
            result = self.interpreter.parse(script_content)
            
            if result.get("success", False):
                self.output("Script syntax is valid.")
            else:
                self.output(f"Syntax error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.output(f"Validation error: {str(e)}")
    
    def clear_script(self):
        """Clear the script editor"""
        if messagebox.askyesno("Clear Script", "Clear all script content?"):
            self.text_widget.delete("1.0", tk.END)
            self.clear_output()
            self.update_line_numbers()
    
    def output(self, text):
        """Add text to output area"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, str(text) + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def clear_output(self):
        """Clear output area"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def get_script_content(self):
        """Get the current script content"""
        return self.text_widget.get("1.0", tk.END).strip()
    
    def set_script_content(self, content):
        """Set the script content"""
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", content)
        self.highlight_syntax()
        self.update_line_numbers()
    
    def set_object(self, game_object):
        """Set the current object and load its script"""
        self.current_object = game_object
        if game_object and hasattr(game_object, 'script_code'):
            self.set_script_content(game_object.script_code)
        else:
            self.clear_script()
    
    def save_to_object(self):
        """Save current script content to the object"""
        if hasattr(self, 'current_object') and self.current_object:
            self.current_object.script_code = self.get_script_content()
            # Notify main editor that project was modified
            if hasattr(self.main_editor, 'project_modified'):
                self.main_editor.project_modified = True
    
    def save_script(self, file_path):
        """Save script to file"""
        try:
            with open(file_path, 'w') as f:
                f.write(self.get_script_content())
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save script: {e}")
            return False
    
    def load_script(self, file_path):
        """Load script from file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            self.set_script_content(content)
            return True
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load script: {e}")
            return False
