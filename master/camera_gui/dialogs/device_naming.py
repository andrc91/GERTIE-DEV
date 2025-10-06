"""
Device naming dialog
"""

import tkinter as tk
from tkinter import messagebox
from config.settings import config, device_names, save_device_names


class DeviceNamingDialog:
    """Device naming dialog"""
    
    def __init__(self, gui):
        self.gui = gui
        
        self.window = tk.Toplevel(gui.root)
        self.window.title("Device Names")
        self.window.geometry("500x400")
        self.window.configure(bg="black")
        self.window.transient(gui.root)
        self.window.grab_set()
        
        self.create_interface()

    def create_interface(self):
        """Create naming interface"""
        main_frame = tk.Frame(self.window, bg="black")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(main_frame, text="Device Names", 
                font=("Arial", 14, "bold"), fg="white", bg="black").pack(pady=10)
        
        # Entries frame
        entries_frame = tk.Frame(main_frame, bg="gray20")
        entries_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.name_entries = {}
        
        for name, slave_info in config.SLAVES.items():
            ip = slave_info["ip"]
            device_frame = tk.Frame(entries_frame, bg="gray20")
            device_frame.pack(fill="x", padx=5, pady=2)
            
            current_name = device_names.get(ip, name)
            tk.Label(device_frame, text=f"{ip}:", fg="white", bg="gray20", width=15).pack(side="left")
            
            name_entry = tk.Entry(device_frame, width=20)
            name_entry.pack(side="left", padx=10)
            name_entry.insert(0, current_name)
            self.name_entries[ip] = name_entry
            
            device_type = "Local Camera" if ip == "127.0.0.1" else f"Network Camera"
            tk.Label(device_frame, text=device_type, fg="gray", bg="gray20").pack(side="right")
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg="black")
        button_frame.pack(fill="x", pady=10)
        
        tk.Button(button_frame, text="Save Names", bg="green", fg="white", 
                 command=self.save_names).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", bg="red", fg="white", 
                 command=self.window.destroy).pack(side="right", padx=5)

    def save_names(self):
        """Save device names"""
        global device_names
        
        for ip, entry in self.name_entries.items():
            name = entry.get().strip()
            if name:
                device_names[ip] = name
            else:
                # Use default if empty
                for slave_name, slave_info in config.SLAVES.items():
                    if slave_info["ip"] == ip:
                        device_names[ip] = slave_name
                        break
        
        save_device_names()
        messagebox.showinfo("Names Saved", "Device names saved successfully!")
        self.window.destroy()
