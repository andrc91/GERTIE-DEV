"""
Main GUI class - modular and clean - FIXED VERSION
"""

import tkinter as tk
from tkinter import ttk
import logging
import threading
import time

from config.settings import config
from widgets.gallery_panel import GalleryPanel
from widgets.camera_frame import CameraFrameManager
from menu.settings_menu import SettingsMenuManager
from menu.system_menu import SystemMenuManager
from core.network_manager import NetworkManager


class MasterVideoGUI:
    """Main GUI application class"""
    
    def __init__(self, root):
        self.root = root
        self.slave_frames = {}
        self.video_labels = {}
        self.heartbeat_labels = {}
        self.gallery_thumbs = []
        
        self.setup_window()
        self.setup_styles()
        
        # Initialize managers
        self.network_manager = NetworkManager(self)
        self.camera_manager = CameraFrameManager(self)
        self.gallery_panel = None
        self.settings_menu = SettingsMenuManager(self)
        self.system_menu = SystemMenuManager(self)
        
        # Setup UI
        self.setup_menu_bar()
        self.setup_layout()
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Start network services
        self.start_services()
        
        # Auto-start streams if enabled (DISABLED by default now)
        if config.FEATURE_FLAGS['AUTO_START_STREAMS']:
            self.root.after(1000, self.camera_manager.start_all_streams)

    def setup_window(self):
        """Configure main window"""
        self.root.title("Multi-Camera Master Control - Modular")
        self.root.configure(bg="black")
        self.root.geometry(config.WINDOW_SIZE)
        self.root.resizable(True, True)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0)  # Gallery (fixed width)
        self.root.grid_columnconfigure(1, weight=1)  # Main content

    def setup_styles(self):
        """Configure TTK styles for better visibility"""
        style = ttk.Style()
        style.theme_use('default')
        
        # Configure styles for performance and visibility
        style.configure("TFrame", background="black")
        style.configure("TLabel", background="black", foreground="white", font=('Arial', 9))
        style.configure("TButton", background="gray20", foreground="white", font=('Arial', 8))
        style.map("TButton", 
                 background=[('active', 'gray30'), ('pressed', 'gray40')])
        
        style.configure("Main.TFrame", background="black")
        style.configure("Gallery.TFrame", background="black") 
        style.configure("Slave.TFrame", background="gray10", relief="solid", borderwidth=1)
        
        style.configure("Dark.TLabel", background="gray20", foreground="white", font=('Arial', 9))
        style.configure("Dark.TButton", background="gray30", foreground="white", font=('Arial', 8))
        style.map("Dark.TButton",
                 background=[('active', 'gray40'), ('pressed', 'gray50')])

    def setup_menu_bar(self):
        """Setup menu bar"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Add menus through managers
        self.settings_menu.create_menu(self.menubar)
        self.system_menu.create_menu(self.menubar)

    def setup_layout(self):
        """Setup main layout"""
        # Left gallery panel
        if config.FEATURE_FLAGS['GALLERY_LEFT_PANEL']:
            self.gallery_panel = GalleryPanel(self.root)
            self.gallery_panel.pack_left()
        
        # Main camera area
        self.main_frame = ttk.Frame(self.root, style="Main.TFrame")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=(2, 5), pady=5)
        
        # Configure main frame grid for 8 cameras (2 rows x 4 columns)
        for i in range(4):
            self.main_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            self.main_frame.grid_rowconfigure(i, weight=1)
        
        # Setup camera grid
        self.camera_manager.setup_camera_grid(self.main_frame)
        
        # Add control buttons frame
        self.setup_control_buttons()

    def setup_control_buttons(self):
        """Setup global control buttons"""
        control_frame = ttk.Frame(self.main_frame, style="TFrame")
        control_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_rowconfigure(0, weight=1)
        control_frame.grid_rowconfigure(1, weight=1)
        control_frame.grid_rowconfigure(2, weight=1)  # Add row for shortcuts
        
        self.capture_all_button = ttk.Button(control_frame, text="Capture All Cameras [Space]", 
                                           command=self.capture_all_stills, style="Dark.TButton")
        self.capture_all_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.sync_time_button = ttk.Button(control_frame, text="Sync Time All Devices", 
                                         command=self.sync_time_all_devices, style="Dark.TButton")
        self.sync_time_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Add manual start streams button to replace auto-start
        self.start_streams_button = ttk.Button(control_frame, text="Start All Video Streams", 
                                             command=self.start_all_video_streams, style="Dark.TButton")
        self.start_streams_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.stop_streams_button = ttk.Button(control_frame, text="Stop All Video Streams", 
                                            command=self.stop_all_video_streams, style="Dark.TButton")
        self.stop_streams_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Add keyboard shortcuts help text
        shortcuts_text = "Shortcuts: [Space] Capture All | [1-8] Toggle Camera | [S] Settings | [G] Gallery | [R] Restart | [Ctrl+Q] Quit"
        shortcuts_label = ttk.Label(control_frame, text=shortcuts_text, style="TLabel", font=('Arial', 9))
        shortcuts_label.grid(row=2, column=0, columnspan=2, padx=5, pady=2, sticky="ew")

    def start_services(self):
        """Start background services"""
        self.network_manager.start_all_services()

    # auto_start_all_streams method removed - replaced with manual start/stop buttons

    def capture_all_stills(self):
        """Capture stills from all cameras"""
        logging.info("Capturing stills from all cameras")
        for ip in self.get_camera_ips():
            self.network_manager.send_command(ip, "CAPTURE_STILL")
            time.sleep(0.1)  # Brief delay between captures

    def sync_time_all_devices(self):
        """Sync time on all devices"""
        from tkinter import messagebox
        from datetime import datetime
        
        if messagebox.askyesno("Sync Time", "Synchronize current time to all devices?"):
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            success_count = 0
            for ip in self.get_camera_ips():
                try:
                    self.network_manager.send_command(ip, f"SET_TIME_{current_time}")
                    success_count += 1
                    time.sleep(0.1)
                except Exception as e:
                    logging.error(f"Error syncing time to {ip}: {e}")
            
            messagebox.showinfo("Time Sync", f"Time synchronization sent to {success_count}/{len(self.get_camera_ips())} devices.")

    def start_all_video_streams(self):
        """Manually start all video streams - user controlled"""
        logging.info("User-triggered: Starting all video streams...")
        self.camera_manager.start_all_streams()

    def stop_all_video_streams(self):
        """Stop all video streams"""
        logging.info("User-triggered: Stopping all video streams...")
        for ip in self.get_camera_ips():
            self.network_manager.send_command(ip, "STOP_STREAM")

    def get_camera_ips(self):
        """Get list of all camera IPs"""
        return [slave["ip"] for slave in config.SLAVES.values()]

    def find_slave_name(self, ip):
        """Find slave name for IP"""
        for name, details in config.SLAVES.items():
            if details["ip"] == ip:
                return name
        return ip
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for efficient workflow"""
        # Space bar - Capture all cameras
        self.root.bind('<space>', lambda e: self.capture_all_stills())
        
        # Number keys 1-8 - Toggle individual camera preview
        for i in range(1, 9):
            camera_name = f'rep{i}'
            if camera_name in config.SLAVES:
                self.root.bind(str(i), lambda e, name=camera_name: self.toggle_camera_preview(name))
        
        # S key - Open settings menu  
        self.root.bind('<s>', lambda e: self.open_camera_settings_for_all())
        self.root.bind('<S>', lambda e: self.open_camera_settings_for_all())
        
        # G key - Open gallery
        self.root.bind('<g>', lambda e: self.open_gallery())
        self.root.bind('<G>', lambda e: self.open_gallery())
        
        # R key - Restart all streams
        self.root.bind('<r>', lambda e: self.restart_all_streams())
        self.root.bind('<R>', lambda e: self.restart_all_streams())
        
        # Escape key - Close dialogs (handled by individual dialogs)
        # Ctrl+Q - Quit application
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        
        logging.info("Keyboard shortcuts initialized")
    
    def toggle_camera_preview(self, camera_name):
        """Toggle individual camera preview visibility"""
        if camera_name in self.slave_frames:
            frame = self.slave_frames[camera_name]
            if frame.winfo_viewable():
                frame.grid_remove()
                logging.info(f"Hiding camera preview: {camera_name}")
            else:
                # Find the appropriate position
                idx = list(config.SLAVES.keys()).index(camera_name)
                row = idx // 4
                col = idx % 4
                frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                logging.info(f"Showing camera preview: {camera_name}")
    
    def open_gallery(self):
        """Open the gallery panel"""
        if self.gallery_panel and self.gallery_panel.panel:
            # Toggle visibility of gallery panel
            if self.gallery_panel.panel.winfo_viewable():
                self.gallery_panel.panel.grid_remove()
                logging.info("Hiding gallery panel")
            else:
                self.gallery_panel.panel.grid(row=0, column=0, sticky="ns")
                logging.info("Showing gallery panel")
    
    def restart_all_streams(self):
        """Restart all video streams"""
        logging.info("Restarting all video streams via keyboard shortcut")
        self.stop_all_video_streams()
        time.sleep(1)
        self.start_all_video_streams()
    
    def open_camera_settings_for_all(self):
        """Open global camera settings dialog"""
        logging.info("Opening camera settings via keyboard shortcut")
        # Use the first camera's IP for global settings
        first_ip = list(config.SLAVES.values())[0]["ip"]
        if hasattr(self, 'settings_menu') and hasattr(self.settings_menu, 'open_camera_settings'):
            self.settings_menu.open_camera_settings(first_ip)
        else:
            logging.warning("Settings menu not properly initialized")
