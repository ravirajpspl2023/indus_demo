# SERVO_VFD Systemd Service Setup Guide

This guide provides complete instructions for setting up your SERVO_VFD project as a systemd service with automatic restart on Raspberry Pi.

## 🗂️ Files You Need

Keep these essential files:
- `servo-vfd.service` - Systemd service configuration
- `service_manager.sh` - Service management utility
- `pre_service_test.py` - Pre-startup testing script

## 🚀 Quick Setup Instructions

### 1. Copy Files to Raspberry Pi

```bash
# Transfer files to your Raspberry Pi
scp servo-vfd.service service_manager.sh pre_service_test.py humac@raspberry-ip:/home/humac/SERVO_VFD/
```

### 2. Manual Service Setup (Recommended)

```bash
# SSH into your Raspberry Pi
ssh humac@raspberry-ip

# Navigate to project directory
cd /home/humac/SERVO_VFD

# Make scripts executable
chmod +x service_manager.sh pre_service_test.py

# Create necessary directories
mkdir -p logs module/config

# Copy service file to systemd
sudo cp servo-vfd.service /etc/systemd/system/

# Set proper permissions
sudo chmod 644 /etc/systemd/system/servo-vfd.service

# Ensure user is in dialout group for serial access
sudo usermod -a -G dialout humac

# Set up udev rules for consistent device naming
sudo tee /etc/udev/rules.d/99-servo-usb.rules > /dev/null << 'EOF'
SUBSYSTEM=="tty", KERNELS=="1-1.1", SYMLINK+="servoX", GROUP="dialout", MODE="0666"
SUBSYSTEM=="tty", KERNELS=="1-1.2", SYMLINK+="servoY", GROUP="dialout", MODE="0666"
SUBSYSTEM=="tty", KERNELS=="1-1.3", SYMLINK+="servoZ", GROUP="dialout", MODE="0666"
SUBSYSTEM=="tty", KERNELS=="1-1.4", SYMLINK+="spindle", GROUP="dialout", MODE="0666"
EOF

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable servo-vfd
```

### 3. Test Before Starting

```bash
# Test all components
python3 pre_service_test.py

# If tests pass, start the service
./service_manager.sh start
```

## 📋 Service Management Commands

### Using Service Manager Script
```bash
./service_manager.sh start      # Start service
./service_manager.sh stop       # Stop service
./service_manager.sh restart    # Restart service
./service_manager.sh status     # Show status
./service_manager.sh logs       # Follow logs
./service_manager.sh enable     # Enable on boot
./service_manager.sh disable    # Disable on boot
./service_manager.sh uninstall  # Remove service
```

### Using systemctl Directly
```bash
sudo systemctl start servo-vfd
sudo systemctl stop servo-vfd
sudo systemctl restart servo-vfd
sudo systemctl status servo-vfd
sudo journalctl -u servo-vfd -f  # View logs
```

## 🔧 Service Configuration

The service is configured to:
- **Auto-restart** on failures (10-second delay, max 3 attempts/minute)
- **Start on boot** when enabled
- **Run as user** `humac` with proper permissions
- **Access USB devices** for serial communication
- **Log to systemd journal** for easy debugging

## 🛠️ Troubleshooting

### Check Service Status
```bash
sudo systemctl status servo-vfd
```

### View Detailed Logs
```bash
# Recent logs
sudo journalctl -u servo-vfd --since "1 hour ago"

# Follow live logs
sudo journalctl -u servo-vfd -f

# Error logs only
sudo journalctl -u servo-vfd -p err
```

### Common Issues

#### 1. Permission Denied
```bash
# Add user to dialout group
sudo usermod -a -G dialout humac
# Logout and login again
```

#### 2. Device Not Found
```bash
# Check USB devices
ls -l /dev/ttyUSB*
ls -l /dev/servo*

# Check udev rules
cat /etc/udev/rules.d/99-servo-usb.rules
```

#### 3. Python Module Not Found
```bash
# Install required packages
pip3 install pymodbus redis paho-mqtt pyserial

# Check Python path
which python3
python3 -c "import sys; print(sys.path)"
```

#### 4. Redis Connection Failed
```bash
# Check Redis status
sudo systemctl status redis
sudo systemctl start redis
```

## 🗑️ Service Removal

To completely remove the service:

```bash
# Stop and disable service
sudo systemctl stop servo-vfd
sudo systemctl disable servo-vfd

# Remove service file
sudo rm /etc/systemd/system/servo-vfd.service

# Reload systemd
sudo systemctl daemon-reload

# Remove udev rules (optional)
sudo rm /etc/udev/rules.d/99-servo-usb.rules
sudo udevadm control --reload-rules
```

## 📁 Project Structure

```
/home/humac/SERVO_VFD/
├── main.py                    # Main application
├── module/                    # Application modules
│   ├── config/
│   │   └── config.json       # Configuration
│   └── ...                    # Other modules
├── logs/                      # Application logs
├── servo-vfd.service         # Service file (copy to /etc/systemd/system/)
├── service_manager.sh         # Service management utility
└── pre_service_test.py        # Pre-startup testing
```

## ✅ Verification Checklist

Before starting the service, verify:

- [ ] User `humac` exists and is in `dialout` group
- [ ] Serial devices are accessible: `/dev/servoX`, `/dev/servoY`, `/dev/servoZ`, `/dev/spindle`
- [ ] Redis server is running and accessible
- [ ] MQTT broker is reachable
- [ ] All Python dependencies are installed
- [ ] Configuration file exists and is correct
- [ ] Service file is copied to `/etc/systemd/system/`

## 🎯 Next Steps

1. Run `python3 pre_service_test.py` to verify everything works
2. Start service with `./service_manager.sh start`
3. Monitor with `./service_manager.sh logs`
4. Enable on boot with `./service_manager.sh enable`

Your SERVO_VFD driver will now run automatically with restart protection!
