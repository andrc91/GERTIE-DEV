#!/bin/bash
echo "=== GERTIE System Test ==="
echo ""
echo "1. Checking Python syntax..."
error_count=0
for file in slave/video_stream.py slave/still_capture.py; do
    python3 -m py_compile "$file" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "  ✅ $file: Syntax OK"
    else
        echo "  ❌ $file: Syntax errors"
        ((error_count++))
    fi
done

echo ""
echo "2. Checking critical functions..."
if grep -q "def handle_video_commands" slave/video_stream.py; then
    echo "  ✅ UDP handler present"
else
    echo "  ❌ UDP handler missing"
    ((error_count++))
fi

echo ""
echo "3. Checking ports..."
if grep -q "6000" slave/still_capture.py; then
    echo "  ✅ Still port correct (6000)"
else
    echo "  ❌ Still port wrong"
    ((error_count++))
fi

echo ""
echo "4. Checking AUTO_START_STREAMS..."
if grep -q "AUTO_START_STREAMS = True" master/camera_gui/config/settings.py 2>/dev/null; then
    echo "  ✅ AUTO_START_STREAMS enabled"
else
    echo "  ⚠️  AUTO_START_STREAMS not found or disabled"
fi

echo ""
if [ $error_count -eq 0 ]; then
    echo "✅ ALL TESTS PASSED"
    exit 0
else
    echo "❌ $error_count TEST(S) FAILED"
    exit 1
fi
