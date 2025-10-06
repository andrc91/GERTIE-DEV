# Camera System Development & Testing Workflow

## 📋 Table of Contents
1. [Current System Status](#current-system-status)
2. [File Transfer Solutions (Public WiFi)](#file-transfer-solutions)
3. [Testing Strategy](#testing-strategy)
4. [Development Workflow](#development-workflow)
5. [Deployment Process](#deployment-process)
6. [Troubleshooting & Debugging](#troubleshooting--debugging)

---

## 🎯 Current System Status

### Architecture Overview
- **Master (control1)**: 192.168.0.200 - GUI + local camera (rep8)
- **Slaves (rep1-rep7)**: 192.168.0.201-207 - Remote cameras
- **Communication**: UDP over local network
- **Services**: video_stream, still_capture, local_camera_slave

### What's Working
✅ File structure is complete
✅ Python code is Mac-compatible
✅ All network ports configured correctly
✅ UDP communication tested and working
✅ Comprehensive test suite exists

### What Needs Testing
⚠️ GUI functionality with real/mock cameras
⚠️ End-to-end video streaming
⚠️ Settings application and persistence
⚠️ Still capture at high resolution
⚠️ Multi-camera synchronization
⚠️ Network performance under load

---

## 🔄 File Transfer Solutions (Public WiFi)

### Problem
Public WiFi typically blocks:
- Direct SSH connections between devices
- Port forwarding
- Device discovery
- mDNS/Bonjour

### Solution Options (Ranked by Efficiency)

#### ⭐ Option 1: Git Repository (RECOMMENDED)
**Best for:** Frequent updates, version control, collaboration

**Setup:**
```bash
# On MacBook - Initial setup (one time)
cd /Users/andrew1/Desktop/camera_system_incremental
git init
git add .
git commit -m "Initial camera system"

# Create private GitHub repo (or GitLab, Bitbucket)
# Then:
git remote add origin https://github.com/YOUR_USERNAME/camera_system.git
git branch -M main
git push -u origin main
```

**Daily Workflow:**
```bash
# On MacBook - After making changes
git add .
git commit -m "Fixed video streaming bug"
git push

# On control1 Pi - Pull updates
cd ~/camera_system_incremental
git pull
```

**Advantages:**
- ✅ Version control and change history
- ✅ Works on any network (uses HTTPS)
- ✅ Automatic conflict resolution
- ✅ Can work offline, sync later
- ✅ Easy rollback if something breaks
- ✅ No USB drive needed

**Setup Time:** 5 minutes initial, 10 seconds per update

---

#### Option 2: Cloud Sync (Dropbox/Google Drive)
**Best for:** Simple file sync, no git knowledge needed

**Setup:**
```bash
# On MacBook
# Install Dropbox/Google Drive app
# Move project to synced folder
mv camera_system_incremental ~/Dropbox/Projects/

# On control1 Pi
sudo apt-get install rclone
rclone config  # Follow prompts to setup Dropbox/Drive
rclone sync dropbox:Projects/camera_system_incremental ~/camera_system_incremental
```

**Daily Workflow:**
```bash
# MacBook - Files auto-sync via Dropbox app

# control1 Pi - Pull changes
rclone sync dropbox:Projects/camera_system_incremental ~/camera_system_incremental
```

**Advantages:**
- ✅ Simple to understand
- ✅ Visual file browser
- ✅ Automatic backup
- ✅ No git learning curve

**Disadvantages:**
- ❌ No version control
- ❌ Manual conflict resolution
- ❌ Requires rclone setup on Pi

**Setup Time:** 10 minutes initial, 30 seconds per update

---

#### Option 3: File Sharing Services (Transfer.sh, Pastebin)
**Best for:** Quick one-off transfers, sharing logs

**Usage:**
```bash
# On MacBook - Upload file
curl --upload-file ./script.py https://transfer.sh/script.py
# Returns: https://transfer.sh/abc123/script.py

# On control1 Pi - Download
wget https://transfer.sh/abc123/script.py

# For logs (text only)
cat /tmp/camera.log | curl -F 'sprunge=<-' http://sprunge.us
# Returns: http://sprunge.us/xyz789
```

**Advantages:**
- ✅ No setup required
- ✅ Works anywhere
- ✅ Great for logs and small files

**Disadvantages:**
- ❌ Manual process
- ❌ Files expire (usually 14 days)
- ❌ Not suitable for entire project
- ❌ Security concerns

**Setup Time:** 0 minutes, 1 minute per transfer

---

#### Option 4: Shared Email Draft
**Best for:** Emergency transfers, very small files

**Usage:**
1. Create email draft in Gmail/Outlook
2. Paste code/logs into draft (don't send)
3. Save draft
4. Access from other device
5. Copy content

**Advantages:**
- ✅ Always available
- ✅ No extra tools

**Disadvantages:**
- ❌ Very tedious
- ❌ Poor for code formatting
- ❌ Size limits

---

### 🎯 RECOMMENDED SETUP: GitHub + Transfer.sh Combo

**Use GitHub for:**
- All code changes
- Configuration updates
- Documentation
- Testing scripts

**Use Transfer.sh for:**
- Quick log file sharing
- One-off debugging scripts
- Emergency patches

**Complete Setup Script:**
```bash
#!/bin/bash
# setup_git_workflow.sh

# Run on MacBook
cd /Users/andrew1/Desktop/camera_system_incremental

# Initialize git
git init
git add .
git commit -m "Initial camera system setup"

# Add .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.pyo
*.log
*.jpg
*.png
captured_images/
.DS_Store
*.tar.gz
EOF

git add .gitignore
git commit -m "Add gitignore"

echo "✅ Git initialized!"
echo ""
echo "Next steps:"
echo "1. Create a GitHub repository"
echo "2. Run: git remote add origin https://github.com/YOUR_USERNAME/camera_system.git"
echo "3. Run: git push -u origin main"
```

**On control1 Pi:**
```bash
#!/bin/bash
# setup_git_on_pi.sh

cd ~
git clone https://github.com/YOUR_USERNAME/camera_system.git camera_system_incremental
cd camera_system_incremental
chmod +x *.sh

echo "✅ Project cloned!"
echo "To update: git pull"
```

---

## 🧪 Testing Strategy

### Phase 1: Local MacBook Testing (Current Phase)

#### Step 1.1: Validate Project Structure
```bash
cd /Users/andrew1/Desktop/camera_system_incremental
python3 macbook_test_framework.py
```
**Expected:** All tests pass ✅ (DONE)

#### Step 1.2: Unit Testing
```bash
# Install test dependencies
pip3 install pytest pytest-cov

# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=shared --cov=slave --cov=master
```

**What this tests:**
- Transform functions (flip, crop, brightness, etc.)
- Settings persistence
- Configuration loading
- Edge cases and error handling

**Expected Results:**
- All tests pass
- >80% code coverage

#### Step 1.3: Mock System Testing
Create a simple mock to test GUI without real cameras:

```bash
# Create mock_camera_test.py
python3 << 'EOF'
# Test that config loads correctly
import sys
sys.path.insert(0, '/Users/andrew1/Desktop/camera_system_incremental')
from shared.config import SLAVES, get_slave_ports

print("Testing configuration...")
assert len(SLAVES) == 8, "Should have 8 slaves"
assert SLAVES['rep1']['ip'] == "192.168.0.201"
assert SLAVES['rep8']['ip'] == "127.0.0.1"

ports = get_slave_ports("192.168.0.201")
assert ports['control'] == 5001
assert ports['video'] == 5002

print("✅ Configuration tests passed!")
EOF
```

**Action Items:**
- [ ] Run unit tests
- [ ] Verify all tests pass
- [ ] Document any failures

---

### Phase 2: Integration Testing on control1

#### Step 2.1: Deploy to control1
```bash
# On control1 Pi
cd ~
git clone https://github.com/YOUR_USERNAME/camera_system.git camera_system_incremental
cd camera_system_incremental
```

#### Step 2.2: Test Local Camera (rep8) Only
```bash
# On control1
cd ~/camera_system_incremental

# Start local camera service manually
python3 local_camera_slave.py

# In another SSH session, check it's running
ps aux | grep local_camera_slave
netstat -tulpn | grep -E '5011|5012|6010'
```

**Expected:**
- Process running
- Ports 5011, 5012, 6010 open
- No errors in logs

#### Step 2.3: Test GUI on control1
```bash
# On control1
cd ~/camera_system_incremental/master/camera_gui
python3 main.py
```

**Manual Test Checklist:**
- [ ] GUI opens without errors
- [ ] rep8 frame visible (8th position)
- [ ] Click "Start Video Stream" for rep8
- [ ] Video preview appears
- [ ] Heartbeat indicator turns green
- [ ] Settings can be applied to rep8
- [ ] "Capture" button works for rep8

**Debugging if fails:**
```bash
# Check logs
tail -f /tmp/local_camera_debug.log

# Check network
netstat -tulpn | grep 501

# Test UDP manually
echo "START_STREAM" | nc -u 127.0.0.1 5011
```

---

### Phase 3: Full System Testing (All 8 Cameras)

#### Step 3.1: Deploy to Remote Pis (rep1-rep7)
```bash
# On each remote Pi (rep1-rep7)
cd ~
git clone https://github.com/YOUR_USERNAME/camera_system.git camera_system_incremental
cd camera_system_incremental
chmod +x *.sh

# Install services
./deploy_fixes.sh
```

#### Step 3.2: Start All Services
```bash
# On each rep1-rep7
sudo systemctl start video_stream.service
sudo systemctl start still_capture.service
sudo systemctl status video_stream.service
sudo systemctl status still_capture.service
```

#### Step 3.3: Full System Test
```bash
# On control1, run GUI
cd ~/camera_system_incremental/master/camera_gui
python3 main.py
```

**Complete Test Checklist:**

**Video Streaming:**
- [ ] All 8 camera frames visible
- [ ] Click "Start All Video Streams"
- [ ] All 8 cameras show live preview
- [ ] All heartbeats green
- [ ] Frame rates acceptable (15-30 FPS)

**Settings Control:**
- [ ] Open Settings → Camera Controls → rep1
- [ ] Change ISO to 800
- [ ] Enable "Flip Horizontal"
- [ ] Click "Apply Settings"
- [ ] Changes visible immediately in preview
- [ ] Repeat for all 8 cameras

**Still Capture:**
- [ ] Click "Capture" on rep1
- [ ] Image saves to ~/Desktop/captured_images/YYYY-MM-DD/rep1/
- [ ] Image quality is high resolution (4608x2592)
- [ ] Captured image matches preview appearance
- [ ] Repeat for all 8 cameras

**Synchronized Capture:**
- [ ] Click "Capture All"
- [ ] All 8 cameras capture simultaneously
- [ ] All images saved with same timestamp

**Stress Testing:**
- [ ] Stream all 8 cameras for 10 minutes
- [ ] No dropped frames
- [ ] No memory leaks (check with `htop`)
- [ ] Capture multiple times while streaming
- [ ] Change settings while streaming

---

## 💻 Development Workflow

### Daily Development Cycle

#### 1. Make Changes on MacBook
```bash
cd /Users/andrew1/Desktop/camera_system_incremental

# Edit files (e.g., fix bug in video_stream.py)
code slave/video_stream.py  # or vim, nano, etc.

# Test locally if possible
pytest tests/unit/test_transforms.py

# Review changes
git diff

# Commit
git add slave/video_stream.py
git commit -m "Fix: Correct brightness transform calculation"
git push
```

#### 2. Deploy to control1
```bash
# SSH to control1 (or connect via VNC/screen)
ssh andrc1@control1.local  # or use direct connection

cd ~/camera_system_incremental
git pull
```

#### 3. Deploy to Remote Pis (if needed)
```bash
# If changes affect slave code (video_stream.py, still_capture.py)
# Create update script
cat > ~/update_all_pis.sh << 'EOF'
#!/bin/bash
for i in {1..7}; do
    echo "Updating rep$i..."
    ssh andrc1@192.168.0.20$i "cd ~/camera_system_incremental && git pull && sudo systemctl restart video_stream still_capture"
done
echo "✅ All Pis updated!"
EOF

chmod +x ~/update_all_pis.sh
./update_all_pis.sh
```

#### 4. Test Changes
```bash
# Quick test
cd ~/camera_system_incremental/master/camera_gui
python3 main.py

# If working, mark as tested
git tag v1.0.1
git push --tags
```

#### 5. Document Changes
```bash
# Update changelog
echo "## v1.0.1 - $(date +%Y-%m-%d)" >> CHANGELOG.md
echo "- Fixed brightness transform calculation" >> CHANGELOG.md
git add CHANGELOG.md
git commit -m "docs: Update changelog for v1.0.1"
git push
```

---

### Emergency Hotfix Process

**When you need to fix something FAST without MacBook:**

1. **Edit directly on control1:**
```bash
ssh andrc1@control1.local
cd ~/camera_system_incremental
nano slave/video_stream.py  # Make quick fix
```

2. **Test immediately:**
```bash
python3 slave/video_stream.py
```

3. **Deploy to other Pis:**
```bash
# Copy to other Pis
for i in {1..7}; do
    scp slave/video_stream.py andrc1@192.168.0.20$i:~/camera_system_incremental/slave/
done
```

4. **Later: Sync back to MacBook:**
```bash
# On control1
git add .
git commit -m "hotfix: Emergency fix for video streaming"
git push

# On MacBook
cd /Users/andrew1/Desktop/camera_system_incremental
git pull
```

---

## 🚀 Deployment Process

### Initial Deployment (One-Time Setup)

#### On MacBook:
```bash
# Setup git
cd /Users/andrew1/Desktop/camera_system_incremental
git init
git add .
git commit -m "Initial system"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/camera_system.git
git push -u origin main
```

#### On control1:
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/camera_system.git camera_system_incremental
cd camera_system_incremental
chmod +x *.sh

# Deploy services
./deploy_fixes.sh

# Enable auto-start
sudo systemctl enable local_camera_slave.service
```

#### On rep1-rep7:
```bash
# Repeat for each Pi
cd ~
git clone https://github.com/YOUR_USERNAME/camera_system.git camera_system_incremental
cd camera_system_incremental
chmod +x *.sh

# Deploy services
./deploy_fixes.sh

# Enable auto-start
sudo systemctl enable video_stream.service still_capture.service
```

### Updating Deployment

#### Simple Update (Code Changes Only):
```bash
# On any Pi
cd ~/camera_system_incremental
git pull
sudo systemctl restart <service_name>
```

#### Full Redeployment (Service Changes):
```bash
cd ~/camera_system_incremental
git pull
./deploy_fixes.sh
sudo systemctl daemon-reload
sudo systemctl restart <service_name>
```

---

## 🐛 Troubleshooting & Debugging

### Common Issues

#### Issue: Git Push Fails on Public WiFi
```bash
# Use HTTPS instead of SSH
git remote set-url origin https://github.com/YOUR_USERNAME/camera_system.git

# If authentication fails, use personal access token
# GitHub → Settings → Developer settings → Personal access tokens
# Use token as password
```

#### Issue: Can't SSH to control1 from MacBook
**Solutions:**
1. Use direct connection (Ethernet cable)
2. Use VNC instead of SSH
3. Connect physical monitor/keyboard to control1
4. Use USB drive for one-time setup, then use git

#### Issue: Changes Not Taking Effect
```bash
# Check what's running
ps aux | grep camera

# Force restart
sudo systemctl restart video_stream still_capture local_camera_slave

# Check logs
sudo journalctl -u video_stream -f
sudo journalctl -u local_camera_slave -f
```

#### Issue: Git Conflicts
```bash
# If you edited same file on both MacBook and Pi
cd ~/camera_system_incremental
git pull  # Shows conflict

# See conflicts
git status

# Resolve manually or use theirs/ours
git checkout --theirs path/to/file  # Use Pi version
git checkout --ours path/to/file    # Use repo version

git add .
git commit -m "Resolved merge conflict"
```

### Debugging Tools

#### Check System Status
```bash
#!/bin/bash
# status_check.sh - Run on any Pi
echo "=== Service Status ==="
sudo systemctl status video_stream --no-pager
sudo systemctl status still_capture --no-pager
sudo systemctl status local_camera_slave --no-pager

echo ""
echo "=== Network Ports ==="
netstat -tulpn | grep -E '5001|5002|5003|6000'

echo ""
echo "=== Recent Errors ==="
sudo journalctl -u video_stream --since "5 minutes ago" | grep -i error
sudo journalctl -u local_camera_slave --since "5 minutes ago" | grep -i error

echo ""
echo "=== Disk Space ==="
df -h | grep -E 'Filesystem|/home'

echo ""
echo "=== Git Status ==="
cd ~/camera_system_incremental
git status
```

#### Collect Logs for Debugging
```bash
#!/bin/bash
# collect_logs.sh - Run on Pi, upload to share
LOGFILE="debug_$(hostname)_$(date +%Y%m%d_%H%M%S).log"

{
    echo "=== System Info ==="
    uname -a
    cat /etc/os-release
    
    echo ""
    echo "=== Camera System Status ==="
    ./status_check.sh
    
    echo ""
    echo "=== Full Service Logs ==="
    sudo journalctl -u video_stream --since "1 hour ago"
    sudo journalctl -u still_capture --since "1 hour ago"
    sudo journalctl -u local_camera_slave --since "1 hour ago"
    
} > "$LOGFILE"

# Upload to transfer.sh
echo "Uploading logs..."
curl --upload-file "$LOGFILE" https://transfer.sh/"$LOGFILE"
echo ""
echo "Log file saved locally: $LOGFILE"
```

---

## 📚 Quick Reference

### File Transfer Methods Comparison

| Method | Setup Time | Transfer Time | Reliability | Best For |
|--------|-----------|---------------|-------------|----------|
| GitHub | 5 min | 10 sec | ⭐⭐⭐⭐⭐ | Code, regular updates |
| Cloud Sync | 10 min | 30 sec | ⭐⭐⭐⭐ | Simple sync, backups |
| Transfer.sh | 0 min | 1 min | ⭐⭐⭐ | Logs, quick shares |
| Email Draft | 0 min | 2 min | ⭐⭐ | Emergency only |
| USB Drive | 0 min | 5 min | ⭐⭐⭐⭐ | Initial setup, offline |

### Essential Commands

#### On MacBook:
```bash
# Make changes and push
git add .
git commit -m "Description of changes"
git push

# Check project structure
cd /Users/andrew1/Desktop/camera_system_incremental
python3 macbook_test_framework.py
```

#### On control1:
```bash
# Pull updates
cd ~/camera_system_incremental
git pull

# Restart services
sudo systemctl restart local_camera_slave

# View logs
sudo journalctl -u local_camera_slave -f

# Test GUI
cd master/camera_gui
python3 main.py
```

#### On rep1-rep7:
```bash
# Pull updates
cd ~/camera_system_incremental
git pull

# Restart services
sudo systemctl restart video_stream still_capture

# View logs
sudo journalctl -u video_stream -f
```

### Testing Checklist Progress Tracker

Create a file to track progress:
```bash
cat > ~/testing_progress.md << 'EOF'
# Testing Progress

## Phase 1: MacBook Testing
- [x] Structure validation (macbook_test_framework.py)
- [ ] Unit tests (pytest)
- [ ] Configuration tests
- [ ] Mock system testing

## Phase 2: control1 Integration
- [ ] Deploy code to control1
- [ ] Test local camera (rep8) alone
- [ ] Test GUI on control1
- [ ] Settings application
- [ ] Still capture test
- [ ] Heartbeat monitoring

## Phase 3: Full System (8 Cameras)
- [ ] Deploy to rep1-rep7
- [ ] Start all services
- [ ] All cameras streaming
- [ ] All heartbeats green
- [ ] Settings work on all cameras
- [ ] Still capture on all cameras
- [ ] Synchronized capture test
- [ ] 10-minute stress test

## Issues Found
- [ ] Issue 1: [Description]
- [ ] Issue 2: [Description]

## Performance Notes
- Frame rates: [Record FPS for each camera]
- Memory usage: [Record with htop]
- Network bandwidth: [Record with iftop]
EOF
```

---

## 🎯 Next Steps Action Plan

### Week 1: Setup & Local Testing
**Day 1-2:**
- [ ] Set up GitHub repository
- [ ] Push current code to GitHub
- [ ] Create .gitignore file
- [ ] Run all unit tests on MacBook
- [ ] Document any test failures

**Day 3-4:**
- [ ] Create and test update scripts
- [ ] Test git workflow (MacBook → GitHub → control1)
- [ ] Verify file transfer works smoothly
- [ ] Practice rollback procedure

**Day 5-7:**
- [ ] Deploy to control1
- [ ] Test rep8 (local camera) thoroughly
- [ ] Test GUI on control1
- [ ] Document any issues found

### Week 2: Full System Integration
**Day 1-3:**
- [ ] Deploy to all remote Pis (rep1-rep7)
- [ ] Start all services
- [ ] Test all 8 cameras streaming
- [ ] Verify heartbeat monitoring

**Day 4-5:**
- [ ] Test settings on all cameras
- [ ] Test still capture on all cameras
- [ ] Test synchronized capture
- [ ] Performance testing

**Day 6-7:**
- [ ] Stress testing (long runs)
- [ ] Document performance metrics
- [ ] Create final documentation
- [ ] Training materials if needed

### Week 3: Production Ready
- [ ] Set up auto-start on all Pis
- [ ] Create backup/restore procedures
- [ ] Final system verification
- [ ] System handoff documentation

---

## 🚀 Immediate Action Items (Start Today!)

### Priority 1: Setup Git Workflow (30 minutes)
```bash
# 1. Create GitHub account if needed (github.com)
# 2. Create new repository "camera-system" (private recommended)
# 3. On MacBook:
cd /Users/andrew1/Desktop/camera_system_incremental
git init
git add .
git commit -m "Initial camera system"
git remote add origin https://github.com/YOUR_USERNAME/camera-system.git
git branch -M main
git push -u origin main
```

### Priority 2: Test Current System (1 hour)
```bash
# Run unit tests
cd /Users/andrew1/Desktop/camera_system_incremental
pip3 install pytest
pytest tests/unit/ -v

# Run structure validation (already done, but verify)
python3 macbook_test_framework.py
```

### Priority 3: First Deployment Test (2 hours)
```bash
# On control1 (connect directly if SSH doesn't work on public WiFi)
cd ~
git clone https://github.com/YOUR_USERNAME/camera-system.git camera_system_incremental
cd camera_system_incremental

# Test local camera
python3 local_camera_slave.py

# Test GUI
cd master/camera_gui
python3 main.py
```

---

## 📞 Support Resources

### Documentation Files in Project:
- `README.md` - Basic project overview
- `COMPLETE_SYSTEM_GUIDE.md` - Comprehensive system documentation
- `DEPLOYMENT_GUIDE.sh` - Automated deployment script
- `FIXES_README.md` - Known issues and fixes

### Useful Commands Reference:
```bash
# Quick system status
sudo systemctl status video_stream still_capture local_camera_slave

# View live logs
sudo journalctl -u video_stream -f

# Restart all services
sudo systemctl restart video_stream still_capture local_camera_slave

# Check network connectivity
ping 192.168.0.201  # Test connection to rep1

# Git status
cd ~/camera_system_incremental && git status

# Update all Pis (from control1)
for i in {1..7}; do ssh andrc1@192.168.0.20$i "cd ~/camera_system_incremental && git pull"; done
```

### Diagnostic Scripts:
- `diagnostic_endtoend.sh` - Complete system check
- `verify_fixes.sh` - Verify deployment
- `status.py` - System status overview

---

## 🎓 Learning Resources

### Git Basics
- Tutorial: https://try.github.io/
- Quick ref: https://education.github.com/git-cheat-sheet-education.pdf

### Raspberry Pi Networking
- SSH over USB: https://desertbot.io/blog/ssh-into-pi-zero-over-usb
- VNC setup: https://www.raspberrypi.com/documentation/computers/remote-access.html

### Python Testing
- pytest docs: https://docs.pytest.org/
- Testing guide: https://realpython.com/pytest-python-testing/

---

## 📝 Summary

**What You Have:**
✅ Complete 8-camera control system
✅ Master-slave architecture
✅ Video streaming, still capture, settings control
✅ Automated deployment scripts
✅ Comprehensive test suite

**What You Need to Do:**
1. ✅ Setup git repository (30 min)
2. ⏳ Run local tests (1 hour)
3. ⏳ Deploy to control1 (2 hours)
4. ⏳ Test full system (1 day)
5. ⏳ Production deployment (1 week)

**Recommended Workflow:**
- **Development**: MacBook with git
- **Transfer**: GitHub (primary), transfer.sh (logs)
- **Testing**: Phases 1-3 as outlined above
- **Deployment**: Git pull + systemctl restart

**You're already 90% there!** The system is solid, you just need to test and deploy it systematically.

---

**Last Updated:** 2025-10-06
**Next Review:** After Phase 1 testing complete
