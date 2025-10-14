"""
Network operations manager - FIXED VERSION with proper port handling
"""

import socket
import threading
import logging
import time
from datetime import datetime
from PIL import Image, ImageTk

try:
    from config.settings import config
except ImportError:
    # Fallback if config import fails
    config = {
        'MASTER_IP': '192.168.0.200',
        'SLAVES': {
            "rep1": {"ip": "192.168.0.201"},
            "rep2": {"ip": "192.168.0.202"},
            "rep3": {"ip": "192.168.0.203"},
            "rep4": {"ip": "192.168.0.204"},
            "rep5": {"ip": "192.168.0.205"},
            "rep6": {"ip": "192.168.0.206"},
            "rep7": {"ip": "192.168.0.207"},
            "rep8": {"ip": "127.0.0.1", "local": True}
        }
    }


class NetworkManager:
    """Manages all network operations with proper port handling"""
    
    def __init__(self, gui):
        self.gui = gui
        self.video_socket = None
        self.still_server = None
        self.active_heartbeats = {}

    def start_all_services(self):
        """Start all network services"""
        logging.info("Starting network services...")
        threading.Thread(target=self.video_receiver, daemon=True).start()
        threading.Thread(target=self.still_receiver, daemon=True).start()
        threading.Thread(target=self.heartbeat_listener, daemon=True).start()
        threading.Thread(target=self.heartbeat_monitor, daemon=True).start()

    def get_device_ports(self, ip):
        """Get correct ports for device based on IP"""
        try:
            # Import the shared config function
            import sys
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent.parent
            sys.path.insert(0, str(project_root))
            from shared.config import get_slave_ports
            return get_slave_ports(ip)
        except ImportError:
            # Fallback if shared config not available
            if ip == "127.0.0.1":  # Local camera uses different ports
                return {
                    'control': 5011,
                    'video': 5012,
                    'video_control': 5014,
                    'still': 6010,
                    'heartbeat': 5013
                }
            else:  # Remote cameras
                return {
                    'control': 5001,
                    'video': 5002,
                    'video_control': 5004,
                    'still': 6000,
                    'heartbeat': 5003
                }

    def send_command(self, ip, command):
        """Send command to device using correct ports with enhanced logging"""
        try:
            print(f"📡 Sending '{command}' to {ip}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5.0)  # Increased timeout for shutdown commands
            
            # Get correct ports for this device
            ports = self.get_device_ports(ip)
            
            # Determine which port to use based on command type
            if command in ("START_STREAM", "STOP_STREAM", "RESTART_STREAM"):
                # Video control commands
                # Local camera slave listens for START/STOP on control port (5011),
                # not the video_control port. Special-case localhost.
                if ip in ("127.0.0.1", "localhost"):
                    port = ports['control']
                else:
                    port = ports.get('video_control', ports['control'])
            elif command in ("sudo poweroff", "SHUTDOWN", "REBOOT", "poweroff", "shutdown", "reboot"):
                # System commands - use control port
                port = ports['control']
            elif command.startswith("SET_TIME"):
                # Time sync commands
                port = ports['control']
            else:
                # Default commands
                port = ports['control']
            
            # Send command
            sock.sendto(command.encode(), (ip, port))
            sock.close()
            
            print(f"   ✅ Sent to {ip}:{port}")
            logging.info(f"Sent command '{command}' to {ip}:{port}")
            
            # Special handling for shutdown - send multiple formats to ensure it works
            if command == "sudo poweroff":
                time.sleep(0.1)
                try:
                    # Send additional shutdown formats
                    for additional_cmd in ["SHUTDOWN", "poweroff"]:
                        sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock2.settimeout(3.0)
                        sock2.sendto(additional_cmd.encode(), (ip, port))
                        sock2.close()
                        logging.info(f"Sent additional shutdown command '{additional_cmd}' to {ip}:{port}")
                        time.sleep(0.1)
                except Exception as e:
                    logging.warning(f"Additional shutdown commands failed for {ip}: {e}")
            
        except Exception as e:
            logging.error(f"Failed to send command '{command}' to {ip}: {e}")

    def video_receiver(self):
        """Receive video frames with proper port handling"""
        try:
            self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 262144)
            self.video_socket.bind(("0.0.0.0", config.VIDEO_PORT))
            
            logging.info(f"Video receiver listening on port {config.VIDEO_PORT}")
            
            while True:
                try:
                    data, addr = self.video_socket.recvfrom(65536)
                    ip = addr[0]
                    
                    # Accept frames from configured slaves
                    slave_ips = [slave["ip"] for slave in config.SLAVES.values()]
                    if ip in slave_ips:
                        self.process_video_frame(ip, data)
                    elif ip in ("127.0.0.1", "localhost"):
                        # Also accept from localhost variants
                        self.process_video_frame("127.0.0.1", data)
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    if "timed out" not in str(e).lower():
                        logging.error(f"Video receiver error: {e}")
                        
        except Exception as e:
            logging.error(f"Video receiver setup error: {e}")

    def process_video_frame(self, ip, data):
        """Process incoming video frame"""
        try:
            import io
            
            # Decode image
            image = Image.open(io.BytesIO(data)).convert("RGB")
            
            # Local camera (rep8) sends BGR data as JPEG, which decodes as RGB in correct order
            # Remote cameras send RGB data as JPEG 
            # No color swap needed - JPEG decoding handles this correctly
            
            # Pass ORIGINAL image to GUI thread - let it decide sizing based on exclusive mode
            # No pre-resize here to preserve quality for exclusive mode enlargement
            
            # Update GUI thread-safely - pass PIL Image for GUI thread to handle sizing
            if ip in self.gui.video_labels:
                self.gui.root.after_idle(
                    lambda: self.update_video_display_safe(ip, image)
                )
                
        except Exception as e:
            logging.error(f"Error processing video frame from {ip}: {e}")

    def update_video_display_safe(self, ip, pil_image):
        """Thread-safe video display update with dynamic sizing for exclusive mode"""
        try:
            if ip in self.gui.video_labels:
                # Check if this camera is in exclusive view mode (GUI thread = safe to check state)
                is_exclusive = (hasattr(self.gui, 'exclusive_ip') and 
                               self.gui.exclusive_ip == ip)
                
                # Resize for exclusive mode if needed
                if is_exclusive:
                    # Enlarge for manual focusing - 3x normal size
                    display_image = pil_image.resize((960, 720), Image.Resampling.LANCZOS)
                else:
                    # Normal grid size - downscale from original for performance
                    display_image = pil_image.resize((320, 240), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage and update label
                image_tk = ImageTk.PhotoImage(display_image)
                self.gui.video_labels[ip].config(image=image_tk, text="")
                self.gui.video_labels[ip].image = image_tk  # Keep reference to prevent garbage collection
        except Exception as e:
            logging.error(f"Error updating video display for {ip}: {e}")

    def still_receiver(self):
        """Receive still images"""
        try:
            self.still_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.still_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.still_server.bind(("0.0.0.0", config.STILL_PORT))
            self.still_server.listen(10)
            
            logging.info(f"Still receiver listening on port {config.STILL_PORT}")
            
            while True:
                try:
                    conn, addr = self.still_server.accept()
                    threading.Thread(target=self.handle_still_connection, 
                                   args=(conn, addr), daemon=True).start()
                except Exception as e:
                    logging.error(f"Still receiver error: {e}")
                    
        except Exception as e:
            logging.error(f"Still receiver setup error: {e}")

    def handle_still_connection(self, conn, addr):
        """Handle still image connection"""
        try:
            ip = addr[0]
            data = b""
            conn.settimeout(30.0)
            
            while True:
                chunk = conn.recv(8192)
                if not chunk:
                    break
                data += chunk
                
            conn.close()
            
            if data and self.gui.gallery_panel:
                self.save_and_display_still(ip, data)
                
        except Exception as e:
            logging.error(f"Error handling still from {addr[0]}: {e}")

    def save_and_display_still(self, ip, data):
        """Save still image to Desktop with dated directories"""
        try:
            from config.settings import device_names
            import os
            from datetime import datetime
            
            # Get device name
            device_name = device_names.get(ip, ip)
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            date_str = now.strftime("%Y-%m-%d")
            
            # Create dated directory structure for Pi environment  
            # Check if we're on a Pi (Linux) or development machine (macOS)
            import platform
            if platform.system() == "Darwin":  # macOS development
                base_path = os.path.expanduser("~/Desktop/captured_images")
            else:  # Linux Pi environment
                base_path = "/home/andrc1/Desktop/captured_images"
                # Ensure base directory exists on Pi
                os.makedirs(base_path, exist_ok=True)
            
            daily_capture_dir = os.path.join(base_path, date_str, device_name)
            
            # Enhanced directory creation with verification
            try:
                os.makedirs(daily_capture_dir, exist_ok=True)
                # Verify directory is writable
                if not os.access(daily_capture_dir, os.W_OK):
                    raise OSError(f"Directory not writable: {daily_capture_dir}")
                logging.info(f"Directory ready: {daily_capture_dir}")
            except Exception as e:
                logging.error(f"Directory creation failed: {e}")
                # Use fallback
                fallback_dir = os.path.join("/tmp", "camera_fallback", device_name)
                os.makedirs(fallback_dir, exist_ok=True)
                daily_capture_dir = fallback_dir
                logging.warning(f"Using fallback directory: {fallback_dir}")
            
            filename = os.path.join(daily_capture_dir, f"{timestamp}.jpg")
            
            with open(filename, "wb") as f:
                f.write(data)
            
            # Add to gallery
            if self.gui.gallery_panel:
                self.gui.root.after_idle(
                    lambda: self.gui.gallery_panel.add_image(filename, device_name, timestamp)
                )
            
            logging.info(f"Saved image from {device_name}: {filename}")
            
        except Exception as e:
            logging.error(f"Error saving still image: {e}")

    def heartbeat_listener(self):
        """Listen for heartbeat messages"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("0.0.0.0", config.HEARTBEAT_PORT))
            
            logging.info(f"Heartbeat listener on port {config.HEARTBEAT_PORT}")
            
            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    ip = addr[0]
                    if data.decode().strip() == "HEARTBEAT":
                        self.active_heartbeats[ip] = time.time()
                        logging.debug(f"Heartbeat from {ip}")
                except Exception as e:
                    logging.error(f"Heartbeat listener error: {e}")
                    
        except Exception as e:
            logging.error(f"Heartbeat listener setup error: {e}")

    def heartbeat_monitor(self):
        """Monitor heartbeat status and update GUI"""
        while True:
            try:
                now = time.time()
                slave_ips = [slave["ip"] for slave in config.SLAVES.values()]
                
                for ip in slave_ips:
                    last_beat = self.active_heartbeats.get(ip, 0)
                    is_alive = (now - last_beat) < 10  # Increased timeout to 10 seconds
                    
                    # Update heartbeat status in GUI
                    if ip in self.gui.heartbeat_labels:
                        color = "green" if is_alive else "red"
                        text = "🟢" if is_alive else "🔴"
                        self.gui.root.after_idle(
                            lambda ip=ip, text=text, color=color: self.update_heartbeat_safe(ip, text, color)
                        )
                
                time.sleep(3)  # Check every 3 seconds
            except Exception as e:
                logging.error(f"Heartbeat monitor error: {e}")
                time.sleep(5)

    def update_heartbeat_safe(self, ip, text, color):
        """Thread-safe heartbeat update"""
        try:
            if ip in self.gui.heartbeat_labels:
                self.gui.heartbeat_labels[ip].config(text=text, foreground=color)
        except Exception as e:
            logging.error(f"Error updating heartbeat for {ip}: {e}")

    def debug_video_streaming(self):
        """Debug function to check video streaming status"""
        logging.info("=== VIDEO STREAMING DEBUG ===")
        for name, slave_info in config.SLAVES.items():
            ip = slave_info["ip"]
            ports = self.get_device_ports(ip)
            last_heartbeat = self.active_heartbeats.get(ip, 0)
            heartbeat_age = time.time() - last_heartbeat if last_heartbeat > 0 else "Never"
            
            logging.info(f"{name} ({ip}):")
            logging.info(f"  Control Port: {ports['control']}")
            logging.info(f"  Video Port: {ports.get('video', 'N/A')}")
            logging.info(f"  Last Heartbeat: {heartbeat_age}")
            logging.info(f"  Video Label Exists: {ip in self.gui.video_labels}")
