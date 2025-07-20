#!/usr/bin/env python3
"""
Axarion Studio Build Script
Creates a standalone executable with embedded engine, assets, and icons
"""

import os
import sys
import subprocess
import shutil
import tempfile
import json
from pathlib import Path

class AxarionStudioBuilder:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.build_dir = self.root_dir / "dist"
        self.temp_dir = None

    def log(self, message):
        """Print build log message"""
        print(f"🔨 {message}")

    def error(self, message):
        """Print error message"""
        print(f"❌ ERROR: {message}")

    def success(self, message):
        """Print success message"""
        print(f"✅ {message}")

    def check_dependencies(self):
        """Check and install required dependencies"""
        self.log("Checking build dependencies...")

        # Check PyInstaller
        try:
            import PyInstaller
            self.success("PyInstaller is available")
        except ImportError:
            self.log("Installing PyInstaller...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                             check=True, capture_output=True)
                self.success("PyInstaller installed")
            except subprocess.CalledProcessError as e:
                self.error(f"Failed to install PyInstaller: {e}")
                return False

        # Check other dependencies
        required_packages = ['pillow', 'pygame', 'tkinterdnd2', 'requests']
        for package in required_packages:
            try:
                if package == 'tkinterdnd2':
                    import tkinterdnd2
                elif package == 'pillow':
                    import PIL
                else:
                    __import__(package.replace('-', '_'))
                self.success(f"{package} is available")
            except ImportError:
                self.log(f"Installing {package}...")
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                 check=True, capture_output=True)
                    self.success(f"{package} installed")
                except subprocess.CalledProcessError as e:
                    self.error(f"Failed to install {package}: {e}")
                    return False

        return True

    def prepare_build_environment(self):
        """Prepare the build environment"""
        self.log("Preparing build environment...")

        # Create temp directory
        self.temp_dir = Path(tempfile.mkdtemp())
        self.log(f"Using temp directory: {self.temp_dir}")

        # Clean previous builds
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(parents=True)

        return True

    def create_spec_file(self):
        """Create PyInstaller spec file"""
        self.log("Creating PyInstaller spec file...")

        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the root directory
root_dir = r"{str(self.root_dir).replace(chr(92), chr(92) + chr(92))}"

a = Analysis(
    [r"{str(self.root_dir / "axarion_engine_editor.py").replace(chr(92), chr(92) + chr(92))}"],
    pathex=[root_dir],
    binaries=[],
    datas=[
        # Include entire engine module
        (os.path.join(root_dir, "engine"), "engine"),
        # Include asset manager
        (os.path.join(root_dir, "asset_manager"), "asset_manager"),
        # Include utils
        (os.path.join(root_dir, "utils"), "utils"),
        # Include assets folder
        (os.path.join(root_dir, "assets"), "assets"),
        # Include Projects folder if it exists
        (os.path.join(root_dir, "Projects"), "Projects"),
        # Include logo and favicon
        (os.path.join(root_dir, "Logo.png"), "."),
        (os.path.join(root_dir, "favicon.png"), "."),
    ],
    hiddenimports=[
        'pygame',
        'numpy',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'tkinterdnd2',
        'requests',
        'json',
        'math',
        'random',
        'time',
        'sys',
        'os',
        'pathlib',
        'threading',
        'subprocess',
        'tkinter',
        'tkinter.ttk',
        'tkinter.font',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.scrolledtext',
        # Engine modules
        'engine.core',
        'engine.game_object',
        'engine.renderer',
        'engine.scene',
        'engine.physics',
        'engine.audio_system',
        'engine.input_system',
        'engine.camera',
        'engine.particle_system',
        'engine.animation_system',
        'engine.tilemap',
        'engine.state_machine',
        'engine.asset_manager',
        # Asset manager modules
        'asset_manager.asset_manager',
        'asset_manager.asset_store',
        'asset_manager.asset_utils',
        'asset_manager.local_assets',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='axarion_engine_editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r"{str(self.root_dir / "favicon.png").replace(chr(92), chr(92) + chr(92))}" if os.path.exists(r"{str(self.root_dir / "favicon.png").replace(chr(92), chr(92) + chr(92))}") else None,
)
"""

        spec_file = self.temp_dir / "axarion_engine_editor.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)

        self.success(f"Spec file created: {spec_file}")
        return spec_file

    def build_executable(self, spec_file):
        """Build the executable using PyInstaller"""
        self.log("Building executable with PyInstaller...")

        try:
            # Run PyInstaller
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                "--distpath", str(self.build_dir),
                "--workpath", str(self.temp_dir / "work"),
                str(spec_file)
            ]

            self.log(f"Running: {' '.join(cmd)}")

            result = subprocess.run(cmd, cwd=str(self.temp_dir), 
                                  capture_output=True, text=True)

            if result.returncode != 0:
                self.error("PyInstaller failed!")
                self.error(f"STDOUT: {result.stdout}")
                self.error(f"STDERR: {result.stderr}")
                return False

            self.success("PyInstaller build completed")
            return True

        except Exception as e:
            self.error(f"Build failed with exception: {e}")
            return False

    def post_build_cleanup(self):
        """Clean up after build"""
        self.log("Performing post-build cleanup...")

        # Remove temp directory
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

        # Check if executable was created
        exe_name = "axarion_engine_editor.exe" if sys.platform == "win32" else "axarion_engine_editor"
        exe_path = self.build_dir / exe_name

        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            self.success(f"Executable created: {exe_path}")
            self.success(f"Size: {size_mb:.1f} MB")
            return True
        else:
            self.error("Executable not found after build")
            return False

    def create_readme(self):
        """Create README for distribution"""
        readme_content = """# axarion_engine_editor - Standalone

This is a standalone build of Axarion Studio.

## Running
- Double-click AxarionStudio.exe (Windows) or AxarionStudio (Linux/Mac) to start
- No installation required - everything is embedded

## Features
- Complete game development environment
- Built-in Asset Manager
- Pygame-based game engine
- Project management and building tools

## System Requirements
- Windows 10+ / Linux / macOS
- 2GB RAM minimum
- OpenGL support for graphics

## Getting Started
1. Run the executable
2. Create a new project or open existing one
3. Use the Asset Manager to import sprites and sounds
4. Write your game code in the editor
5. Run and test your game
6. Build to distribute

Built with Axarion Engine v0.9.4
"""

        readme_path = self.build_dir / "README.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        self.success("README created")

    def build(self):
        """Main build process"""
        print("🚀 Starting Axarion Studio Build Process")
        print("="*50)

        # Step 1: Check dependencies
        if not self.check_dependencies():
            self.error("Dependency check failed")
            return False

        # Step 2: Prepare build environment
        if not self.prepare_build_environment():
            self.error("Failed to prepare build environment")
            return False

        # Step 3: Create spec file
        spec_file = self.create_spec_file()
        if not spec_file:
            self.error("Failed to create spec file")
            return False

        # Step 4: Build executable
        if not self.build_executable(spec_file):
            self.error("Failed to build executable")
            return False

        # Step 5: Post-build cleanup and verification
        if not self.post_build_cleanup():
            self.error("Post-build cleanup failed")
            return False

        # Step 6: Create documentation
        self.create_readme()

        print("="*50)
        self.success("🎉 Axarion Studio build completed successfully!")
        self.success(f"📁 Output directory: {self.build_dir}")

        return True

def main():
    """Main entry point"""
    builder = AxarionStudioBuilder()

    try:
        success = builder.build()
        if success:
            print("\n✨ Build completed! You can now distribute the executable.")
            sys.exit(0)
        else:
            print("\n💥 Build failed! Check the error messages above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()