#!/usr/bin/env python3
"""
Axarion Engine - Main Entry Point
A 2D desktop game engine with custom editor and AXScript support
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add engine modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from editor.main_editor import AxarionEditor
from engine.core import AxarionEngine

def main():
    """Main entry point for Axarion Engine"""
    try:
        # Initialize the main Tkinter window
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        # Create and run the editor
        editor = AxarionEditor(root)
        editor.run()
        
    except Exception as e:
        messagebox.showerror("Axarion Engine Error", f"Failed to start engine: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("Starting Axarion Engine...")
    main()
