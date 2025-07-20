import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
from pathlib import Path
import json
from PIL import Image, ImageTk
import threading

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    print("Warning: tkinterdnd2 not available. Drag and drop functionality will be limited.")

try:
    from .asset_utils import AssetUtils
except ImportError:
    from asset_utils import AssetUtils

class LocalAssetsPanel:
    """Panel for managing local assets with drag-and-drop functionality"""

    def __init__(self, parent):
        self.parent = parent
        self.assets_dir = Path("assets/local")
        self.metadata_file = Path("assets/metadata.json")
        self.asset_utils = AssetUtils()
        self.selected_assets = set()  # Track selected assets

        # Create assets directories if they don't exist
        self.ensure_asset_directories()

        # Load asset metadata
        self.load_metadata()

        # Create UI
        self.create_ui()

        # Load existing assets
        self.refresh_assets()

    def ensure_asset_directories(self):
        """Create asset directories if they don't exist"""
        directories = [
            self.assets_dir / "images",
            self.assets_dir / "sounds", 
            self.assets_dir / "fonts",
            self.assets_dir / "other"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def load_metadata(self):
        """Load asset metadata from JSON file"""
        self.metadata = {}
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
                self.metadata = {}

    def save_metadata(self):
        """Save asset metadata to JSON file"""
        try:
            self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")

    def create_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = tk.Frame(self.parent, bg='#0C0F2E')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        self.create_header(main_frame)

        # Toolbar
        self.create_toolbar(main_frame)

        # Asset grid
        self.create_asset_grid(main_frame)

    def create_header(self, parent):
        """Create the header section"""
        header_frame = tk.Frame(parent, bg='#12153C', height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(header_frame, text="Local Assets",
                              font=('Segoe UI', 18, 'bold'),
                              bg="#12153C", fg='white')
        title_label.pack(side=tk.LEFT, pady=20, padx=20)

        # Drop zone indicator
        drop_label = tk.Label(header_frame,
                             text="📁 Drag & Drop .py, .txt, images, audio & more here",
                             font=('Segoe UI', 11),
                             bg='#12153C', fg='#cccccc')
        drop_label.pack(side=tk.LEFT, pady=20, padx=(0, 20))

        # Asset count
        self.count_label = tk.Label(header_frame, text="0 assets",
                                   font=('Segoe UI', 10),
                                   bg='#12153C', fg='#999999')
        self.count_label.pack(side=tk.RIGHT, pady=20, padx=20)

    def create_toolbar(self, parent):
        """Create the toolbar with filter and import buttons"""
        toolbar_frame = tk.Frame(parent, bg="#080B2A", height=50)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        toolbar_frame.pack_propagate(False)

        # Filter section
        filter_frame = tk.Frame(toolbar_frame, bg='#080B2A')
        filter_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20)

        filter_label = tk.Label(filter_frame, text="Filter:",
                               font=('Segoe UI', 10),
                               bg='#080B2A', fg='white')
        filter_label.pack(side=tk.LEFT, pady=15)

        # Filter combobox
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                   values=["All", "Images", "Sounds", "Fonts", "Python", "Text", "Other"],
                                   state="readonly", width=10)
        filter_combo.pack(side=tk.LEFT, pady=15, padx=(10, 0))
        filter_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        # Search box
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(filter_frame, textvariable=self.search_var,
                               font=('Segoe UI', 10), width=20,
                               bg='#0C0F2E', fg='white', insertbackground='white')
        search_entry.pack(side=tk.LEFT, pady=15, padx=(20, 0))
        search_entry.bind('<KeyRelease>', self.on_search_change)

        # Action buttons
        button_frame = tk.Frame(toolbar_frame, bg='#0C0F2E')
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20)

        # Import button
        import_btn = tk.Button(button_frame, text="Import Files",
                              command=self.import_files,
                              bg='#EC4899', fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat', height=1, width=12,
                              cursor='hand2')
        import_btn.pack(side=tk.RIGHT, pady=12, padx=(0, 10))

        # Refresh button
        refresh_btn = tk.Button(button_frame, text="Refresh",
                               command=self.refresh_assets,
                               bg='#9333EA', fg='white',
                               font=('Segoe UI', 10),
                               relief='flat', height=1, width=8,
                               cursor='hand2')
        refresh_btn.pack(side=tk.RIGHT, pady=12, padx=(0, 10))

        # Open folder button
        folder_btn = tk.Button(button_frame, text="Open Folder",
                              command=self.open_assets_folder,
                              bg='#6c757d', fg='white',
                              font=('Segoe UI', 10),
                              relief='flat', height=1, width=10,
                              cursor='hand2')
        folder_btn.pack(side=tk.RIGHT, pady=12, padx=(0, 10))

        # Delete selected button
        self.delete_btn = tk.Button(button_frame, text="Delete",
                                     command=self.delete_selected_assets,
                                     bg='#dc3545', fg='white',  # Change to 'white'
                                     font=('Segoe UI', 10, 'bold'),
                                     relief='flat', height=1, width=15,
                                     cursor='hand2', state='disabled')
        self.delete_btn.pack(side=tk.RIGHT, pady=12)

    def create_asset_grid(self, parent):
        """Create the scrollable asset grid"""
        # Create scrollable frame
        canvas_frame = tk.Frame(parent, bg='#0C0F2E')
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas and scrollbar
        self.canvas = tk.Canvas(canvas_frame, bg='#0C0F2E', highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient='horizontal', command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid frame inside canvas
        self.grid_frame = tk.Frame(self.canvas, bg='#0C0F2E')
        self.canvas_window = self.canvas.create_window(0, 0, anchor='nw', window=self.grid_frame)

        # Pack scrollbars and canvas
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        self.canvas.pack(side='left', fill='both', expand=True)

        # Bind events
        self.grid_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        # Setup drag and drop if available
        if DND_AVAILABLE:
            self.setup_drag_drop()
        else:
            # Show fallback message
            fallback_label = tk.Label(self.grid_frame,
                                     text="Drag & Drop not available.\nUse Import Files button instead.",
                                     font=('Segoe UI', 12),
                                     bg='#0C0F2E', fg='#999999',
                                     justify=tk.CENTER)
            fallback_label.pack(pady=50)

    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        try:
            # Make canvas accept drops
            self.canvas.drop_target_register(DND_FILES)
            self.canvas.dnd_bind('<<Drop>>', self.on_drop)

            # Also make the grid frame accept drops
            self.grid_frame.drop_target_register(DND_FILES)
            self.grid_frame.dnd_bind('<<Drop>>', self.on_drop)
        except Exception as e:
            print(f"Error setting up drag and drop: {e}")

    def on_drop(self, event):
        """Handle file drop"""
        try:
            files = event.data.split()
            valid_files = []

            for file_path in files:
                # Clean up the file path
                file_path = file_path.strip('{}')
                if os.path.isfile(file_path):
                    valid_files.append(file_path)

            if valid_files:
                self.import_dropped_files(valid_files)
            else:
                messagebox.showwarning("Warning", "No valid files were dropped.")

        except Exception as e:
            messagebox.showerror("Error", f"Error processing dropped files: {e}")

    def import_dropped_files(self, file_paths):
        """Import dropped files"""
        imported_count = 0

        for file_path in file_paths:
            try:
                if self.import_single_file(file_path):
                    imported_count += 1
            except Exception as e:
                print(f"Error importing {file_path}: {e}")

        if imported_count > 0:
            self.refresh_assets()
            messagebox.showinfo("Success", f"Imported {imported_count} file(s) successfully!")
        else:
            messagebox.showwarning("Warning", "No files were imported.")

    def import_files(self):
        """Open file dialog to import files"""
        file_paths = filedialog.askopenfilenames(
            title="Select files to import",
            filetypes=[
                ("Python files", "*.py"),
                ("Text files", "*.txt"),
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("Audio files", "*.mp3 *.wav *.ogg *.m4a"),
                ("Font files", "*.ttf *.otf *.woff *.woff2"),
                ("Data files", "*.json *.md *.yml *.yaml"),
                ("All files", "*.*")
            ]
        )

        if file_paths:
            self.import_dropped_files(file_paths)

    def import_single_file(self, source_path):
        """Import a single file to the assets directory"""
        try:
            file_path = Path(source_path)

            # Determine target directory based on file type
            target_dir = self.get_target_directory(file_path.suffix.lower())

            # Create unique filename if file already exists
            target_path = target_dir / file_path.name
            counter = 1
            while target_path.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                target_path = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1

            # Copy file
            shutil.copy2(source_path, target_path)

            # Add to metadata
            file_info = {
                'name': target_path.name,
                'type': self.asset_utils.get_file_type(target_path.suffix),
                'size': target_path.stat().st_size,
                'imported_at': str(Path(source_path).stat().st_mtime),
                'path': str(target_path.relative_to(self.assets_dir))
            }

            self.metadata[str(target_path.relative_to(self.assets_dir))] = file_info
            self.save_metadata()

            return True

        except Exception as e:
            print(f"Error importing file {source_path}: {e}")
            return False

    def get_target_directory(self, file_ext):
        """Get target directory based on file extension"""
        image_exts = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'}
        audio_exts = {'.mp3', '.wav', '.ogg', '.m4a', '.flac'}
        font_exts = {'.ttf', '.otf', '.woff', '.woff2'}
        python_exts = {'.py'}
        text_exts = {'.txt'}

        if file_ext in image_exts:
            return self.assets_dir / "images"
        elif file_ext in audio_exts:
            return self.assets_dir / "sounds"
        elif file_ext in font_exts:
            return self.assets_dir / "fonts"
        elif file_ext in python_exts:
            return self.assets_dir / "other"  # Keep in other folder for now
        elif file_ext in text_exts:
            return self.assets_dir / "other"  # Keep in other folder for now
        else:
            return self.assets_dir / "other"

    def refresh_assets(self):
        """Refresh the asset grid"""
        # Clear selection
        self.selected_assets.clear()
        self.update_delete_button()

        # Clear existing assets
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        # Load all assets
        assets = self.load_all_assets()

        # Apply filters
        filtered_assets = self.apply_filters(assets)

        # Update count
        self.count_label.config(text=f"{len(filtered_assets)} assets")

        if not filtered_assets:
            # Show empty state
            self.show_empty_state()
        else:
            # Create asset grid
            self.create_assets_display(filtered_assets)

    def load_all_assets(self):
        """Load all assets from the assets directory"""
        assets = []

        for root, dirs, files in os.walk(self.assets_dir):
            for file in files:
                if file.startswith('.') or file == '.gitkeep':
                    continue

                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.assets_dir)

                # Get metadata or create basic info
                metadata = self.metadata.get(str(relative_path), {})

                asset_info = {
                    'name': file,
                    'path': file_path,
                    'relative_path': relative_path,
                    'type': metadata.get('type', self.asset_utils.get_file_type(file_path.suffix)),
                    'size': file_path.stat().st_size,
                    'metadata': metadata
                }

                assets.append(asset_info)

        return assets

    def apply_filters(self, assets):
        """Apply current filters to assets"""
        filtered = assets

        # Apply type filter
        filter_type = self.filter_var.get()
        if filter_type != "All":
            filtered = [a for a in filtered if a['type'].title() == filter_type]

        # Apply search filter
        search_term = self.search_var.get().lower()
        if search_term:
            filtered = [a for a in filtered if search_term in a['name'].lower()]

        return filtered

    def show_empty_state(self):
        """Show empty state message"""
        empty_frame = tk.Frame(self.grid_frame, bg='#0C0F2E')
        empty_frame.pack(fill=tk.BOTH, expand=True, pady=100)

        # Icon
        icon_label = tk.Label(empty_frame, text="📁",
                             font=('Segoe UI', 48),
                             bg='#0C0F2E', fg='#666666')
        icon_label.pack()

        # Message
        message_label = tk.Label(empty_frame,
                                text="No assets found",
                                font=('Segoe UI', 16, 'bold'),
                                bg='#0C0F2E', fg='#999999')
        message_label.pack(pady=(10, 5))

        # Instruction
        instruction_label = tk.Label(empty_frame,
                                    text="Import files using the Import button or drag & drop them here",
                                    font=('Segoe UI', 12),
                                    bg='#0C0F2E', fg='#666666')
        instruction_label.pack()

    def create_assets_display(self, assets):
        """Create the asset grid display"""
        # Calculate grid dimensions
        grid_width = 5  # Assets per row

        for i, asset in enumerate(assets):
            row = i // grid_width
            col = i % grid_width

            # Create asset card
            asset_card = self.create_asset_card(self.grid_frame, asset)
            asset_card.grid(row=row, column=col, padx=10, pady=10, sticky='nw')

    def create_asset_card(self, parent, asset):
        """Create an individual asset card"""
        card_frame = tk.Frame(parent, bg='#0C0F2E', relief='flat', bd=1)
        card_frame.config(highlightbackground='#0C0F2E', highlightthickness=1)

        # Selection checkbox
        asset_id = str(asset['relative_path'])
        checkbox_var = tk.BooleanVar()
        checkbox = tk.Checkbutton(card_frame, variable=checkbox_var,
                                 bg='#0C0F2E', fg='white', activebackground='#0C0F2E',
                                 selectcolor='#9333EA', relief='flat',
                                 command=lambda: self.toggle_asset_selection(asset_id, checkbox_var.get()))
        checkbox.pack(anchor='ne', padx=5, pady=2)

        # Thumbnail
        thumbnail_frame = tk.Frame(card_frame, bg='#0C0F2E', width=120, height=100)
        thumbnail_frame.pack(pady=(0, 5))
        thumbnail_frame.pack_propagate(False)

        # Get thumbnail
        thumbnail = self.get_asset_thumbnail(asset)
        if thumbnail:
            thumbnail_label = tk.Label(thumbnail_frame, image=thumbnail, bg='#2d2d2d')
            thumbnail_label.image = thumbnail  # Keep reference
            thumbnail_label.pack(expand=True)
        else:
            # Fallback icon
            icon = self.asset_utils.get_file_type_icon(asset['type'])
            icon_label = tk.Label(thumbnail_frame, text=icon,
                                 font=('Segoe UI', 24),
                                 bg='#0C0F2E', fg='#cccccc')
            icon_label.pack(expand=True)

        # File name (truncated)
        name = asset['name']
        if len(name) > 15:
            name = name[:12] + "..."

        name_label = tk.Label(card_frame, text=name,
                             font=('Segoe UI', 9, 'bold'),
                             bg='#0C0F2E', fg='white',
                             wraplength=120)
        name_label.pack(pady=(0, 5))

        # File info
        size_text = self.asset_utils.format_file_size(asset['size'])
        type_text = asset['type'].title()

        info_label = tk.Label(card_frame, text=f"{type_text} • {size_text}",
                             font=('Segoe UI', 8),
                             bg='#0C0F2E', fg='#999999')
        info_label.pack(pady=(0, 5))

        # Buttons frame for multiple buttons
        buttons_frame = tk.Frame(card_frame, bg='#0C0F2E')
        buttons_frame.pack(pady=(0, 5))

        # Copy as Path button
        copy_btn = tk.Button(buttons_frame, text="📋 Path",
                            command=lambda: self.copy_asset_path(asset),
                            bg='#9333EA', fg='white',
                            font=('Segoe UI', 7),
                            relief='flat', height=1, width=8,
                            cursor='hand2')
        copy_btn.pack(side=tk.LEFT, padx=(0, 2))

        # Copy Text Inside button for .txt and .py files
        file_ext = asset['path'].suffix.lower()
        if file_ext in ['.txt', '.py']:
            copy_text_btn = tk.Button(buttons_frame, text="📄 Text",
                                     command=lambda: self.copy_text_content(asset),
                                     bg='#EC4899', fg='white',
                                     font=('Segoe UI', 7),
                                     relief='flat', height=1, width=8,
                                     cursor='hand2')
            copy_text_btn.pack(side=tk.LEFT)

        # Bind events
        card_frame.bind('<Button-1>', lambda e: self.on_asset_click(asset))
        card_frame.bind('<Double-Button-1>', lambda e: self.on_asset_double_click(asset))
        card_frame.bind('<Button-3>', lambda e: self.on_asset_right_click(e, asset))

        # Hover effects
        def on_enter(e):
            if asset_id in self.selected_assets:
                card_frame.config(bg='#1a1a4a', highlightbackground='#9333EA')
            else:
                card_frame.config(bg='#0C0F2E', highlightbackground='#007ACC')

        def on_leave(e):
            if asset_id in self.selected_assets:
                card_frame.config(bg='#1a1a4a', highlightbackground='#9333EA')
            else:
                card_frame.config(bg='#0C0F2E', highlightbackground='#404040')

        card_frame.bind('<Enter>', on_enter)
        card_frame.bind('<Leave>', on_leave)

        return card_frame

    def get_asset_thumbnail(self, asset):
        """Get thumbnail for asset"""
        try:
            if asset['type'] == 'images':
                # Generate image thumbnail
                with Image.open(asset['path']) as img:
                    img.thumbnail((100, 80), Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error creating thumbnail for {asset['name']}: {e}")

        return None

    def on_asset_click(self, asset):
        """Handle asset click"""
        print(f"Clicked asset: {asset['name']}")

    def on_asset_double_click(self, asset):
        """Handle asset double-click"""
        try:
            # Open file with default system application
            if os.name == 'nt':  # Windows
                os.startfile(asset['path'])
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{asset["path"]}"' if sys.platform == 'darwin' else f'xdg-open "{asset["path"]}"')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")

    def on_asset_right_click(self, event, asset):
        """Handle asset right-click context menu"""
        context_menu = tk.Menu(self.parent, tearoff=0)

        # Copy path option (always available)
        context_menu.add_command(label="📋 Copy Path", 
                                command=lambda: self.copy_asset_path(asset))

        # Copy content for text files (prioritize .txt and .py)
        file_ext = Path(asset['path']).suffix.lower()
        
        if file_ext in ['.txt', '.py']:
            context_menu.add_command(label="📄 Copy Text Inside", 
                                    command=lambda: self.copy_text_content(asset))
        elif file_ext in {'.md', '.json', '.yml', '.yaml', '.xml', '.html', '.css', '.js'}:
            context_menu.add_command(label="📄 Copy Content", 
                                    command=lambda: self.copy_text_content(asset))

        context_menu.add_separator()
        context_menu.add_command(label="👁️ Open", 
                                command=lambda: self.on_asset_double_click(asset))
        context_menu.add_command(label="📁 Show in Explorer", 
                                command=lambda: self.show_in_explorer(asset))
        context_menu.add_separator()
        context_menu.add_command(label="🗑️ Delete", 
                                command=lambda: self.delete_asset(asset))

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def copy_asset_path(self, asset):
        """Copy asset path to clipboard"""
        try:
            # Copy relative path for use in code
            relative_path = str(asset['relative_path']).replace('\\', '/')
            engine_path = f"assets/local/{relative_path}"

            self.parent.clipboard_clear()
            self.parent.clipboard_append(engine_path)

            # Show feedback with usage example
            file_ext = Path(asset['path']).suffix.lower()
            usage_example = ""

            if file_ext in {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}:
                usage_example = f"\nExample usage:\nplayer.load_sprite(\"{engine_path}\")"
            elif file_ext in {'.mp3', '.wav', '.ogg'}:
                usage_example = f"\nExample usage:\nengine.audio.play_sound(\"{engine_path}\")"
            elif file_ext in {'.ttf', '.otf'}:
                usage_example = f"\nExample usage:\nfont = pygame.font.Font(\"{engine_path}\", 24)"

            messagebox.showinfo("Path Copied", 
                              f"Asset path copied to clipboard:\n{engine_path}{usage_example}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy path: {e}")

    def copy_text_content(self, asset):
        """Copy text file content to clipboard"""
        try:
            with open(asset['path'], 'r', encoding='utf-8') as f:
                content = f.read()

            self.parent.clipboard_clear()
            self.parent.clipboard_append(content)

            # Show feedback with file type specific message
            lines = len(content.split('\n'))
            chars = len(content)
            file_ext = asset['path'].suffix.lower()
            
            if file_ext == '.py':
                file_type = "Python code"
                usage_hint = "Ready to paste into your project!"
            elif file_ext == '.txt':
                file_type = "Text content"
                usage_hint = "Template or documentation copied!"
            else:
                file_type = "File content"
                usage_hint = "Content ready to use!"

            messagebox.showinfo("Text Copied", 
                              f"{file_type} copied to clipboard:\n"
                              f"• {lines} lines\n"
                              f"• {chars} characters\n"
                              f"• From: {asset['name']}\n\n"
                              f"{usage_hint}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy file content: {e}")

    def show_in_explorer(self, asset):
        """Show file in system file explorer"""
        try:
            if os.name == 'nt':  # Windows
                os.system(f'explorer /select,"{asset["path"]}"')
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open -R "{asset["path"]}"')
            else:  # Linux
                os.system(f'xdg-open "{asset["path"].parent}"')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open explorer: {e}")

    def delete_asset(self, asset):
        """Delete asset file"""
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete '{asset['name']}'?\n"
                              "This action cannot be undone."):
            try:
                # Remove file
                asset['path'].unlink()

                # Remove from metadata
                relative_path = str(asset['relative_path'])
                if relative_path in self.metadata:
                    del self.metadata[relative_path]
                    self.save_metadata()

                # Refresh display
                self.refresh_assets()

                messagebox.showinfo("Success", f"Deleted '{asset['name']}'")
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete file: {e}")

    def open_assets_folder(self):
        """Open the assets folder in file explorer"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(self.assets_dir)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{self.assets_dir}"')
            else:  # Linux
                os.system(f'xdg-open "{self.assets_dir}"')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}")

    def on_filter_change(self, event):
        """Handle filter change"""
        self.refresh_assets()

    def on_search_change(self, event):
        """Handle search change"""
        self.refresh_assets()

    def toggle_asset_selection(self, asset_id, selected):
        """Toggle asset selection"""
        if selected:
            self.selected_assets.add(asset_id)
        else:
            self.selected_assets.discard(asset_id)
        
        self.update_delete_button()
        self.update_card_appearance(asset_id, selected)

    def update_delete_button(self):
        """Update delete button state based on selection"""
        if self.selected_assets:
            self.delete_btn.config(state='normal')
            count = len(self.selected_assets)
            self.delete_btn.config(text=f"Delete ({count})")
        else:
            self.delete_btn.config(state='disabled')
            self.delete_btn.config(text="Delete")

    def update_card_appearance(self, asset_id, selected):
        """Update card appearance based on selection"""
        # Find and update the card visual state
        for widget in self.grid_frame.winfo_children():
            # This is a simplified approach - in practice you might want to store card references
            pass

    def delete_selected_assets(self):
        """Delete all selected assets"""
        if not self.selected_assets:
            return

        count = len(self.selected_assets)
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete {count} selected asset(s)?\n"
                              "This action cannot be undone."):
            deleted_count = 0
            failed_deletions = []

            for asset_id in list(self.selected_assets):
                try:
                    # Find the asset file
                    asset_path = self.assets_dir / asset_id
                    
                    if asset_path.exists():
                        # Remove file
                        asset_path.unlink()
                        deleted_count += 1

                        # Remove from metadata
                        if asset_id in self.metadata:
                            del self.metadata[asset_id]

                except Exception as e:
                    failed_deletions.append(f"{asset_id}: {str(e)}")

            # Save metadata
            if deleted_count > 0:
                self.save_metadata()

            # Clear selection and refresh
            self.selected_assets.clear()
            self.refresh_assets()

            # Show results
            if failed_deletions:
                error_msg = f"Deleted {deleted_count} asset(s).\n\nFailed to delete:\n" + "\n".join(failed_deletions)
                messagebox.showwarning("Partial Success", error_msg)
            else:
                messagebox.showinfo("Success", f"Successfully deleted {deleted_count} asset(s)!")

    def on_frame_configure(self, event):
        """Handle grid frame size change"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Handle canvas size change"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)