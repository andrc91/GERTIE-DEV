#!/usr/bin/env python3
"""
Launch script for the modular camera GUI
Integrates with existing camera system structure
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path for shared config access
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Add camera_gui to path
camera_gui_root = Path(__file__).parent
sys.path.insert(0, str(camera_gui_root))

def main():
    """Launch the modular camera GUI"""
    print("🚀 Launching Modular Camera GUI...")
    print(f"📁 Project root: {project_root}")
    print(f"📁 Camera GUI root: {camera_gui_root}")
    
    try:
        # Import and launch the main GUI
        from main import main as launch_gui
        launch_gui()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📝 Make sure all dependencies are installed:")
        print("   pip3 install pillow")
        print("   pip3 install opencv-python")
        
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        
        # Fall back to test structure
        print("🧪 Falling back to structure test...")
        try:
            from test_structure import main as test_main
            test_main()
        except Exception as test_e:
            print(f"❌ Test also failed: {test_e}")

if __name__ == "__main__":
    main()
