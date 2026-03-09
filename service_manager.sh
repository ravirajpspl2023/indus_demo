#!/bin/bash

# SERVO_VFD Service Management Script
# Easy commands to manage the service

SERVICE_NAME="servo-vfd"

case "$1" in
    start)
        echo "Starting $SERVICE_NAME service..."
        sudo systemctl start "$SERVICE_NAME"
        sudo systemctl status "$SERVICE_NAME" --no-pager
        ;;
    stop)
        echo "Stopping $SERVICE_NAME service..."
        sudo systemctl stop "$SERVICE_NAME"
        ;;
    restart)
        echo "Restarting $SERVICE_NAME service..."
        sudo systemctl restart "$SERVICE_NAME"
        sudo systemctl status "$SERVICE_NAME" --no-pager
        ;;
    status)
        echo "Status of $SERVICE_NAME service:"
        sudo systemctl status "$SERVICE_NAME" --no-pager
        ;;
    logs)
        echo "Following logs for $SERVICE_NAME service (Ctrl+C to exit):"
        sudo journalctl -u "$SERVICE_NAME" -f
        ;;
    enable)
        echo "Enabling $SERVICE_NAME service on boot..."
        sudo systemctl enable "$SERVICE_NAME"
        echo "Service enabled for auto-start on boot."
        ;;
    disable)
        echo "Disabling $SERVICE_NAME service..."
        sudo systemctl disable "$SERVICE_NAME"
        echo "Service disabled from auto-start."
        ;;
    uninstall)
        echo "Uninstalling $SERVICE_NAME service..."
        sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true
        sudo systemctl disable "$SERVICE_NAME" 2>/dev/null || true
        sudo rm -f "/etc/systemd/system/$SERVICE_NAME.service"
        sudo systemctl daemon-reload
        echo "Service uninstalled."
        ;;
    *)
        echo "SERVO_VFD Service Manager"
        echo "Usage: $0 {start|stop|restart|status|logs|enable|disable|uninstall}"
        echo
        echo "Commands:"
        echo "  start     - Start the service"
        echo "  stop      - Stop the service"
        echo "  restart   - Restart the service"
        echo "  status    - Show service status"
        echo "  logs      - Follow service logs"
        echo "  enable    - Enable auto-start on boot"
        echo "  disable   - Disable auto-start on boot"
        echo "  uninstall - Remove the service"
        exit 1
        ;;
esac
