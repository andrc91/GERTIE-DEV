# Integrated Raspberry Pi Camera Control System

This system enables a **central master GUI** to control multiple Raspberry Pi slave devices over UDP. Each slave can:
- Stream video in real-time
- Capture high-resolution still images
- Respond to start, stop, capture, shutdown, and reboot commands

---

## 📁 Project Structure

```
camera_system_integrated/
├── master/
│   ├── __main__.py         # Master GUI launcher
│   └── gui.py              # GUI logic for stream and control
│
├── slave/
│   ├── __main__.py         # Slave command listener
│   ├── video_stream.py     # Video streaming logic
│   ├── still_capture.py    # High-res capture logic
│   └── command_handler.py  # Command dispatching logic
│
├── shared/
│   ├── config.py           # Shared ports, IPs, slave list
│   └── logger.py           # Logging config
```

---

## 🛠️ Installation

### Prerequisites

On each Raspberry Pi:
```bash
sudo apt update
sudo apt install -y python3-opencv python3-picamera2 libcamera-apps
```

---

## 🚀 Running the System

### On the Master (GUI Host)
```bash
cd camera_system_integrated/master
python3 -m master
```

### On a Slave (Camera Pi)
```bash
cd camera_system_integrated/slave
python3 -m slave
```

---

## ⚙️ Auto-Start Setup (Optional)

Use the provided systemd services to start on boot.

```bash
sudo cp camera_master.service /etc/systemd/system/
sudo cp camera_slave.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable either:
sudo systemctl enable --now camera_master.service
# or
sudo systemctl enable --now camera_slave.service
```

---

## 🧪 Test Command

In Python:
```python
from master.gui import MasterVideoGUI
gui = MasterVideoGUI(tk.Tk())
gui.send_command("192.168.0.50", "capture")
```

---

## 📄 License

MIT