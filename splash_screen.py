
import tkinter as tk
from tkinter import ttk
import os
import threading
import time
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class SplashScreen:
    def __init__(self, on_complete_callback):
        self.on_complete_callback = on_complete_callback
        self.splash = tk.Toplevel()
        self.splash.title("")
        self.splash.geometry("600x350")
        self.splash.configure(bg='#0C0F2E')
        self.splash.resizable(False, False)
        self.splash.overrideredirect(True)  # Remove window decorations
        
        # Center the splash screen
        self.splash.update_idletasks()
        x = (self.splash.winfo_screenwidth() // 2) - (self.splash.winfo_width() // 2)
        y = (self.splash.winfo_screenheight() // 2) - (self.splash.winfo_height() // 2)
        self.splash.geometry(f'+{x}+{y}')
        
        # Create main frame
        main_frame = tk.Frame(self.splash, bg='#0C0F2E')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo container (centered)
        logo_frame = tk.Frame(main_frame, bg='#0C0F2E')
        logo_frame.pack(expand=True, fill=tk.BOTH)
        
        # Load and display logo (much larger)
        self.load_logo(logo_frame)
        
        # Loading text at bottom
        loading_frame = tk.Frame(main_frame, bg='#0C0F2E', height=120)
        loading_frame.pack(side=tk.BOTTOM, fill=tk.X)
        loading_frame.pack_propagate(False)
        
        # Loading Editor text
        self.editor_label = tk.Label(
            loading_frame,
            text="Loading Editor",
            bg='#0C0F2E',
            fg='white',
            font=('Segoe UI', 12)
        )
        self.editor_label.pack(pady=(10, 5))
        
        # Engine version
        self.version_label = tk.Label(
            loading_frame,
            text="Axarion Engine v1.0.1",
            bg='#0C0F2E',
            fg='#888888',
            font=('Segoe UI', 10)
        )
        self.version_label.pack(pady=(0, 5))
        
        # Loading label
        self.loading_label = tk.Label(
            loading_frame,
            text="Loading...",
            bg='#0C0F2E',
            fg='white',
            font=('Segoe UI', 11)
        )
        self.loading_label.pack(pady=(0, 15))
        
        # Start loading sequence
        self.start_loading_sequence()
    
    def load_logo(self, parent):
        """Load and display the logo at a much larger size"""
        try:
            logo_paths = [
                "Logo.png",
                "assets/Logo.png",
                os.path.join(os.path.dirname(__file__), "Logo.png"),
                os.path.join(os.path.dirname(__file__), "assets", "Logo.png")
            ]
            
            logo_found = False
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    if PIL_AVAILABLE:
                        # Use PIL for better scaling
                        logo_pil = Image.open(logo_path)
                        # Adjust for smaller window - 400px wide max
                        logo_pil.thumbnail((400, 200), Image.Resampling.LANCZOS)
                        logo_image = ImageTk.PhotoImage(logo_pil)
                        logo_label = tk.Label(parent, image=logo_image, bg='#0C0F2E')
                        logo_label.image = logo_image  # Keep reference
                        logo_label.pack(expand=True)
                        logo_found = True
                        break
                    else:
                        # Use tkinter PhotoImage
                        logo_image = tk.PhotoImage(file=logo_path)
                        # Scale appropriately for smaller window
                        if logo_image.width() < 300:
                            # Zoom moderately for smaller window
                            logo_image = logo_image.zoom(1, 1)
                        logo_label = tk.Label(parent, image=logo_image, bg='#0C0F2E')
                        logo_label.image = logo_image  # Keep reference
                        logo_label.pack(expand=True)
                        logo_found = True
                        break
            
            if not logo_found:
                # Fallback text
                fallback_label = tk.Label(
                    parent,
                    text="AXARION\nENGINE",
                    bg='#0C0F2E',
                    fg='white',
                    font=('Segoe UI', 48, 'bold'),
                    justify=tk.CENTER
                )
                fallback_label.pack(expand=True)
                
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Fallback text
            fallback_label = tk.Label(
                parent,
                text="AXARION\nENGINE",
                bg='#0C0F2E',
                fg='white',
                font=('Segoe UI', 48, 'bold'),
                justify=tk.CENTER
            )
            fallback_label.pack(expand=True)
    
    def start_loading_sequence(self):
        """Start the loading sequence with different stages"""
        def loading_thread():
            stages = [
                ("Initializing Engine", 0.8),
                ("Loading Assets", 0.6),
                ("Setting up Editor", 0.5),
                ("Preparing Workspace", 0.4),
                ("Loading Complete", 0.3)
            ]
            
            for stage_text, delay in stages:
                # Update loading text
                self.splash.after(0, lambda text=stage_text: self.loading_label.config(text=text))
                
                # Just wait for the delay without animating dots
                time.sleep(delay)
            
            # Close splash and open main editor
            self.splash.after(0, self.close_splash)
        
        # Start loading in separate thread
        loading_thread_obj = threading.Thread(target=loading_thread, daemon=True)
        loading_thread_obj.start()
    
    def close_splash(self):
        """Close splash screen and call completion callback"""
        self.splash.destroy()
        if self.on_complete_callback:
            self.on_complete_callback()
