"""
Gallery panel widget for captured images
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import logging

from config.settings import config


class GalleryPanel:
    """Left-side gallery panel for captured images"""
    
    def __init__(self, root):
        self.root = root
        self.panel = None
        self.canvas = None
        self.thumbnails_frame = None
        self.thumbnails = []
        
        self.create_panel()

    def create_panel(self):
        """Create the gallery panel"""
        self.panel = ttk.Frame(self.root, width=config.GALLERY_WIDTH)
        self.panel.grid_propagate(False)  # Maintain fixed width
        
        # Header
        header = ttk.Frame(self.panel)
        header.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(header, text="Captured Images", 
                 font=('Arial', 12, 'bold')).pack(side="left")
        
        ttk.Button(header, text="Clear", 
                  command=self.clear_all).pack(side="right")
        
        # Scrollable content
        self.create_scrollable_content()

    def create_scrollable_content(self):
        """Create scrollable content area"""
        content_frame = ttk.Frame(self.panel)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(content_frame, bg="black", width=280)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", 
                                 command=self.canvas.yview)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.thumbnails_frame = ttk.Frame(self.canvas)
        self.thumbnails_frame.bind(
            "<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.thumbnails_frame, anchor="nw")
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)

    def pack_left(self):
        """Pack the panel on the left side"""
        self.panel.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)

    def add_image(self, filepath, device_name, timestamp):
        """Add new image to gallery"""
        try:
            # Create thumbnail
            image = Image.open(filepath).resize((260, 195)).convert("RGB")
            image_tk = ImageTk.PhotoImage(image)
            
            # Create thumbnail frame
            thumb_frame = tk.Frame(self.thumbnails_frame, bd=1, 
                                  relief="raised", bg="gray20")
            thumb_frame.pack(fill="x", padx=5, pady=2)
            
            # Image display
            img_label = tk.Label(thumb_frame, image=image_tk, bg="gray20")
            img_label.image = image_tk  # Keep reference
            img_label.pack()
            
            # Info and controls
            info_frame = tk.Frame(thumb_frame, bg="gray20")
            info_frame.pack(fill="x", padx=5, pady=2)
            
            # Caption
            caption = tk.Label(info_frame, text=f"{device_name} - {timestamp}", 
                             font=("Arial", 8), fg="white", bg="gray20")
            caption.pack(side="left")
            
            # Controls
            controls = tk.Frame(info_frame, bg="gray20")
            controls.pack(side="right")
            
            tk.Button(controls, text="View", font=("Arial", 7),
                     command=lambda: self.view_image(filepath)).pack(side="left", padx=1)
            tk.Button(controls, text="Del", font=("Arial", 7), bg="red", fg="white",
                     command=lambda: self.delete_image(thumb_frame, filepath)).pack(side="left", padx=1)
            
            # Click to view
            img_label.bind("<Button-1>", lambda e: self.view_image(filepath))
            
            self.thumbnails.append(thumb_frame)
            
            # Memory management
            if len(self.thumbnails) > 20:
                old_thumb = self.thumbnails.pop(0)
                old_thumb.destroy()
            
            # Update scroll and auto-scroll to bottom
            # Removed update_idletasks - let GUI update naturally
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.yview_moveto(1.0)
            
        except Exception as e:
            logging.error(f"Error adding image to gallery: {e}")

    def view_image(self, filepath):
        """View full-size image"""
        try:
            top = tk.Toplevel(self.root)
            top.title(os.path.basename(filepath))
            top.configure(bg="black")
            
            img = Image.open(filepath)
            # Scale to fit screen
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            max_w, max_h = int(screen_w * 0.8), int(screen_h * 0.8)
            
            scale = min(max_w / img.width, max_h / img.height, 1.0)
            if scale < 1.0:
                new_size = (int(img.width * scale), int(img.height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            img_tk = ImageTk.PhotoImage(img)
            label = tk.Label(top, image=img_tk, bg="black")
            label.image = img_tk
            label.pack(padx=10, pady=10)
            
        except Exception as e:
            logging.error(f"Error viewing image: {e}")

    def delete_image(self, widget, filepath):
        """Delete image with confirmation"""
        from tkinter import messagebox
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Delete {os.path.basename(filepath)}?"):
            try:
                os.remove(filepath)
                widget.destroy()
                if widget in self.thumbnails:
                    self.thumbnails.remove(widget)
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            except Exception as e:
                logging.error(f"Error deleting image: {e}")

    def clear_all(self):
        """Clear all thumbnails from gallery"""
        from tkinter import messagebox
        
        if messagebox.askyesno("Clear Gallery", 
                              "Remove all images from gallery?\n\n"
                              "Images will remain in the folder."):
            for thumb in self.thumbnails:
                thumb.destroy()
            self.thumbnails.clear()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        try:
            delta = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(delta, "units")
        except Exception as e:
            logging.error(f"Mouse wheel error: {e}")
