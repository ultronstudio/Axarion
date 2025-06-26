"""
Axarion Engine Game Packager
Tool for packaging Python games into exe files with GUI interface
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import subprocess
import json
import shutil
import threading
from pathlib import Path

class GamePackager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Axarion Game Packager - Package Games to EXE")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Configuration
        self.project_path = ""
        self.output_path = ""
        self.main_file = ""
        self.game_name = ""
        self.include_assets = True
        self.icon_file = ""

        self.setup_ui()

    def setup_ui(self):
        """Create user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="🎮 Axarion Game Packager", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Project selection
        ttk.Label(main_frame, text="📁 Project:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.project_var = tk.StringVar()
        project_entry = ttk.Entry(main_frame, textvariable=self.project_var, width=50)
        project_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", 
                  command=self.select_project).grid(row=1, column=2, pady=5)

        # Main file
        ttk.Label(main_frame, text="🐍 Main file:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.main_var = tk.StringVar()
        main_entry = ttk.Entry(main_frame, textvariable=self.main_var, width=50)
        main_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Select", 
                  command=self.select_main_file).grid(row=2, column=2, pady=5)

        # Game name
        ttk.Label(main_frame, text="🎯 Game name:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value="MyGame")
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=50)
        name_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)

        # Output folder
        ttk.Label(main_frame, text="📦 Output:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar()
        output_entry = ttk.Entry(main_frame, textvariable=self.output_var, width=50)
        output_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Select", 
                  command=self.select_output).grid(row=4, column=2, pady=5)

        # Icon (optional)
        ttk.Label(main_frame, text="🖼️ Icon (optional):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.icon_var = tk.StringVar()
        icon_entry = ttk.Entry(main_frame, textvariable=self.icon_var, width=50)
        icon_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Select", 
                  command=self.select_icon).grid(row=5, column=2, pady=5)

        # Options
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Packaging Options", padding="10")
        options_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        options_frame.columnconfigure(0, weight=1)

        self.assets_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="📁 Include assets folder", 
                       variable=self.assets_var).grid(row=0, column=0, sticky=tk.W)

        self.console_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="💻 Show console", 
                       variable=self.console_var).grid(row=1, column=0, sticky=tk.W)

        self.single_file_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="📋 Single file (slower startup)", 
                       variable=self.single_file_var).grid(row=2, column=0, sticky=tk.W)

        # Progress bar
        self.progress_var = tk.StringVar(value="Ready to package")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=7, column=0, columnspan=3, pady=10)

        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=3, pady=20)

        ttk.Button(button_frame, text="🏗️ Check Dependencies", 
                  command=self.check_dependencies).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="📦 Package Game", 
                  command=self.package_game, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="📋 Generate Spec", 
                  command=self.generate_spec).pack(side=tk.LEFT, padx=5)

        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="📝 Output Log", padding="5")
        log_frame.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Configure layout
        main_frame.rowconfigure(10, weight=1)

    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def select_project(self):
        """Select project folder"""
        folder = filedialog.askdirectory(title="Select project folder")
        if folder:
            self.project_var.set(folder)
            self.project_path = folder

            # Automatically find main file
            for file in ["main.py", "game.py", "app.py"]:
                if os.path.exists(os.path.join(folder, file)):
                    self.main_var.set(file)
                    break

            # Set output folder
            if not self.output_var.get():
                self.output_var.set(os.path.join(folder, "dist"))

    def select_main_file(self):
        """Select main file"""
        if not self.project_path:
            messagebox.showwarning("Warning", "Please select project folder first")
            return

        file = filedialog.askopenfilename(
            title="Select main Python file",
            initialdir=self.project_path,
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if file:
            # Relative path to project
            rel_path = os.path.relpath(file, self.project_path)
            self.main_var.set(rel_path)

    def select_output(self):
        """Select output folder"""
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_var.set(folder)

    def select_icon(self):
        """Select icon"""
        file = filedialog.askopenfilename(
            title="Select icon",
            filetypes=[("Icons", "*.ico"), ("Images", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
        )
        if file:
            self.icon_var.set(file)

    def check_dependencies(self):
        """Check PyInstaller"""
        self.log("🔍 Checking dependencies...")

        try:
            import PyInstaller
            self.log(f"✅ PyInstaller found: version {PyInstaller.__version__}")
        except ImportError:
            self.log("❌ PyInstaller is not installed")
            response = messagebox.askyesno(
                "Missing PyInstaller", 
                "PyInstaller is not installed. Do you want to install it?"
            )
            if response:
                self.install_pyinstaller()
            return False

        # Check pygame
        try:
            import pygame
            self.log(f"✅ Pygame found: version {pygame.version.ver}")
        except ImportError:
            self.log("⚠️ Pygame is not installed - may be needed for the game")

        return True

    def install_pyinstaller(self):
        """Install PyInstaller"""
        self.log("📦 Installing PyInstaller...")
        self.progress_bar.start()

        def install():
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                             check=True, capture_output=True, text=True)
                self.log("✅ PyInstaller successfully installed")
            except subprocess.CalledProcessError as e:
                self.log(f"❌ Installation error: {e}")
            finally:
                self.progress_bar.stop()

        threading.Thread(target=install, daemon=True).start()

    def generate_spec(self):
        """Generate .spec file"""
        if not self.validate_inputs():
            return

        self.log("📋 Generating specification file...")

        spec_content = self.create_spec_content()

        spec_file = os.path.join(self.project_path, f"{self.name_var.get()}.spec")

        try:
            with open(spec_file, 'w', encoding='utf-8') as f:
                f.write(spec_content)
            self.log(f"✅ Specification created: {spec_file}")
            messagebox.showinfo("Done", f"Specification created at:\n{spec_file}")
        except Exception as e:
            self.log(f"❌ Error creating specification: {e}")

    def create_spec_content(self):
        """Create .spec file content"""
        game_name = self.name_var.get()
        main_file = self.main_var.get()

        # Basic data files
        datas = []
        if self.assets_var.get():
            assets_path = os.path.join(self.project_path, "assets")
            if os.path.exists(assets_path):
                datas.append("('assets', 'assets')")

        # Engine files
        engine_path = os.path.join(self.project_path, "engine")
        if os.path.exists(engine_path):
            datas.append("('engine', 'engine')")

        # Scripting files
        scripting_path = os.path.join(self.project_path, "scripting")
        if os.path.exists(scripting_path):
            datas.append("('scripting', 'scripting')")

        datas_str = "[" + ", ".join(datas) + "]" if datas else "[]"

        icon_line = f"icon='{self.icon_var.get()}'," if self.icon_var.get() else ""
        console_line = "console=True," if self.console_var.get() else "console=False,"

        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
# Axarion Engine Game Package Specification
# Generated by Game Packager

a = Analysis(
    ['{main_file}'],
    pathex=[],
    binaries=[],
    datas={datas_str},
    hiddenimports=['pygame', 'json', 'math', 'random', 'typing'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='{game_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    {console_line}
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_line}
)
"""
        return spec_content

    def validate_inputs(self):
        """Validate inputs"""
        if not self.project_path:
            messagebox.showerror("Error", "Select project folder")
            return False

        if not self.main_var.get():
            messagebox.showerror("Error", "Select main file")
            return False

        main_path = os.path.join(self.project_path, self.main_var.get())
        if not os.path.exists(main_path):
            messagebox.showerror("Error", "Main file does not exist")
            return False

        if not self.name_var.get():
            messagebox.showerror("Error", "Enter game name")
            return False

        if not self.output_var.get():
            messagebox.showerror("Error", "Select output folder")
            return False

        return True

    def package_game(self):
        """Package game to exe"""
        if not self.validate_inputs():
            return

        if not self.check_dependencies():
            return

        self.log("🚀 Starting game packaging...")
        self.progress_bar.start()
        self.progress_var.set("Packaging game...")

        def package():
            try:
                # Create output folder
                os.makedirs(self.output_var.get(), exist_ok=True)

                # Prepare PyInstaller arguments
                args = [
                    sys.executable, "-m", "PyInstaller",
                    "--clean",
                    "--distpath", self.output_var.get(),
                    "--workpath", os.path.join(self.output_var.get(), "build"),
                    "--specpath", self.project_path,
                    "--name", self.name_var.get()
                ]

                # Add options
                if self.single_file_var.get():
                    args.append("--onefile")
                else:
                    args.append("--onedir")

                if not self.console_var.get():
                    args.append("--windowed")

                if self.icon_var.get():
                    args.extend(["--icon", self.icon_var.get()])

                # Add data
                if self.assets_var.get():
                    assets_path = os.path.join(self.project_path, "assets")
                    if os.path.exists(assets_path):
                        args.extend(["--add-data", f"{assets_path};assets"])

                # Add engine folder - REQUIRED for Axarion games
                engine_path = os.path.join(self.project_path, "engine")
                if os.path.exists(engine_path):
                    args.extend(["--add-data", f"{engine_path};engine"])
                    self.log("✅ Including Axarion Engine - players won't need separate installation")
                else:
                    self.log("⚠️ Warning: No engine folder found - looking for system-wide installation")

                # Add scripting folder - AXScript support
                scripting_path = os.path.join(self.project_path, "scripting")
                if os.path.exists(scripting_path):
                    args.extend(["--add-data", f"{scripting_path};scripting"])
                    self.log("✅ Including AXScript system")

                # Add utils folder if exists
                utils_path = os.path.join(self.project_path, "utils")
                if os.path.exists(utils_path):
                    args.extend(["--add-data", f"{utils_path};utils"])
                    self.log("✅ Including utility modules")

                # Hidden imports
                hidden_imports = ["pygame", "json", "math", "random", "typing"]
                for imp in hidden_imports:
                    args.extend(["--hidden-import", imp])

                # Main file
                args.append(os.path.join(self.project_path, self.main_var.get()))

                self.log(f"📋 Running: {' '.join(args)}")

                # Run PyInstaller
                result = subprocess.run(
                    args, 
                    cwd=self.project_path,
                    capture_output=True, 
                    text=True
                )

                if result.returncode == 0:
                    self.log("✅ Packaging completed successfully!")
                    exe_path = os.path.join(self.output_var.get(), f"{self.name_var.get()}.exe")
                    self.log(f"📦 EXE file: {exe_path}")

                    # Show result
                    messagebox.showinfo(
                        "Done!", 
                        f"Game was successfully packaged!\n\nEXE file: {exe_path}"
                    )

                    # Option to open folder
                    if messagebox.askyesno("Open folder", "Do you want to open the output folder?"):
                        if sys.platform == "win32":
                            os.startfile(self.output_var.get())
                        else:
                            subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", 
                                          self.output_var.get()])
                else:
                    self.log(f"❌ Packaging error:")
                    self.log(result.stderr)
                    messagebox.showerror("Error", f"Packaging failed:\n{result.stderr[:500]}")

            except Exception as e:
                self.log(f"❌ Unexpected error: {e}")
                messagebox.showerror("Error", f"Unexpected error: {e}")
            finally:
                self.progress_bar.stop()
                self.progress_var.set("Ready to package")

        # Run in new thread
        threading.Thread(target=package, daemon=True).start()

    def create_sample_project(self):
        """Create sample project"""
        folder = filedialog.askdirectory(title="Select folder for sample project")
        if not folder:
            return

        project_folder = os.path.join(folder, "MyFirstAxarionProject")
        os.makedirs(project_folder, exist_ok=True)

        # Create main file
        main_content = '''"""
My first Axarion project
Simple game created with Axarion Engine
"""

from engine.core import AxarionEngine
from engine.game_object import GameObject

def main():
    # Create engine
    engine = AxarionEngine(800, 600, "My first game")
    engine.initialize()

    # Create scene
    scene = engine.create_scene("Main")
    engine.current_scene = scene

    # Create player
    player = GameObject("Player", "rectangle")
    player.position = (400, 300)
    player.set_property("width", 50)
    player.set_property("height", 50)
    player.set_property("color", (100, 150, 255))

    # Control script
    player.script_code = """
var speed = 200;

function update() {
    if (keyPressed("ArrowLeft")) {
        move(-speed * 0.016, 0);
    }
    if (keyPressed("ArrowRight")) {
        move(speed * 0.016, 0);
    }
    if (keyPressed("ArrowUp")) {
        move(0, -speed * 0.016);
    }
    if (keyPressed("ArrowDown")) {
        move(0, speed * 0.016);
    }
}
"""

    scene.add_object(player)

    # Start game
    engine.run()

if __name__ == "__main__":
    main()
'''

        with open(os.path.join(project_folder, "main.py"), 'w', encoding='utf-8') as f:
            f.write(main_content)

        self.log(f"✅ Sample project created at: {project_folder}")
        messagebox.showinfo("Done", f"Sample project created at:\n{project_folder}")

    def run(self):
        """Start application"""
        self.log("🎮 Axarion Game Packager started")
        self.log("📝 Select project and configure packaging options")
        self.log("💡 Tip: Use 'Check Dependencies' before packaging")
        self.root.mainloop()

def main():
    """Main function"""
    print("🎮 Starting Axarion Game Packager...")
    app = GamePackager()
    app.run()

if __name__ == "__main__":
    main()