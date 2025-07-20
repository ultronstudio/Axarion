import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import tkinter.font as tkfont
import os
import sys
import subprocess
import threading
import tempfile
import shutil
from pathlib import Path
import json

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available - using fallback logo display")


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

    def update_colors(self, start_color=None, end_color=None, text=None):
        """Update button colors and text"""
        if start_color:
            self.start_color = start_color
        if end_color:
            self.end_color = end_color
        if text:
            self.text = text
        self.draw_gradient()

    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb):
        """Convert RGB tuple to hex color"""
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

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


class AxarionGameBuilder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Axarion Game Builder")
        self.root.geometry("700x800")
        self.root.configure(bg='#0C0F2E')
        self.root.resizable(False, False)

        # Build configuration
        self.selected_game_file = None
        self.selected_icon_file = None
        self.build_thread = None
        self.building = False
        self.icon_status_label = None

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#0C0F2E')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header section with logo
        self.create_header(main_frame)

        # File selection area
        self.create_file_selection_area(main_frame)

        # Console area with build button
        self.create_console_area(main_frame)

    def create_header(self, parent):
        """Create header with logo and title"""
        header_frame = tk.Frame(parent, bg='#1a1d4a', relief='raised', bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Try to load Builder_Logo.png
        try:
            logo_paths = [
                "Builder_Logo.png",
                "assets/Builder_Logo.png", 
                "attached_assets/Builder_Logo.png",
                os.path.join(os.path.dirname(__file__), "Builder_Logo.png"),
                os.path.join(os.path.dirname(__file__), "assets", "Builder_Logo.png"),
                os.path.join(os.path.dirname(__file__), "attached_assets", "Builder_Logo.png")
            ]

            logo_found = False
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    if PIL_AVAILABLE:
                        logo_pil = Image.open(logo_path)
                        logo_pil.thumbnail((650, 325), Image.Resampling.LANCZOS)
                        logo_image = ImageTk.PhotoImage(logo_pil)
                        logo_label = tk.Label(header_frame, image=logo_image, bg='#1a1d4a')
                        logo_label.image = logo_image  # Keep reference
                        logo_label.pack(pady=20)
                        logo_found = True
                        break
                    else:
                        logo_image = tk.PhotoImage(file=logo_path)
                        # Don't subsample to keep it larger
                        logo_label = tk.Label(header_frame, image=logo_image, bg='#1a1d4a')
                        logo_label.image = logo_image  # Keep reference
                        logo_label.pack(pady=20)
                        logo_found = True
                        break

            if not logo_found:
                # Fallback header
                title_label = tk.Label(header_frame,
                                       text="🚀 AXARION\nGAME BUILDER",
                                       font=('Segoe UI', 24, 'bold'),
                                       bg='#1a1d4a',
                                       fg='white',
                                       justify=tk.CENTER)
                title_label.pack(pady=20)

        except Exception as e:
            print(f"Could not load Builder_Logo.png: {e}")
            # Fallback header
            title_label = tk.Label(header_frame,
                                   text="🚀 AXARION\nGAME BUILDER",
                                   font=('Segoe UI', 24, 'bold'),
                                   bg='#1a1d4a',
                                   fg='white',
                                   justify=tk.CENTER)
            title_label.pack(pady=20)

    def create_file_selection_area(self, parent):
        """Create file selection area with icon and game file selection"""
        selection_frame = tk.Frame(parent, bg='#0C0F2E')
        selection_frame.pack(fill=tk.X, pady=(0, 20))

        # Left side - Icon selection
        icon_frame = tk.Frame(selection_frame, bg='#1a1d4a', relief='raised', bd=1, width=200)
        icon_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        icon_frame.pack_propagate(False)

        # Icon preview area
        self.icon_preview_frame = tk.Frame(icon_frame, bg='#0C0F2E', width=150, height=150)
        self.icon_preview_frame.pack(pady=20, padx=25)
        self.icon_preview_frame.pack_propagate(False)

        # Default icon placeholder
        self.icon_preview_label = tk.Label(self.icon_preview_frame,
                                           text="🚀",
                                           font=('Segoe UI', 48),
                                           bg='#0C0F2E',
                                           fg='#FF6B35')
        self.icon_preview_label.pack(expand=True)

        # Choose icon button
        icon_btn = GradientButton(icon_frame,
                                  text="Change Icon",
                                  command=self.choose_icon,
                                  width=120,
                                  height=35,
                                  start_color='#FF6B35',
                                  end_color='#FF8E53')
        icon_btn.pack(pady=(10, 20))

        # Right side - Game file selection and other buttons
        buttons_frame = tk.Frame(selection_frame, bg='#0C0F2E')
        buttons_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Game file selection
        game_label = tk.Label(buttons_frame,
                              text="Select Python Game File:",
                              font=('Segoe UI', 12, 'bold'),
                              bg='#0C0F2E',
                              fg='white')
        game_label.pack(anchor='w', pady=(0, 10))

        self.game_file_label = tk.Label(buttons_frame,
                                        text="No game file selected",
                                        font=('Segoe UI', 10),
                                        bg='#1a1d4a',
                                        fg='#888888',
                                        relief='sunken',
                                        bd=1,
                                        anchor='w',
                                        padx=10,
                                        pady=5)
        self.game_file_label.pack(fill=tk.X, pady=(0, 10))

        # Choose game file button
        game_btn = GradientButton(buttons_frame,
                                  text="Choose Game File",
                                  command=self.choose_game_file,
                                  width=150,
                                  height=35,
                                  start_color='#EC4899',
                                  end_color='#F472B6')
        game_btn.pack(anchor='w', pady=(0, 10))

        # Build button next to game file selection
        self.build_btn_top = GradientButton(buttons_frame,
                                           text="BUILD",
                                           command=self.start_build,
                                           width=150,
                                           height=35,
                                           start_color='#9333EA',
                                           end_color='#A855F7')
        self.build_btn_top.pack(anchor='w', pady=(0, 20))

        # Icon status label
        self.icon_status_label = tk.Label(buttons_frame,
                                          text="No icon selected",
                                          font=('Segoe UI', 9),
                                          bg='#0C0F2E',
                                          fg='#888888')
        self.icon_status_label.pack(anchor='w', pady=(0, 10))

        # Build type selection
        build_type_frame = tk.Frame(buttons_frame, bg='#0C0F2E')
        build_type_frame.pack(anchor='w', pady=(0, 20))

        build_type_label = tk.Label(build_type_frame,
                                   text="Build Type:",
                                   font=('Segoe UI', 10, 'bold'),
                                   bg='#0C0F2E',
                                   fg='white')
        build_type_label.pack(anchor='w')

        self.build_single_exe = tk.BooleanVar(value=True)
        self.build_type_checkbox = tk.Checkbutton(build_type_frame,
                                                 text="Single EXE file (recommended)",
                                                 variable=self.build_single_exe,
                                                 font=('Segoe UI', 9),
                                                 bg='#0C0F2E',
                                                 fg='white',
                                                 selectcolor='#1a1d4a',
                                                 activebackground='#0C0F2E',
                                                 activeforeground='white')
        self.build_type_checkbox.pack(anchor='w', pady=(5, 0))

        build_help_label = tk.Label(build_type_frame,
                                   text="Unchecked: Creates folder with EXE + assets",
                                   font=('Segoe UI', 8),
                                   bg='#0C0F2E',
                                   fg='#888888')
        build_help_label.pack(anchor='w', pady=(2, 0))

    def create_console_area(self, parent):
        """Create console output area"""
        console_frame = tk.Frame(parent, bg='#0C0F2E')
        console_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Console label
        console_label = tk.Label(console_frame,
                                 text="CONSOLE",
                                 font=('Segoe UI', 16, 'bold'),
                                 bg='#0C0F2E',
                                 fg='white')
        console_label.pack(anchor='w', pady=(0, 10))

        # Console text area
        console_inner_frame = tk.Frame(console_frame, bg='#000000', relief='sunken', bd=2)
        console_inner_frame.pack(fill=tk.BOTH, expand=True)

        self.console_text = scrolledtext.ScrolledText(console_inner_frame,
                                                      bg='#000000',
                                                      fg='#00FF00',
                                                      font=('Consolas', 10),
                                                      wrap=tk.WORD,
                                                      state='disabled')
        self.console_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add welcome message
        self.log_message("🚀 Axarion Game Builder Ready")
        self.log_message("Select a Python game file and click Build to create an EXE")

        # Build button at bottom of console area
        build_frame = tk.Frame(console_frame, bg='#0C0F2E')
        build_frame.pack(fill=tk.X, pady=(10, 0))

        self.build_btn = GradientButton(build_frame,
                                        text="BUILD",
                                        command=self.start_build,
                                        width=660,
                                        height=60,
                                        start_color='#9333EA',
                                        end_color='#A855F7')
        self.build_btn.pack()

    def choose_icon(self):
        """Choose icon file for the EXE"""
        file_path = filedialog.askopenfilename(
            title="Select Icon File for EXE",
            filetypes=[
                ("Recommended: ICO files", "*.ico"),
                ("PNG files (will be converted)", "*.png"),
                ("JPEG files (will be converted)", "*.jpg;*.jpeg"),
                ("All supported images", "*.ico;*.png;*.jpg;*.jpeg"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            # Create Builder_Icons folder if it doesn't exist
            builder_icons_dir = os.path.join(os.path.dirname(__file__), "Builder_Icons")
            os.makedirs(builder_icons_dir, exist_ok=True)
            
            # Copy icon to Builder_Icons folder
            filename = os.path.basename(file_path)
            icon_destination = os.path.join(builder_icons_dir, filename)
            
            try:
                shutil.copy2(file_path, icon_destination)
                self.selected_icon_file = icon_destination
                self.icon_status_label.configure(text=f"Icon: {filename}", fg='white')
                self.log_message(f"✓ Icon saved to Builder_Icons: {filename}")
                
                # Try to preview the icon
                try:
                    if PIL_AVAILABLE and file_path.lower().endswith(('.png', '.ico', '.jpg', '.jpeg')):
                        icon_image = Image.open(icon_destination)
                        # Convert to RGBA if needed for preview
                        if icon_image.mode not in ('RGBA', 'RGB'):
                            icon_image = icon_image.convert('RGBA')
                        icon_image.thumbnail((100, 100), Image.Resampling.LANCZOS)
                        icon_photo = ImageTk.PhotoImage(icon_image)
                        self.icon_preview_label.configure(image=icon_photo, text="")
                        self.icon_preview_label.image = icon_photo  # Keep reference

                        # Show format info
                        if file_path.lower().endswith('.ico'):
                            self.log_message("✓ ICO format - optimal for Windows executables")
                        else:
                            self.log_message("ℹ️ Will be converted to ICO format during build")
                    else:
                        self.icon_preview_label.configure(text="🖼️", image="")
                        self.log_message("⚠️ Icon preview not available - PIL not installed")
                except Exception as e:
                    self.log_message(f"⚠️ Could not preview icon: {e}")
                    self.icon_preview_label.configure(text="❓", image="")
                    
            except Exception as e:
                self.log_message(f"❌ Failed to copy icon to Builder_Icons: {e}")
                self.selected_icon_file = file_path  # Fallback to original path

    def choose_game_file(self):
        """Choose Python game file to build"""
        file_path = filedialog.askopenfilename(
            title="Select Python Game File",
            filetypes=[
                ("Python files", "*.py"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self.selected_game_file = file_path
            filename = os.path.basename(file_path)
            self.game_file_label.configure(text=filename, fg='white')
            self.log_message(f"✓ Game file selected: {filename}")

    def log_message(self, message):
        """Add message to console"""
        self.console_text.configure(state='normal')
        self.console_text.insert(tk.END, f"{message}\n")
        self.console_text.configure(state='disabled')
        self.console_text.see(tk.END)
        self.root.update_idletasks()

    def start_build(self):
        """Start the build process"""
        if self.building:
            self.log_message("❌ Build already in progress!")
            return

        if not self.selected_game_file:
            messagebox.showerror("Error", "Please select a Python game file first!")
            return

        if not os.path.exists(self.selected_game_file):
            messagebox.showerror("Error", "Selected game file does not exist!")
            return

        # Start build in separate thread
        self.building = True
        self.build_btn.update_colors(start_color='#666666', end_color='#888888', text="BUILDING...")
        self.build_btn_top.update_colors(start_color='#666666', end_color='#888888', text="BUILDING...")

        self.build_thread = threading.Thread(target=self.build_game, daemon=True)
        self.build_thread.start()

    def build_game(self):
        """Build the game using PyInstaller with bundled engine"""
        try:
            self.log_message("🔨 Starting build process...")
            
            # Check PyInstaller
            self.log_message("📦 Checking PyInstaller...")
            try:
                result = subprocess.run([sys.executable, "-c", "import PyInstaller"], 
                                       capture_output=True, text=True)
                if result.returncode != 0:
                    self.log_message("📦 Installing PyInstaller...")
                    result = subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                                           capture_output=True, text=True)
                    if result.returncode != 0:
                        self.log_message(f"❌ Failed to install PyInstaller: {result.stderr}")
                        return
                    self.log_message("✓ PyInstaller installed successfully")
                else:
                    self.log_message("✓ PyInstaller is available")
            except Exception as e:
                self.log_message(f"❌ Error checking PyInstaller: {e}")
                return

            # Create temp directory for build
            temp_dir = tempfile.mkdtemp(prefix="axarion_build_")
            self.log_message(f"📁 Using temp directory: {temp_dir}")

            try:
                # Copy game file to temp directory
                game_name = os.path.splitext(os.path.basename(self.selected_game_file))[0]
                temp_game_file = os.path.join(temp_dir, f"{game_name}.py")
                shutil.copy2(self.selected_game_file, temp_game_file)
                self.log_message(f"📋 Copied game file to: {temp_game_file}")

                # Copy engine folder to temp directory
                engine_source = os.path.join(os.path.dirname(__file__), "engine")
                if os.path.exists(engine_source):
                    engine_dest = os.path.join(temp_dir, "engine")
                    shutil.copytree(engine_source, engine_dest)
                    self.log_message("📦 Bundled Axarion Engine")
                else:
                    self.log_message("⚠️ Engine folder not found, game may not work standalone")

                # Prepare PyInstaller command
                output_dir = os.path.join(os.path.dirname(self.selected_game_file), "dist")
                os.makedirs(output_dir, exist_ok=True)

                # Choose build type based on checkbox
                if self.build_single_exe.get():
                    build_mode = "--onefile"
                    self.log_message("🎯 Building as single EXE file")
                else:
                    build_mode = "--onedir"
                    self.log_message("📁 Building as folder with separate files")

                cmd = [
                    sys.executable, "-m", "PyInstaller",
                    build_mode,
                    "--windowed",
                    "--distpath", output_dir,
                    "--workpath", os.path.join(temp_dir, "work"),
                    "--specpath", temp_dir,
                    "--name", game_name
                ]

                # Add icon if selected
                if self.selected_icon_file and os.path.exists(self.selected_icon_file):
                    self.log_message(f"🎨 Adding custom icon: {os.path.basename(self.selected_icon_file)}")
                    
                    # Always convert to ICO format in temp directory for best compatibility
                    ico_path = os.path.join(temp_dir, f"{game_name}_icon.ico")
                    
                    try:
                        if PIL_AVAILABLE:
                            # Convert image to ICO format
                            img = Image.open(self.selected_icon_file)
                            self.log_message(f"📷 Processing icon: {img.size}, mode: {img.mode}")
                            
                            # Ensure proper format for ICO
                            if img.mode == 'RGBA':
                                # Keep transparency
                                pass
                            elif img.mode == 'LA':
                                img = img.convert('RGBA')
                            elif img.mode not in ('RGB', 'RGBA'):
                                img = img.convert('RGBA')
                            
                            # Create multiple sizes for ICO (required for Windows)
                            icon_sizes = [256, 128, 64, 48, 32, 16]
                            icon_images = []
                            
                            for size in icon_sizes:
                                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                                icon_images.append(resized)
                            
                            # Save as ICO with multiple sizes
                            icon_images[0].save(
                                ico_path, 
                                format='ICO',
                                sizes=[(size, size) for size in icon_sizes],
                                append_images=icon_images[1:]
                            )
                            
                            cmd.extend(["--icon", ico_path])
                            self.log_message(f"✅ Icon converted to ICO: {ico_path}")
                            self.log_message(f"📊 ICO file size: {os.path.getsize(ico_path) / 1024:.1f} KB")
                            
                        else:
                            # PIL not available, try direct copy if it's already ICO
                            if self.selected_icon_file.lower().endswith('.ico'):
                                shutil.copy2(self.selected_icon_file, ico_path)
                                cmd.extend(["--icon", ico_path])
                                self.log_message(f"✅ Using ICO file directly: {ico_path}")
                            else:
                                self.log_message("⚠️ PIL not available - cannot convert non-ICO files")
                                self.log_message("💡 Install Pillow with: pip install Pillow")
                                
                    except Exception as e:
                        self.log_message(f"❌ Icon processing failed: {e}")
                        self.log_message("🔄 Continuing build without custom icon")
                else:
                    self.log_message("🎨 No custom icon selected - using PyInstaller default")

                # Add comprehensive engine packaging
                cmd.extend([
                    # Core Python modules
                    "--hidden-import", "pygame",
                    "--hidden-import", "pygame.mixer",
                    "--hidden-import", "pygame.font",
                    "--hidden-import", "pygame.image",
                    "--hidden-import", "pygame.transform",
                    "--hidden-import", "pygame.display",
                    "--hidden-import", "pygame.event",
                    "--hidden-import", "pygame.time",
                    "--hidden-import", "pygame.key",
                    "--hidden-import", "pygame.mouse",
                    "--hidden-import", "pygame.locals",
                    # Engine modules
                    "--hidden-import", "engine",
                    "--hidden-import", "engine.core",
                    "--hidden-import", "engine.renderer",
                    "--hidden-import", "engine.game_object",
                    "--hidden-import", "engine.scene",
                    "--hidden-import", "engine.physics",
                    "--hidden-import", "engine.audio_system",
                    "--hidden-import", "engine.input_system",
                    "--hidden-import", "engine.camera",
                    "--hidden-import", "engine.particle_system",
                    "--hidden-import", "engine.animation_system",
                    "--hidden-import", "engine.tilemap",
                    "--hidden-import", "engine.state_machine",
                    "--hidden-import", "engine.asset_manager",
                    # Standard library modules commonly used in games
                    "--hidden-import", "math",
                    "--hidden-import", "random",
                    "--hidden-import", "json",
                    "--hidden-import", "os",
                    "--hidden-import", "sys",
                    "--hidden-import", "pathlib",
                    # Bundle engine folder as data
                    "--add-data", f"{engine_dest}{os.pathsep}engine"
                ])

                cmd.append(temp_game_file)

                self.log_message("🔨 Building executable...")
                self.log_message("=" * 80)
                self.log_message("EXACT PYINSTALLER COMMAND:")
                self.log_message(" ".join(cmd))
                self.log_message("=" * 80)
                
                # Show individual command parts for debugging
                self.log_message("COMMAND BREAKDOWN:")
                for i, part in enumerate(cmd):
                    if "--icon" in part or (i > 0 and cmd[i-1] == "--icon"):
                        self.log_message(f"  [{i}] {part} ← ICON PARAMETER")
                    else:
                        self.log_message(f"  [{i}] {part}")
                self.log_message("=" * 80)

                # Run PyInstaller
                self.log_message("🚀 Executing PyInstaller...")
                result = subprocess.run(cmd, cwd=temp_dir, capture_output=True, text=True)

                # Show PyInstaller output
                self.log_message("=" * 80)
                self.log_message("PYINSTALLER OUTPUT:")
                if result.stdout:
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            self.log_message(f"OUT: {line}")
                if result.stderr:
                    for line in result.stderr.split('\n'):
                        if line.strip():
                            self.log_message(f"ERR: {line}")
                self.log_message("=" * 80)
                self.log_message(f"PyInstaller exit code: {result.returncode}")

                if result.returncode == 0:
                    if self.build_single_exe.get():
                        # Single file build
                        exe_name = f"{game_name}.exe" if sys.platform == "win32" else game_name
                        exe_path = os.path.join(output_dir, exe_name)

                        if os.path.exists(exe_path):
                            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # Size in MB
                            self.log_message("🎉 BUILD SUCCESSFUL!")
                            self.log_message(f"✓ Single EXE created: {exe_path}")
                            self.log_message(f"📊 File size: {file_size:.1f} MB")
                            self.log_message("🚀 Single file - easy to distribute!")
                        else:
                            self.log_message("❌ Build completed but executable not found")
                    else:
                        # Folder build
                        folder_path = os.path.join(output_dir, game_name)
                        exe_name = f"{game_name}.exe" if sys.platform == "win32" else game_name
                        exe_path = os.path.join(folder_path, exe_name)

                        if os.path.exists(exe_path):
                            # Calculate total folder size
                            total_size = 0
                            for dirpath, dirnames, filenames in os.walk(folder_path):
                                for filename in filenames:
                                    filepath = os.path.join(dirpath, filename)
                                    total_size += os.path.getsize(filepath)
                            folder_size = total_size / (1024 * 1024)  # Size in MB

                            self.log_message("🎉 BUILD SUCCESSFUL!")
                            self.log_message(f"✓ Game folder created: {folder_path}")
                            self.log_message(f"✓ Main executable: {exe_path}")
                            self.log_message(f"📊 Total folder size: {folder_size:.1f} MB")
                            self.log_message("🚀 Distribute the entire folder together!")
                        else:
                            self.log_message("❌ Build completed but executable not found")

            finally:
                # Clean up temp directory
                try:
                    shutil.rmtree(temp_dir)
                    self.log_message("🧹 Cleaned up temporary files")
                except Exception as e:
                    self.log_message(f"⚠️ Could not clean temp directory: {e}")

        except Exception as e:
            self.log_message(f"❌ Build failed with exception: {e}")
        finally:
            # Reset build button
            self.building = False
            self.root.after(0, self.reset_build_button)

    def reset_build_button(self):
        """Reset build button to normal state"""
        self.build_btn.update_colors(start_color='#9333EA', end_color='#A855F7', text="BUILD")
        self.build_btn_top.update_colors(start_color='#9333EA', end_color='#A855F7', text="BUILD")

    def run(self):
        """Start the application"""
        # Set icon if available
        try:
            icon_paths = [
                "buildericon.png",
                "favicon.png",
                "assets/buildericon.png",
                "assets/favicon.png",
                os.path.join(os.path.dirname(__file__), "buildericon.png"),
                os.path.join(os.path.dirname(__file__), "favicon.png"),
                os.path.join(os.path.dirname(__file__), "assets", "buildericon.png"),
                os.path.join(os.path.dirname(__file__), "assets", "favicon.png")
            ]

            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    icon = tk.PhotoImage(file=icon_path)
                    self.root.iconphoto(False, icon)
                    break
        except Exception as e:
            print(f"Could not load favicon: {e}")

        self.root.mainloop()


def main():
    """Main entry point for the Game Builder"""
    app = AxarionGameBuilder()
    app.run()

if __name__ == "__main__":
    main()