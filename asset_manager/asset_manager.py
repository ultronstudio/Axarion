import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import webbrowser

# Import asset manager components
from .local_assets import LocalAssetsPanel

class AssetManagerWindow:
    """Main Asset Manager window with simplified interface"""

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.local_assets_panel = None

        self.create_window()

    def create_window(self):
        """Create the Asset Manager window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Axarion Asset Manager")
        self.window.geometry("1000x700")
        self.window.configure(bg='#0C0F2E')

        # Make window modal
        self.window.transient(self.parent)
        self.window.grab_set()

        # Set minimum size
        self.window.minsize(800, 600)

        # Center window on screen
        self.center_window()

        # Configure close protocol
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Create UI
        self.create_ui()

    def center_window(self):
        """Center the window on the screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def create_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = tk.Frame(self.window, bg='#0C0F2E')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title bar
        self.create_title_bar(main_frame)

        # Content area
        self.create_content_area(main_frame)

    def create_title_bar(self, parent):
        """Create the title bar"""
        # Title bar
        title_frame = tk.Frame(parent, bg='#1a1d4a', height=50)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        title_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(title_frame, text="Asset Manager",
                              font=('Segoe UI', 16, 'bold'),
                              bg='#1a1d4a', fg='white')
        title_label.pack(side=tk.LEFT, pady=15, padx=20)

        # Subtitle
        subtitle_label = tk.Label(title_frame, 
                                 text="Manage local assets and browse the Asset Store",
                                 font=('Segoe UI', 10),
                                 bg='#1a1d4a', fg='#cccccc')
        subtitle_label.pack(side=tk.LEFT, pady=15)

    def create_content_area(self, parent):
        """Create the main content area with Local Assets"""
        content_frame = tk.Frame(parent, bg='#0C0F2E')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Create paned window for resizable panels
        paned_window = tk.PanedWindow(content_frame, orient=tk.HORIZONTAL,
                                     sashwidth=3, sashrelief='flat',
                                     bg='#2d2d2d', sashpad=0)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Left sidebar
        self.create_sidebar(paned_window)

        # Main content area with Local Assets
        self.create_main_content(paned_window)

    def create_sidebar(self, parent):
        """Create the left sidebar with navigation"""
        sidebar_frame = tk.Frame(parent, bg="#12153C", width=200)

        # Sidebar title
        sidebar_title = tk.Label(sidebar_frame, text="ASSET MANAGER",
                                font=('Segoe UI', 9, 'bold'),
                                bg='#12153C', fg='#cccccc')
        sidebar_title.pack(pady=(20, 10))

        # Local Assets indicator (always active)
        local_btn = tk.Label(sidebar_frame, text="📁 Local Assets",
                            bg='#9333EA', fg='white',
                            font=('Segoe UI', 11, 'bold'),
                            relief='flat', height=2, width=15)
        local_btn.pack(pady=5, padx=10, fill=tk.X)

        # Asset Store button
        store_btn = tk.Button(sidebar_frame, text="🌐 Asset Store",
                             command=self.open_asset_store,
                             bg="#29294b", fg='white',
                             font=('Segoe UI', 11),
                             relief='flat', height=2, width=15,
                             cursor='hand2')
        store_btn.pack(pady=5, padx=10, fill=tk.X)

        # Separator
        separator = tk.Frame(sidebar_frame, bg='#444', height=2)
        separator.pack(fill=tk.X, pady=20, padx=10)

        # Info section
        info_frame = tk.Frame(sidebar_frame, bg='#0C0F2E')
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        info_title = tk.Label(info_frame, text="About",
                             font=('Segoe UI', 9, 'bold'),
                             bg='#0C0F2E', fg='#cccccc')
        info_title.pack(anchor=tk.W)

        info_text = """
Import assets using drag & drop
or browse the community
Asset Store for free resources.

Supported formats:
• Python: .py files
• Text: .txt files  
• Images: PNG, JPG, GIF
• Audio: MP3, WAV, OGG
• Fonts: TTF, OTF
• Data: JSON, MD, YAML
        """

        info_label = tk.Label(info_frame, text=info_text,
                             font=('Segoe UI', 8),
                             bg='#0C0F2E', fg='#999999',
                             justify=tk.LEFT, anchor=tk.NW)
        info_label.pack(anchor=tk.W, pady=(5, 0))

        parent.add(sidebar_frame)

    def create_main_content(self, parent):
        """Create the main content area with Local Assets panel"""
        self.main_content_frame = tk.Frame(parent, bg='#0C0F2E')

        # Create Local Assets panel
        self.local_assets_panel = LocalAssetsPanel(self.main_content_frame)

        parent.add(self.main_content_frame)

    def open_asset_store(self):
        """Open Asset Store in external browser"""
        try:
            store_url = "https://axarion.onrender.com/assets.html"
            webbrowser.open(store_url)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open Asset Store: {e}")

    def on_close(self):
        """Handle window close"""
        try:
            # Release grab and destroy window
            self.window.grab_release()
            self.window.destroy()
        except:
            pass