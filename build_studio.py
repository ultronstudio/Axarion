
#!/usr/bin/env python3
"""
Cross-platform build script for Axarion Studio
"""

import os
import sys
import subprocess
import platform

def build_axarion_studio():
    """Build Axarion Studio for current platform"""
    
    print(f"🏗️ Building Axarion Studio for {platform.system()}...")
    
    # Base PyInstaller arguments
    args = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--onefile", 
        "--windowed",
        "--name", "AxarionStudio",
    ]
    
    # Platform-specific data separator
    separator = ";" if platform.system() == "Windows" else ":"
    
    # Add data directories
    data_dirs = [
        ("engine", "engine"),
        ("utils", "utils"),
        ("assets", "assets"),
        ("DOCS", "DOCS")
    ]
    
    for src, dst in data_dirs:
        if os.path.exists(src):
            args.extend(["--add-data", f"{src}{separator}{dst}"])
    
    # Hidden imports
    hidden_imports = [
        "tkinter", "pygame", "json", "threading", 
        "subprocess", "pathlib", "typing", "PIL"
    ]
    
    for imp in hidden_imports:
        args.extend(["--hidden-import", imp])
    
    # Main script
    args.append("axarion_studio.py")
    
    print(f"📋 Running: {' '.join(args)}")
    
    try:
        result = subprocess.run(args, check=True)
        print("✅ Build completed successfully!")
        
        # Show output location
        exe_name = "AxarionStudio.exe" if platform.system() == "Windows" else "AxarionStudio"
        exe_path = os.path.join("dist", exe_name)
        
        if os.path.exists(exe_path):
            print(f"📦 Executable: {os.path.abspath(exe_path)}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    build_axarion_studio()
