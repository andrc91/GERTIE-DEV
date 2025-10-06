#!/usr/bin/env python3
"""
Multi-Camera Master Control - Modular Version
Entry point for the application
"""

import sys
import os
import tkinter as tk
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.gui_base import MasterVideoGUI
from config.settings import load_all_settings
import logging

def main():
    """Main entry point"""
    logging.basicConfig(level=logging.INFO, 
                       format='[%(asctime)s] %(levelname)s: %(message)s')
    
    # Load all configuration
    load_all_settings()
    
    # Launch GUI
    root = tk.Tk()
    app = MasterVideoGUI(root)
    
    try:
        root.mainloop()
    except Exception as e:
        logging.error(f"GUI error: {e}")

if __name__ == "__main__":
    main()
