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
        
        # CRITICAL FIX: Fixed-interval timer architecture for smooth GUI
        # Replace after_idle() with scheduled timers to prevent event saturation
        self.latest_frames = {}  # Buffer latest frame per camera
        self.frame_timers = {}  # Active timer IDs per camera
        self.photo_images = {}  # Reusable PhotoImage objects per camera
        
        # Timer intervals for smooth GUI (milliseconds)
        self.grid_update_interval = 250  # 4 Hz update rate for grid mode
        self.exclusive_update_interval = 67  # 15 Hz for exclusive mode
        
        # Frame dropping for network thread
        self.last_frame_time = {}  # Track when last frame was accepted
        self.frame_interval_grid = 0.25  # Accept 4 fps from network in grid mode
        self.frame_interval_exclusive = 0.067  # Accept 15 fps in exclusive mode
        
        # INSTRUMENTATION: Performance metrics
        self.frames_received = {}  # Total frames received per camera
        self.frames_displayed = {}  # Total frames actually displayed
        self.frames_dropped = {}  # Frames dropped by rate limiting
        self.perf_start_time = time.time()
        self.last_perf_log = time.time()
        
        # GUI HEARTBEAT MONITOR: Detect event loop stalls
        self.heartbeat_interval = 200  # Check every 200ms
        self.heartbeat_count = 0
        self.last_heartbeat = time.time()
        self.heartbeat_stalls = 0
        self._start_heartbeat_monitor()

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
        """Send command to device using correct ports - NON-BLOCKING version"""
        # Run in background thread to avoid blocking GUI
        def _send_thread():
            try:
                print(f"📡 Sending '{command}' to {ip}")
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1.0)  # 1s timeout sufficient for local network
                
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
                    try:
                        # Send additional shutdown formats
                        for additional_cmd in ["SHUTDOWN", "poweroff"]:
                            sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            sock2.settimeout(1.0)
                            sock2.sendto(additional_cmd.encode(), (ip, port))
                            sock2.close()
                            logging.info(f"Sent additional shutdown command '{additional_cmd}' to {ip}:{port}")
                    except Exception as e:
                        logging.warning(f"Additional shutdown commands failed for {ip}: {e}")
                
            except Exception as e:
                logging.error(f"Failed to send command '{command}' to {ip}: {e}")
        
        # Execute in background thread - return immediately to GUI
        cmd_thread = threading.Thread(target=_send_thread, daemon=True)
        cmd_thread.start()

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
        """Process incoming video frame with frame buffering instead of queuing"""
        try:
            import io
            
            # INSTRUMENTATION: Track frames received
            if ip not in self.frames_received:
                self.frames_received[ip] = 0
                self.frames_displayed[ip] = 0
                self.frames_dropped[ip] = 0
                self.last_frame_time[ip] = 0
            self.frames_received[ip] += 1
            
            # Rate limit frames BEFORE decode to save CPU
            current_time = time.time()
            is_exclusive = (hasattr(self.gui, 'exclusive_ip') and 
                           self.gui.exclusive_ip == ip)
            
            # Determine frame interval based on display mode
            min_interval = self.frame_interval_exclusive if is_exclusive else self.frame_interval_grid
            time_since_last = current_time - self.last_frame_time[ip]
            
            if time_since_last < min_interval:
                # DROP frame early - don't waste CPU on decode/resize
                self.frames_dropped[ip] += 1
                return
            
            # Update last frame time
            self.last_frame_time[ip] = current_time
            
            # Decode image (only if frame passed rate limit)
            image = Image.open(io.BytesIO(data)).convert("RGB")
            
            # Pre-resize based on display mode
            if is_exclusive:
                # Exclusive mode: Larger preview (960x720)
                display_image = image.resize((960, 720), Image.Resampling.BILINEAR)
            else:
                # Grid mode: Standard preview size (320x240)
                display_image = image.resize((320, 240), Image.Resampling.BILINEAR)
            
            # NEW: Buffer frame instead of queuing GUI update
            self.latest_frames[ip] = display_image
            
            # NEW: Start timer if not already running for this camera
            if ip not in self.frame_timers and ip in self.gui.video_labels:
                self._start_frame_timer(ip)
                
        except Exception as e:
            logging.error(f"Error processing video frame from {ip}: {e}")

    def _start_frame_timer(self, ip):
        """Start a fixed-interval timer for this camera's updates"""
        is_exclusive = (hasattr(self.gui, 'exclusive_ip') and 
                       self.gui.exclusive_ip == ip)
        interval = self.exclusive_update_interval if is_exclusive else self.grid_update_interval
        
        # Schedule the update function
        timer_id = self.gui.root.after(interval, lambda: self._timer_update_display(ip))
        self.frame_timers[ip] = timer_id

    def _timer_update_display(self, ip):
        """Timer-driven display update - runs at fixed interval, not event-driven"""
        try:
            # Check if we should continue updating this camera
            if ip not in self.gui.video_labels:
                # Camera removed, stop timer
                if ip in self.frame_timers:
                    del self.frame_timers[ip]
                return
            
            # Check if we have a buffered frame
            if ip in self.latest_frames:
                pil_image = self.latest_frames[ip]
                
                # OPTIMIZED: Better PhotoImage reuse to reduce object churn
                try:
                    if ip not in self.photo_images:
                        # First time - create PhotoImage with the image
                        self.photo_images[ip] = ImageTk.PhotoImage(pil_image)
                    else:
                        # Reuse existing PhotoImage - paste is more efficient
                        # This avoids creating new objects in the GUI thread
                        self.photo_images[ip].paste(pil_image)
                except Exception as e:
                    # If paste fails (size mismatch), recreate PhotoImage
                    logging.debug(f"PhotoImage paste failed for {ip}, recreating: {e}")
                    self.photo_images[ip] = ImageTk.PhotoImage(pil_image)
                
                # Update the label widget - minimal operations
                label = self.gui.video_labels.get(ip)
                if label:
                    label.config(image=self.photo_images[ip], text="")
                    label.image = self.photo_images[ip]  # Keep reference
                
                # Clear the buffer
                del self.latest_frames[ip]
                self.frames_displayed[ip] += 1
                
                # Log performance periodically
                current_time = time.time()
                if current_time - self.last_perf_log >= 10.0:
                    self._log_performance_metrics()
                    self.last_perf_log = current_time
            
            # Schedule next update
            is_exclusive = (hasattr(self.gui, 'exclusive_ip') and 
                           self.gui.exclusive_ip == ip)
            interval = self.exclusive_update_interval if is_exclusive else self.grid_update_interval
            timer_id = self.gui.root.after(interval, lambda: self._timer_update_display(ip))
            self.frame_timers[ip] = timer_id
            
        except Exception as e:
            logging.error(f"Error in timer update for {ip}: {e}")
            # Restart timer even on error
            if ip in self.gui.video_labels:
                is_exclusive = (hasattr(self.gui, 'exclusive_ip') and 
                               self.gui.exclusive_ip == ip)
                interval = self.exclusive_update_interval if is_exclusive else self.grid_update_interval
                timer_id = self.gui.root.after(interval, lambda: self._timer_update_display(ip))
                self.frame_timers[ip] = timer_id

    def stop_camera_timer(self, ip):
        """Stop the timer for a specific camera"""
        if ip in self.frame_timers:
            self.gui.root.after_cancel(self.frame_timers[ip])
            del self.frame_timers[ip]
        if ip in self.photo_images:
            del self.photo_images[ip]
        if ip in self.latest_frames:
            del self.latest_frames[ip]

    def stop_all_timers(self):
        """Stop all camera timers (useful for mode changes)"""
        for ip in list(self.frame_timers.keys()):
            self.stop_camera_timer(ip)

    def _log_performance_metrics(self):
        """Log comprehensive performance metrics for debugging"""
        try:
            elapsed = time.time() - self.perf_start_time
            
            logging.info("=" * 60)
            logging.info(f"[PERF] GUI Performance Metrics (after {elapsed:.1f}s)")
            logging.info("=" * 60)
            
            total_received = sum(self.frames_received.values())
            total_displayed = sum(self.frames_displayed.values())
            total_dropped = sum(self.frames_dropped.values())
            
            if total_received > 0:
                drop_rate = (total_dropped / total_received) * 100
                display_rate = (total_displayed / total_received) * 100
                logging.info(f"[PERF] OVERALL: Received={total_received}, Dropped={total_dropped} ({drop_rate:.1f}%), Displayed={total_displayed} ({display_rate:.1f}%)")
            
            for ip in sorted(self.frames_received.keys()):
                received = self.frames_received[ip]
                displayed = self.frames_displayed[ip]
                dropped = self.frames_dropped.get(ip, 0)
                
                if received > 0 and elapsed > 0:
                    fps = displayed / elapsed
                    drop_rate = (dropped / received) * 100
                    
                    # Get device name for logging
                    device_name = ip.replace(".", "_")
                    if ip == "127.0.0.1":
                        device_name = "rep8"
                    elif ip.startswith("192.168.0."):
                        last_octet = int(ip.split(".")[-1])
                        device_name = f"rep{last_octet - 200}"
                    
                    logging.info(f"[PERF] {device_name:5s} ({ip}): {fps:4.1f} FPS | Recv={received:4d} | Dropped={dropped:4d} ({drop_rate:5.1f}%) | Queued={queued:3d} | Skipped={skipped:3d}")
            
            logging.info("=" * 60)
            
        except Exception as e:
            logging.error(f"Error logging performance metrics: {e}")

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
            
            # Add to gallery using scheduled timer to avoid blocking
            if self.gui.gallery_panel:
                # OPTIMIZED: Batch gallery updates to prevent event queue saturation
                if not hasattr(self, '_gallery_update_queue'):
                    self._gallery_update_queue = []
                    self._gallery_update_pending = False
                
                # Queue the update
                self._gallery_update_queue.append((filename, device_name, timestamp))
                
                # Schedule batch update if not already pending
                if not self._gallery_update_pending:
                    self._gallery_update_pending = True
                    # Process gallery updates in batches every 250ms
                    self.gui.root.after(250, self._process_gallery_batch)
                
                # Notify GUI with minimal delay
                self.gui.root.after(10, self.gui.on_image_received)
            
            logging.info(f"Saved image from {device_name}: {filename}")
            
        except Exception as e:
            logging.error(f"Error saving still image: {e}")

    def _process_gallery_batch(self):
        """Process batched gallery updates to prevent event queue saturation"""
        try:
            if hasattr(self, '_gallery_update_queue') and self._gallery_update_queue:
                # Process up to 3 images per batch to prevent blocking
                batch_size = min(3, len(self._gallery_update_queue))
                for _ in range(batch_size):
                    if self._gallery_update_queue:
                        filename, device_name, timestamp = self._gallery_update_queue.pop(0)
                        if self.gui.gallery_panel:
                            self.gui.gallery_panel.add_image(filename, device_name, timestamp)
                
                # If more items remain, schedule next batch
                if self._gallery_update_queue:
                    self.gui.root.after(250, self._process_gallery_batch)
                else:
                    self._gallery_update_pending = False
            else:
                self._gallery_update_pending = False
        except Exception as e:
            logging.error(f"Error processing gallery batch: {e}")
            self._gallery_update_pending = False

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
                    
                    # Update heartbeat status in GUI using timer instead of after_idle
                    if ip in self.gui.heartbeat_labels:
                        color = "green" if is_alive else "red"
                        text = "🟢" if is_alive else "🔴"
                        # Use after() with minimal delay instead of after_idle to prevent event queue saturation
                        self.gui.root.after(10,
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
    
    def _start_heartbeat_monitor(self):
        """Start GUI heartbeat monitor to detect event loop stalls"""
        def heartbeat_tick():
            try:
                current_time = time.time()
                elapsed = current_time - self.last_heartbeat
                
                # Detect stall if heartbeat delayed > 300ms (expected 200ms)
                if elapsed > 0.3:
                    self.heartbeat_stalls += 1
                    logging.warning(f"GUI heartbeat stall detected: {elapsed:.3f}s delay (stalls: {self.heartbeat_stalls})")
                
                self.heartbeat_count += 1
                self.last_heartbeat = current_time
                
                # Log heartbeat health every 30 seconds
                if self.heartbeat_count % 150 == 0:
                    logging.info(f"GUI heartbeat: {self.heartbeat_count} ticks, {self.heartbeat_stalls} stalls")
                
                # Schedule next heartbeat
                self.gui.root.after(self.heartbeat_interval, heartbeat_tick)
                
            except Exception as e:
                logging.error(f"Heartbeat monitor error: {e}")
                # Restart heartbeat even on error
                self.gui.root.after(self.heartbeat_interval, heartbeat_tick)
        
        # Start the heartbeat
        self.gui.root.after(self.heartbeat_interval, heartbeat_tick)
        logging.info("GUI heartbeat monitor started")

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
