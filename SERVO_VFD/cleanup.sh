#!/bin/bash

# SERVO_VFD Cleanup Script
# Removes unnecessary Docker files and keeps only essential systemd files

echo "=== SERVO_VFD Cleanup ==="
echo "Removing Docker-related files..."

# Remove Docker files (if they exist)
rm -f Dockerfile docker-compose.yml .dockerignore DOCKER_README.md

# Remove installation scripts (keeping only service manager)
rm -f install_service.sh fix_service.sh

# Remove test files (keeping pre-service test)
rm -f test_delta_addresses.py test_serial_ports.py

# Remove DELTA_C200 test files
rm -f module/connectors/DELTA_C200/AddressValidator.py

echo "✓ Cleanup complete!"
echo ""
echo "Essential files retained:"
echo "  - servo-vfd.service (systemd service)"
echo "  - service_manager.sh (service management)"
echo "  - pre_service_test.py (pre-startup testing)"
echo "  - SYSTEMD_SETUP_GUIDE.md (setup instructions)"
echo ""
echo "Project files retained:"
echo "  - main.py and all module/ files"
echo "  - config.json"
echo "  - setup.txt"
echo ""
echo "Ready for systemd service setup!"
