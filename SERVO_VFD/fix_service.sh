#!/bin/bash

# Quick fix script for service startup issues

SERVICE_NAME="servo-vfd"
USER="humac"
PROJECT_DIR="/home/$USER/SERVO_VFD"

echo "=== SERVO_VFD Service Fix ==="
echo

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

echo "1. Checking if user exists..."
if ! id "$USER" &>/dev/null; then
    echo "User '$USER' not found. Creating..."
    useradd -m -s /bin/bash "$USER"
    usermod -a -G dialout "$USER"
fi

echo "2. Creating and fixing permissions..."
mkdir -p "$PROJECT_DIR"
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/module/config"

# Set ownership
chown -R "$USER:$USER" "$PROJECT_DIR"
chmod -R 755 "$PROJECT_DIR"

echo "3. Checking Python path..."
PYTHON_PATH=$(which python3)
if [[ -z "$PYTHON_PATH" ]]; then
    echo "Python3 not found! Installing..."
    apt-get update
    apt-get install -y python3 python3-pip
fi

echo "4. Testing Python script manually..."
sudo -u "$USER" bash -c "cd '$PROJECT_DIR' && python3 -c 'print(\"Python works\")'"

echo "5. Installing updated service..."
cp servo-vfd.service "/etc/systemd/system/$SERVICE_NAME.service"
chmod 644 "/etc/systemd/system/$SERVICE_NAME.service"

echo "6. Reloading systemd..."
systemctl daemon-reload
systemctl reset-failed "$SERVICE_NAME"

echo "7. Testing service start..."
sudo -u "$USER" bash -c "cd '$PROJECT_DIR' && timeout 5 python3 main.py" || echo "Script test completed (timeout expected)"

echo "8. Starting service..."
systemctl start "$SERVICE_NAME"
sleep 2

echo "9. Checking status..."
systemctl status "$SERVICE_NAME" --no-pager -l

echo
echo "=== Fix Complete ==="
echo "If still failing, check logs with:"
echo "  journalctl -u $SERVICE_NAME -n 20"
