#!/usr/bin/env python3
"""
GERTIE Automated Troubleshooting System
Timeout-resistant diagnostic and repair tool
Run with: python3 gertie_troubleshoot.py "error description" "optional log data"
"""

import sys
import os
import re
import json
import subprocess
import difflib
from pathlib import Path
from datetime import datetime

class GERTIETroubleshooter:
    def __init__(self):
        self.base_path = Path("/Users/andrew1/Desktop/camera_system_integrated_final")
        self.original_path = Path("/Users/andrew1/Desktop/original working/camera_system_integrated_final copy")
        self.progress_log = self.base_path / "upgrade_tracker/test_progress_log.txt"
        self.desktop_log = self.base_path / "upgrade_tracker/desktop_patch_log.txt"
        
        # Known issues and their fixes
        self.known_issues = {
            "port 6000 not listening": self.fix_port_binding,
            "no video preview": self.fix_video_preview,
            "still capture failed": self.fix_still_capture,
            "syntax error": self.fix_syntax_error,
            "import error": self.fix_import_error,
            "camera initialization": self.fix_camera_init,
            "no frames received": self.fix_frame_reception
        }
        
        self.critical_files = {
            "video": "slave/video_stream.py",
            "still": "slave/still_capture.py",
            "network": "master/camera_gui/core/network_manager.py",
            "config": "shared/config.py",
            "settings": "master/camera_gui/config/settings.py"
        }
        
        self.phase_number = self.get_next_phase()
        self.fixes_applied = []
        self.findings = []
        
    def get_next_phase(self):
        """Get next phase number from desktop log"""
        if not self.desktop_log.exists():
            return 1
        
        with open(self.desktop_log, 'r') as f:
            content = f.read()
        
        phases = re.findall(r'Phase (\d+)', content)
        if phases:
            return int(phases[-1]) + 1
        return 1
    
    def diagnose(self, error_description, log_data=""):
        """Main diagnostic entry point"""
        print("=" * 80)
        print(f"GERTIE AUTOMATED TROUBLESHOOTING - Phase {self.phase_number:03d}")
        print("=" * 80)
        print(f"Timestamp: {datetime.now()}")
        print(f"Error: {error_description[:100]}...")
        print("")
        
        # Analyze error
        issue_type = self.identify_issue_type(error_description, log_data)
        print(f"🔍 Identified Issue Type: {issue_type}")
        
        # Run appropriate fix
        if issue_type in self.known_issues:
            print(f"🔧 Applying known fix for: {issue_type}")
            self.known_issues[issue_type](error_description, log_data)
        else:
            print("🔍 Running comprehensive diagnosis...")
            self.comprehensive_diagnosis(error_description, log_data)
        
        # Update logs
        self.update_logs()
        
        # Generate report
        self.generate_report()
        
    def identify_issue_type(self, error_description, log_data):
        """Identify the type of issue from error description and logs"""
        combined = (error_description + " " + log_data).lower()
        
        # Check for known patterns
        patterns = {
            "port 6000 not listening": r"port 6000.*not listening|6000.*not bound",
            "no video preview": r"video.*not.*display|preview.*not.*showing|no.*frames",
            "still capture failed": r"still.*capture.*fail|capture.*error",
            "syntax error": r"syntaxerror|invalid syntax|expected.*block",
            "import error": r"importerror|modulenotfounderror|no module named",
            "camera initialization": r"picamera2.*fail|camera.*not.*found|camera.*error",
            "no frames received": r"no.*frame.*received|frame.*not.*arriving"
        }
        
        for issue_type, pattern in patterns.items():
            if re.search(pattern, combined):
                return issue_type
        
        return "unknown"
    
    def fix_port_binding(self, error_description, log_data):
        """Fix port binding issue (5001 vs 6000)"""
        print("\n📌 Fixing Port Binding Issue")
        
        still_capture = self.base_path / self.critical_files["still"]
        
        with open(still_capture, 'r') as f:
            content = f.read()
        
        # Check current binding
        if "control_port = ports['control']" in content:
            print("  ❌ Found incorrect port binding (control_port)")
            
            # Fix it
            content = content.replace(
                "control_port = ports['control']",
                "still_port = ports['still']"
            )
            content = content.replace(
                'bind(("0.0.0.0", control_port))',
                'bind(("0.0.0.0", still_port))'
            )
            content = content.replace(
                'Listening for commands on port {control_port}',
                'Listening for STILL commands on port {still_port}'
            )
            
            with open(still_capture, 'w') as f:
                f.write(content)
            
            print("  ✅ Fixed port binding (now using port 6000)")
            self.fixes_applied.append("Port binding: 5001 → 6000")
            self.findings.append("still_capture binding to wrong port")
        else:
            print("  ✅ Port binding already correct")
    
    def fix_video_preview(self, error_description, log_data):
        """Fix video preview issues"""
        print("\n📌 Fixing Video Preview Issue")
        
        # Check AUTO_START_STREAMS
        settings_file = self.base_path / self.critical_files["settings"]
        
        with open(settings_file, 'r') as f:
            content = f.read()
        
        if "'AUTO_START_STREAMS': False" in content:
            print("  ❌ AUTO_START_STREAMS is disabled")
            
            content = content.replace(
                "'AUTO_START_STREAMS': False",
                "'AUTO_START_STREAMS': True"
            )
            
            with open(settings_file, 'w') as f:
                f.write(content)
            
            print("  ✅ Enabled AUTO_START_STREAMS")
            self.fixes_applied.append("Enabled AUTO_START_STREAMS")
            self.findings.append("Auto-start was disabled")
        
        # Add debug logging to video_stream.py
        self.add_video_debug_logging()
    
    def add_video_debug_logging(self):
        """Add debug logging to video streaming"""
        video_stream = self.base_path / self.critical_files["video"]
        
        with open(video_stream, 'r') as f:
            content = f.read()
        
        # Add logging for START_STREAM
        if 'logging.info(f"[VIDEO] START_STREAM received' not in content:
            content = re.sub(
                r'if command == "START_STREAM":',
                'if command == "START_STREAM":\n                logging.info(f"[VIDEO] START_STREAM received for {device_name}")',
                content
            )
            
            with open(video_stream, 'w') as f:
                f.write(content)
            
            print("  ✅ Added debug logging to video_stream.py")
            self.fixes_applied.append("Added video debug logging")
    
    def fix_syntax_error(self, error_description, log_data):
        """Fix Python syntax errors"""
        print("\n📌 Fixing Syntax Errors")
        
        # Extract filename from error
        match = re.search(r'File "([^"]+)"', log_data)
        if match:
            error_file = match.group(1)
            if "camera_system_integrated_final" in error_file:
                rel_path = error_file.split("camera_system_integrated_final/")[-1]
                print(f"  🔍 Syntax error in: {rel_path}")
                
                # Check syntax
                result = subprocess.run(
                    f"python3 -m py_compile {self.base_path / rel_path}",
                    shell=True, capture_output=True, text=True
                )
                
                if result.returncode != 0:
                    print(f"  ❌ Syntax error confirmed")
                    print(f"  Error: {result.stderr[:200]}")
                    
                    # Common fixes
                    if "expected 'except' or 'finally'" in result.stderr:
                        self.fix_try_except_structure(rel_path)
                    else:
                        print("  ⚠️ Manual fix required")
                        self.findings.append(f"Syntax error in {rel_path}: {result.stderr[:100]}")
    
    def fix_try_except_structure(self, file_path):
        """Fix try/except/finally structure"""
        full_path = self.base_path / file_path
        
        print(f"  🔧 Fixing try/except structure in {file_path}")
        
        with open(full_path, 'r') as f:
            lines = f.readlines()
        
        # This would need more sophisticated parsing for a general fix
        # For now, log it for manual review
        self.findings.append(f"Try/except structure issue in {file_path}")
        print("  ⚠️ Complex syntax fix needed - review manually")
    
    def comprehensive_diagnosis(self, error_description, log_data):
        """Run comprehensive diagnosis when issue type is unknown"""
        print("\n📋 Running Comprehensive Diagnosis")
        
        # Compare critical files with original
        for name, file_path in self.critical_files.items():
            self.compare_with_original(file_path)
        
        # Check all port configurations
        self.check_port_configurations()
        
        # Check service configurations
        self.check_service_configs()
    
    def compare_with_original(self, file_path):
        """Compare a file with the original working version"""
        current = self.base_path / file_path
        original = self.original_path / file_path
        
        if not current.exists() or not original.exists():
            return
        
        with open(current, 'r') as f:
            current_lines = f.readlines()
        with open(original, 'r') as f:
            original_lines = f.readlines()
        
        differ = difflib.unified_diff(
            original_lines, current_lines,
            fromfile=f"original/{file_path}",
            tofile=f"current/{file_path}",
            lineterm='', n=1
        )
        
        differences = list(differ)
        if len(differences) > 10:  # Significant differences
            self.findings.append(f"{file_path}: {len(differences)} lines differ from original")
    
    def check_port_configurations(self):
        """Check all port configurations"""
        print("\n🔌 Checking Port Configurations")
        
        config_file = self.base_path / self.critical_files["config"]
        with open(config_file, 'r') as f:
            content = f.read()
        
        expected_ports = {
            "VIDEO_PORT = 5002": "Video streaming",
            "STILL_PORT = 6000": "Still capture",
            "CONTROL_PORT = 5001": "Control commands",
            "VIDEO_CONTROL_PORT = 5004": "Video control"
        }
        
        for port_def, description in expected_ports.items():
            if port_def in content:
                print(f"  ✅ {description}: {port_def}")
            else:
                print(f"  ❌ {description}: Not found or incorrect")
                self.findings.append(f"Port configuration issue: {description}")
    
    def update_logs(self):
        """Update tracking logs"""
        # Update test_progress_log.txt
        with open(self.progress_log, 'a') as f:
            timestamp = datetime.now(datetime.UTC).isoformat()
            
            # ACTION entry
            fixes = ";".join(self.fixes_applied) if self.fixes_applied else "diagnosis_only"
            f.write(f"ACTION|TS:{timestamp}|PH:{self.phase_number:03d}|M:automated_troubleshoot|A:fix|T:multiple|L:0|R:ok|Msg:{fixes}\n")
            
            # DISCOVERY entry
            findings = ";".join(self.findings) if self.findings else "no_issues_found"
            f.write(f"DISCOVERY|TS:{timestamp}|M:automated_troubleshoot|Findings:{findings}|Understanding:automated_diagnosis|State:{{\"phase\":\"{self.phase_number:03d}\"}}\n")
        
        # Update desktop_patch_log.txt
        with open(self.desktop_log, 'a') as f:
            f.write(f"\n=== Phase {self.phase_number:03d} Automated Troubleshooting ===\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"Fixes Applied: {', '.join(self.fixes_applied) if self.fixes_applied else 'None'}\n")
            f.write(f"Findings: {', '.join(self.findings) if self.findings else 'None'}\n")
            f.write("Status: Complete\n")
    
    def generate_report(self):
        """Generate troubleshooting report"""
        report = f"""
================================================================================
GERTIE TROUBLESHOOTING REPORT - Phase {self.phase_number:03d}
================================================================================

Timestamp: {datetime.now()}

FIXES APPLIED:
{chr(10).join(f"  ✅ {fix}" for fix in self.fixes_applied) if self.fixes_applied else "  None"}

FINDINGS:
{chr(10).join(f"  🔍 {finding}" for finding in self.findings) if self.findings else "  None"}

DEPLOYMENT INSTRUCTIONS:
1. Copy to USB:
   cp -r {self.base_path} /Volumes/USB/

2. On control1:
   cp -r /media/USB/camera_system_integrated_final /home/andrc1/
   cd /home/andrc1/camera_system_integrated_final
   ./sync_to_slaves.sh

3. Verify:
   ./deploy_and_test.sh

VERIFICATION COMMANDS:
{self.get_verification_commands()}

================================================================================
"""
        print(report)
        
        # Save report
        report_file = self.base_path / f"troubleshoot_report_phase_{self.phase_number:03d}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"Report saved to: {report_file}")
    
    def get_verification_commands(self):
        """Get verification commands based on fixes applied"""
        commands = []
        
        if any("port" in fix.lower() for fix in self.fixes_applied):
            commands.append("# Check port 6000:")
            commands.append("for i in {1..7}; do ssh andrc1@192.168.0.20$i 'netstat -uln | grep 6000'; done")
        
        if any("video" in fix.lower() for fix in self.fixes_applied):
            commands.append("# Test video streaming:")
            commands.append("timeout 3 nc -l -u 5002 | head -c 100 | xxd")
        
        if any("syntax" in fix.lower() for fix in self.fixes_applied):
            commands.append("# Check Python syntax:")
            commands.append("python3 -m py_compile slave/*.py")
        
        return "\n".join(commands) if commands else "# No specific verification needed"

def main():
    """Main entry point"""
    troubleshooter = GERTIETroubleshooter()
    
    if len(sys.argv) > 1:
        error_description = sys.argv[1]
        log_data = sys.argv[2] if len(sys.argv) > 2 else ""
    else:
        print("Usage: python3 gertie_troubleshoot.py \"error description\" [\"log data\"]")
        print("\nEnter error description (or 'test' for test mode):")
        error_description = input("> ").strip()
        
        if error_description == "test":
            error_description = "Video previews not displaying"
            log_data = "Port 6000 not listening"
        else:
            print("\nEnter relevant log data (optional, press Enter to skip):")
            log_data = input("> ").strip()
    
    troubleshooter.diagnose(error_description, log_data)

if __name__ == "__main__":
    main()
