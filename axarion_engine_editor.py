import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import tkinter.font as tkfont
from tkinter import Text
import ast
import threading
import subprocess
import sys
import os
import json
from pathlib import Path
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available - using fallback buttons")

# Import the Asset Manager
try:
    from asset_manager.asset_manager import AssetManagerWindow
    ASSET_MANAGER_AVAILABLE = True
except ImportError:
    ASSET_MANAGER_AVAILABLE = False
    print("Asset Manager not available - missing dependencies")


class SyntaxHighlighter:
    """Advanced syntax highlighter for Python and JavaScript"""

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.setup_tags()

    def setup_tags(self):
        """Configure syntax highlighting tags"""
        # Python keywords
        python_keywords = [
            'def', 'class', 'import', 'from', 'if', 'else', 'elif', 'try',
            'except', 'finally', 'for', 'while', 'in', 'not', 'and', 'or',
            'is', 'None', 'True', 'False', 'return', 'break', 'continue',
            'pass', 'with', 'as', 'lambda', 'yield', 'global', 'nonlocal'
        ]

        self.text_widget.tag_configure("keyword", foreground="#569CD6")
        self.text_widget.tag_configure("string", foreground="#CE9178")
        self.text_widget.tag_configure("comment", foreground="#6A9955")
        self.text_widget.tag_configure("number", foreground="#B5CEA8")
        self.text_widget.tag_configure("operator", foreground="#D4D4D4")
        self.text_widget.tag_configure("builtin", foreground="#DCDCAA")

    def highlight_syntax(self, event=None):
        """Configure syntax highlighting text"""
        # Python keywords
        python_keywords = [
            'def', 'class', 'import', 'from', 'if', 'else', 'elif', 'try',
            'except', 'finally', 'for', 'while', 'in', 'not', 'and', 'or',
            'is', 'None', 'True', 'False', 'return', 'break', 'continue',
            'pass', 'with', 'as', 'lambda', 'yield', 'global', 'nonlocal'
        ]

        # Get all text
        content = self.text_widget.get("1.0", "end-1c")

        # Clear existing tags
        for tag in ["keyword", "string", "comment", "number", "builtin"]:
            self.text_widget.tag_remove(tag, "1.0", "end")

        # Highlight Python keywords
        import re
        for keyword in python_keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            for match in re.finditer(pattern, content):
                start_pos = f"1.0+{match.start()}c"
                end_pos = f"1.0+{match.end()}c"
                self.text_widget.tag_add("keyword", start_pos, end_pos)

        # Highlight strings
        string_pattern = r'(["\'])(?:(?=(\\?))\2.)*?\1'
        for match in re.finditer(string_pattern, content):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_widget.tag_add("string", start_pos, end_pos)

        # Highlight comments
        comment_pattern = r'#.*?$'
        for match in re.finditer(comment_pattern, content, re.MULTILINE):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_widget.tag_add("comment", start_pos, end_pos)

        # Highlight numbers
        number_pattern = r'\b\d+\.?\d*\b'
        for match in re.finditer(number_pattern, content):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_widget.tag_add("number", start_pos, end_pos)


class GradientButton(tk.Canvas):
    """Custom gradient button widget"""

    def __init__(self,
                 parent,
                 text="",
                 command=None,
                 width=120,
                 height=35,
                 start_color="#9333EA",
                 end_color="#EC4899",
                 text_color="white",
                 **kwargs):
        super().__init__(parent,
                         width=width,
                         height=height,
                         highlightthickness=0,
                         **kwargs)
        self.text = text
        self.command = command
        self.start_color = start_color
        self.end_color = end_color
        self.text_color = text_color
        self.width = width
        self.height = height
        self.is_pressed = False

        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        self.draw_gradient()

    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb):
        """Convert RGB tuple to hex color"""
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]),
                                            int(rgb[2]))

    def interpolate_color(self, start_rgb, end_rgb, factor):
        """Interpolate between two RGB colors"""
        return tuple(start_rgb[i] + factor * (end_rgb[i] - start_rgb[i])
                     for i in range(3))

    def draw_gradient(self, hover=False, pressed=False):
        """Draw the gradient background"""
        self.delete("all")

        start_rgb = self.hex_to_rgb(self.start_color)
        end_rgb = self.hex_to_rgb(self.end_color)

        # Adjust colors for hover/pressed states
        if pressed:
            start_rgb = tuple(max(0, c - 30) for c in start_rgb)
            end_rgb = tuple(max(0, c - 30) for c in end_rgb)
        elif hover:
            start_rgb = tuple(min(255, c + 20) for c in start_rgb)
            end_rgb = tuple(min(255, c + 20) for c in end_rgb)

        # Create gradient
        for i in range(self.height):
            factor = i / self.height
            color_rgb = self.interpolate_color(start_rgb, end_rgb, factor)
            color_hex = self.rgb_to_hex(color_rgb)
            self.create_line(0, i, self.width, i, fill=color_hex, width=1)

        # Add rounded rectangle border
        self.create_rectangle(0,
                              0,
                              self.width,
                              self.height,
                              outline="#444",
                              width=1)

        # Add text
        self.create_text(self.width // 2,
                         self.height // 2,
                         text=self.text,
                         fill=self.text_color,
                         font=('Segoe UI', 9, 'bold'))

    def on_click(self, event):
        self.is_pressed = True
        self.draw_gradient(pressed=True)

    def on_release(self, event):
        self.is_pressed = False
        self.draw_gradient()
        if self.command:
            self.command()

    def on_enter(self, event):
        if not self.is_pressed:
            self.draw_gradient(hover=True)

    def on_leave(self, event):
        if not self.is_pressed:
            self.draw_gradient()


class RoundedGradientButton(tk.Canvas):
    """Custom rounded gradient button widget"""

    def __init__(self,
                 parent,
                 text="",
                 command=None,
                 width=120,
                 height=35,
                 start_color="#9333EA",
                 end_color="#EC4899",
                 text_color="white",
                 corner_radius=12,
                 **kwargs):
        super().__init__(parent,
                         width=width,
                         height=height,
                         highlightthickness=0,
                         bg='#0C0F2E',
                         **kwargs)
        self.text = text
        self.command = command
        self.start_color = start_color
        self.end_color = end_color
        self.text_color = text_color
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.is_pressed = False

        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        self.draw_rounded_gradient()

    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb):
        """Convert RGB tuple to hex color"""
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]),
                                            int(rgb[2]))

    def interpolate_color(self, start_rgb, end_rgb, factor):
        """Interpolate between two RGB colors"""
        return tuple(start_rgb[i] + factor * (end_rgb[i] - start_rgb[i])
                     for i in range(3))

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=12, **kwargs):
        """Create a rounded rectangle on the canvas"""
        import math

        points = []

        # Ensure radius doesn't exceed half of width or height
        max_radius = min((x2 - x1) // 2, (y2 - y1) // 2)
        radius = min(radius, max_radius)

        # Top-left corner
        for i in range(90, 181, 5):
            angle = math.radians(i)
            x = x1 + radius + radius * math.cos(angle)
            y = y1 + radius + radius * math.sin(angle)
            points.extend([x, y])

        # Top-right corner
        for i in range(0, 91, 5):
            angle = math.radians(i)
            x = x2 - radius + radius * math.cos(angle)
            y = y1 + radius + radius * math.sin(angle)
            points.extend([x, y])

        # Bottom-right corner
        for i in range(270, 361, 5):
            angle = math.radians(i)
            x = x2 - radius + radius * math.cos(angle)
            y = y2 - radius + radius * math.sin(angle)
            points.extend([x, y])

        # Bottom-left corner
        for i in range(180, 271, 5):
            angle = math.radians(i)
            x = x1 + radius + radius * math.cos(angle)
            y = y2 - radius + radius * math.sin(angle)
            points.extend([x, y])

        return self.create_polygon(points, smooth=True, **kwargs)

    def draw_rounded_gradient(self, hover=False, pressed=False):
        """Draw the rounded gradient background"""
        self.delete("all")

        start_rgb = self.hex_to_rgb(self.start_color)
        end_rgb = self.hex_to_rgb(self.end_color)

        # Adjust colors for hover/pressed states
        if pressed:
            start_rgb = tuple(max(0, c - 30) for c in start_rgb)
            end_rgb = tuple(max(0, c - 30) for c in end_rgb)
        elif hover:
            start_rgb = tuple(min(255, c + 20) for c in start_rgb)
            end_rgb = tuple(min(255, c + 20) for c in end_rgb)

        # Create a proper rounded rectangle with gradient
        self.create_rounded_rect_with_gradient(start_rgb, end_rgb)

        # Add text
        self.create_text(self.width // 2,
                         self.height // 2,
                         text=self.text,
                         fill=self.text_color,
                         font=('Segoe UI', 11, 'bold'))

    def create_rounded_rect_with_gradient(self, start_rgb, end_rgb):
        """Create a rounded rectangle with proper gradient"""
        import math

        # Calculate corner points for rounded rectangle
        r = min(self.corner_radius, self.width // 2, self.height // 2)

        # For each y position, calculate the x boundaries and draw gradient lines
        for y in range(self.height):
            # Calculate left and right boundaries for this y position
            if y < r:
                # Top corners
                offset = math.sqrt(r * r - (r - y) *
                                   (r - y)) if (r - y) <= r else r
                left_x = max(0, int(r - offset))
                right_x = min(self.width, int(self.width - r + offset))
            elif y >= self.height - r:
                # Bottom corners
                offset = math.sqrt(r * r - (y - (self.height - r - 1)) *
                                   (y - (self.height - r - 1))) if (
                                       y - (self.height - r - 1)) <= r else r
                left_x = max(0, int(r - offset))
                right_x = min(self.width, int(self.width - r + offset))
            else:
                # Middle section - full width
                left_x = 0
                right_x = self.width

            # Draw gradient line for this y position
            if right_x > left_x:
                for x in range(left_x, right_x):
                    if self.width > 1:
                        factor = x / (self.width - 1)
                    else:
                        factor = 0
                    color_rgb = self.interpolate_color(start_rgb, end_rgb,
                                                       factor)
                    color_hex = self.rgb_to_hex(color_rgb)
                    self.create_rectangle(x,
                                          y,
                                          x + 1,
                                          y + 1,
                                          fill=color_hex,
                                          outline=color_hex)

    def on_click(self, event):
        self.is_pressed = True
        self.draw_rounded_gradient(pressed=True)

    def on_release(self, event):
        self.is_pressed = False
        self.draw_rounded_gradient()
        if self.command:
            self.command()

    def on_enter(self, event):
        if not self.is_pressed:
            self.draw_rounded_gradient(hover=True)

    def on_leave(self, event):
        if not self.is_pressed:
            self.draw_rounded_gradient()


class AxarionStudio:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Axarion Engine Editor")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0C0F2E')

        # Configure style for Axarion theme
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Axarion theme configuration - dark blue with purple/pink gradients
        self.style.configure('TNotebook', background='#0C0F2E', borderwidth=0)
        self.style.configure('TNotebook.Tab',
                             background='#1a1d4a',
                             foreground='white',
                             padding=[20, 8],
                             focuscolor='none')
        self.style.map('TNotebook.Tab',
                       background=[('selected', '#9333EA'),
                                   ('active', '#7C3AED')])

        # Configure Treeview for Axarion theme
        self.style.configure('Treeview',
                             background='#0C0F2E',
                             foreground='white',
                             fieldbackground='#0C0F2E',
                             borderwidth=0)
        self.style.configure('Treeview.Heading',
                             background='#1a1d4a',
                             foreground='white')

        self.current_file = None
        self.file_contents = {}
        self.asset_manager_window = None
        self.current_project_path = None
        self.unsaved_files = set()  # Track files with unsaved changes

        # Set up quit confirmation
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface"""
        # Create main container
        main_frame = tk.Frame(self.root, bg='#0C0F2E')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create toolbar
        self.create_toolbar(main_frame)

        # Create main content area
        self.create_main_content(main_frame)

        # Create status bar
        self.create_status_bar(main_frame)

    def create_toolbar(self, parent):
        """Create the toolbar with tabs"""
        # Main toolbar container
        toolbar_frame = tk.Frame(parent, bg='#1a1d4a', height=80)
        toolbar_frame.pack(fill=tk.X, pady=(0, 5))
        toolbar_frame.pack_propagate(False)

        # Tab navigation bar
        tab_frame = tk.Frame(toolbar_frame, bg='#1a1d4a', height=35)
        tab_frame.pack(fill=tk.X, side=tk.TOP)
        tab_frame.pack_propagate(False)

        # Tab buttons
        self.current_tab = "File"
        self.tab_buttons = {}

        tabs = [
            ("File", "#007ACC"),
            ("Edit", "#404040"),
            ("About", "#404040"),
        ]

        if ASSET_MANAGER_AVAILABLE:
            tabs.append(("Asset Manager", "#404040"))

        for tab_name, bg_color in tabs:
            btn = tk.Button(tab_frame,
                            text=tab_name,
                            command=lambda t=tab_name: self.switch_tab(t),
                            bg='#9333EA' if tab_name == "File" else "#1a1d4a",
                            fg='white',
                            relief='flat',
                            font=('Segoe UI', 10,
                                  'bold' if tab_name == "File" else 'normal'),
                            padx=20,
                            pady=8,
                            cursor='hand2',
                            bd=0)
            btn.pack(side=tk.LEFT, padx=(0, 2))
            self.tab_buttons[tab_name] = btn

        # Content area for buttons
        self.button_content_frame = tk.Frame(toolbar_frame, bg='#1a1d4a')
        self.button_content_frame.pack(fill=tk.BOTH,
                                       expand=True,
                                       padx=10,
                                       pady=(5, 10))

        # Initialize with File tab content
        self.create_file_buttons(self.button_content_frame)

    def switch_tab(self, tab_name):
        """Switch to a different tab"""
        # Remove the early return that was preventing tab switching

        # Update current tab
        self.current_tab = tab_name

        # Update button styles
        for name, btn in self.tab_buttons.items():
            if name == tab_name:
                btn.configure(bg='#9333EA',
                              fg='white',
                              font=('Segoe UI', 10, 'bold'))
            else:
                btn.configure(bg='#1a1d4a',
                              fg='white',
                              font=('Segoe UI', 10, 'normal'))

        # Clear current content
        for widget in self.button_content_frame.winfo_children():
            widget.destroy()

        # Load new content
        if tab_name == "File":
            self.create_file_buttons(self.button_content_frame)
        elif tab_name == "Edit":
            self.create_edit_buttons(self.button_content_frame)
        elif tab_name == "About":
            self.create_about_buttons(self.button_content_frame)
        elif tab_name == "Asset Manager":
            self.create_asset_buttons(self.button_content_frame)

    def create_file_buttons(self, parent):
        """Create file operation buttons"""
        buttons = [("New File", self.new_file), ("Open File", self.open_file),
                   ("Save", self.save_file), ("Save As", self.save_as_file)]

        for text, command in buttons:
            btn = GradientButton(parent,
                                 text=text,
                                 command=command,
                                 width=80,
                                 height=30,
                                 start_color='#7C3AED',
                                 end_color='#9333EA')
            btn.pack(side=tk.LEFT, padx=(0, 5))

        # Add project close button if project is open
        if self.current_project_path:
            btn = GradientButton(parent,
                                 text="Close Project",
                                 command=self.close_project,
                                 width=100,
                                 height=30,
                                 start_color='#EC4899',
                                 end_color='#F472B6')
            btn.pack(side=tk.LEFT, padx=(10, 5))

    def create_edit_buttons(self, parent):
        """Create edit operation buttons"""
        buttons = [("Undo", self.undo), ("Redo", self.redo),
                   ("Find", self.find_text), ("Replace", self.replace_text)]

        for text, command in buttons:
            btn = GradientButton(parent,
                                 text=text,
                                 command=command,
                                 width=70,
                                 height=30,
                                 start_color='#7C3AED',
                                 end_color='#9333EA')
            btn.pack(side=tk.LEFT, padx=(0, 5))

    def create_about_buttons(self, parent):
        """Create about buttons"""
        btn = GradientButton(parent,
                             text="About Axarion Engine",
                             command=self.show_about_window,
                             width=150,
                             height=30,
                             start_color='#9333EA',
                             end_color='#A855F7')
        btn.pack(side=tk.LEFT)

        # Info label
        info_label = tk.Label(
            parent,
            text="Information about Axarion Engine and Development Team",
            bg='#1a1d4a',
            fg='white',
            font=('Segoe UI', 9))
        info_label.pack(side=tk.LEFT, padx=(15, 0))

    def create_asset_buttons(self, parent):
        """Create asset manager buttons"""
        btn = GradientButton(parent,
                             text="Open Asset Manager",
                             command=self.open_asset_manager,
                             width=150,
                             height=30,
                             start_color='#9333EA',
                             end_color='#A855F7')
        btn.pack(side=tk.LEFT)

        # Info label
        info_label = tk.Label(
            parent,
            text="Manage local assets and browse the Asset Store",
            bg='#1a1d4a',
            fg='white',
            font=('Segoe UI', 9))
        info_label.pack(side=tk.LEFT, padx=(15, 0))

    def create_main_content(self, parent):
        """Create the main content area"""
        content_frame = tk.Frame(parent, bg='#0C0F2E')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Create paned window for splitter
        self.paned_window = tk.PanedWindow(content_frame,
                                           orient=tk.HORIZONTAL,
                                           sashwidth=5,
                                           sashrelief='raised',
                                           bg='#1a1d4a',
                                           sashpad=2)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Left panel - File explorer
        self.create_file_explorer()

        # Right panel - Editor
        self.create_editor_panel()

    def create_file_explorer(self):
        """Create simplified project file explorer"""
        explorer_frame = tk.Frame(self.paned_window, bg='#0C0F2E', width=250)

        # Title
        title_frame = tk.Frame(explorer_frame, bg='#1a1d4a', height=30)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_text = "PROJECT" if self.current_project_path else "WORKSPACE"
        title_label = tk.Label(title_frame,
                               text=title_text,
                               bg='#1a1d4a',
                               fg='white',
                               font=('Segoe UI', 9, 'bold'))
        title_label.pack(pady=5)

        # File tree
        tree_frame = tk.Frame(explorer_frame, bg='#0C0F2E')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.file_tree = ttk.Treeview(tree_frame, show='tree')
        self.file_tree.pack(fill=tk.BOTH, expand=True)

        self.load_project_files()

        # Bind double-click to open file
        self.file_tree.bind('<Double-1>', self.on_file_double_click)

        self.paned_window.add(explorer_frame)

    def create_editor_panel(self):
        """Create the main editor panel"""
        editor_frame = tk.Frame(self.paned_window, bg='#0C0F2E')

        # Editor notebook for multiple files
        self.editor_notebook = ttk.Notebook(editor_frame)
        self.editor_notebook.pack(fill=tk.BOTH, expand=True)

        # Configure editor notebook style
        self.style.configure('Editor.TNotebook', background='#0C0F2E')
        self.style.configure('Editor.TNotebook.Tab',
                             background='#1a1d4a',
                             foreground='#FFD700',
                             padding=[15, 8])
        self.style.map('Editor.TNotebook.Tab',
                       background=[('selected', '#0C0F2E'),
                                   ('active', '#7C3AED')])

        self.paned_window.add(editor_frame)

        # Create welcome tab
        self.create_welcome_tab()

    def create_welcome_tab(self):
        """Create welcome tab"""
        welcome_frame = tk.Frame(self.editor_notebook, bg='#0C0F2E')

        # Main welcome content
        content_frame = tk.Frame(welcome_frame, bg='#0C0F2E')
        content_frame.pack(expand=True, fill=tk.BOTH)

        # Logo instead of welcome text
        try:
            # Check multiple locations for logo (for bundled app)
            logo_paths = [
                "Logo.png",  # Current directory
                "assets/Logo.png",  # Bundled assets
                os.path.join(os.path.dirname(__file__),
                             "Logo.png"),  # Script directory
                os.path.join(os.path.dirname(__file__), "assets",
                             "Logo.png")  # Script assets
            ]

            logo_found = False
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    # Use PIL to resize logo if available
                    if PIL_AVAILABLE:
                        from PIL import Image, ImageTk
                        logo_pil = Image.open(logo_path)
                        # Resize logo to larger size (max width 450px, maintain aspect ratio)
                        logo_pil.thumbnail((450, 225),
                                           Image.Resampling.LANCZOS)
                        logo_image = ImageTk.PhotoImage(logo_pil)
                        logo_label = tk.Label(content_frame,
                                              image=logo_image,
                                              bg='#0C0F2E')
                        logo_label.image = logo_image  # Keep reference
                        logo_label.pack(pady=(80, 30))
                        logo_found = True
                        break
                    else:
                        # Fallback without PIL - try to use original but with smaller padding
                        logo_image = tk.PhotoImage(file=logo_path)
                        # Keep original size or slightly reduce if too large
                        # Check if image is very large and subsample only if needed
                        if logo_image.width() > 600 or logo_image.height(
                        ) > 300:
                            logo_image = logo_image.subsample(2, 2)
                        elif logo_image.width() > 450 or logo_image.height(
                        ) > 225:
                            logo_image = logo_image.subsample(
                                1, 1)  # Keep original size
                        logo_label = tk.Label(content_frame,
                                              image=logo_image,
                                              bg='#0C0F2E')
                        logo_label.image = logo_image  # Keep reference
                        logo_label.pack(pady=(80, 30))
                        logo_found = True
                        break

            if not logo_found:
                # Fallback to text if logo not found
                welcome_label = tk.Label(
                    content_frame,
                    text="Welcome to Axarion Engine Editor",
                    bg='#0C0F2E',
                    fg='white',
                    font=('Segoe UI', 20, 'bold'))
                welcome_label.pack(pady=(100, 30))

                subtitle_label = tk.Label(
                    content_frame,
                    text="Professional 2D Game Development Environment",
                    bg='#0C0F2E',
                    fg='white',
                    font=('Segoe UI', 12))
                subtitle_label.pack(pady=(0, 50))
        except Exception as e:
            print(f"Could not load logo: {e}")
            # Fallback to text
            welcome_label = tk.Label(content_frame,
                                     text="Welcome to Axarion Engine Editor",
                                     bg='#0C0F2E',
                                     fg='white',
                                     font=('Segoe UI', 20, 'bold'))
            welcome_label.pack(pady=(100, 30))

            subtitle_label = tk.Label(
                content_frame,
                text="Professional 2D Game Development Environment",
                bg='#0C0F2E',
                fg='white',
                font=('Segoe UI', 12))
            subtitle_label.pack(pady=(0, 50))

        # Project management section - horizontal layout
        project_frame = tk.Frame(content_frame,
                                 bg='#0C0F2E',
                                 relief='flat',
                                 bd=0)
        project_frame.pack(pady=20, padx=50)

        project_title = tk.Label(project_frame,
                                 text="Get Started",
                                 bg='#0C0F2E',
                                 fg='white',
                                 font=('Segoe UI', 14, 'bold'))
        project_title.pack(pady=(20, 20))

        # Horizontal button container
        button_container = tk.Frame(project_frame, bg='#0C0F2E')
        button_container.pack(pady=(0, 20))

        # Create rounded gradient buttons
        try:
            # Create new project button with rounded gradient
            new_project_btn = RoundedGradientButton(
                button_container,
                text="Create New Project",
                command=self.create_new_project,
                width=220,
                height=50,
                start_color='#9333EA',
                end_color='#A855F7',
                corner_radius=12)
            new_project_btn.pack(side=tk.LEFT, padx=(0, 15))

            # Open existing project button with rounded gradient
            open_project_btn = RoundedGradientButton(
                button_container,
                text="Open Existing Project",
                command=self.open_existing_project,
                width=220,
                height=50,
                start_color='#EC4899',
                end_color='#F472B6',
                corner_radius=12)
            open_project_btn.pack(side=tk.LEFT, padx=(15, 0))

        except Exception as e:
            print(f"Error creating rounded buttons: {e}")
            # Fallback to regular gradient buttons if rounded buttons fail
            new_project_btn = GradientButton(button_container,
                                             text="Create New Project",
                                             command=self.create_new_project,
                                             width=220,
                                             height=50,
                                             start_color='#9333EA',
                                             end_color='#A855F7')
            new_project_btn.pack(side=tk.LEFT, padx=(0, 15))

            open_project_btn = GradientButton(
                button_container,
                text="Open Existing Project",
                command=self.open_existing_project,
                width=220,
                height=50,
                start_color='#EC4899',
                end_color='#F472B6')
            open_project_btn.pack(side=tk.LEFT, padx=(15, 0))

        # Quick info with yellow text
        info_text = """
• Projects are organized in the Projects folder
• Each project contains game.py as the main entry point
• Use Asset Manager to import sprites, sounds, and other resources
• Assets can be easily referenced in your code with path copying
        """

        info_label = tk.Label(content_frame,
                              text=info_text,
                              bg='#0C0F2E',
                              fg='white',
                              font=('Segoe UI', 10),
                              justify=tk.LEFT)
        info_label.pack(pady=(30, 0))

        self.editor_notebook.add(welcome_frame, text="Welcome  ✕")

    def create_new_project(self):
        """Create a new Axarion game project"""
        # Create dialog for project name
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Project")
        dialog.geometry("400x250")
        dialog.configure(bg='#0C0F2E')
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f'+{x}+{y}')

        # Dialog content
        title_label = tk.Label(dialog,
                               text="Create New Axarion Project",
                               font=('Segoe UI', 14, 'bold'),
                               bg='#0C0F2E',
                               fg='white')
        title_label.pack(pady=(30, 20))

        # Project name input
        name_label = tk.Label(dialog,
                              text="Project Name:",
                              font=('Segoe UI', 10),
                              bg='#0C0F2E',
                              fg='white')
        name_label.pack(pady=(0, 5))

        name_var = tk.StringVar(value="MyGame")
        name_entry = tk.Entry(dialog,
                              textvariable=name_var,
                              font=('Segoe UI', 12),
                              width=25,
                              bg='#1a1d4a',
                              fg='white',
                              insertbackground='white')
        name_entry.pack(pady=(0, 20))
        name_entry.select_range(0, tk.END)
        name_entry.focus()

        # Buttons
        button_frame = tk.Frame(dialog, bg='#0C0F2E')
        button_frame.pack(pady=20)

        def create_project():
            project_name = name_var.get().strip()
            if not project_name:
                messagebox.showerror("Error", "Please enter a project name.")
                return

            if self.create_project_folder(project_name):
                self.current_project_path = str(
                    Path("Projects") / project_name)
                dialog.destroy()
                self.load_project_files()
                messagebox.showinfo(
                    "Success",
                    f"Project '{project_name}' created successfully!")

        def cancel():
            dialog.destroy()

        create_btn = GradientButton(button_frame,
                                    text="Create Project",
                                    command=create_project,
                                    width=120,
                                    height=30,
                                    start_color='#9333EA',
                                    end_color='#A855F7')
        create_btn.pack(side=tk.LEFT, padx=(0, 10))

        cancel_btn = GradientButton(button_frame,
                                    text="Cancel",
                                    command=cancel,
                                    width=80,
                                    height=30,
                                    start_color='#EC4899',
                                    end_color='#F472B6')
        cancel_btn.pack(side=tk.LEFT)

        # Bind Enter key
        dialog.bind('<Return>', lambda e: create_project())

    def create_project_folder(self, project_name):
        """Create project folder with basic structure"""
        try:
            # Create Projects directory if it doesn't exist
            projects_dir = Path("Projects")
            projects_dir.mkdir(exist_ok=True)

            # Create project folder
            project_dir = projects_dir / project_name
            if project_dir.exists():
                if not messagebox.askyesno(
                        "Project Exists",
                        f"Project '{project_name}' already exists. Overwrite?"
                ):
                    return False

            project_dir.mkdir(exist_ok=True)

            # Create game.py with basic template
            game_py_content = f'''"""
{project_name} - Axarion Engine Game

This is the main entry point for your Axarion Engine game.
Import your assets and start building your game here!
"""

# Simple engine import - works with standalone Axarion Engine Editor
from engine import AxarionEngine, GameObject, Scene
import pygame

class {project_name.replace(' ', '')}Game:
    def __init__(self):
        # Initialize the Axarion Engine
        self.engine = AxarionEngine(1280, 720, "{project_name}")

        # Initialize pygame
        pygame.init()

        # Initialize engine
        if not self.engine.initialize():
            print("Warning: Engine initialization had issues, but continuing...")

        # Create main scene
        self.main_scene = self.engine.create_scene("MainScene")
        self.engine.current_scene = self.main_scene

        # Setup game objects
        self.setup_game()

    def setup_game(self):
        """Setup your game objects here"""
        # Example: Create a player object
        player = GameObject("Player", "rectangle")
        player.position = (640, 360)  # Center of screen
        player.set_property("width", 50)
        player.set_property("height", 50)
        player.set_property("color", (100, 200, 255))  # Light blue
        player.is_static = True

        # Add player to scene
        self.main_scene.add_object(player)

        # Store reference for movement
        self.player = player

    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        speed = 300  # pixels per second

        while self.engine.running:
            delta_time = clock.tick(60) / 1000.0  # Convert to seconds

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.engine.stop()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.engine.stop()

            # Handle input for player movement
            keys = pygame.key.get_pressed()
            x, y = self.player.position

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.player.position = (x, y - speed * delta_time)
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.player.position = (x, y + speed * delta_time)
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.player.position = (x - speed * delta_time, y)
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.player.position = (x + speed * delta_time, y)

            # Update game
            if self.engine.current_scene:
                self.engine.current_scene.update(delta_time)

            # Render game
            if self.engine.renderer:
                self.engine.renderer.clear()
                if self.engine.current_scene:
                    self.engine.current_scene.render(self.engine.renderer)
                self.engine.renderer.present()

        # Cleanup
        self.engine.cleanup()

if __name__ == "__main__":
    game = {project_name.replace(' ', '')}Game()
    game.run()
'''

            # Write game.py file
            game_py_path = project_dir / "game.py"
            with open(game_py_path, 'w', encoding='utf-8') as f:
                f.write(game_py_content)

            # Create README.md
            readme_content = f'''# {project_name}

Created with Axarion Engine

## How to Run
1. Open this project in Axarion Engine Editor
2. Run `game.py` to start the game
3. Use WASD or arrow keys to move the player

## Project Structure
- `game.py` - Main game entry point
- Add your assets using the Asset Manager
- Import assets in your code using the copied paths

## Getting Started
1. Use the Asset Manager to import sprites, sounds, and other assets
2. Right-click assets to copy their paths for use in code
3. Check the Axarion Engine documentation for more features

Happy game development!
'''

            readme_path = project_dir / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)

            return True

        except Exception as e:
            messagebox.showerror("Error", f"Could not create project: {e}")
            return False

    def open_existing_project(self):
        """Open an existing project"""
        projects_dir = Path("Projects")
        if not projects_dir.exists():
            messagebox.showinfo(
                "No Projects",
                "No Projects folder found. Create a new project first.")
            return

        project_dir = filedialog.askdirectory(title="Select Project Folder",
                                              initialdir=str(projects_dir))

        if project_dir:
            # Check if it's a valid project (contains game.py)
            game_py_path = Path(project_dir) / "game.py"
            if game_py_path.exists():
                self.current_project_path = project_dir
                self.open_file_in_editor(str(game_py_path))
                self.load_project_files()
                messagebox.showinfo(
                    "Project Opened",
                    f"Opened project: {Path(project_dir).name}")
            else:
                messagebox.showwarning(
                    "Invalid Project",
                    "Selected folder doesn't contain a game.py file.")

    def close_project(self):
        """Close the current project and return to workspace view"""
        self.current_project_path = None
        self.unsaved_files.clear()  # Clear unsaved files tracking
        self.load_project_files()
        self.update_window_title()  # Update title to remove project name

        # Refresh the file tab to remove the close project button
        if self.current_tab == "File":
            for widget in self.button_content_frame.winfo_children():
                widget.destroy()
            self.create_file_buttons(self.button_content_frame)

    def create_status_bar(self, parent):
        """Create status bar"""
        self.status_bar = tk.Label(parent,
                                   text="Ready",
                                   bg='#9333EA',
                                   fg='white',
                                   anchor=tk.W,
                                   padx=10,
                                   font=('Segoe UI', 9))
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def load_project_files(self):
        """Load project files into the file tree (simplified for project-only view)"""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        # Update title based on current state
        if hasattr(self, 'paned_window'):
            for widget in self.paned_window.panes():
                frame = self.paned_window.nametowidget(widget)
                if hasattr(frame, 'winfo_children'):
                    for child in frame.winfo_children():
                        if isinstance(child,
                                      tk.Frame) and child.winfo_children():
                            title_frame = child.winfo_children()[0]
                            if isinstance(
                                    title_frame,
                                    tk.Frame) and title_frame.winfo_children():
                                title_label = title_frame.winfo_children()[0]
                                if isinstance(title_label, tk.Label):
                                    title_text = "PROJECT" if self.current_project_path else "WORKSPACE"
                                    title_label.configure(text=title_text)
                                    break

        # If we have a current project, show only its files
        if self.current_project_path and os.path.exists(
                self.current_project_path):
            project_name = os.path.basename(self.current_project_path)
            self.add_project_files_only("", self.current_project_path,
                                        project_name)
        else:
            # Show just the Projects folder for project creation
            projects_dir = Path("Projects")
            if projects_dir.exists():
                self.add_directory_to_tree("", str(projects_dir), "Projects")
            else:
                # Show message to create first project
                info_node = self.file_tree.insert("",
                                                  'end',
                                                  text="No project open",
                                                  open=False)
                self.file_tree.insert(
                    info_node,
                    'end',
                    text="Create a new project to get started")

    def add_project_files_only(self, parent, path, name):
        """Add only project files to the tree (simplified view)"""
        try:
            # Add project root node
            project_node = self.file_tree.insert(parent,
                                                 'end',
                                                 text=name,
                                                 values=[path],
                                                 open=True)

            # Add only relevant files in the project directory
            try:
                items = sorted(os.listdir(path))
                for item in items:
                    item_path = os.path.join(path, item)
                    if os.path.isfile(item_path):
                        # Show all files in project directory
                        self.file_tree.insert(project_node,
                                              'end',
                                              text=item,
                                              values=[item_path])
                    elif os.path.isdir(item_path) and not item.startswith('.'):
                        # Show subdirectories but don't expand them deeply
                        sub_node = self.file_tree.insert(project_node,
                                                         'end',
                                                         text=item,
                                                         values=[item_path],
                                                         open=False)
                        # Add just one level of files in subdirectories
                        try:
                            sub_items = os.listdir(
                                item_path)[:10]  # Limit to first 10 items
                            for sub_item in sub_items:
                                if os.path.isfile(
                                        os.path.join(item_path, sub_item)):
                                    self.file_tree.insert(sub_node,
                                                          'end',
                                                          text=sub_item,
                                                          values=[
                                                              os.path.join(
                                                                  item_path,
                                                                  sub_item)
                                                          ])
                        except PermissionError:
                            pass
            except PermissionError:
                pass

        except Exception as e:
            print(f"Error loading project directory {path}: {e}")

    def add_directory_to_tree(self, parent, path, name):
        """Add directory and its contents to the tree"""
        try:
            # Add directory node
            dir_node = self.file_tree.insert(parent,
                                             'end',
                                             text=name,
                                             values=[path],
                                             open=True)

            # Add files and subdirectories
            try:
                items = sorted(os.listdir(path))
                for item in items:
                    if item.startswith('.'):
                        continue

                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        self.add_directory_to_tree(dir_node, item_path, item)
                    else:
                        # Only show relevant file types
                        if item.endswith(
                            ('.py', '.txt', '.md', '.json', '.yml', '.yaml')):
                            self.file_tree.insert(dir_node,
                                                  'end',
                                                  text=item,
                                                  values=[item_path])
            except PermissionError:
                pass

        except Exception as e:
            print(f"Error loading directory {path}: {e}")

    def on_file_double_click(self, event):
        """Handle file double-click in tree"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            values = self.file_tree.item(item, 'values')
            if values:
                file_path = values[0]
                if os.path.isfile(file_path):
                    self.open_file_in_editor(file_path)

    def open_file_in_editor(self, file_path):
        """Open file in a new editor tab"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Create new tab
            editor_frame = tk.Frame(self.editor_notebook, bg='#1e1e1e')

            # Create text editor with syntax highlighting
            text_frame = tk.Frame(editor_frame, bg='#1e1e1e')
            text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Line numbers
            line_frame = tk.Frame(text_frame, bg='#2d2d2d', width=50)
            line_frame.pack(side=tk.LEFT, fill=tk.Y)
            line_frame.pack_propagate(False)

            line_text = tk.Text(line_frame,
                                width=4,
                                bg='#2d2d2d',
                                fg='#858585',
                                font=('Consolas', 10),
                                state='disabled',
                                wrap='none',
                                cursor='arrow')
            line_text.pack(fill=tk.BOTH, expand=True)

            # Main text editor
            text_editor = tk.Text(text_frame,
                                  bg='#1e1e1e',
                                  fg='white',
                                  font=('Consolas', 11),
                                  wrap='none',
                                  undo=True,
                                  maxundo=-1,
                                  insertbackground='white',
                                  selectbackground='#264F78')
            text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Scrollbars - dark theme compatible
            v_scrollbar = tk.Scrollbar(text_frame,
                                       orient='vertical',
                                       command=text_editor.yview,
                                       bg='#2d2d2d',
                                       activebackground='#404040',
                                       troughcolor='#1e1e1e',
                                       highlightthickness=0,
                                       relief='flat',
                                       bd=0,
                                       width=12)
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_editor.config(yscrollcommand=v_scrollbar.set)

            # Configure scrollbar style safely
            try:
                v_scrollbar.configure(bg='#2d2d2d',
                                      activebackground='#404040',
                                      troughcolor='#1e1e1e')
            except:
                pass

            h_scrollbar = tk.Scrollbar(editor_frame,
                                       orient='horizontal',
                                       command=text_editor.xview,
                                       bg='#2d2d2d',
                                       activebackground='#404040',
                                       troughcolor='#1e1e1e',
                                       highlightthickness=0,
                                       relief='flat',
                                       bd=0,
                                       width=12)
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            text_editor.config(xscrollcommand=h_scrollbar.set)

            # Configure scrollbar style safely
            try:
                h_scrollbar.configure(bg='#2d2d2d',
                                      activebackground='#404040',
                                      troughcolor='#1e1e1e')
            except:
                pass

            # Insert content
            text_editor.insert('1.0', content)

            # Setup syntax highlighting
            highlighter = SyntaxHighlighter(text_editor)
            text_editor.bind('<KeyRelease>', highlighter.highlight_syntax)
            text_editor.bind('<Button-1>', highlighter.highlight_syntax)
            highlighter.highlight_syntax()

            # Track file modifications
            def on_text_change(event=None):
                self.mark_file_modified(file_path)
                self.update_line_numbers(text_editor, line_text)

            # Update line numbers and track changes
            self.update_line_numbers(text_editor, line_text)
            text_editor.bind('<KeyRelease>', on_text_change)
            text_editor.bind(
                '<Button-1>',
                lambda e: self.update_line_numbers(text_editor, line_text))

            # Bind scroll events to synchronize line numbers
            def sync_line_numbers(*args):
                line_text.yview_moveto(text_editor.yview()[0])

            def on_scroll(*args):
                text_editor.yview(*args)
                sync_line_numbers()

            def on_mousewheel(event):
                text_editor.yview_scroll(int(-1 * (event.delta / 120)),
                                         "units")
                sync_line_numbers()
                return "break"

            # Configure scrollbar to sync line numbers
            v_scrollbar.config(command=on_scroll)
            text_editor.bind('<MouseWheel>', on_mousewheel)
            text_editor.bind(
                '<Button-4>', lambda e:
                (on_mousewheel(type('obj', (object, ), {'delta': 120})
                               ()), "break")[1])
            text_editor.bind(
                '<Button-5>', lambda e:
                (on_mousewheel(type('obj', (object, ), {'delta': -120})
                               ()), "break")[1])

            # Add tab with close button
            filename = os.path.basename(file_path)
            tab_text = f"{filename}  ✕"
            self.editor_notebook.add(editor_frame, text=tab_text)
            self.editor_notebook.select(editor_frame)

            # Bind tab close functionality
            self.editor_notebook.bind("<Button-1>", self.on_tab_click)

            # Store file info
            self.file_contents[file_path] = {
                'text_widget': text_editor,
                'original_content': content,
                'modified': False
            }

            self.current_file = file_path
            self.update_status(f"Opened: {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")

    def update_line_numbers(self, text_widget, line_widget):
        """Update line numbers display"""
        line_widget.config(state='normal')
        line_widget.delete('1.0', 'end')

        # Get number of lines
        lines = int(text_widget.index('end-1c').split('.')[0])

        # Add line numbers
        line_numbers = '\n'.join(str(i) for i in range(1, lines + 1))
        line_widget.insert('1.0', line_numbers)
        line_widget.config(state='disabled')

        # Synchronize scrolling
        line_widget.yview_moveto(text_widget.yview()[0])

    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.config(text=message)

    def on_closing(self):
        """Handle window closing event with unsaved work check"""
        if self.has_unsaved_work():
            # Create confirmation dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Unsaved Changes")
            dialog.geometry("400x200")
            dialog.configure(bg='#0C0F2E')
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()

            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() //
                                                      2)
            dialog.geometry(f'+{x}+{y}')

            # Warning icon and message
            warning_frame = tk.Frame(dialog, bg='#0C0F2E')
            warning_frame.pack(pady=20)

            title_label = tk.Label(warning_frame,
                                   text="⚠️ Unsaved Changes",
                                   font=('Segoe UI', 14, 'bold'),
                                   bg='#0C0F2E',
                                   fg='#FFD700')
            title_label.pack(pady=(0, 10))

            message_label = tk.Label(
                warning_frame,
                text=
                "You have unsaved changes in your project.\nDo you want to quit without saving?",
                font=('Segoe UI', 10),
                bg='#0C0F2E',
                fg='white',
                justify=tk.CENTER)
            message_label.pack()

            # Buttons
            button_frame = tk.Frame(dialog, bg='#0C0F2E')
            button_frame.pack(pady=20)

            def save_and_quit():
                self.save_all_files()
                dialog.destroy()
                self.root.destroy()

            def quit_without_saving():
                dialog.destroy()
                self.root.destroy()

            def cancel_quit():
                dialog.destroy()

            # Save and quit button
            save_btn = GradientButton(button_frame,
                                      text="Save & Quit",
                                      command=save_and_quit,
                                      width=100,
                                      height=30,
                                      start_color='#22C55E',
                                      end_color='#16A34A')
            save_btn.pack(side=tk.LEFT, padx=(0, 10))

            # Quit without saving button
            quit_btn = GradientButton(button_frame,
                                      text="Quit",
                                      command=quit_without_saving,
                                      width=70,
                                      height=30,
                                      start_color='#EF4444',
                                      end_color='#DC2626')
            quit_btn.pack(side=tk.LEFT, padx=(0, 10))

            # Cancel button
            cancel_btn = GradientButton(button_frame,
                                        text="Cancel",
                                        command=cancel_quit,
                                        width=70,
                                        height=30,
                                        start_color='#6B7280',
                                        end_color='#4B5563')
            cancel_btn.pack(side=tk.LEFT)

            # Bind Escape key to cancel
            dialog.bind('<Escape>', lambda e: cancel_quit())
            dialog.focus()
        else:
            # No unsaved work, quit immediately
            self.root.destroy()

    def has_unsaved_work(self):
        """Check if there are any unsaved changes"""
        # Check if project is open and has unsaved files
        if self.current_project_path and len(self.unsaved_files) > 0:
            return True

        # Check if any open editor tabs have unsaved content
        for file_path, file_info in self.file_contents.items():
            if file_info.get('modified', False):
                return True

        return False

    def mark_file_modified(self, file_path):
        """Mark a file as having unsaved changes"""
        self.unsaved_files.add(file_path)
        if file_path in self.file_contents:
            self.file_contents[file_path]['modified'] = True

        # Update window title to show unsaved indicator
        self.update_window_title()

    def mark_file_saved(self, file_path):
        """Mark a file as saved"""
        self.unsaved_files.discard(file_path)
        if file_path in self.file_contents:
            self.file_contents[file_path]['modified'] = False

        # Update window title
        self.update_window_title()

    def on_tab_click(self, event):
        """Handle tab click events to detect close button clicks"""
        try:
            # Get the tab that was clicked using the correct identify method
            element = self.editor_notebook.identify(event.x, event.y)

            if element == "label":
                # Get the tab index at the click position
                clicked_tab = self.editor_notebook.index(
                    f"@{event.x},{event.y}")
                if clicked_tab is not None:
                    tab_text = self.editor_notebook.tab(clicked_tab, "text")

                    # Check if the click was on the close button (✕)
                    if "✕" in tab_text:
                        # Find the file path associated with this tab
                        tab_widget = self.editor_notebook.nametowidget(
                            self.editor_notebook.tabs()[clicked_tab])
                        tab_name = None

                        for file_path, file_info in self.file_contents.items():
                            if file_info['text_widget'].winfo_parent() == str(
                                    tab_widget):
                                tab_name = file_path
                                break

                        # Calculate approximate position of close button (✕)
                        # Get tab text without close button to estimate text width
                        text_without_close = tab_text.replace("  ✕", "")

                        # Get font and calculate text width
                        try:
                            font = tkfont.nametofont("TkDefaultFont")
                            text_width = font.measure(text_without_close)
                            close_button_start = text_width + 10  # Add some padding

                            # Get tab boundaries
                            tab_bbox = self.editor_notebook.bbox(clicked_tab)
                            if tab_bbox:
                                tab_x, tab_y, tab_width, tab_height = tab_bbox
                                click_x_in_tab = event.x - tab_x

                                # Check if click is in the close button area (right side of tab)
                                if click_x_in_tab > close_button_start:
                                    self.close_tab(clicked_tab, tab_name)
                                    return "break"  # Prevent normal tab selection
                        except:
                            # Fallback - if click is in the last 30 pixels of the tab
                            tab_bbox = self.editor_notebook.bbox(clicked_tab)
                            if tab_bbox:
                                tab_x, tab_y, tab_width, tab_height = tab_bbox
                                click_x_in_tab = event.x - tab_x
                                if click_x_in_tab > tab_width - 30:
                                    self.close_tab(clicked_tab, tab_name)
                                    return "break"

        except Exception as e:
            print(f"Tab click error: {e}")

    def close_tab(self, tab_index, file_path=None):
        """Close a specific tab"""
        try:
            # Check if file has unsaved changes
            if file_path and file_path in self.unsaved_files:
                result = messagebox.askyesnocancel(
                    "Unsaved Changes",
                    f"'{os.path.basename(file_path)}' has unsaved changes.\nSave before closing?",
                    icon='warning')

                if result is None:  # Cancel
                    return
                elif result:  # Yes - save
                    if file_path in self.file_contents:
                        try:
                            content = self.file_contents[file_path][
                                'text_widget'].get('1.0', 'end-1c')
                            with open(file_path, 'w',
                                      encoding='utf-8') as file:
                                file.write(content)
                            self.mark_file_saved(file_path)
                        except Exception as e:
                            messagebox.showerror("Error",
                                                 f"Could not save file: {e}")
                            return

            # Remove from notebook
            self.editor_notebook.forget(tab_index)

            # Clean up file tracking
            if file_path:
                if file_path in self.file_contents:
                    del self.file_contents[file_path]
                self.unsaved_files.discard(file_path)
                if self.current_file == file_path:
                    # Set current file to the currently selected tab if any
                    current_tab = self.editor_notebook.select()
                    if current_tab:
                        # Find the file path for the current tab
                        for fp, file_info in self.file_contents.items():
                            if file_info['text_widget'].winfo_parent(
                            ) == current_tab:
                                self.current_file = fp
                                break
                        else:
                            self.current_file = None
                    else:
                        self.current_file = None

            self.update_window_title()
            self.update_status("Tab closed")

        except Exception as e:
            print(f"Error closing tab: {e}")

    def update_window_title(self):
        """Update window title with unsaved indicator"""
        base_title = "Axarion Engine Editor"
        if self.current_project_path:
            project_name = os.path.basename(self.current_project_path)
            base_title += f" - {project_name}"

        if len(self.unsaved_files) > 0:
            base_title += " *"

        self.root.title(base_title)

    def save_all_files(self):
        """Save all open files that have unsaved changes"""
        for file_path in list(self.unsaved_files):
            if file_path in self.file_contents:
                try:
                    content = self.file_contents[file_path]['text_widget'].get(
                        '1.0', 'end-1c')
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(content)
                    self.mark_file_saved(file_path)
                except Exception as e:
                    print(f"Error saving file {file_path}: {e}")

        self.update_status("All files saved")

    def show_about_window(self):
        """Show the About window with engine information"""
        # Create about dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("About Axarion Engine Editor")
        dialog.geometry("520x650")
        dialog.configure(bg='#0C0F2E')
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f'+{x}+{y}')

        # Main content frame
        main_frame = tk.Frame(dialog, bg='#0C0F2E')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Logo section
        try:
            logo_paths = [
                "Logo.png",  # Current directory
                "assets/Logo.png",  # Bundled assets
                os.path.join(os.path.dirname(__file__),
                             "Logo.png"),  # Script directory
                os.path.join(os.path.dirname(__file__), "assets",
                             "Logo.png")  # Script assets
            ]

            logo_found = False
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    if PIL_AVAILABLE:
                        from PIL import Image, ImageTk
                        logo_pil = Image.open(logo_path)
                        logo_pil.thumbnail((200, 100),
                                           Image.Resampling.LANCZOS)
                        logo_image = ImageTk.PhotoImage(logo_pil)
                        logo_label = tk.Label(main_frame,
                                              image=logo_image,
                                              bg='#0C0F2E')
                        logo_label.image = logo_image  # Keep reference
                        logo_label.pack(pady=(0, 20))
                        logo_found = True
                        break
                    else:
                        logo_image = tk.PhotoImage(file=logo_path)
                        logo_image = logo_image.subsample(2, 2)
                        logo_label = tk.Label(main_frame,
                                              image=logo_image,
                                              bg='#0C0F2E')
                        logo_label.image = logo_image  # Keep reference
                        logo_label.pack(pady=(0, 20))
                        logo_found = True
                        break

            if not logo_found:
                title_label = tk.Label(main_frame,
                                       text="AXARION ENGINE",
                                       font=('Segoe UI', 18, 'bold'),
                                       bg='#0C0F2E',
                                       fg='white')
                title_label.pack(pady=(0, 20))
        except Exception:
            title_label = tk.Label(main_frame,
                                   text="AXARION ENGINE",
                                   font=('Segoe UI', 18, 'bold'),
                                   bg='#0C0F2E',
                                   fg='white')
            title_label.pack(pady=(0, 20))

        # Version and Engine info
        version_frame = tk.Frame(main_frame,
                                 bg='#1a1d4a',
                                 relief='raised',
                                 bd=1)
        version_frame.pack(fill=tk.X, pady=(0, 15), padx=10)

        engine_info = tk.Label(
            version_frame,
            text="Professional 2D Game Development Environment",
            font=('Segoe UI', 12, 'bold'),
            bg='#1a1d4a',
            fg='white')
        engine_info.pack(pady=10)

        version_label = tk.Label(version_frame,
                                 text="Engine Version: 1.0.0",
                                 font=('Segoe UI', 10),
                                 bg='#1a1d4a',
                                 fg='#FFD700')
        version_label.pack(pady=(0, 5))

        build_label = tk.Label(version_frame,
                               text="Engine Build: 7.20.2025",
                               font=('Segoe UI', 10),
                               bg='#1a1d4a',
                               fg='#FFD700')
        build_label.pack(pady=(0, 10))

        # Features section
        features_frame = tk.Frame(main_frame, bg='#0C0F2E')
        features_frame.pack(fill=tk.X, pady=(0, 15))

        features_title = tk.Label(features_frame,
                                  text="New Features:",
                                  font=('Segoe UI', 12, 'bold'),
                                  bg='#0C0F2E',
                                  fg='white')
        features_title.pack(anchor='w')

        features_text = """• Integrated & Enhanced Asset Manager
• Fresh, Modern Editor UI
• Centralized Projects Folder
• Brand New Asset Manager Feature
• Revamped "About" Section
• Simple EXE Builder
• New Editor Logo And Name
• Save and Exit + Warning Feature When Closed"""

        features_label = tk.Label(features_frame,
                                  text=features_text,
                                  font=('Segoe UI', 10),
                                  bg='#0C0F2E',
                                  fg='white',
                                  justify=tk.LEFT,
                                  anchor='w',
                                  wraplength=480)
        features_label.pack(fill=tk.X, pady=(5, 0))

        # Team section
        team_frame = tk.Frame(main_frame, bg='#1a1d4a', relief='raised', bd=1)
        team_frame.pack(fill=tk.X, pady=(0, 20), padx=10)

        team_title = tk.Label(team_frame,
                              text="Development Team:",
                              font=('Segoe UI', 12, 'bold'),
                              bg='#1a1d4a',
                              fg='white')
        team_title.pack(pady=(10, 5))

        team_text = """Lead Developer: The_Sun_Kitsune
Programmer: Zuha
Designer: Mjio
Ideas: Ultron01
Beta Tester: Jerry"""

        team_label = tk.Label(team_frame,
                              text=team_text,
                              font=('Segoe UI', 10),
                              bg='#1a1d4a',
                              fg='white',
                              justify=tk.CENTER,
                              wraplength=450)
        team_label.pack(pady=(0, 10))

        # Copyright and links
        copyright_frame = tk.Frame(main_frame, bg='#0C0F2E')
        copyright_frame.pack(fill=tk.X, pady=(0, 10))

        copyright_label = tk.Label(
            copyright_frame,
            text="© 2025 Axarion Engine. All rights reserved.",
            font=('Segoe UI', 8),
            bg='#0C0F2E',
            fg='#888888')
        copyright_label.pack()

        links_label = tk.Label(copyright_frame,
                               text="",
                               font=('Segoe UI', 9),
                               bg='#0C0F2E',
                               fg='white')
        links_label.pack(pady=(5, 0))

        # Close button
        button_frame = tk.Frame(main_frame, bg='#0C0F2E')
        button_frame.pack(pady=(20, 0))

        close_btn = GradientButton(button_frame,
                                   text="Close",
                                   command=dialog.destroy,
                                   width=100,
                                   height=35,
                                   start_color='#9333EA',
                                   end_color='#A855F7')
        close_btn.pack()

        # Bind Escape key to close
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        dialog.focus()

    def open_asset_manager(self):
        """Open the Asset Manager window"""
        if not ASSET_MANAGER_AVAILABLE:
            messagebox.showerror(
                "Error",
                "Asset Manager is not available. Please install required dependencies:\n"
                "- tkinterdnd2\n"
                "- Pillow\n"
                "- requests")
            return

        try:
            if self.asset_manager_window is None or not self.asset_manager_window.window.winfo_exists(
            ):
                self.asset_manager_window = AssetManagerWindow(self.root)
            else:
                self.asset_manager_window.window.lift()
                self.asset_manager_window.window.focus()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Asset Manager: {e}")

    # File operations
    def new_file(self):
        """Create a new file"""
        # Create new untitled tab
        editor_frame = tk.Frame(self.editor_notebook, bg='#1e1e1e')

        text_frame = tk.Frame(editor_frame, bg='#1e1e1e')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        text_editor = tk.Text(text_frame,
                              bg='#1e1e1e',
                              fg='white',
                              font=('Consolas', 11),
                              wrap='none',
                              undo=True,
                              maxundo=-1,
                              insertbackground='white',
                              selectbackground='#264F78')
        text_editor.pack(fill=tk.BOTH, expand=True)

        # Setup syntax highlighting
        highlighter = SyntaxHighlighter(text_editor)
        text_editor.bind('<KeyRelease>', highlighter.highlight_syntax)
        text_editor.bind('<Button-1>', highlighter.highlight_syntax)

        self.editor_notebook.add(editor_frame, text="Untitled  ✕")
        self.editor_notebook.select(editor_frame)

        self.update_status("Created new file")

    def open_file(self):
        """Open file dialog"""
        file_path = filedialog.askopenfilename(title="Open File",
                                               filetypes=[
                                                   ("Python files", "*.py"),
                                                   ("Text files", "*.txt"),
                                                   ("Markdown files", "*.md"),
                                                   ("JSON files", "*.json"),
                                                   ("All files", "*.*")
                                               ])

        if file_path:
            self.open_file_in_editor(file_path)

    def save_file(self):
        """Save current file"""
        if self.current_file and self.current_file in self.file_contents:
            try:
                content = self.file_contents[
                    self.current_file]['text_widget'].get('1.0', 'end-1c')
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.mark_file_saved(self.current_file)
                self.update_status(
                    f"Saved: {os.path.basename(self.current_file)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save file as dialog"""
        file_path = filedialog.asksaveasfilename(title="Save File As",
                                                 defaultextension=".py",
                                                 filetypes=[
                                                     ("Python files", "*.py"),
                                                     ("Text files", "*.txt"),
                                                     ("All files", "*.*")
                                                 ])

        if file_path:
            try:
                # Get current tab content
                current_tab = self.editor_notebook.select()
                if current_tab:
                    # Find text widget in current tab
                    for widget in self.editor_notebook.nametowidget(
                            current_tab).winfo_children():
                        text_widget = self.find_text_widget(widget)
                        if text_widget:
                            content = text_widget.get('1.0', 'end-1c')
                            with open(file_path, 'w',
                                      encoding='utf-8') as file:
                                file.write(content)
                            self.current_file = file_path
                            self.mark_file_saved(file_path)
                            self.update_status(
                                f"Saved as: {os.path.basename(file_path)}")
                            break
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def find_text_widget(self, widget):
        """Recursively find Text widget"""
        if isinstance(widget, tk.Text):
            return widget
        for child in widget.winfo_children():
            result = self.find_text_widget(child)
            if result:
                return result
        return None

    def get_current_text_widget(self):
        """Get the text widget from currently active tab"""
        current_tab = self.editor_notebook.select()
        if not current_tab:
            return None

        try:
            tab_widget = self.editor_notebook.nametowidget(current_tab)
            return self.find_text_widget(tab_widget)
        except tk.TclError:
            return None

    # Edit operations
    def undo(self):
        """Undo last action"""
        current_tab = self.editor_notebook.select()
        if current_tab:
            text_widget = self.get_current_text_widget()
            if text_widget:
                try:
                    text_widget.edit_undo()
                    self.update_status("Undo performed")
                except tk.TclError:
                    self.update_status("Nothing to undo")

    def redo(self):
        """Redo last undone action"""
        current_tab = self.editor_notebook.select()
        if current_tab:
            text_widget = self.get_current_text_widget()
            if text_widget:
                try:
                    text_widget.edit_redo()
                    self.update_status("Redo performed")
                except tk.TclError:
                    self.update_status("Nothing to redo")

    def find_text(self):
        """Open find dialog"""
        text_widget = self.get_current_text_widget()
        if not text_widget:
            self.update_status("No file open to search in")
            return

        # Create find dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Find")
        dialog.geometry("400x150")
        dialog.configure(bg='#0C0F2E')
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f'+{x}+{y}')

        # Dialog content
        tk.Label(dialog,
                 text="Find:",
                 bg='#0C0F2E',
                 fg='white',
                 font=('Segoe UI', 10)).pack(pady=10)

        search_var = tk.StringVar()
        entry = tk.Entry(dialog,
                         textvariable=search_var,
                         font=('Segoe UI', 11),
                         bg='#1a1d4a',
                         fg='white',
                         insertbackground='white',
                         width=30)
        entry.pack(pady=5)
        entry.focus()

        button_frame = tk.Frame(dialog, bg='#0C0F2E')
        button_frame.pack(pady=15)

        def find_next():
            search_term = search_var.get()
            if search_term:
                # Clear previous highlights
                text_widget.tag_remove("highlight", "1.0", "end")

                # Get current cursor position
                current_pos = text_widget.index(tk.INSERT)

                # Search from current position
                pos = text_widget.search(search_term, current_pos, "end")
                if not pos:
                    # Search from beginning
                    pos = text_widget.search(search_term, "1.0", current_pos)

                if pos:
                    end = f"{pos}+{len(search_term)}c"
                    text_widget.tag_add("highlight", pos, end)
                    text_widget.tag_configure("highlight",
                                              background="#FFD700",
                                              foreground="black")
                    text_widget.mark_set(tk.INSERT, end)
                    text_widget.see(pos)
                    self.update_status(f"Found: {search_term}")
                else:
                    self.update_status(f"Not found: {search_term}")

        def close_dialog():
            text_widget.tag_remove("highlight", "1.0", "end")
            dialog.destroy()

        GradientButton(button_frame,
                       text="Find Next",
                       command=find_next,
                       width=80,
                       height=25,
                       start_color='#9333EA',
                       end_color='#A855F7').pack(side=tk.LEFT, padx=5)
        GradientButton(button_frame,
                       text="Close",
                       command=close_dialog,
                       width=60,
                       height=25,
                       start_color='#EC4899',
                       end_color='#F472B6').pack(side=tk.LEFT, padx=5)

        # Bind Enter key
        dialog.bind('<Return>', lambda e: find_next())
        dialog.bind('<Escape>', lambda e: close_dialog())

    def replace_text(self):
        """Open replace dialog"""
        text_widget = self.get_current_text_widget()
        if not text_widget:
            self.update_status("No file open to replace in")
            return

        # Create replace dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Replace")
        dialog.geometry("400x200")
        dialog.configure(bg='#0C0F2E')
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f'+{x}+{y}')

        # Dialog content
        tk.Label(dialog,
                 text="Find:",
                 bg='#0C0F2E',
                 fg='white',
                 font=('Segoe UI', 10)).pack(pady=5)

        find_var = tk.StringVar()
        find_entry = tk.Entry(dialog,
                              textvariable=find_var,
                              font=('Segoe UI', 11),
                              bg='#1a1d4a',
                              fg='white',
                              insertbackground='white',
                              width=30)
        find_entry.pack(pady=2)
        find_entry.focus()

        tk.Label(dialog,
                 text="Replace with:",
                 bg='#0C0F2E',
                 fg='white',
                 font=('Segoe UI', 10)).pack(pady=(10, 5))

        replace_var = tk.StringVar()
        replace_entry = tk.Entry(dialog,
                                 textvariable=replace_var,
                                 font=('Segoe UI', 11),
                                 bg='#1a1d4a',
                                 fg='white',
                                 insertbackground='white',
                                 width=30)
        replace_entry.pack(pady=2)

        button_frame = tk.Frame(dialog, bg='#0C0F2E')
        button_frame.pack(pady=15)

        def replace_next():
            find_text = find_var.get()
            replace_text = replace_var.get()
            if find_text:
                current_pos = text_widget.index(tk.INSERT)
                pos = text_widget.search(find_text, current_pos, "end")
                if not pos:
                    pos = text_widget.search(find_text, "1.0", current_pos)

                if pos:
                    end = f"{pos}+{len(find_text)}c"
                    text_widget.delete(pos, end)
                    text_widget.insert(pos, replace_text)
                    text_widget.mark_set(tk.INSERT,
                                         f"{pos}+{len(replace_text)}c")
                    self.update_status(
                        f"Replaced: {find_text} → {replace_text}")
                else:
                    self.update_status(f"Not found: {find_text}")

        def replace_all():
            find_text = find_var.get()
            replace_text = replace_var.get()
            if find_text:
                content = text_widget.get("1.0", "end-1c")
                count = content.count(find_text)
                if count > 0:
                    new_content = content.replace(find_text, replace_text)
                    text_widget.delete("1.0", "end")
                    text_widget.insert("1.0", new_content)
                    self.update_status(f"Replaced {count} occurrences")
                else:
                    self.update_status(f"Not found: {find_text}")

        def close_dialog():
            dialog.destroy()

        GradientButton(button_frame,
                       text="Replace",
                       command=replace_next,
                       width=70,
                       height=25,
                       start_color='#9333EA',
                       end_color='#A855F7').pack(side=tk.LEFT, padx=2)
        GradientButton(button_frame,
                       text="Replace All",
                       command=replace_all,
                       width=80,
                       height=25,
                       start_color='#7C3AED',
                       end_color='#9333EA').pack(side=tk.LEFT, padx=2)
        GradientButton(button_frame,
                       text="Close",
                       command=close_dialog,
                       width=60,
                       height=25,
                       start_color='#EC4899',
                       end_color='#F472B6').pack(side=tk.LEFT, padx=2)

        # Bind keys
        dialog.bind('<Return>', lambda e: replace_next())
        dialog.bind('<Escape>', lambda e: close_dialog())

    def stop_execution(self):
        """Stop current execution by killing Python processes"""
        try:
            if os.name == 'nt':  # Windows
                # Kill all Python processes that might be running our game
                subprocess.run(['taskkill', '/f', '/im', 'python.exe'],
                               capture_output=True,
                               text=True)
                subprocess.run(['taskkill', '/f', '/im', 'pythonw.exe'],
                               capture_output=True,
                               text=True)
            else:  # Linux/Mac
                # Kill Python processes that contain our current file
                if self.current_file:
                    filename = os.path.basename(self.current_file)
                    subprocess.run(['pkill', '-f', filename],
                                   capture_output=True,
                                   text=True)
                else:
                    # Kill all Python processes (be careful!)
                    subprocess.run(['pkill', '-f', 'python'],
                                   capture_output=True,
                                   text=True)

            self.update_status("Execution stopped")

        except Exception as e:
            self.update_status(f"Error stopping execution: {e}")

    def build_project(self):
        """Build project as standalone executable with embedded engine"""
        # Try to detect current project from open file or project path
        project_path = None

        if self.current_project_path:
            project_path = self.current_project_path
        elif self.current_file:
            # Try to find project based on current file
            file_path = Path(self.current_file)
            if "Projects" in file_path.parts:
                # Find the project directory
                parts = file_path.parts
                projects_index = parts.index("Projects")
                if projects_index + 1 < len(parts):
                    project_name = parts[projects_index + 1]
                    project_path = str(Path("Projects") / project_name)

        if not project_path or not os.path.exists(project_path):
            messagebox.showwarning(
                "Warning",
                "Please open a project first or make sure you have a file from the project open"
            )
            return

        # Check if main game.py exists
        game_py_path = os.path.join(project_path, "game.py")
        if not os.path.exists(game_py_path):
            messagebox.showerror("Error",
                                 "game.py not found in current project")
            return

        # Update current project path
        self.current_project_path = project_path

        # Create build dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Build Project")
        dialog.geometry("500x350")
        dialog.configure(bg='#0C0F2E')
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f'+{x}+{y}')

        # Dialog content
        title_label = tk.Label(dialog,
                               text="Build Standalone Game",
                               font=('Segoe UI', 14, 'bold'),
                               bg='#0C0F2E',
                               fg='white')
        title_label.pack(pady=(20, 15))

        info_label = tk.Label(
            dialog,
            text=
            "This will create a standalone .exe file with embedded Axarion Engine",
            font=('Segoe UI', 10),
            bg='#0C0F2E',
            fg='white',
            wraplength=450)
        info_label.pack(pady=(0, 15))

        # Progress text area
        progress_frame = tk.Frame(dialog, bg='#1a1d4a', relief='sunken', bd=1)
        progress_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        progress_text = scrolledtext.ScrolledText(progress_frame,
                                                  height=10,
                                                  width=50,
                                                  bg='#1e1e1e',
                                                  fg='white',
                                                  font=('Consolas', 9))
        progress_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Buttons
        button_frame = tk.Frame(dialog, bg='#0C0F2E')
        button_frame.pack(pady=15)

        build_btn = None
        cancel_btn = None

    def run(self):
        """Start the application"""
        # Set icon if available (check multiple locations for bundled app)
        try:
            icon_paths = [
                "favicon.png",  # Current directory
                "assets/favicon.png",  # Bundled assets
                os.path.join(os.path.dirname(__file__),
                             "favicon.png"),  # Script directory
                os.path.join(os.path.dirname(__file__), "assets",
                             "favicon.png")  # Script assets
            ]

            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    icon = tk.PhotoImage(file=icon_path)
                    self.root.iconphoto(False, icon)
                    break

        except Exception as e:
            print(f"Could not load favicon: {e}")

        self.root.mainloop()


if __name__ == "__main__":
    app = AxarionStudio()
    app.run()
