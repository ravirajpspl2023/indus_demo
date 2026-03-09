#!/bin/bash

# SERVO_VFD Service Installation Script
# This script installs the systemctl service for automatic management

set -e

SERVICE_NAME="servo-vfd"
SERVICE_FILE="servo-vfd.service"
INSTALL_PATH="/etc/systemd/system/$SERVICE_NAME.service"
USER="humac"
PROJECT_DIR="/home/$USER/SERVO_VFD"

echo "=== SERVO_VFD Service Installation ==="
echo

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

# Check if user exists
if ! id "$USER" &>/dev/null; then
    echo "User '$USER' not found. Creating user..."
    useradd -m -s /bin/bash "$USER"
    usermod -a -G dialout "$USER"
    echo "User '$USER' created and added to dialout group"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/module/config"
chown -R "$USER:$USER" "$PROJECT_DIR"

# Copy service file
echo "Installing systemd service..."
cp "$SERVICE_FILE" "$INSTALL_PATH"
chmod 644 "$INSTALL_PATH"

# Create log directory
mkdir -p "$PROJECT_DIR/logs"
chown "$USER:$USER" "$PROJECT_DIR/logs"

# Set up udev rules for consistent device naming
echo "Setting up udev rules..."
cat > /etc/udev/rules.d/99-servo-usb.rules << EOF
SUBSYSTEM=="tty", KERNELS=="1-1.1", SYMLINK+="servoX", GROUP="dialout", MODE="0666"
SUBSYSTEM=="tty", KERNELS=="1-1.2", SYMLINK+="servoY", GROUP="dialout", MODE="0666"
SUBSYSTEM=="tty", KERNELS=="1-1.3", SYMLINK+="servoZ", GROUP="dialout", MODE="0666"
SUBSYSTEM=="tty", KERNELS=="1-1.4", SYMLINK+="spindle", GROUP="dialout", MODE="0666"
EOF

# Reload udev rules
udevadm control --reload-rules
udevadm trigger

# Reload systemd and enable service
echo "Enabling and starting service..."
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

# Show service status
echo
echo "=== Service Status ==="
systemctl status "$SERVICE_NAME" --no-pager

echo
echo "=== Installation Complete ==="
echo "Service commands:"
echo "  status: systemctl status $SERVICE_NAME"
echo "  start:  systemctl start $SERVICE_NAME"
echo "  stop:   systemctl stop $SERVICE_NAME"
echo "  restart: systemctl restart $SERVICE_NAME"
echo "  logs:   journalctl -u $SERVICE_NAME -f"
echo
echo "Service will auto-restart on failures."
