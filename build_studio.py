
#!/usr/bin/env python3
"""
Interactive Build System for Axarion Studio
"""

import os
import sys
import subprocess
import platform
import time

def clear_screen():
    """Clear console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print ASCII art header"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║      █████╗ ██╗  ██╗ █████╗ ██████╗ ██╗ ██████╗ ███╗   ██╗                ║
║     ██╔══██╗╚██╗██╔╝██╔══██╗██╔══██╗██║██╔═══██╗████╗  ██║                ║
║     ███████║ ╚███╔╝ ███████║██████╔╝██║██║   ██║██╔██╗ ██║                ║
║     ██╔══██║ ██╔██╗ ██╔══██║██╔══██╗██║██║   ██║██║╚██╗██║                ║
║     ██║  ██║██╔╝ ██╗██║  ██║██║  ██║██║╚██████╔╝██║ ╚████║                ║
║     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝                ║
║                                                                              ║
║                      🚀 AUTOMATED BUILD SYSTEM 🚀                            ║
║                                                                              ║
║          Building complete Axarion Engine into executable application        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

def print_separator():
    """Print section separator"""
    print("=" * 80)

def print_box(title, content, width=80):
    """Print content in a box"""
    print("┌" + "─" * (width - 2) + "┐")
    print(f"│ {title:<{width - 4}} │")
    print("├" + "─" * (width - 2) + "┤")
    for line in content:
        print(f"│ {line:<{width - 4}} │")
    print("└" + "─" * (width - 2) + "┘")

def get_user_choice(prompt, options):
    """Get user choice with validation"""
    while True:
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"  [{i}] {option}")
        
        try:
            choice = int(input("\nEnter your choice (number): "))
            if 1 <= choice <= len(options):
                return choice - 1
            else:
                print(f"❌ Invalid choice. Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")

def get_yes_no(prompt):
    """Get yes/no input"""
    while True:
        answer = input(f"{prompt} (y/n): ").lower().strip()
        if answer in ['y', 'yes']:
            return True
        elif answer in ['n', 'no']:
            return False
        else:
            print("❌ Please enter 'y' for yes or 'n' for no")

def check_dependencies():
    """Check build dependencies"""
    print_box("🔍 DEPENDENCY CHECK", ["Checking required build tools..."])
    
    dependencies = {
        'python': {'cmd': [sys.executable, '--version'], 'name': 'Python'},
        'pyinstaller': {'cmd': [sys.executable, '-m', 'PyInstaller', '--version'], 'name': 'PyInstaller'}
    }
    
    missing = []
    
    for dep, info in dependencies.items():
        try:
            result = subprocess.run(info['cmd'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1] if result.stdout else "Unknown"
                print(f"✅ {info['name']}: {version}")
            else:
                print(f"❌ {info['name']}: Not found")
                missing.append(dep)
        except FileNotFoundError:
            print(f"❌ {info['name']}: Not found")
            missing.append(dep)
    
    if missing:
        if 'pyinstaller' in missing:
            print("\n🔧 Installing PyInstaller...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
                print("✅ PyInstaller installed successfully!")
            except subprocess.CalledProcessError:
                print("❌ Failed to install PyInstaller")
                return False
    
    return True

def show_build_options():
    """Show current build configuration"""
    current_platform = platform.system()
    print_box("📋 BUILD CONFIGURATION", [
        f"Current Platform: {current_platform}",
        f"Python Version: {sys.version.split()[0]}",
        f"Architecture: {platform.machine()}",
        "",
        "Available build targets:",
        "• Windows (exe)",
        "• Linux (binary)",
        "• macOS (app)",
        "• Cross-platform (all)"
    ])

def build_for_platform(target_platform, show_console, output_name="AxarionStudio"):
    """Build for specific platform"""
    print_separator()
    print(f"🏗️  BUILDING FOR {target_platform.upper()}")
    print_separator()
    
    # Base PyInstaller arguments
    args = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--name", output_name,
    ]
    
    # Platform-specific configurations
    if target_platform == "windows":
        args.extend(["--onefile"])
        if not show_console:
            args.append("--windowed")
        separator = ";"
    elif target_platform == "linux":
        args.extend(["--onefile"])
        separator = ":"
    elif target_platform == "macos":
        args.extend(["--onefile", "--windowed"])
        separator = ":"
    else:
        args.extend(["--onefile"])
        separator = ";" if os.name == 'nt' else ":"
    
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
        "tkinter", "tkinter.ttk", "tkinter.filedialog", "tkinter.messagebox",
        "tkinter.scrolledtext", "tkinter.simpledialog",
        "pygame", "json", "threading", "subprocess", "pathlib", "typing", "PIL",
        "os", "sys", "platform", "time", "re"
    ]
    
    for imp in hidden_imports:
        args.extend(["--hidden-import", imp])
    
    # Main script
    args.append("axarion_studio.py")
    
    print("📋 Build command:")
    print(" ".join(args))
    print()
    
    # Execute build
    print("🚀 Starting build process...")
    start_time = time.time()
    
    try:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Show progress
        for line in process.stdout:
            if "INFO:" in line:
                print(f"📦 {line.strip()}")
            elif "WARNING:" in line:
                print(f"⚠️  {line.strip()}")
            elif "ERROR:" in line:
                print(f"❌ {line.strip()}")
        
        process.wait()
        
        if process.returncode == 0:
            build_time = time.time() - start_time
            print(f"\n✅ Build completed successfully in {build_time:.1f} seconds!")
            
            # Show output location
            exe_name = f"{output_name}.exe" if target_platform == "windows" else output_name
            exe_path = os.path.join("dist", exe_name)
            
            if os.path.exists(exe_path):
                file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
                print(f"📦 Executable: {os.path.abspath(exe_path)}")
                print(f"📏 Size: {file_size:.1f} MB")
                return True
            else:
                print(f"⚠️  Build completed but executable not found at expected location")
                return False
        else:
            print(f"❌ Build failed with return code: {process.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def main():
    """Main interactive build process"""
    clear_screen()
    print_header()
    
    # Welcome message
    print("Welcome to the Axarion Studio Automated Build System!")
    print("This tool will compile the complete Axarion Engine and Studio into executable applications.")
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Missing dependencies. Please install them and try again.")
        return
    
    print("\n" + "="*80)
    input("Press Enter to continue...")
    clear_screen()
    
    # Show build options
    show_build_options()
    
    # Platform selection
    platforms = [
        "Windows (exe)",
        "Linux (binary)", 
        "macOS (app)",
        "All platforms (cross-compile)"
    ]
    
    platform_choice = get_user_choice("🎯 Select target platform:", platforms)
    platform_map = ["windows", "linux", "macos", "all"]
    selected_platform = platform_map[platform_choice]
    
    # Console option
    show_console = get_yes_no("💻 Show console window in final application?")
    
    # Custom name option
    custom_name = get_yes_no("📝 Use custom application name?")
    app_name = "AxarionStudio"
    if custom_name:
        app_name = input("Enter application name (default: AxarionStudio): ").strip()
        if not app_name:
            app_name = "AxarionStudio"
    
    # Confirmation
    clear_screen()
    print_box("🔍 BUILD SUMMARY", [
        f"Platform: {platforms[platform_choice]}",
        f"Console: {'Yes' if show_console else 'No'}",
        f"App Name: {app_name}",
        "",
        "This will create a complete executable package including:",
        "• Axarion Studio IDE",
        "• Complete Axarion Engine",
        "• All assets and documentation",
        "• Build system and templates"
    ])
    
    if not get_yes_no("🚀 Proceed with build?"):
        print("Build cancelled.")
        return
    
    # Build process
    clear_screen()
    print("🏗️  STARTING BUILD PROCESS")
    print("="*80)
    
    success_count = 0
    total_builds = 0
    
    if selected_platform == "all":
        # Build for all platforms
        for platform_name in ["windows", "linux", "macos"]:
            print(f"\n🔄 Building for {platform_name}...")
            total_builds += 1
            if build_for_platform(platform_name, show_console, f"{app_name}_{platform_name}"):
                success_count += 1
            print("="*80)
    else:
        # Build for single platform
        total_builds = 1
        if build_for_platform(selected_platform, show_console, app_name):
            success_count += 1
    
    # Final summary
    print("\n" + "="*80)
    print("🎉 BUILD PROCESS COMPLETE!")
    print("="*80)
    
    if success_count == total_builds:
        print(f"✅ All {total_builds} build(s) completed successfully!")
    else:
        print(f"⚠️  {success_count}/{total_builds} build(s) completed successfully")
    
    print("\n📁 Output files are located in the 'dist' directory")
    print("🎮 You can now distribute your Axarion Studio executable!")
    
    # Open dist folder option
    if get_yes_no("📂 Open output folder?"):
        dist_path = os.path.abspath("dist")
        try:
            if sys.platform == "win32":
                os.startfile(dist_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", dist_path])
            else:
                subprocess.run(["xdg-open", dist_path])
        except Exception as e:
            print(f"❌ Could not open folder: {e}")
            print(f"📁 Manual path: {dist_path}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Build process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
