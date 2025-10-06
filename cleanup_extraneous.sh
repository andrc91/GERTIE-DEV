#!/bin/bash
# Cleanup Script for camera_system_incremental
# Moves extraneous files to to_be_deleted directory

TARGET_DIR="/Users/andrew1/Desktop/to_be_deleted"
SOURCE_DIR="/Users/andrew1/Desktop/camera_system_incremental"

mkdir -p "$TARGET_DIR"

echo "=== CAMERA SYSTEM CLEANUP ==="
echo "Moving extraneous files to: $TARGET_DIR"
echo ""

MOVED=0
cd "$SOURCE_DIR"

# CATEGORY 1: Redundant Fix Documentation
echo "📄 Moving redundant fix documentation..."

files_to_move=(
    "AUTOMATION_COMPLETE.md"
    "CAPTURE_FAILURE_DIAGNOSIS.md"
    "COMPREHENSIVE_FIX_GUIDE.md"
    "COMPREHENSIVE_SETTINGS_FIX.md"
    "CRITICAL_FIXES_DEPLOYED.md"
    "CRITICAL_PATCHES.md"
    "DEFINITIVE_FIXES_SUMMARY.md"
    "DEPLOYMENT_SUMMARY.md"
    "DEPLOYMENT_WORKFLOW.md"
    "DEVICE_DETECTION_FIX.md"
    "DEVICE_NAMING_RESOLVED.md"
    "DIAGNOSIS_AND_FIXES.md"
    "DIAGNOSIS_POST_FIX.md"
    "ENHANCED_STILL_CAPTURE_FIXES.md"
    "ETHERNET_NETWORK_SOLUTION.md"
    "FINAL_AUTOMATION_REPORT.md"
    "FINAL_FIXES_COMPLETE.md"
    "FINAL_MINIMAL_FIXES.md"
    "FINAL_SOLUTION_SUMMARY.md"
    "FIXES_COMPLETED.md"
    "FIXES_README.md"
    "GUI_PREVIEW_DISCONNECT_FIXED.md"
    "GUI_PREVIEW_FLOW_FIXED.md"
    "ISSUE_RESOLVED_FINAL.md"
    "MINIMAL_FIXES_SUMMARY.md"
    "OFFLINE_DEVICE_DETECTION_FIX.md"
    "PORT_FIX_SOLUTION.md"
    "README_FINAL_SOLUTION.md"
    "RECOVERY_STATUS_SUMMARY.md"
    "SESSION_CONTINUITY.md"
    "SETTINGS_ISSUE_RESOLVED.md"
    "STILL_CAPTURE_EMERGENCY_FIX.md"
    "STILL_CAPTURE_FINAL_FIX.md"
    "PROGRESS_REPORT.md"
)

for file in "${files_to_move[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "$TARGET_DIR/"
        echo "  ✓ Moved: $file"
        ((MOVED++))
    fi
done

# CATEGORY 2: Deployment Scripts
echo ""
echo "🚀 Moving redundant deployment scripts..."

deploy_scripts=(
    "COMPLETE_DEPLOYMENT.sh"
    "DEPLOYMENT_GUIDE.sh"
    "apply_complete_fix.sh"
    "deploy_complete_fix.sh"
    "deploy_definitive_fixes.sh"
    "deploy_offline_fix.sh"
)

for file in "${deploy_scripts[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "$TARGET_DIR/"
        echo "  ✓ Moved: $file"
        ((MOVED++))
    fi
done

# CATEGORY 3: Diagnostic Scripts
echo ""
echo "🔧 Moving one-off diagnostic scripts..."

diagnostic_scripts=(
    "device_specific_diagnostic.py"
    "diagnose_capture_failure.sh"
    "diagnose_ports.sh"
    "diagnose_services_no_nc.sh"
    "diagnose_still_capture.sh"
    "emergency_diagnostic.py"
    "fix_brightness_settings.py"
    "fix_device_naming_final.py"
    "fix_resolution_settings.py"
    "master_diagnostic.sh"
    "master_diagnostic_comprehensive.py"
    "monitor_settings_access.sh"
    "quick_fix_capture.sh"
    "quick_settings_test.sh"
    "verify_comprehensive_fix.sh"
    "verify_definitive_fixes.sh"
    "verify_device_detection.sh"
    "verify_fixes.sh"
    "verify_offline_detection.sh"
    "verify_resolution_fix.py"
    "verify_transforms_production.py"
)

for file in "${diagnostic_scripts[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "$TARGET_DIR/"
        echo "  ✓ Moved: $file"
        ((MOVED++))
    fi
done

# CATEGORY 4: Test Scripts
echo ""
echo "🧪 Moving standalone test scripts..."

test_scripts=(
    "test_color_fix.py"
    "test_device_detection.py"
    "test_device_naming.py"
    "test_device_naming_comprehensive.py"
    "test_gui_to_preview_flow.py"
    "test_high_resolution.py"
    "test_local_camera.py"
    "test_manual_capture.sh"
    "test_rep8_video.py"
    "test_settings_creation.py"
    "test_simple_device_naming.py"
    "test_transform_coverage.py"
    "test_video_isolation.py"
    "debug_transforms.py"
)

for file in "${test_scripts[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "$TARGET_DIR/"
        echo "  ✓ Moved: $file"
        ((MOVED++))
    fi
done

# CATEGORY 5: Backup Files
echo ""
echo "💾 Moving backup files..."

for file in *.backup *.resolution_backup; do
    if [ -f "$file" ]; then
        mv "$file" "$TARGET_DIR/"
        echo "  ✓ Moved: $file"
        ((MOVED++))
    fi
done

# CATEGORY 6: Log Files
echo ""
echo "📊 Moving log and progress files..."

log_files=(
    "automated_upgrade.log"
    "automated_upgrade_log.json"
    "progress_timeline.json"
    "progress_tracker.json"
    "progress_tracker.py"
    "upgrade_log.txt"
    "upgrade_status_report.json"
    ".coverage"
)

for file in "${log_files[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "$TARGET_DIR/"
        echo "  ✓ Moved: $file"
        ((MOVED++))
    fi
done

# CATEGORY 7: Automation Scripts
echo ""
echo "⚙️  Moving automation scripts..."

automation_scripts=(
    "automated_incremental_upgrade.py"
    "checkpoint.sh"
    "restore.sh"
    "create_default_settings.py"
    "sync_settings.py"
    "sync_to_slaves.sh"
)

for file in "${automation_scripts[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "$TARGET_DIR/"
        echo "  ✓ Moved: $file"
        ((MOVED++))
    fi
done

# CATEGORY 8: Offline Services
echo ""
echo "🔌 Moving offline service files..."

offline_services=(
    "still_capture_offline.service"
    "video_stream_offline.service"
)

for file in "${offline_services[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "$TARGET_DIR/"
        echo "  ✓ Moved: $file"
        ((MOVED++))
    fi
done

echo ""
echo "================================"
echo "✅ Cleanup Complete!"
echo "   Files moved: $MOVED"
echo "   Location: $TARGET_DIR"
echo ""
echo "📋 Remaining Core Files:"
echo "   - README.md"
echo "   - COMPLETE_SYSTEM_GUIDE.md"
echo "   - DEVELOPMENT_WORKFLOW.md"
echo "   - requirements.txt, pytest.ini"
echo "   - Core dirs: master/, slave/, shared/, tests/, scripts/"
echo "   - Service files: *.service (standard)"
echo "   - Settings: rep*_settings.json"
echo "   - Tools: setup_pi.sh, deploy_fixes.sh, diagnostic_endtoend.sh, status.py"
echo ""
