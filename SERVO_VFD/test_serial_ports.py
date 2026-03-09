#!/usr/bin/env python3
"""
Serial Port Test Utility
Tests serial port accessibility in Docker container
"""

import serial
import serial.tools.list_ports
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_serial_ports():
    """List available serial ports"""
    print("Available Serial Ports:")
    print("=" * 50)
    
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found!")
        return False
    
    for port in ports:
        print(f"Port: {port.device}")
        print(f"  Name: {port.name}")
        print(f"  Description: {port.description}")
        print(f"  HWID: {port.hwid}")
        print()
    
    return True

def test_specific_port(port_device):
    """Test if we can open a specific serial port"""
    try:
        ser = serial.Serial(port_device, timeout=1)
        print(f"✓ Successfully opened {port_device}")
        ser.close()
        return True
    except Exception as e:
        print(f"✗ Failed to open {port_device}: {e}")
        return False

if __name__ == "__main__":
    print("Serial Port Test Utility")
    print("=" * 50)
    
    # List all ports
    test_serial_ports()
    
    # Test specific ports from your config
    test_ports = ['/dev/servoX', '/dev/servoY', '/dev/servoZ', '/dev/spindle']
    
    print("Testing Configured Ports:")
    print("=" * 50)
    
    for port in test_ports:
        test_specific_port(port)
