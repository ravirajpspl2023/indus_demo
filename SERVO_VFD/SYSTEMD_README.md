# SERVO_VFD Systemd Service Setup

This guide shows how to run your SERVO_VFD project as a systemd service with automatic restart on errors.

## Files Created:
- **`servo-vfd.service`** - Systemd service configuration
- **`install_service.sh`** - Installation script
- **`service_manager.sh`** - Service management utility

## Installation:

### 1. Copy Files to Raspberry Pi
```bash
# Copy these files to your Raspberry Pi SERVO_VFD directory
scp servo-vfd.service install_service.sh service_manager.sh humac@raspberry-ip:/home/humac/SERVO_VFD/
```

### 2. Run Installation Script
```bash
cd /home/humac/SERVO_VFD
chmod +x install_service.sh service_manager.sh
sudo ./install_service.sh
```

### 3. Manual Installation (Alternative)
```bash
# Copy service file
sudo cp servo-vfd.service /etc/systemd/system/

# Set permissions
sudo chmod 644 /etc/systemd/system/servo-vfd.service

# Create directories
mkdir -p logs
sudo chown -R humac:humac /home/humac/SERVO_VFD

# Reload and enable
sudo systemctl daemon-reload
sudo systemctl enable servo-vfd
sudo systemctl start servo-vfd
```

## Service Features:

### **Automatic Restart**
- Restarts on crashes/failures
- 10-second delay between restarts
- Maximum 3 restart attempts per minute

### **Security**
- Runs as non-root user (humac)
- Limited device access
- Protected filesystem

### **Device Access**
- USB serial ports: /dev/ttyUSB0-3
- Symlinked devices: /dev/servoX/Y/Z/spindle

## Service Management:

### **Using Service Manager Script**
```bash
./service_manager.sh start      # Start service
./service_manager.sh stop       # Stop service
./service_manager.sh restart    # Restart service
./service_manager.sh status     # Show status
./service_manager.sh logs       # Follow logs
./service_manager.sh enable     # Enable on boot
./service_manager.sh disable    # Disable on boot
```

### **Using systemctl Directly**
```bash
sudo systemctl start servo-vfd
sudo systemctl stop servo-vfd
sudo systemctl restart servo-vfd
sudo systemctl status servo-vfd
sudo journalctl -u servo-vfd -f  # View logs
```

## Troubleshooting:

### **Check Service Status**
```bash
sudo systemctl status servo-vfd
```

### **View Logs**
```bash
# Recent logs
sudo journalctl -u servo-vfd --since "1 hour ago"

# Follow live logs
sudo journalctl -u servo-vfd -f

# Check for errors
sudo journalctl -u servo-vfd -p err
```

### **Common Issues:**

1. **Permission Denied**: Ensure user is in dialout group
   ```bash
   sudo usermod -a -G dialout humac
   ```

2. **Device Not Found**: Check USB connections and udev rules
   ```bash
   ls -l /dev/servo*
   ls -l /dev/ttyUSB*
   ```

3. **Redis Connection**: Ensure Redis is running
   ```bash
   sudo systemctl status redis
   ```

## Advantages over Docker:
- ✅ No container complexity
- ✅ Direct hardware access
- ✅ Lower resource usage
- ✅ Faster startup
- ✅ Easier debugging
- ✅ Built-in auto-restart
- ✅ System-level integration

## Service Configuration:
The service is configured to:
- Start automatically on boot
- Restart automatically on failures
- Log to systemd journal
- Run with proper permissions
- Access required USB devices
