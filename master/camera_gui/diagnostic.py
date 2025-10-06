#!/usr/bin/env python3
"""
Diagnostic script for shutdown and video streaming issues
"""

import socket
import time
import logging
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from shared.config import get_slave_ports, SLAVES
    print("✅ Using shared config")
except ImportError:
    print("⚠️ Shared config not found, using fallback")
    SLAVES = {
        "rep1": {"ip": "192.168.0.201"},
        "rep2": {"ip": "192.168.0.202"},
        "rep3": {"ip": "192.168.0.203"},
        "rep4": {"ip": "192.168.0.204"},
        "rep5": {"ip": "192.168.0.205"},
        "rep6": {"ip": "192.168.0.206"},
        "rep7": {"ip": "192.168.0.207"},
        "rep8": {"ip": "127.0.0.1"},
    }
    
    def get_slave_ports(ip):
        if ip == "127.0.0.1":
            return {'control': 5011, 'video': 5012, 'still': 6010, 'heartbeat': 5013}
        else:
            return {'control': 5001, 'video': 5002, 'still': 6000, 'heartbeat': 5003}

def test_device_connectivity(ip, ports):
    """Test if device is reachable on control port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        sock.sendto(b"PING", (ip, ports['control']))
        sock.close()
        return True
    except Exception as e:
        return False

def send_shutdown_command(ip, ports):
    """Send shutdown command with multiple formats"""
    print(f"📡 Sending shutdown to {ip}:{ports['control']}")
    
    commands = ["sudo poweroff", "SHUTDOWN", "poweroff", "shutdown"]
    
    for command in commands:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5.0)
            sock.sendto(command.encode(), (ip, ports['control']))
            sock.close()
            print(f"  ✅ Sent: {command}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ❌ Failed {command}: {e}")

def send_video_start_command(ip, ports):
    """Send video start command"""
    print(f"📹 Starting video stream for {ip}")
    
    video_port = ports.get('video_control', ports['control'])
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3.0)
        sock.sendto(b"START_STREAM", (ip, video_port))
        sock.close()
        print(f"  ✅ START_STREAM sent to {ip}:{video_port}")
    except Exception as e:
        print(f"  ❌ Failed to start stream: {e}")

def diagnose_rep7_issue():
    """Specifically diagnose rep7 (.207) streaming issue"""
    print("\n🔍 DIAGNOSING REP7 (.207) VIDEO STREAMING ISSUE")
    print("=" * 60)
    
    ip = "192.168.0.207"
    ports = get_slave_ports(ip)
    
    print(f"📍 Device: rep7 ({ip})")
    print(f"🔌 Control Port: {ports['control']}")
    print(f"📹 Video Port: {ports.get('video', 'N/A')}")
    print(f"🎛️ Video Control Port: {ports.get('video_control', 'N/A')}")
    
    # Test connectivity
    print("\n🔗 Testing connectivity...")
    if test_device_connectivity(ip, ports):
        print("  ✅ Device appears reachable")
    else:
        print("  ❌ Device may not be reachable or responsive")
    
    # Try starting video stream
    print("\n📹 Attempting to start video stream...")
    send_video_start_command(ip, ports)
    
    # Check if we can listen for video frames
    print("\n👂 Listening for video frames (5 seconds)...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", 5002))  # Standard video port
        sock.settimeout(5.0)
        
        frames_received = 0
        start_time = time.time()
        
        while time.time() - start_time < 5:
            try:
                data, addr = sock.recvfrom(65536)
                if addr[0] == ip:
                    frames_received += 1
                    print(f"  📸 Frame {frames_received} received from {ip} ({len(data)} bytes)")
            except socket.timeout:
                break
        
        sock.close()
        
        if frames_received > 0:
            print(f"  ✅ Received {frames_received} frames from rep7")
        else:
            print(f"  ❌ No frames received from rep7")
            
    except Exception as e:
        print(f"  ❌ Error listening for frames: {e}")

def test_shutdown_all():
    """Test shutdown all functionality"""
    print("\n🔌 TESTING SHUTDOWN ALL FUNCTIONALITY")
    print("=" * 50)
    
    for name, slave_info in SLAVES.items():
        ip = slave_info["ip"]
        ports = get_slave_ports(ip)
        
        print(f"\n📱 Testing {name} ({ip})")
        
        # Test connectivity first
        if test_device_connectivity(ip, ports):
            print("  🟢 Device reachable")
            # Note: Not actually sending shutdown in test mode
            print(f"  📡 Would send shutdown to {ip}:{ports['control']}")
        else:
            print("  🔴 Device not reachable")

def main():
    """Main diagnostic function"""
    print("🔧 CAMERA SYSTEM DIAGNOSTICS")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--rep7":
            diagnose_rep7_issue()
        elif sys.argv[1] == "--shutdown":
            test_shutdown_all()
        elif sys.argv[1] == "--shutdown-real":
            print("⚠️ REAL SHUTDOWN TEST - This will actually shutdown devices!")
            response = input("Are you sure? Type 'YES' to continue: ")
            if response == "YES":
                for name, slave_info in SLAVES.items():
                    ip = slave_info["ip"]
                    ports = get_slave_ports(ip)
                    send_shutdown_command(ip, ports)
            else:
                print("Aborted.")
    else:
        print("Available options:")
        print("  --rep7           Diagnose rep7 video streaming")
        print("  --shutdown       Test shutdown connectivity (safe)")
        print("  --shutdown-real  Actually send shutdown commands (DANGER)")
        
        print("\n🎯 Quick device status check:")
        for name, slave_info in SLAVES.items():
            ip = slave_info["ip"]
            ports = get_slave_ports(ip)
            
            if test_device_connectivity(ip, ports):
                print(f"  🟢 {name} ({ip}) - Reachable")
            else:
                print(f"  🔴 {name} ({ip}) - Not reachable")

if __name__ == "__main__":
    main()
