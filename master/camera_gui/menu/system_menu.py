"""
System controls menu manager
"""

import tkinter as tk
from tkinter import messagebox
import logging


class SystemMenuManager:
    """Manages the system controls menu"""
    
    def __init__(self, gui):
        self.gui = gui

    def create_menu(self, menubar):
        """Create system controls menu"""
        system_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="System Controls", menu=system_menu)
        
        # Global controls
        system_menu.add_command(label="Shutdown All Devices", command=self.shutdown_all)
        system_menu.add_command(label="Reboot All Devices", command=self.reboot_all)
        system_menu.add_separator()
        
        # Individual device controls
        device_menu = tk.Menu(system_menu, tearoff=0)
        system_menu.add_cascade(label="Individual Device Controls", menu=device_menu)
        
        from config.settings import config, device_names
        for name, slave_info in config.SLAVES.items():
            ip = slave_info["ip"]
            device_name = device_names.get(ip, name)
            
            device_submenu = tk.Menu(device_menu, tearoff=0)
            device_menu.add_cascade(label=device_name, menu=device_submenu)
            
            device_submenu.add_command(label="Reboot", 
                                     command=lambda ip=ip: self.reboot_device(ip))
            device_submenu.add_command(label="Shutdown", 
                                     command=lambda ip=ip: self.shutdown_device(ip))

    def shutdown_all(self):
        """Shutdown all devices using sudo poweroff"""
        if messagebox.askyesno("Confirm Shutdown", "Shutdown all slave devices using 'sudo poweroff'?"):
            logging.info("Initiating shutdown sequence for all devices (sudo poweroff)")
            
            for ip in self.gui.get_camera_ips():
                try:
                    self.gui.network_manager.send_command(ip, "sudo poweroff")
                    logging.info(f"sudo poweroff command sent to {ip}")
                except Exception as e:
                    logging.error(f"Error shutting down {ip}: {e}")
            
            messagebox.showinfo("Shutdown", "sudo poweroff commands sent to all devices")

    def reboot_all(self):
        """Reboot all devices"""
        if messagebox.askyesno("Confirm Reboot", "Reboot all slave devices?"):
            logging.info("Initiating reboot sequence for all devices")
            
            for ip in self.gui.get_camera_ips():
                try:
                    self.gui.network_manager.send_command(ip, "REBOOT")
                    logging.info(f"Reboot command sent to {ip}")
                except Exception as e:
                    logging.error(f"Error rebooting {ip}: {e}")
            
            messagebox.showinfo("Reboot", "Reboot commands sent to all devices")

    def shutdown_device(self, ip):
        """Shutdown individual device using sudo poweroff"""
        from config.settings import device_names
        device_name = device_names.get(ip, ip)
        
        if messagebox.askyesno("Confirm Shutdown", f"Shutdown {device_name} using 'sudo poweroff'?"):
            try:
                self.gui.network_manager.send_command(ip, "sudo poweroff")
                messagebox.showinfo("Shutdown", f"sudo poweroff command sent to {device_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to shutdown {device_name}: {e}")

    def reboot_device(self, ip):
        """Reboot individual device"""
        from config.settings import device_names
        device_name = device_names.get(ip, ip)
        
        if messagebox.askyesno("Confirm Reboot", f"Reboot {device_name}?"):
            try:
                self.gui.network_manager.send_command(ip, "REBOOT")
                messagebox.showinfo("Reboot", f"Reboot command sent to {device_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reboot {device_name}: {e}")
