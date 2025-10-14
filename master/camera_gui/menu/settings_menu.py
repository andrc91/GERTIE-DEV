"""
Settings menu manager
"""

import tkinter as tk
from tkinter import messagebox
import json
import os


class SettingsMenuManager:
    """Manages the settings menu"""

    def __init__(self, gui):
        self.gui = gui

    def create_menu(self, menubar):
        """Create settings menu"""
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        # Camera Controls submenu
        camera_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Camera Controls", menu=camera_menu)

        # Individual camera controls
        from config.settings import config, device_names
        for name, slave_info in config.SLAVES.items():
            ip = slave_info["ip"]
            device_name = device_names.get(ip, name)
            camera_menu.add_command(
                label=f"{device_name} Camera Settings...",
                command=lambda ip=ip: self.open_camera_settings(ip),
            )

        camera_menu.add_separator()
        camera_menu.add_command(
            label="Global Hardware Settings...",
            command=self.open_global_hardware_settings,
        )
        camera_menu.add_command(
            label="Global Image Adjustments...",
            command=self.open_global_image_adjustments,
        )

        # Device management
        settings_menu.add_separator()
        settings_menu.add_command(
            label="Application Preferences...", command=self.open_app_preferences
        )
        settings_menu.add_command(
            label="Device Names...", command=self.open_device_naming
        )
        settings_menu.add_command(
            label="Reset All Cameras", command=self.reset_all_cameras
        )
        settings_menu.add_command(
            label="Sync Time All Devices", command=self.sync_time_all
        )

    def open_camera_settings(self, ip):
        """Open camera settings dialog"""
        CameraSettingsDialog(self.gui, ip)

    def open_global_hardware_settings(self):
        """Open global hardware settings"""
        messagebox.showinfo("Global Hardware", "Global hardware settings dialog")

    def open_global_image_adjustments(self):
        """Open global image adjustments"""
        messagebox.showinfo("Global Image", "Global image adjustments dialog")

    def open_device_naming(self):
        """Open device naming dialog"""
        from dialogs.device_naming import DeviceNamingDialog

        DeviceNamingDialog(self.gui)
    
    def open_app_preferences(self):
        """Open application preferences dialog"""
        AppPreferencesDialog(self.gui)

    def reset_all_cameras(self):
        """Reset all cameras to defaults"""
        if messagebox.askyesno("Reset All", "Reset all cameras to defaults?"):
            for ip in self.gui.get_camera_ips():
                self.gui.network_manager.send_command(ip, "RESET_CAMERA_DEFAULTS")
            messagebox.showinfo("Reset Complete", "All cameras reset to defaults")

    def sync_time_all(self):
        """Sync time to all devices"""
        if messagebox.askyesno("Sync Time", "Sync time to all devices?"):
            from datetime import datetime

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for ip in self.gui.get_camera_ips():
                self.gui.network_manager.send_command(ip, f"SET_TIME_{current_time}")
            messagebox.showinfo("Time Sync", "Time sync commands sent to all devices")


class CameraSettingsDialog:
    """Camera settings dialog"""

    def __init__(self, gui, ip):
        self.gui = gui
        self.ip = ip

        self.window = tk.Toplevel(gui.root)
        self.window.title(f"Camera Settings - {ip}")
        self.window.geometry("500x400")
        self.window.configure(bg="black")
        self.window.transient(gui.root)
        self.window.grab_set()

        # Load saved settings before creating interface
        self.settings = self.load_camera_settings()

        self.create_interface()

    def get_settings_filename(self):
        """Get settings filename for this camera"""
        safe_ip = self.ip.replace(".", "_").replace(":", "_")
        return f"camera_settings_{safe_ip}.json"

    def load_camera_settings(self):
        """Load persisted settings for this camera"""
        settings_file = self.get_settings_filename()
        try:
            if os.path.exists(settings_file):
                with open(settings_file, "r") as f:
                    settings = json.load(f)
                return settings
            else:
                # Defaults
                return {
                    "iso": 400,
                    "brightness": 0,
                    "flip_horizontal": False,
                    "flip_vertical": False,
                    "grayscale": False,
                    "rotation": 0,
                    "crop_enabled": False,
                    "crop_x": 0,
                    "crop_y": 0,
                    "crop_width": 100,
                    "crop_height": 100,
                }
        except Exception as e:
            print(f"Error loading settings for {self.ip}: {e}")
            return {
                "iso": 400,
                "brightness": 0,
                "flip_horizontal": False,
                "flip_vertical": False,
                "grayscale": False,
                "rotation": 0,
                "crop_enabled": False,
                "crop_x": 0,
                "crop_y": 0,
                "crop_width": 100,
                "crop_height": 100,
            }

    def save_camera_settings(self):
        """Save current settings to file"""
        settings_file = self.get_settings_filename()
        current_settings = {
            "iso": self.iso_var.get(),
            "brightness": self.brightness_var.get(),
            "flip_horizontal": self.flip_h_var.get(),
            "flip_vertical": self.flip_v_var.get(),
            "grayscale": self.grayscale_var.get(),
            "rotation": int(self.rotation_var.get()),
            "crop_enabled": self.crop_enabled_var.get(),
            "crop_x": self.crop_x_var.get(),
            "crop_y": self.crop_y_var.get(),
            "crop_width": self.crop_width_var.get(),
            "crop_height": self.crop_height_var.get(),
        }
        try:
            with open(settings_file, "w") as f:
                json.dump(current_settings, f, indent=2)
            print(f"Settings saved for {self.ip}")
        except Exception as e:
            print(f"Error saving settings for {self.ip}: {e}")

        self.create_interface()

    def create_interface(self):
        """Create settings interface with scroll support"""
        canvas = tk.Canvas(self.window, bg="black", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="black")

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        main_frame = tk.Frame(scrollable_frame, bg="black")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(
            main_frame,
            text=f"Camera Settings - {self.ip}",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="black",
        ).pack(pady=10)

        # Basic settings frame
        settings_frame = tk.Frame(main_frame, bg="gray20")
        settings_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # ISO
        iso_frame = tk.LabelFrame(settings_frame, text="ISO", fg="white", bg="gray20")
        iso_frame.pack(fill="x", padx=5, pady=5)

        self.iso_var = tk.IntVar(value=self.settings["iso"])
        tk.Scale(
            iso_frame,
            from_=100,
            to=1600,
            orient="horizontal",
            variable=self.iso_var,
            bg="gray20",
            fg="white",
        ).pack(fill="x", padx=5, pady=5)

        # Brightness
        brightness_frame = tk.LabelFrame(
            settings_frame, text="Brightness", fg="white", bg="gray20"
        )
        brightness_frame.pack(fill="x", padx=5, pady=5)

        self.brightness_var = tk.IntVar(value=self.settings["brightness"])
        tk.Scale(
            brightness_frame,
            from_=-50,
            to=50,
            orient="horizontal",
            variable=self.brightness_var,
            bg="gray20",
            fg="white",
        ).pack(fill="x", padx=5, pady=5)

        # Transform
        transform_frame = tk.LabelFrame(
            settings_frame, text="Transform", fg="white", bg="gray20"
        )
        transform_frame.pack(fill="x", padx=5, pady=5)

        self.flip_h_var = tk.BooleanVar(value=self.settings["flip_horizontal"])
        self.flip_v_var = tk.BooleanVar(value=self.settings["flip_vertical"])
        self.grayscale_var = tk.BooleanVar(value=self.settings["grayscale"])

        tk.Checkbutton(
            transform_frame,
            text="Flip Horizontal",
            variable=self.flip_h_var,
            fg="white",
            bg="gray20",
            selectcolor="gray30",
            activebackground="gray20",
            activeforeground="white",
        ).pack(anchor="w")
        tk.Checkbutton(
            transform_frame,
            text="Flip Vertical",
            variable=self.flip_v_var,
            fg="white",
            bg="gray20",
            selectcolor="gray30",
            activebackground="gray20",
            activeforeground="white",
        ).pack(anchor="w")
        tk.Checkbutton(
            transform_frame,
            text="Grayscale",
            variable=self.grayscale_var,
            fg="white",
            bg="gray20",
            selectcolor="gray30",
            activebackground="gray20",
            activeforeground="white",
        ).pack(anchor="w")

        # Rotation
        rotation_frame = tk.Frame(transform_frame, bg="gray20")
        rotation_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(rotation_frame, text="Rotation:", fg="white", bg="gray20").pack(
            side="left"
        )
        self.rotation_var = tk.StringVar(value=str(self.settings["rotation"]))
        rotation_options = ["0", "90", "180", "270"]
        rotation_menu = tk.OptionMenu(rotation_frame, self.rotation_var, *rotation_options)
        rotation_menu.config(bg="gray30", fg="white")
        rotation_menu.pack(side="left", padx=5)

        # Crop
        crop_frame = tk.LabelFrame(
            settings_frame, text="Crop (Advanced)", fg="white", bg="gray20"
        )
        crop_frame.pack(fill="x", padx=5, pady=5)

        self.crop_enabled_var = tk.BooleanVar(value=self.settings["crop_enabled"])
        tk.Checkbutton(
            crop_frame,
            text="Enable Crop",
            variable=self.crop_enabled_var,
            fg="white",
            bg="gray20",
            selectcolor="gray30",
            activebackground="gray20",
            activeforeground="white",
        ).pack(anchor="w")

        crop_coords_frame = tk.Frame(crop_frame, bg="gray20")
        crop_coords_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(crop_coords_frame, text="X:", fg="white", bg="gray20").grid(
            row=0, column=0, sticky="w"
        )
        self.crop_x_var = tk.IntVar(value=self.settings["crop_x"])
        tk.Entry(crop_coords_frame, textvariable=self.crop_x_var, width=8).grid(
            row=0, column=1, padx=2
        )

        tk.Label(crop_coords_frame, text="Y:", fg="white", bg="gray20").grid(
            row=0, column=2, sticky="w", padx=(10, 0)
        )
        self.crop_y_var = tk.IntVar(value=self.settings["crop_y"])
        tk.Entry(crop_coords_frame, textvariable=self.crop_y_var, width=8).grid(
            row=0, column=3, padx=2
        )

        tk.Label(crop_coords_frame, text="Width:", fg="white", bg="gray20").grid(
            row=1, column=0, sticky="w"
        )
        self.crop_width_var = tk.IntVar(value=self.settings["crop_width"])
        tk.Entry(crop_coords_frame, textvariable=self.crop_width_var, width=8).grid(
            row=1, column=1, padx=2
        )

        tk.Label(crop_coords_frame, text="Height:", fg="white", bg="gray20").grid(
            row=1, column=2, sticky="w", padx=(10, 0)
        )
        self.crop_height_var = tk.IntVar(value=self.settings["crop_height"])
        tk.Entry(crop_coords_frame, textvariable=self.crop_height_var, width=8).grid(
            row=1, column=3, padx=2
        )

        # Factory Reset
        reset_frame = tk.LabelFrame(
            settings_frame, text="Factory Reset", fg="red", bg="gray20"
        )
        reset_frame.pack(fill="x", padx=5, pady=5)

        self.factory_reset_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            reset_frame,
            text="⚠️ Reset this camera to factory defaults (clears all settings)",
            variable=self.factory_reset_var,
            fg="red",
            bg="gray20",
            selectcolor="gray30",
            activebackground="gray20",
            activeforeground="red",
        ).pack(anchor="w", padx=5, pady=5)

        # Buttons
        button_frame = tk.Frame(main_frame, bg="black")
        button_frame.pack(fill="x", pady=10)

        tk.Button(
            button_frame, text="Apply", bg="green", fg="white", command=self.apply_settings
        ).pack(side="left", padx=5)
        tk.Button(
            button_frame, text="Cancel", bg="red", fg="white", command=self.window.destroy
        ).pack(side="right", padx=5)

    def apply_settings(self):
        """Apply camera settings - USER TRIGGERED ONLY"""
        print(f"🔧 Applying settings to {self.ip}...")

        if self.factory_reset_var.get():
            confirm = messagebox.askyesno(
                "Factory Reset Confirmation",
                f"Are you sure you want to reset {self.ip} to factory defaults?\n\nThis will clear ALL settings and cannot be undone.",
                icon="warning",
            )
            if confirm:
                print(f"🏭 Performing factory reset on {self.ip}...")
                self.gui.network_manager.send_command(
                    self.ip, "RESET_TO_FACTORY_DEFAULTS"
                )
                messagebox.showinfo("Factory Reset", f"Factory reset sent to {self.ip}")
                self.window.destroy()
                return
            else:
                self.factory_reset_var.set(False)
                return

        # Build package
        settings_package = {
            "iso": self.iso_var.get(),
            "brightness": self.brightness_var.get(),
            "flip_horizontal": self.flip_h_var.get(),
            "flip_vertical": self.flip_v_var.get(),
            "grayscale": self.grayscale_var.get(),
            "rotation": int(self.rotation_var.get()),
            "crop_enabled": self.crop_enabled_var.get(),
            "crop_x": self.crop_x_var.get(),
            "crop_y": self.crop_y_var.get(),
            "crop_width": self.crop_width_var.get(),
            "crop_height": self.crop_height_var.get(),
        }

        settings_json = json.dumps(settings_package)
        print(f"   📤 Sending settings package: {settings_json}")
        self.gui.network_manager.send_command(
            self.ip, f"SET_ALL_SETTINGS_{settings_json}"
        )

        # Save locally
        self.save_camera_settings()

        print(f"✅ Settings package sent to {self.ip}")
        messagebox.showinfo("Settings Applied", f"Settings applied to {self.ip}")
        self.window.destroy()


class AppPreferencesDialog:
    """Application preferences dialog"""
    
    def __init__(self, gui):
        self.gui = gui
        
        self.window = tk.Toplevel(gui.root)
        self.window.title("Application Preferences")
        self.window.geometry("400x200")
        self.window.resizable(False, False)
        
        # Create main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Application Preferences", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Audio feedback checkbox
        self.audio_var = tk.BooleanVar(value=self.gui.audio.enabled)
        audio_check = ttk.Checkbutton(
            main_frame,
            text="Enable Audio Feedback (sound on capture)",
            variable=self.audio_var,
            command=self.on_audio_toggle
        )
        audio_check.pack(pady=10, anchor="w")
        
        # Info label
        info_label = ttk.Label(main_frame, 
                              text="Plays a sound effect when capturing images from cameras",
                              font=("Arial", 9),
                              foreground="gray")
        info_label.pack(pady=(0, 20), anchor="w")
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side="bottom", fill="x", pady=(20, 0))
        
        # Close button
        close_button = ttk.Button(button_frame, text="Close", command=self.window.destroy)
        close_button.pack(side="right")
    
    def on_audio_toggle(self):
        """Handle audio checkbox toggle"""
        enabled = self.audio_var.get()
        self.gui.audio.set_enabled(enabled)
        
        # Save preference
        self.gui.save_app_preferences({'audio_feedback_enabled': enabled})
        
        # Play sound to test if enabling
        if enabled:
            self.gui.audio.play_capture_sound()
