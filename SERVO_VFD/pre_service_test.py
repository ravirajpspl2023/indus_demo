#!/usr/bin/env python3
"""
Quick test script to verify serial devices and basic functionality
before running as a service
"""

import os
import sys
import logging
import serial
import serial.tools.list_ports

# Add project path
sys.path.insert(0, '/home/humac/SERVO_VFD')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_serial_devices():
    """Test if all required serial devices are available"""
    print("=== Serial Device Test ===")
    
    # List all serial ports
    ports = serial.tools.list_ports.comports()
    print(f"Found {len(ports)} serial ports:")
    for port in ports:
        print(f"  {port.device} - {port.description}")
    
    # Test specific devices
    devices = ['/dev/servoX', '/dev/servoY', '/dev/servoZ', '/dev/spindle']
    available = []
    
    for device in devices:
        if os.path.exists(device):
            try:
                ser = serial.Serial(device, timeout=1)
                ser.close()
                print(f"✓ {device} - Accessible")
                available.append(device)
            except Exception as e:
                print(f"✗ {device} - Error: {e}")
        else:
            print(f"✗ {device} - Not found")
    
    return len(available) == len(devices)

def test_redis_connection():
    """Test Redis connectivity"""
    print("\n=== Redis Connection Test ===")
    
    try:
        import redis
        from module.config.config import config
        
        redis_config = config.get_redis_config()
        r = redis.Redis(**redis_config, socket_connect_timeout=5)
        r.ping()
        print("✓ Redis connection successful")
        return True
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        return False

def test_mqtt_connection():
    """Test MQTT connectivity"""
    print("\n=== MQTT Connection Test ===")
    
    try:
        import paho.mqtt.client as mqtt
        from module.config.config import config
        
        mqtt_config = config.get_mqtt_config()
        client = mqtt.Client()
        client.connect(mqtt_config['host'], mqtt_config['port'], 5)
        client.disconnect()
        print("✓ MQTT connection successful")
        return True
    except Exception as e:
        print(f"✗ MQTT connection failed: {e}")
        return False

def test_imports():
    """Test if all modules can be imported"""
    print("\n=== Import Test ===")
    
    try:
        from module.humac_driver import humac_driver
        print("✓ Main driver import successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def main():
    print("SERVO_VFD Pre-Service Test")
    print("=" * 40)
    
    tests = [
        ("Serial Devices", test_serial_devices),
        ("Redis Connection", test_redis_connection),
        ("MQTT Connection", test_mqtt_connection),
        ("Module Imports", test_imports)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} test crashed: {e}")
            results.append((name, False))
    
    print("\n=== Test Summary ===")
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Service should start successfully.")
        return 0
    else:
        print("\n❌ Some tests failed. Fix issues before starting service.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
