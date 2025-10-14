"""
Individual camera frame widget and manager - FIXED VERSION
"""

import tkinter as tk
from tkinter import ttk
import logging

from config.settings import config, device_names


class CameraFrame:
    """Individual camera display frame"""
    
    def __init__(self, parent_gui, ip, name, parent_frame, row, col):
        self.parent_gui = parent_gui
        self.ip = ip
        self.name = name
        self.frame = None
        self.video_label = None
        self.heartbeat_label = None
        
        self.create_frame(parent_frame, row, col)

    def create_frame(self, parent_frame, row, col):
        """Create the camera frame widget"""
        # Main frame with visible border
        self.frame = ttk.Frame(parent_frame, style="Slave.TFrame")
        self.frame.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
        
        # Configure frame grid
        self.frame.grid_rowconfigure(1, weight=1)  # Video area gets most space
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Header with name and status
        self.create_header()
        
        # Video display
        self.create_video_display()
        
        # Controls
        self.create_controls()

    def create_header(self):
        """Create header with name and heartbeat"""
        header_frame = ttk.Frame(self.frame, style="Slave.TFrame")
        header_frame.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Get display name
        display_name = device_names.get(self.ip, self.name)
        name_text = f"{display_name} ({self.ip})"
        
        name_label = ttk.Label(header_frame, text=name_text, style="Dark.TLabel")
        name_label.grid(row=0, column=0, sticky="w")
        
        self.heartbeat_label = ttk.Label(header_frame, text="🔴", foreground="red", style="Dark.TLabel")
        self.heartbeat_label.grid(row=0, column=1, sticky="e")
        
        # Store in parent GUI for heartbeat updates
        self.parent_gui.heartbeat_labels[self.ip] = self.heartbeat_label

    def create_video_display(self):
        """Create video display area"""
        video_frame = ttk.Frame(self.frame, style="Slave.TFrame") 
        video_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        
        # Video canvas with dynamic sizing for 8 cameras
        self.video_label = tk.Label(video_frame, 
                                   bg="gray20", 
                                   text="Connecting...\nVideo Stream", 
                                   fg="white", 
                                   font=('Arial', 10))
        self.video_label.pack(fill="both", expand=True)
        
        # Store in parent GUI for video updates
        self.parent_gui.video_labels[self.ip] = self.video_label

    def create_controls(self):
        """Create control buttons - ONLY Capture and Options as specified"""
        controls_frame = ttk.Frame(self.frame, style="Slave.TFrame")
        controls_frame.grid(row=2, column=0, sticky="ew", padx=2, pady=2)
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Capture button
        capture_btn = ttk.Button(controls_frame, 
                               text="Capture", 
                               command=self.capture_still,
                               style="Dark.TButton")
        capture_btn.grid(row=0, column=0, sticky="ew", padx=1)
        
        # Options button  
        options_btn = ttk.Button(controls_frame, 
                               text="Options", 
                               command=self.open_options,
                               style="Dark.TButton")
        options_btn.grid(row=0, column=1, sticky="ew", padx=1)

    def capture_still(self):
        """Capture still image"""
        logging.info(f"Capturing still from {self.ip}")
        self.parent_gui.network_manager.send_command(self.ip, "CAPTURE_STILL")

    def open_options(self):
        """Open camera options"""
        self.parent_gui.settings_menu.open_camera_settings(self.ip)

    def update_video(self, image_tk):
        """Update video display"""
        if self.video_label:
            self.video_label.config(image=image_tk, text="")
            self.video_label.image = image_tk

    def update_heartbeat(self, status):
        """Update heartbeat status"""
        if self.heartbeat_label:
            color = "green" if status else "red"
            text = "🟢" if status else "🔴"
            self.heartbeat_label.config(text=text, foreground=color)


class CameraFrameManager:
    """Manages all camera frames"""
    
    def __init__(self, gui):
        self.gui = gui
        self.camera_frames = {}

    def setup_camera_grid(self, parent_frame):
        """Setup grid of camera frames"""
        logging.info("Setting up camera grid for 8 cameras (2x4)")
        
        # Configure grid weights for proper sizing
        for i in range(config.NUM_COLS):  # 4 columns
            parent_frame.grid_columnconfigure(i, weight=1)
        for i in range(config.NUM_ROWS):  # 2 rows
            parent_frame.grid_rowconfigure(i, weight=1)
        
        # Create camera frames for all 8 cameras
        for i, (name, slave_info) in enumerate(config.SLAVES.items()):
            row = i // config.NUM_COLS  # 0 or 1
            col = i % config.NUM_COLS   # 0, 1, 2, or 3
            ip = slave_info["ip"]
            
            logging.info(f"Creating camera frame {i+1}: {name} ({ip}) at position ({row}, {col})")
            
            camera_frame = CameraFrame(self.gui, ip, name, parent_frame, row, col)
            self.camera_frames[ip] = camera_frame
            # Also store by name in gui.slave_frames for keyboard shortcuts
            self.gui.slave_frames[name] = camera_frame.frame

    def start_all_streams(self):
        """Start all camera streams"""
        logging.info("Starting all camera streams")
        for ip in self.camera_frames.keys():
            self.gui.network_manager.send_command(ip, "START_STREAM")
            
    def get_camera_frame(self, ip):
        """Get camera frame by IP"""
        return self.camera_frames.get(ip)
