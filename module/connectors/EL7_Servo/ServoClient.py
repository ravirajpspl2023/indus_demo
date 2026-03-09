try:
    from pymodbus.client import ModbusSerialClient
    from pymodbus.exceptions import ModbusException
except ImportError:
    raise ImportError("Install with:  pip install pymodbus pyserial")


import logging

log = logging.getLogger(__name__)


class ServoClient:
    """
    RS-485 Modbus RTU connection to EL7-RS servo drive.

    Parameters
    ----------
    port     : Serial port  e.g. 'COM3'  or  '/dev/ttyUSB0'
    slave_id : Modbus slave address  (Pr5.31, default=4)
    baudrate : Baud rate             (Pr5.30, default=57600)
    timeout  : Read timeout seconds
    """
    def __init__(self, port, slave_id=1, baudrate=9600,bytesize=8,stopbits=1,parity='N', timeout=1.0):
        self.slave_id = slave_id
        self.port=port
        self._client = ModbusSerialClient(
            port=port, baudrate=baudrate,
            bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout,
        )
        if not self._client.connect():
            ConnectionError(f"Cannot open{ port }")
        log.info(f"Connected  port={port}  slave={slave_id}  baud={baudrate}")

    def read_registers(self, start_addr, count):
        """Read `count` holding registers from start_addr."""
        resp = self._client.read_holding_registers(
            address=start_addr, count=count, device_id=self.slave_id)
        if resp.isError():
            raise ModbusException(f"Read error addr=0x{start_addr:04X} count={count}")
        return list(resp.registers)

    def write_register(self, addr, value):
        """Write single 16-bit register (Function 06)."""
        resp = self._client.write_register(
            address=addr, value=int(value) & 0xFFFF, slave=self.slave_id)
        if resp.isError():
            raise ModbusException(f"Write error addr=0x{addr:04X}")

    def write_registers(self, start_addr, values):
        """Write multiple 16-bit registers (Function 16)."""
        resp = self._client.write_registers(
            address=start_addr, values=[v & 0xFFFF for v in values],
            slave=self.slave_id)
        if resp.isError():
            raise ModbusException(f"Multi-write error addr=0x{start_addr:04X}")

    def close(self):
        self._client.close()

    def __enter__(self): return self
    def __exit__(self, *_): self.close()