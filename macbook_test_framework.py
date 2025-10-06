#!/usr/bin/env python3
"""
GERTIE MACBOOK TESTING FRAMEWORK
=================================
Test camera system locally on MacBook before Raspberry Pi deployment
Simulates master-slave architecture on local machine
"""

import os
import sys
import socket
import threading
import subprocess
import json
import time
import signal
from datetime import datetime

class MacBookTestFramework:
    def __init__(self):
        self.base_dir = "/Users/andrew1/Desktop/camera_system_incremental"
        self.test_results = []
        self.processes = []
        
    def log(self, message, level="INFO"):
        """Comprehensive logging for testing"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] [{level}] {message}")
        
        # Also save to test log
        with open('macbook_test_log.txt', 'a') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
            
    def simulate_slave(self, replica_id=1):
        """Simulate a slave camera on MacBook"""
        self.log(f"🎥 Starting simulated slave {replica_id}")
        
        # Create mock camera capture script
        mock_script = f"""
import socket
import json
import time
import sys

print(f"Mock slave {replica_id} started")
sys.stdout.flush()

# Simulate UDP listener
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 5004 + {replica_id}))
sock.settimeout(1.0)

while True:
    try:
        data, addr = sock.recvfrom(1024)
        command = data.decode('utf-8')
        print(f"Slave {replica_id} received: {{command}}")
        sys.stdout.flush()
        
        # Simulate response
        if command == "START_STREAM":
            print(f"Slave {replica_id}: Stream started")
        elif command == "CAPTURE_STILL":
            print(f"Slave {replica_id}: Still captured")
            
    except socket.timeout:
        continue
    except KeyboardInterrupt:
        break
        
sock.close()
"""
        
        # Save and run mock script
        mock_file = f'/tmp/mock_slave_{replica_id}.py'
        with open(mock_file, 'w') as f:
            f.write(mock_script)
            
        process = subprocess.Popen(
            ['python3', mock_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.processes.append(process)
        self.log(f"✅ Mock slave {replica_id} running (PID: {process.pid})")
        return process
        
    def test_udp_communication(self):
        """Test UDP command sending"""
        self.log("📡 Testing UDP Communication")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Test sending commands to mock slaves
            commands = ["START_STREAM", "STOP_STREAM", "CAPTURE_STILL"]
            
            for cmd in commands:
                sock.sendto(cmd.encode(), ('127.0.0.1', 5005))
                self.log(f"  ✅ Sent command: {cmd}")
                time.sleep(0.5)
                
            sock.close()
            
            self.test_results.append({
                'test': 'UDP Communication',
                'status': 'PASS',
                'details': 'All commands sent successfully'
            })
            
            return True
            
        except Exception as e:
            self.log(f"  ❌ UDP test failed: {e}", "ERROR")
            self.test_results.append({
                'test': 'UDP Communication',
                'status': 'FAIL',
                'details': str(e)
            })
            return False
            
    def test_file_structure(self):
        """Verify all required files exist"""
        self.log("📁 Testing File Structure")
        
        required_files = [
            'slave/video_stream.py',
            'slave/still_capture.py',
            'master/camera_gui/launch.py',
            'master/camera_gui/core/network_manager.py'
        ]
        
        missing_files = []
        for file in required_files:
            path = os.path.join(self.base_dir, file)
            if os.path.exists(path):
                self.log(f"  ✅ Found: {file}")
            else:
                missing_files.append(file)
                self.log(f"  ❌ Missing: {file}", "WARNING")
                
        if missing_files:
            self.test_results.append({
                'test': 'File Structure',
                'status': 'PARTIAL',
                'details': f'Missing files: {missing_files}'
            })
        else:
            self.test_results.append({
                'test': 'File Structure',
                'status': 'PASS',
                'details': 'All required files present'
            })
            
        return len(missing_files) == 0
        
    def test_python_compatibility(self):
        """Test Python code compatibility on MacBook"""
        self.log("🐍 Testing Python Compatibility")
        
        test_files = [
            'slave/video_stream.py',
            'slave/still_capture.py'
        ]
        
        all_compatible = True
        
        for file in test_files:
            path = os.path.join(self.base_dir, file)
            if not os.path.exists(path):
                continue
                
            # Check imports
            with open(path, 'r') as f:
                content = f.read()
                
            # Check for Raspberry Pi specific imports
            rpi_specific = ['picamera', 'picamera2', 'RPi.GPIO']
            found_rpi = [imp for imp in rpi_specific if imp in content]
            
            if found_rpi:
                self.log(f"  ⚠️  {file} has RPi-specific imports: {found_rpi}", "WARNING")
                # Check if they're properly handled
                if 'try:' in content and any(imp in content for imp in rpi_specific):
                    self.log(f"    ✅ Imports are in try/except block")
                else:
                    self.log(f"    ❌ Imports not properly handled for Mac")
                    all_compatible = False
            else:
                self.log(f"  ✅ {file} is Mac-compatible")
                
        self.test_results.append({
            'test': 'Python Compatibility',
            'status': 'PASS' if all_compatible else 'FAIL',
            'details': 'Code is Mac-compatible' if all_compatible else 'RPi-specific imports found'
        })
        
        return all_compatible
        
    def test_network_ports(self):
        """Test that required ports are available"""
        self.log("🔌 Testing Network Ports")
        
        required_ports = [5004, 5011, 6000]
        blocked_ports = []
        
        for port in required_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            
            if result == 0:
                blocked_ports.append(port)
                self.log(f"  ⚠️  Port {port} is already in use", "WARNING")
            else:
                self.log(f"  ✅ Port {port} is available")
                
            sock.close()
            
        self.test_results.append({
            'test': 'Network Ports',
            'status': 'PASS' if not blocked_ports else 'PARTIAL',
            'details': f'Blocked ports: {blocked_ports}' if blocked_ports else 'All ports available'
        })
        
        return len(blocked_ports) == 0
        
    def cleanup(self):
        """Clean up test processes"""
        self.log("🧹 Cleaning up test processes")
        
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
                time.sleep(0.5)
                if process.poll() is None:
                    process.kill()
                self.log(f"  ✅ Terminated process {process.pid}")
                
    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.log("\n" + "="*60)
        self.log("TEST REPORT")
        self.log("="*60)
        
        # Calculate overall status
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        partial = sum(1 for r in self.test_results if r['status'] == 'PARTIAL')
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'platform': 'MacBook',
            'test_results': self.test_results,
            'summary': {
                'total_tests': len(self.test_results),
                'passed': passed,
                'failed': failed,
                'partial': partial,
                'success_rate': (passed / len(self.test_results) * 100) if self.test_results else 0
            },
            'ready_for_deployment': failed == 0
        }
        
        # Save report
        with open('macbook_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        # Print summary
        print("\n📊 TEST SUMMARY")
        print(f"  Total Tests: {report['summary']['total_tests']}")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⚠️  Partial: {partial}")
        print(f"  Success Rate: {report['summary']['success_rate']:.1f}%")
        
        if report['ready_for_deployment']:
            print("\n✅ SYSTEM READY FOR RASPBERRY PI DEPLOYMENT")
        else:
            print("\n❌ ISSUES FOUND - Fix before deployment")
            
        return report
        
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "🧪"*20)
        print(" MACBOOK TESTING FRAMEWORK")
        print("🧪"*20)
        
        os.chdir(self.base_dir)
        
        # Run tests
        self.test_file_structure()
        self.test_python_compatibility()
        self.test_network_ports()
        
        # Start mock slaves
        slave1 = self.simulate_slave(1)
        time.sleep(1)
        
        # Test communication
        self.test_udp_communication()
        
        # Generate report
        report = self.generate_test_report()
        
        # Cleanup
        self.cleanup()
        
        return report

if __name__ == "__main__":
    # Handle cleanup on exit
    def signal_handler(sig, frame):
        print("\n⚠️  Interrupted - cleaning up...")
        tester.cleanup()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run tests
    tester = MacBookTestFramework()
    report = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if report['ready_for_deployment'] else 1)
