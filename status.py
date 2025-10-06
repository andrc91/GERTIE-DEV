#!/usr/bin/env python3
"""
Quick status viewer for GERTIE upgrade progress
"""

import json
import os
from pathlib import Path
from datetime import datetime

def get_status():
    base_dir = Path("/Users/andrew1/Desktop/camera_system_incremental")
    
    # Load progress tracker data
    progress_file = base_dir / "progress_tracker.json"
    if progress_file.exists():
        with open(progress_file, 'r') as f:
            progress_data = json.load(f)
    else:
        progress_data = None
        
    # Load automated upgrade log
    upgrade_log = base_dir / "automated_upgrade_log.json"
    if upgrade_log.exists():
        with open(upgrade_log, 'r') as f:
            upgrade_data = json.load(f)
    else:
        upgrade_data = None
        
    # Load test report
    test_report = base_dir / "macbook_test_report.json"
    if test_report.exists():
        with open(test_report, 'r') as f:
            test_data = json.load(f)
    else:
        test_data = None
        
    # Display status
    print("\n" + "🚀 "*20)
    print(" "*20 + "GERTIE QUICK STATUS")
    print("🚀 "*20)
    
    # Progress Overview
    if progress_data:
        metrics = progress_data.get('metrics', {})
        print(f"\n📊 PROGRESS: {metrics.get('completion_percentage', 0):.1f}% ({metrics.get('completed', 0)}/{metrics.get('total_phases', 18)} phases)")
        print(f"🎯 Confidence: {metrics.get('confidence_score', 0)}%")
        
        # Visual bar
        completed = metrics.get('completed', 0)
        total = metrics.get('total_phases', 18)
        bar_length = 40
        filled = int(bar_length * completed / total)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"   [{bar}]")
        
    # System Status
    if upgrade_data:
        system_status = upgrade_data.get('system_status', {})
        print("\n✅ SYSTEM CHECKS:")
        print(f"   • Syntax: {system_status.get('video_stream_syntax', 'Unknown')}")
        print(f"   • UDP Handler: {'✓' if system_status.get('has_udp_handler') else '✗'}")
        print(f"   • Port 6000: {'✓' if system_status.get('port_6000') else '✗'}")
        print(f"   • No Duplicates: {'✓' if not system_status.get('duplicate_functions') else '✗'}")
        
    # Test Results
    if test_data:
        summary = test_data.get('summary', {})
        print("\n🧪 TEST RESULTS:")
        print(f"   • Success Rate: {summary.get('success_rate', 0):.1f}%")
        print(f"   • Passed: {summary.get('passed', 0)}")
        print(f"   • Failed: {summary.get('failed', 0)}")
        print(f"   • Ready for Deploy: {'YES' if test_data.get('ready_for_deployment') else 'NO'}")
        
    # Checkpoints
    checkpoint_dir = base_dir / '.checkpoints'
    if checkpoint_dir.exists():
        checkpoints = sorted([f.name for f in checkpoint_dir.glob('*.tar.gz')])
        print(f"\n💾 CHECKPOINTS: {len(checkpoints)} available")
        if checkpoints:
            print(f"   Latest: {checkpoints[-1]}")
            
    # Next Phase
    if progress_data:
        phase_status = progress_data.get('phase_status', {})
        next_phase = None
        for phase_num in range(1, 19):
            if phase_status.get(str(phase_num)) == 'PENDING':
                next_phase = phase_num
                break
                
        if next_phase:
            print(f"\n➡️  NEXT: Phase {next_phase:02d}")
            
    # Last Update
    if progress_data:
        last_updated = progress_data.get('last_updated', '')
        if last_updated:
            try:
                dt = datetime.fromisoformat(last_updated)
                print(f"\n🕐 Last Updated: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                pass
                
    print("\n" + "="*60)
    print("Use 'python3 progress_tracker.py' for detailed view")
    print("="*60 + "\n")

if __name__ == "__main__":
    get_status()
