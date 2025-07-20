import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

class AssetStorePanel:
    """Simplified Asset Store panel that just opens external browser"""

    def __init__(self, parent):
        self.parent = parent
        self.store_url = "https://axarion.onrender.com/assets.html"
        self.create_ui()

    def create_ui(self):
        """Create simple UI with external link"""
        # Main container
        main_frame = tk.Frame(self.parent, bg='#0C0F2E')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Center content
        content_frame = tk.Frame(main_frame, bg='#0C0F2E')
        content_frame.pack(expand=True)

        # Asset Store info
        title_label = tk.Label(content_frame,
                              text="🌐 Axarion Asset Store",
                              font=('Segoe UI', 18, 'bold'),
                              bg='#0C0F2E', fg='white')
        title_label.pack(pady=(50, 20))

        info_label = tk.Label(content_frame,
                             text="Browse thousands of free assets for your games",
                             font=('Segoe UI', 12),
                             bg='#0C0F2E', fg='#cccccc')
        info_label.pack(pady=10)

        # Open button
        open_btn = tk.Button(content_frame,
                            text="🚀 Open Asset Store",
                            command=self.open_store,
                            bg='#9333EA', fg='white',
                            font=('Segoe UI', 14, 'bold'),
                            relief='flat', padx=30, pady=15,
                            cursor='hand2')
        open_btn.pack(pady=30)

        # Features list
        features_text = """Available Assets:
• 2D Sprites and Characters
• Background Images and Tiles
• Sound Effects and Music
• Fonts and Typography
• Game Templates
• UI Elements"""

        features_label = tk.Label(content_frame,
                                 text=features_text,
                                 font=('Segoe UI', 11),
                                 bg='#0C0F2E', fg='#999999',
                                 justify=tk.LEFT)
        features_label.pack(pady=20)

    def open_store(self):
        """Open Asset Store in external browser"""
        try:
            webbrowser.open(self.store_url)
            messagebox.showinfo("Asset Store", 
                              f"Asset Store opened in external browser.\n\nURL: {self.store_url}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open Asset Store: {e}")

    def cleanup(self):
        """Clean up resources - nothing to clean"""
        pass