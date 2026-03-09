"""
============================================================
Leadshine EL7-RS Series AC Servo Drive — Modbus RTU Client
============================================================
Library  : pymodbus >= 3.x
Protocol : Modbus RTU over RS-485 (RJ45 port)
Default  : Baud=57600, 8N1, Slave ID=4

Design:
  - Each parameter Class (0,1,2,3,4,5,6,B,8,9) is a Python class
  - On read()  → one bulk Modbus read (start_addr to last_addr)
  - Parameters are auto-mapped from the bulk response by offset
  - 32-bit parameters = two consecutive 16-bit registers (Hi+Lo)
  - on write() → single register write via Fn06

Usage:
    from leadshine_el7rs_modbus import ServoClient, Class0, Class5, ClassB

    servo = ServoClient(port='COM3', slave_id=4)

    c0 = Class0(servo)
    c0.read()
    print(c0.pr0_01)          # Control Mode
    print(c0.pr0_04)          # Inertia Ratio

    cB = ClassB(servo)
    cB.read()
    print(cB.motor_speed_rpm)
    print(cB.motor_torque_pct)
    print(cB.dc_bus_voltage_v)
    print(cB.current_alarm)

    c5 = Class5(servo)
    c5.read()
    c5.pr5_31 = 5             # change slave ID
    c5.write('pr5_31')

    servo.close()
============================================================
"""

from dataclasses import dataclass
from typing import Optional, Any, List, Dict
import logging

try:
    from pymodbus.client import ModbusSerialClient
    from pymodbus.exceptions import ModbusException
except ImportError:
    raise ImportError("Install with:  pip install pymodbus pyserial")

log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
#  Parameter Descriptor
# ─────────────────────────────────────────────────────────────
@dataclass
class ParamDef:
    code   : str
    name   : str
    addr   : int
    bits   : int  = 16
    rw     : str  = "R/W"
    default: Any  = 0
    unit   : str  = ""
    note   : str  = ""


# ─────────────────────────────────────────────────────────────
#  Modbus Serial Client Wrapper
# ─────────────────────────────────────────────────────────────
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
    def __init__(self, port, slave_id=1, baudrate=9600, timeout=1.0):
        self.slave_id = slave_id
        self._client = ModbusSerialClient(
            port=port, baudrate=baudrate,
            bytesize=8, parity='N', stopbits=1, timeout=timeout,
        )
        if not self._client.connect():
            raise ConnectionError(f"Cannot open {port}")
        log.info(f"Connected  port={port}  slave={slave_id}  baud={baudrate}")

    def read_registers(self, start_addr, count):
        """Read `count` holding registers from start_addr."""
        resp = self._client.read_holding_registers(
            address=start_addr, count=count, slave=self.slave_id)
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


# ─────────────────────────────────────────────────────────────
#  Base Parameter Class
# ─────────────────────────────────────────────────────────────
class _BaseParamClass:
    """
    Base class for all EL7-RS parameter groups.

    Subclass defines:
        CLASS_NAME : str
        PARAMS     : List[ParamDef]  — ordered list of parameters

    read()  → one bulk Modbus call from start_addr to end_addr
    write() → single register write back to drive
    """
    CLASS_NAME = "Base"
    PARAMS: List[ParamDef] = []

    def __init__(self, client: ServoClient):
        self._client = client
        self._attr_map: Dict[str, str] = {
            p.code: self._to_attr(p.code) for p in self.PARAMS
        }
        for attr in self._attr_map.values():
            setattr(self, attr, None)

    @staticmethod
    def _to_attr(code):
        # "Pr0.01" -> "pr0_01"   "PrB.06" -> "prb_06"
        return code.lower().replace('.', '_')

    @property
    def start_addr(self):
        return min(p.addr for p in self.PARAMS)

    @property
    def end_addr(self):
        return max(p.addr + (1 if p.bits == 32 else 0) for p in self.PARAMS)

    @property
    def read_count(self):
        return self.end_addr - self.start_addr + 1

    # ── BULK READ ──────────────────────────────────────────
    def read(self):
        """
        One Modbus call reads ALL registers for this Class
        (from start_addr to end_addr), then maps each
        ParamDef to its attribute automatically.
        """
        log.info(f"[{self.CLASS_NAME}]  "
                 f"0x{self.start_addr:04X} ~ 0x{self.end_addr:04X}  "
                 f"({self.read_count} registers)")

        regs = self._client.read_registers(self.start_addr, self.read_count)

        for p in self.PARAMS:
            offset = p.addr - self.start_addr
            if offset < 0 or offset >= len(regs):
                continue

            if p.bits == 32:
                hi = regs[offset]
                lo = regs[offset + 1] if (offset + 1) < len(regs) else 0
                val = (hi << 16) | lo
                if val >= 0x80000000:    # signed 32-bit
                    val -= 0x100000000
            else:
                val = regs[offset]
                if val >= 0x8000:        # signed 16-bit
                    val -= 0x10000

            setattr(self, self._attr_map[p.code], val)

        log.info(f"  -> {len(self.PARAMS)} params mapped")

    # ── WRITE ──────────────────────────────────────────────
    def write(self, attr_name):
        """Write a single parameter back to drive by attribute name."""
        code = next(
            (c for c, a in self._attr_map.items() if a == attr_name), None)
        if code is None:
            raise ValueError(f"Unknown attribute: {attr_name}")

        p = next(x for x in self.PARAMS if x.code == code)
        if p.rw == 'R':
            raise PermissionError(f"{code} is read-only!")

        value = getattr(self, attr_name)
        if value is None:
            raise ValueError(f"{attr_name} is None — read first or set a value")

        if p.bits == 32:
            v = int(value) & 0xFFFFFFFF
            self._client.write_registers(p.addr, [(v >> 16) & 0xFFFF, v & 0xFFFF])
        else:
            self._client.write_register(p.addr, int(value) & 0xFFFF)

        log.info(f"Written  {code}  (0x{p.addr:04X})  = {value}")

    # ── PRINT ──────────────────────────────────────────────
    def print_all(self):
        print(f"\n{'='*72}")
        print(f"  {self.CLASS_NAME}")
        print(f"  Bulk read range: 0x{self.start_addr:04X} ~ 0x{self.end_addr:04X}  ({self.read_count} regs)")
        print(f"{'='*72}")
        print(f"  {'Code':<10} {'Hex Addr':<10} {'Name':<42} {'Value':<10} {'Unit'}")
        print(f"  {'-'*75}")
        for p in self.PARAMS:
            v = getattr(self, self._attr_map[p.code])
            print(f"  {p.code:<10} 0x{p.addr:04X}     {p.name:<42} {str(v):<10} {p.unit}")
        print(f"{'='*72}\n")

    def to_dict(self):
        return {
            p.code: {
                "name": p.name,
                "addr": f"0x{p.addr:04X}",
                "value": getattr(self, self._attr_map[p.code]),
                "unit": p.unit,
            }
            for p in self.PARAMS
        }

    def __repr__(self):
        return (f"<{self.__class__.__name__} "
                f"0x{self.start_addr:04X}~0x{self.end_addr:04X} "
                f"{len(self.PARAMS)} params>")


# ═══════════════════════════════════════════════════════════════
#  CLASS 0 — Basic Settings   0x0001 ~ 0x006B
# ═══════════════════════════════════════════════════════════════
class Class0(_BaseParamClass):
    CLASS_NAME = "Class 0 — Basic Settings"
    PARAMS = [
        ParamDef("Pr0.00","Model-following/ZTC Bandwidth",      0x0001,16,"R/W",1,    "0.1Hz"),
        ParamDef("Pr0.01","Control Mode Settings",              0x0003,16,"R/W",0,    "",    "0=Pos|1=Vel|2=Torque|6=PR"),
        ParamDef("Pr0.02","Real-time Auto Gain Adjusting",      0x0005,16,"R/W",0x1,  ""),
        ParamDef("Pr0.03","Real-time Auto Stiffness Adjusting", 0x0007,16,"R/W",11,   "",    "0~31"),
        ParamDef("Pr0.04","Inertia Ratio",                      0x0009,16,"R/W",250,  "%"),
        ParamDef("Pr0.05","Command Pulse Input Selection",       0x000B,16,"R/W",0,    "",    "0=200kHz|1=4MHz"),
        ParamDef("Pr0.06","Command Pulse Polarity Inversion",   0x000D,16,"R/W",0,    ""),
        ParamDef("Pr0.07","Command Pulse Input Mode",           0x000F,16,"R/W",3,    "",    "0=CW/CCW|1=Pulse+Dir|3=AB×4"),
        ParamDef("Pr0.08","1st Cmd Pulse Count/Revolution",     0x0010,32,"R/W",10000,"pulse/rev"),
        ParamDef("Pr0.09","1st Cmd Freq Divider Numerator",     0x0012,32,"R/W",1,    ""),
        ParamDef("Pr0.10","1st Cmd Freq Divider Denominator",   0x0014,32,"R/W",1,    ""),
        ParamDef("Pr0.11","Encoder Output Pulse Count/Rev",     0x0017,16,"R/W",2500, "pulse/rev"),
        ParamDef("Pr0.12","Pulse Output Logic Inversion",       0x0019,16,"R/W",0,    ""),
        ParamDef("Pr0.13","1st Torque Limit",                   0x001B,16,"R/W",350,  "%"),
        ParamDef("Pr0.14","Excessive Position Deviation",       0x001D,16,"R/W",30,   "x10k pulse"),
        ParamDef("Pr0.15","Absolute Encoder Settings",          0x001F,16,"R/W",0,    "",    "0=Inc|1=Abs single|2=Abs multi"),
        ParamDef("Pr0.16","Regenerative Resistance",            0x0021,16,"R/W",100,  "Ohm"),
        ParamDef("Pr0.17","Regenerative Resistor Power Rating", 0x0023,16,"R/W",50,   "W"),
        ParamDef("Pr0.22","PR and P/S/T Mode Switching",        0x002D,16,"R/W",0,    ""),
        ParamDef("Pr0.25","Auxiliary Function",                 0x0033,16,"R/W",0,    ""),
        ParamDef("Pr0.26","Simulated I/O",                      0x0035,16,"R/W",0,    ""),
        ParamDef("Pr0.30","Encoder Feedback Mode",              0x0037,16,"R/W",0,    ""),
        ParamDef("Pr0.31","External Encoder Type",              0x0039,16,"R/W",0,    ""),
        ParamDef("Pr0.32","External Encoder Direction",         0x003B,16,"R/W",0,    ""),
        ParamDef("Pr0.33","Excessive Hybrid Deviation",         0x0043,16,"R/W",16000,""),
        ParamDef("Pr0.34","Clear Hybrid Control Deviation",     0x0045,16,"R/W",0,    ""),
        ParamDef("Pr0.35","Ext Encoder Divider Numerator",      0x0047,16,"R/W",0,    ""),
        ParamDef("Pr0.36","Ext Encoder Divider Denominator",    0x0049,16,"R/W",10000,""),
        ParamDef("Pr0.37","Ext Encoder Feedback Pulse/Rev",     0x004B,16,"R/W",0,    "pulse/rev"),
        ParamDef("Pr0.38","Z-signal Pulse Input Source",        0x004D,16,"R/W",0,    ""),
        ParamDef("Pr0.40","Mapping Parameter 1",                0x0050,32,"R/W",0,    ""),
        ParamDef("Pr0.41","Mapping Parameter 2",                0x0052,32,"R/W",0,    ""),
        ParamDef("Pr0.42","Mapping Parameter 3",                0x0054,32,"R/W",0,    ""),
        ParamDef("Pr0.43","Mapping Parameter 4",                0x0056,32,"R/W",0,    ""),
        ParamDef("Pr0.50","Mapping Param 1 Indicator",          0x0064,32,"R/W",0x49, ""),
        ParamDef("Pr0.51","Mapping Param 2 Indicator",          0x0066,32,"R/W",0x49, ""),
        ParamDef("Pr0.52","Mapping Param 3 Indicator",          0x0068,32,"R/W",0x49, ""),
        ParamDef("Pr0.53","Mapping Param 4 Indicator",          0x006A,32,"R/W",0x49, ""),
    ]


# ═══════════════════════════════════════════════════════════════
#  CLASS 1 — Gain Adjustment   0x0101 ~ 0x014F
# ═══════════════════════════════════════════════════════════════
class Class1(_BaseParamClass):
    CLASS_NAME = "Class 1 — Gain Adjustment"
    PARAMS = [
        ParamDef("Pr1.00","1st Position Loop Gain",             0x0101,16,"R/W",320,  "0.1/s"),
        ParamDef("Pr1.01","1st Velocity Loop Gain",             0x0103,16,"R/W",180,  "Hz"),
        ParamDef("Pr1.02","1st Integral Time Const Vel Loop",   0x0105,16,"R/W",310,  "0.1ms","10000=Disable"),
        ParamDef("Pr1.03","1st Velocity Detection Filter",      0x0107,16,"R/W",15,   ""),
        ParamDef("Pr1.04","1st Torque Filter Time Constant",    0x0109,16,"R/W",126,  "0.1ms"),
        ParamDef("Pr1.05","2nd Position Loop Gain",             0x010B,16,"R/W",380,  "0.1/s"),
        ParamDef("Pr1.06","2nd Velocity Loop Gain",             0x010D,16,"R/W",180,  "Hz"),
        ParamDef("Pr1.07","2nd Integral Time Const Vel Loop",   0x010F,16,"R/W",10000,"0.1ms"),
        ParamDef("Pr1.08","2nd Velocity Detection Filter",      0x0111,16,"R/W",15,   ""),
        ParamDef("Pr1.09","2nd Torque Filter Time Constant",    0x0113,16,"R/W",126,  "0.1ms"),
        ParamDef("Pr1.10","Velocity Feed Forward Gain",         0x0115,16,"R/W",300,  "%"),
        ParamDef("Pr1.11","Velocity FF Filter Time Constant",   0x0117,16,"R/W",50,   "0.1ms"),
        ParamDef("Pr1.12","Torque Feed Forward Gain",           0x0119,16,"R/W",0,    "%"),
        ParamDef("Pr1.13","Torque FF Filter Time Constant",     0x011B,16,"R/W",0,    "0.1ms"),
        ParamDef("Pr1.15","Position Ctrl Gain Switching Mode",  0x011F,16,"R/W",0,    ""),
        ParamDef("Pr1.17","Position Ctrl Gain Switching Level", 0x0123,16,"R/W",50,   ""),
        ParamDef("Pr1.18","Hysteresis at Gain Switching",       0x0125,16,"R/W",33,   ""),
        ParamDef("Pr1.19","Position Ctrl Switching Time",       0x0127,16,"R/W",33,   "0.1ms"),
        ParamDef("Pr1.35","Position Cmd Pulse Filter Time",     0x0147,16,"R/W",8,    ""),
        ParamDef("Pr1.39","Special Function Register 2",        0x014F,16,"R/W",0,    ""),
    ]


# ═══════════════════════════════════════════════════════════════
#  CLASS 2 — Vibration Suppression   0x0201 ~ 0x026F
# ═══════════════════════════════════════════════════════════════
class Class2(_BaseParamClass):
    CLASS_NAME = "Class 2 — Vibration Suppression"
    PARAMS = [
        ParamDef("Pr2.00","Adaptive Filtering Mode",            0x0201,16,"R/W",0,    ""),
        ParamDef("Pr2.01","1st Notch Filter Frequency",         0x0203,16,"R/W",4000, "Hz"),
        ParamDef("Pr2.02","1st Notch Filter Width",             0x0205,16,"R/W",4,    ""),
        ParamDef("Pr2.03","1st Notch Filter Depth",             0x0207,16,"R/W",0,    ""),
        ParamDef("Pr2.04","2nd Notch Filter Frequency",         0x0209,16,"R/W",4000, "Hz"),
        ParamDef("Pr2.05","2nd Notch Filter Width",             0x020B,16,"R/W",4,    ""),
        ParamDef("Pr2.06","2nd Notch Filter Depth",             0x020D,16,"R/W",0,    ""),
        ParamDef("Pr2.07","3rd Notch Filter Frequency",         0x020F,16,"R/W",4000, "Hz"),
        ParamDef("Pr2.08","3rd Notch Filter Width",             0x0211,16,"R/W",4,    ""),
        ParamDef("Pr2.09","3rd Notch Filter Depth",             0x0213,16,"R/W",0,    ""),
        ParamDef("Pr2.14","1st Damping Frequency",              0x021D,16,"R/W",0,    "Hz"),
        ParamDef("Pr2.16","2nd Damping Frequency",              0x0221,16,"R/W",0,    "Hz"),
        ParamDef("Pr2.22","Position Cmd Smoothing Filter",      0x022D,16,"R/W",0,    "0.1ms"),
        ParamDef("Pr2.23","Position Cmd FIR Filter",            0x022F,16,"R/W",0,    ""),
        ParamDef("Pr2.48","Adjustment Mode",                    0x0261,16,"R/W",0,    ""),
        ParamDef("Pr2.50","MFC Type",                           0x0265,16,"R/W",0,    ""),
        ParamDef("Pr2.51","Velocity FF Compensation Coeff",     0x0267,16,"R/W",0,    ""),
        ParamDef("Pr2.52","Torque FF Compensation Coeff",       0x0269,16,"R/W",0,    ""),
        ParamDef("Pr2.53","Dynamic Friction Compensation",      0x026B,16,"R/W",0,    ""),
        ParamDef("Pr2.54","Overshoot Time Coefficient",         0x026D,16,"R/W",0,    ""),
        ParamDef("Pr2.55","Overshoot Suppression Gain",         0x026F,16,"R/W",0,    ""),
    ]


# ═══════════════════════════════════════════════════════════════
#  CLASS 3 — Velocity / Torque Control   0x0301 ~ 0x037B
# ═══════════════════════════════════════════════════════════════
class Class3(_BaseParamClass):
    CLASS_NAME = "Class 3 — Velocity / Torque Control"
    PARAMS = [
        ParamDef("Pr3.00","Velocity Int/Ext Switching",         0x0301,16,"R/W",1,    "",   "0=Analog|1=Internal"),
        ParamDef("Pr3.01","Velocity Cmd Direction Selection",   0x0303,16,"R/W",0,    ""),
        ParamDef("Pr3.02","Velocity Cmd Input Gain",            0x0305,16,"R/W",500,  "rpm/V"),
        ParamDef("Pr3.03","Velocity Cmd Input Inversion",       0x0307,16,"R/W",0,    ""),
        ParamDef("Pr3.04","1st Internal Speed",                 0x0309,16,"R/W",0,    "rpm"),
        ParamDef("Pr3.05","2nd Internal Speed",                 0x030B,16,"R/W",0,    "rpm"),
        ParamDef("Pr3.06","3rd Internal Speed",                 0x030D,16,"R/W",0,    "rpm"),
        ParamDef("Pr3.07","4th Internal Speed",                 0x030F,16,"R/W",0,    "rpm"),
        ParamDef("Pr3.08","5th Internal Speed",                 0x0311,16,"R/W",0,    "rpm"),
        ParamDef("Pr3.09","6th Internal Speed",                 0x0313,16,"R/W",0,    "rpm"),
        ParamDef("Pr3.10","7th Internal Speed",                 0x0315,16,"R/W",0,    "rpm"),
        ParamDef("Pr3.11","8th Internal Speed",                 0x0317,16,"R/W",0,    "rpm"),
        ParamDef("Pr3.12","Acceleration Time",                  0x0319,16,"R/W",100,  "ms"),
        ParamDef("Pr3.13","Deceleration Time",                  0x031B,16,"R/W",100,  "ms"),
        ParamDef("Pr3.14","Sigmoid Accel/Decel",                0x031D,16,"R/W",0,    "ms"),
        ParamDef("Pr3.15","Zero Speed Clamp Selection",         0x031F,16,"R/W",0,    ""),
        ParamDef("Pr3.16","Zero Speed Clamp Level",             0x0321,16,"R/W",30,   "rpm"),
        ParamDef("Pr3.17","Torque Int/Ext Switching",           0x0323,16,"R/W",0,    "",   "0=Analog|1=Pr3.22"),
        ParamDef("Pr3.18","Torque Cmd Direction Selection",     0x0325,16,"R/W",0,    ""),
        ParamDef("Pr3.19","Torque Cmd Input Gain",              0x0327,16,"R/W",30,   "%/V"),
        ParamDef("Pr3.20","Torque Cmd Input Inversion",         0x0329,16,"R/W",0,    ""),
        ParamDef("Pr3.21","Velocity Limit in Torque Mode",      0x032B,16,"R/W",0,    "rpm"),
        ParamDef("Pr3.22","Torque Command via RS485",           0x032D,16,"R/W",0,    "%",  "Write torque setpoint here"),
        ParamDef("Pr3.23","Zero Speed Delay Time",              0x032F,16,"R/W",0,    "ms"),
        ParamDef("Pr3.24","Maximum Motor Speed",                0x0331,16,"R/W",0,    "rpm"),
        ParamDef("Pr3.29","Analog 1 Clamping Voltage",          0x033B,16,"R/W",0,    "mV"),
        ParamDef("Pr3.30","Analog 3 Clamping Voltage",          0x033D,16,"R/W",0,    "mV"),
        ParamDef("Pr3.58","Speed Regulation Ratio 1",           0x0374,16,"R/W",10,   ""),
        ParamDef("Pr3.59","Speed Regulation Ratio 2",           0x0375,16,"R/W",20,   ""),
        ParamDef("Pr3.60","Speed Regulation Ratio 3",           0x0376,16,"R/W",40,   ""),
        ParamDef("Pr3.61","Speed Regulation Ratio 4",           0x0377,16,"R/W",80,   ""),
    ]


# ═══════════════════════════════════════════════════════════════
#  CLASS 4 — I/O Monitoring Settings   0x0401 ~ 0x0489
# ═══════════════════════════════════════════════════════════════
class Class4(_BaseParamClass):
    CLASS_NAME = "Class 4 — I/O Monitoring Settings"
    PARAMS = [
        ParamDef("Pr4.00","Digital Input DI1 Function",         0x0401,16,"R/W",0x01, ""),
        ParamDef("Pr4.01","Digital Input DI2 Function",         0x0403,16,"R/W",0x02, ""),
        ParamDef("Pr4.02","Digital Input DI3 Function",         0x0405,16,"R/W",0x08, ""),
        ParamDef("Pr4.03","Digital Input DI4 Function",         0x0407,16,"R/W",0x04, ""),
        ParamDef("Pr4.04","Digital Input DI5 Function",         0x0409,16,"R/W",0x03, ""),
        ParamDef("Pr4.05","Digital Input DI6 Function",         0x040B,16,"R/W",0x00, ""),
        ParamDef("Pr4.06","Digital Input DI7 Function",         0x040D,16,"R/W",0x00, ""),
        ParamDef("Pr4.07","Digital Input DI8 Function",         0x040F,16,"R/W",0x27, ""),
        ParamDef("Pr4.10","Digital Output DO1 Function",        0x0415,16,"R/W",0x02, ""),
        ParamDef("Pr4.11","Digital Output DO2 Function",        0x0417,16,"R/W",0x04, ""),
        ParamDef("Pr4.12","Digital Output DO3 Function",        0x0419,16,"R/W",0x03, ""),
        ParamDef("Pr4.13","Digital Output DO4 Function",        0x041B,16,"R/W",0x01, ""),
        ParamDef("Pr4.14","Digital Output DO5 Function",        0x041D,16,"R/W",0x22, ""),
        ParamDef("Pr4.22","AI-1 Zero Drift Compensation",       0x042D,16,"R/W",0,    "mV"),
        ParamDef("Pr4.23","AI-1 Filter",                        0x042F,16,"R/W",0,    ""),
        ParamDef("Pr4.24","AI-1 Overvoltage Protection",        0x0431,16,"R/W",0,    "mV"),
        ParamDef("Pr4.28","AI-3 Zero Drift Compensation",       0x043F,16,"R/W",20,   "mV"),
        ParamDef("Pr4.29","AI-3 Filter",                        0x0441,16,"R/W",1,    ""),
        ParamDef("Pr4.30","AI-3 Overvoltage Protection",        0x0443,16,"R/W",0,    "mV"),
        ParamDef("Pr4.31","Positioning Complete Range",         0x0445,16,"R/W",50,   "pulse"),
        ParamDef("Pr4.32","Positioning Complete Output",        0x0447,16,"R/W",50,   ""),
        ParamDef("Pr4.33","INP Positioning Delay Time",         0x0449,16,"R/W",1000, "ms"),
        ParamDef("Pr4.34","Zero Speed Detection Level",         0x044B,16,"R/W",150,  "rpm"),
        ParamDef("Pr4.35","Velocity Coincidence Range",         0x044D,16,"R/W",0,    "rpm"),
        ParamDef("Pr4.36","Arrival Velocity",                   0x044F,16,"R/W",30,   "rpm"),
        ParamDef("Pr4.43","Emergency Stop Function",            0x0457,16,"R/W",0,    ""),
        ParamDef("Pr4.64","AO1 Output Function",                0x0481,16,"R/W",0,    ""),
        ParamDef("Pr4.65","AO1 Signal Selection",               0x0483,16,"R/W",0x04, ""),
        ParamDef("Pr4.66","AO1 Amplification",                  0x0485,16,"R/W",100,  "%"),
        ParamDef("Pr4.67","AO1 Communication Output Value",     0x0487,16,"R/W",0,    ""),
        ParamDef("Pr4.68","AO1 Output Offset",                  0x0489,16,"R/W",0,    ""),
    ]


# ═══════════════════════════════════════════════════════════════
#  CLASS 5 — Extension Settings  (RS485 setup lives here!)
#  Address range: 0x0500 ~ 0x0549
# ═══════════════════════════════════════════════════════════════
class Class5(_BaseParamClass):
    CLASS_NAME = "Class 5 — Extension Settings  [RS485 here!]"
    PARAMS = [
        ParamDef("Pr5.00","2nd Pulse Count/Revolution",         0x0500,32,"R/W",10000,"pulse/rev"),
        ParamDef("Pr5.01","2nd Cmd Freq Divider Numerator",     0x0502,32,"R/W",1,    ""),
        ParamDef("Pr5.02","2nd Cmd Freq Divider Denominator",   0x0504,32,"R/W",1,    ""),
        ParamDef("Pr5.04","Driver Prohibition Input",           0x0509,16,"R/W",0,    ""),
        ParamDef("Pr5.06","Servo-off Mode",                     0x050D,16,"R/W",0,    ""),
        ParamDef("Pr5.08","DC Bus Undervoltage Alarm",          0x0513,16,"R/W",50,   "V"),
        ParamDef("Pr5.09","Main Power-off Detection Time",      0x0515,16,"R/W",0,    "ms"),
        ParamDef("Pr5.10","Servo-off due to Alarm Mode",        0x0517,16,"R/W",0,    ""),
        ParamDef("Pr5.11","Servo Braking Torque",               0x0519,16,"R/W",0,    "%"),
        ParamDef("Pr5.12","Overload Level Setting",             0x051B,16,"R/W",0,    "%"),
        ParamDef("Pr5.15","I/O Digital Filter",                 0x051F,16,"R/W",3,    "x0.1ms"),
        ParamDef("Pr5.17","Counter Clearing Input Mode",        0x0523,16,"R/W",1,    ""),
        ParamDef("Pr5.20","Position Unit Settings",             0x0529,16,"R/W",0,    ""),
        ParamDef("Pr5.21","Torque Limit Selection",             0x052B,16,"R/W",0,    ""),
        ParamDef("Pr5.22","2nd Torque Limit",                   0x052D,16,"R/W",300,  "%"),
        ParamDef("Pr5.23","+ve Torque Warning Threshold",       0x052F,16,"R/W",0,    "%"),
        ParamDef("Pr5.24","-ve Torque Warning Threshold",       0x0531,16,"R/W",0,    "%"),
        ParamDef("Pr5.28","LED Initial Status",                 0x0539,16,"R/W",1,    ""),
        ParamDef("Pr5.29","RS485 Communication Mode",           0x053B,16,"R/W",0,    "",   "0=Modbus RTU"),
        ParamDef("Pr5.30","RS485 Baud Rate",                    0x053D,16,"R/W",5,    "",   "0=2400|1=4800|2=9600|3=19200|4=38400|5=57600|6=115200"),
        ParamDef("Pr5.31","RS485 Slave Address",                0x053F,16,"R/W",4,    "",   "1~247"),
        ParamDef("Pr5.32","Max Cmd Pulse Input Frequency",      0x0541,16,"R/W",0,    ""),
        ParamDef("Pr5.35","Front Panel Lock Setting",           0x0547,16,"R/W",0,    ""),
        ParamDef("Pr5.37","Torque Saturation Alarm Time",       0x0549,16,"R/W",500,  "ms"),
    ]


# ═══════════════════════════════════════════════════════════════
#  CLASS 6 — Other Settings   0x0603 ~ 0x067F
# ═══════════════════════════════════════════════════════════════
class Class6(_BaseParamClass):
    CLASS_NAME = "Class 6 — Other Settings"
    PARAMS = [
        ParamDef("Pr6.01","Encoder Zero Position Compensation",  0x0603,16,"R/W",0,  ""),
        ParamDef("Pr6.03","JOG Torque Command",                  0x0607,16,"R/W",350,"%"),
        ParamDef("Pr6.04","JOG Velocity Command",                0x0609,16,"R/W",30, "rpm"),
        ParamDef("Pr6.05","Position 3rd Gain Valid Time",        0x060B,16,"R/W",0,  "ms"),
        ParamDef("Pr6.06","Position 3rd Gain Scale Factor",      0x060D,16,"R/W",100,"%"),
        ParamDef("Pr6.07","Torque Command Additional Value",     0x060F,16,"R/W",0,  "%", "Gravity compensation"),
        ParamDef("Pr6.08","+ve Direction Torque Compensation",   0x0611,16,"R/W",0,  "%"),
        ParamDef("Pr6.09","-ve Direction Torque Compensation",   0x0613,16,"R/W",0,  "%"),
        ParamDef("Pr6.11","Current Response Settings",           0x0617,16,"R/W",100,""),
        ParamDef("Pr6.14","Max Time to Stop After Disable",      0x061D,16,"R/W",500,"ms"),
        ParamDef("Pr6.20","Trial Run Distance",                  0x0629,16,"R/W",10, "rev"),
        ParamDef("Pr6.21","Trial Run Waiting Time",              0x062B,16,"R/W",300,"ms"),
        ParamDef("Pr6.22","Number of Trial Run Cycles",          0x062D,16,"R/W",5,  ""),
        ParamDef("Pr6.25","Trial Run Acceleration",              0x0633,16,"R/W",200,"ms"),
        ParamDef("Pr6.28","Observer Gain",                       0x0639,16,"R/W",0,  ""),
        ParamDef("Pr6.29","Observer Filter",                     0x063B,16,"R/W",0,  ""),
        ParamDef("Pr6.56","Blocked Rotor Alarm Torque",          0x0671,16,"R/W",300,"%"),
        ParamDef("Pr6.57","Blocked Rotor Alarm Delay Time",      0x0673,16,"R/W",400,"ms"),
        ParamDef("Pr6.63","Absolute Multiturn Data Limit",       0x067F,16,"R/W",0,  ""),
    ]


# ═══════════════════════════════════════════════════════════════
#  CLASS B — Status / Monitor Parameters (READ ONLY)
#  Address range: 0x0B00 ~ 0x0B1E    ★ Real-time monitoring
# ═══════════════════════════════════════════════════════════════
class ClassB(_BaseParamClass):
    CLASS_NAME = "Class B — Status Monitor (Read Only)"
    PARAMS = [
        ParamDef("PrB.00","Software Version DSP",              0x0B00,16,"R",0,""),
        ParamDef("PrB.01","Software Version CPLD",             0x0B01,16,"R",0,""),
        ParamDef("PrB.02","Software Version Others",           0x0B02,16,"R",0,""),
        ParamDef("PrB.03","Current Alarm Code",                0x0B03,16,"R",0,"",  "0=No alarm"),
        ParamDef("PrB.04","Motor Not Rotating Cause",          0x0B04,16,"R",0,""),
        ParamDef("PrB.05","Driver Operation Status",           0x0B05,16,"R",0,""),
        ParamDef("PrB.06","Motor Speed Before Filter",         0x0B06,16,"R",0,"rpm"),
        ParamDef("PrB.07","Motor Torque",                      0x0B07,16,"R",0,"%"),
        ParamDef("PrB.08","Motor Current",                     0x0B08,16,"R",0,"A"),
        ParamDef("PrB.09","Motor Speed After Filter",          0x0B09,16,"R",0,"rpm"),
        ParamDef("PrB.10","DC Bus Voltage",                    0x0B0A,16,"R",0,"V"),
        ParamDef("PrB.11","Driver Temperature",                0x0B0B,16,"R",0,"deg C"),
        ParamDef("PrB.12","External Analog Input 1 AI-1",      0x0B0C,16,"R",0,"mV"),
        ParamDef("PrB.13","External Analog Input 2 AI-2",      0x0B0D,16,"R",0,"mV"),
        ParamDef("PrB.14","External Analog Input 3 AI-3",      0x0B0E,16,"R",0,"mV"),
        ParamDef("PrB.15","Motor Overload Rate",               0x0B0F,16,"R",0,"%"),
        ParamDef("PrB.16","Vent Overload Rate",                0x0B10,16,"R",0,"%"),
        ParamDef("PrB.17","Physical DI Input Status",          0x0B11,16,"R",0,"", "Bit0=DI1...Bit7=DI8"),
        ParamDef("PrB.18","Physical DO Output Status",         0x0B12,16,"R",0,"", "Bit0=DO1...Bit4=DO5"),
        ParamDef("PrB.20","Command Position Cmd Unit 32bit",   0x0B14,32,"R",0,""),
        ParamDef("PrB.21","Motor Position Cmd Unit 32bit",     0x0B16,32,"R",0,""),
        ParamDef("PrB.22","Position Deviation Cmd Unit 32bit", 0x0B18,32,"R",0,""),
        ParamDef("PrB.23","Command Position Enc Unit 32bit",   0x0B1A,32,"R",0,""),
        ParamDef("PrB.24","Motor Position Enc Unit 32bit",     0x0B1C,32,"R",0,""),
        ParamDef("PrB.25","Position Deviation Enc Unit 32bit", 0x0B1D,32,"R",0,""),
    ]

    # ── Convenient named properties ──────────────────────────
    @property
    def motor_speed_rpm(self):    return self.prb_06
    @property
    def motor_torque_pct(self):   return self.prb_07
    @property
    def motor_current_a(self):    return self.prb_08
    @property
    def dc_bus_voltage_v(self):   return self.prb_0a
    @property
    def driver_temp_c(self):      return self.prb_0b
    @property
    def current_alarm(self):      return self.prb_03
    @property
    def overload_rate_pct(self):  return self.prb_0f
    @property
    def di_status_bits(self):     return self.prb_11
    @property
    def do_status_bits(self):     return self.prb_12
    @property
    def position_cmd(self):       return self.prb_20   # 32-bit
    @property
    def position_actual(self):    return self.prb_21   # 32-bit
    @property
    def position_deviation(self): return self.prb_22   # 32-bit

    def di_active(self, ch):
        """Check if DI channel (1~8) is active. Returns bool."""
        if self.prb_11 is None: return False
        return bool((self.prb_11 >> (ch - 1)) & 1)

    def do_active(self, ch):
        """Check if DO channel (1~5) is active. Returns bool."""
        if self.prb_12 is None: return False
        return bool((self.prb_12 >> (ch - 1)) & 1)


# ═══════════════════════════════════════════════════════════════
#  CLASS 8 — PR-Control Parameters   0x6000 ~ 0x602F
# ═══════════════════════════════════════════════════════════════
class Class8(_BaseParamClass):
    CLASS_NAME = "Class 8 — PR-Control Parameters"
    PARAMS = [
        ParamDef("Pr8.00","PR Control Enable",                  0x6000,16,"R/W",0,  "",  "0=Off|1=On"),
        ParamDef("Pr8.01","PR Path Count",                      0x6001,16,"R/W",16, ""),
        ParamDef("Pr8.02","PR Control Operation",               0x6002,16,"R/W",0,  ""),
        ParamDef("Pr8.06","Software Positive Limit Hi",         0x6006,16,"R/W",0,  ""),
        ParamDef("Pr8.07","Software Positive Limit Lo",         0x6007,16,"R/W",0,  ""),
        ParamDef("Pr8.08","Software Negative Limit Hi",         0x6008,16,"R/W",0,  ""),
        ParamDef("Pr8.09","Software Negative Limit Lo",         0x6009,16,"R/W",0,  ""),
        ParamDef("Pr8.10","Homing Mode",                        0x600A,16,"R/W",0,  "",  "0=None|1=Z|2=DI"),
        ParamDef("Pr8.11","Homing Zero Position Hi",            0x600B,16,"R/W",0,  ""),
        ParamDef("Pr8.12","Homing Zero Position Lo",            0x600C,16,"R/W",0,  ""),
        ParamDef("Pr8.13","Home Position Offset Hi",            0x600D,16,"R/W",0,  ""),
        ParamDef("Pr8.14","Home Position Offset Lo",            0x600E,16,"R/W",0,  ""),
        ParamDef("Pr8.15","High Homing Velocity",               0x600F,16,"R/W",200,"rpm"),
        ParamDef("Pr8.16","Low Homing Velocity",                0x6010,16,"R/W",50, "rpm"),
        ParamDef("Pr8.17","Homing Acceleration",                0x6011,16,"R/W",100,"ms"),
        ParamDef("Pr8.18","Homing Deceleration",                0x6012,16,"R/W",100,"ms"),
        ParamDef("Pr8.19","Homing Torque Holding Time",         0x6013,16,"R/W",100,"ms"),
        ParamDef("Pr8.20","Homing Torque",                      0x6014,16,"R/W",100,"%"),
        ParamDef("Pr8.21","Homing Overtravel Alarm Range",      0x6015,16,"R/W",0,  "rev"),
        ParamDef("Pr8.22","Emergency Stop at Limit Decel",      0x6016,16,"R/W",10, "ms"),
        ParamDef("Pr8.23","STP Emergency Stop Decel",           0x6017,16,"R/W",50, "ms"),
        ParamDef("Pr8.24","IO Combination Trigger Mode",        0x601A,16,"R/W",0,  ""),
        ParamDef("Pr8.25","IO Combination Filter",              0x601B,16,"R/W",5,  "ms"),
        ParamDef("Pr8.26","S-code Current Output",              0x601C,16,"R/W",0,  ""),
        ParamDef("Pr8.27","PR Warning Status",                  0x601D,16,"R/W",0,  ""),
        ParamDef("Pr8.39","JOG Velocity",                       0x6027,16,"R/W",100,"rpm"),
        ParamDef("Pr8.40","JOG Acceleration",                   0x6028,16,"R/W",100,"ms"),
        ParamDef("Pr8.41","JOG Deceleration",                   0x6029,16,"R/W",100,"ms"),
        ParamDef("Pr8.42","Command Position Hi (Read)",         0x602A,16,"R",  0,  ""),
        ParamDef("Pr8.43","Command Position Lo (Read)",         0x602B,16,"R",  0,  ""),
        ParamDef("Pr8.44","Motor Position Hi (Read)",           0x602C,16,"R",  0,  ""),
        ParamDef("Pr8.45","Motor Position Lo (Read)",           0x602D,16,"R",  0,  ""),
        ParamDef("Pr8.46","Input IO Status",                    0x602E,16,"R",  0,  ""),
        ParamDef("Pr8.47","Output IO Status",                   0x602F,16,"R",  0,  ""),
    ]


# ═══════════════════════════════════════════════════════════════
#  CLASS 9 — PR-Control Path Parameters  0x6200 ~ 0x627F
#  PR0~PR15, each path = 8 registers
# ═══════════════════════════════════════════════════════════════
class Class9(_BaseParamClass):
    CLASS_NAME = "Class 9 — PR-Control Path Parameters (PR0~PR15)"

    # Auto-generate all 16 PR paths
    PARAMS = []
    for _i in range(16):
        _base = 0x6200 + _i * 8
        PARAMS += [
            ParamDef(f"Pr9.{_i*8+0:03d}", f"PR{_i} Mode",          _base+0,16,"R/W",0,  ""),
            ParamDef(f"Pr9.{_i*8+1:03d}", f"PR{_i} Position Hi",   _base+1,16,"R/W",0,  ""),
            ParamDef(f"Pr9.{_i*8+2:03d}", f"PR{_i} Position Lo",   _base+2,16,"R/W",0,  ""),
            ParamDef(f"Pr9.{_i*8+3:03d}", f"PR{_i} Velocity",      _base+3,16,"R/W",60, "rpm"),
            ParamDef(f"Pr9.{_i*8+4:03d}", f"PR{_i} Accel Time",    _base+4,16,"R/W",100,"ms"),
            ParamDef(f"Pr9.{_i*8+5:03d}", f"PR{_i} Decel Time",    _base+5,16,"R/W",100,"ms"),
            ParamDef(f"Pr9.{_i*8+6:03d}", f"PR{_i} Pause Time",    _base+6,16,"R/W",0,  "ms"),
            ParamDef(f"Pr9.{_i*8+7:03d}", f"PR{_i} Special Param", _base+7,16,"R/W",0,  ""),
        ]

    def get_path(self, n):
        """Get dict for PR path n (0~15)."""
        b = n * 8
        keys = ['mode','pos_hi','pos_lo','velocity','accel_ms','decel_ms','pause_ms','special']
        return {k: getattr(self, self._attr_map[self.PARAMS[b+i].code])
                for i, k in enumerate(keys)}

    def position_32bit(self, n):
        """Combine pos_hi + pos_lo into signed 32-bit integer."""
        d = self.get_path(n)
        if d['pos_hi'] is None: return None
        v = ((d['pos_hi'] & 0xFFFF) << 16) | (d['pos_lo'] & 0xFFFF)
        return v - 0x100000000 if v >= 0x80000000 else v


# ═══════════════════════════════════════════════════════════════
#  ServoMonitor — read all classes in one call
# ═══════════════════════════════════════════════════════════════
class ServoMonitor:
    """
    One-stop wrapper — creates all class objects and reads them.

    Example:
        with ServoMonitor('COM3', slave_id=4) as mon:
            mon.read_all()
            print(mon.status.motor_speed_rpm)
            print(mon.status.current_alarm)
            print(mon.comm.pr5_31)      # slave ID

            mon.status.read()           # quick re-read of status only
    """
    def __init__(self, port, slave_id=1, baudrate=9600):
        self.client  = ServoClient(port, slave_id, baudrate)
        self.basic   = Class0(self.client)
        self.gain    = Class1(self.client)
        self.vib     = Class2(self.client)
        self.veltrq  = Class3(self.client)
        self.io      = Class4(self.client)
        self.comm    = Class5(self.client)
        self.other   = Class6(self.client)
        self.status  = ClassB(self.client)
        self.pr_ctrl = Class8(self.client)
        self.pr_path = Class9(self.client)
        self._all    = [self.basic, self.gain, self.vib, self.veltrq,
                        self.io, self.comm, self.other,
                        self.status, self.pr_ctrl, self.pr_path]

    def read_all(self):
        for cls in self._all:
            try:    cls.read()
            except Exception as e:
                log.error(f"Failed {cls.CLASS_NAME}: {e}")

    def read_status_only(self):
        """Fastest — only ClassB real-time registers."""
        self.status.read()

    def close(self): self.client.close()
    def __enter__(self): return self
    def __exit__(self, *_): self.close()


# ─────────────────────────────────────────────────────────────
#  Quick demo / test
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys, time
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")

    # PORT     = sys.argv[1] if len(sys.argv) > 1 else "COM3"
    # SLAVE_ID = int(sys.argv[2]) if len(sys.argv) > 2 else 4

    PORT = "/dev/servoX"
    SLAVE_ID = 1
    

    print(f"\n{'='*60}")
    print(f"  Leadshine EL7-RS  port={PORT}  slave={SLAVE_ID}")
    print(f"{'='*60}")

    try:
        with ServoClient(PORT, slave_id=SLAVE_ID) as servo:

            # ── Class 5: check RS485 settings ─────────────
            print("\n[Class 5] RS485 / Extension Settings")
            c5 = Class5(servo)
            c5.read()
            print(f"  Baud Rate setting : Pr5.30 = {c5.pr5_30}  (5=57600bps)")
            print(f"  Slave Address     : Pr5.31 = {c5.pr5_31}")
            print(f"  Comm Mode         : Pr5.29 = {c5.pr5_29}  (0=Modbus RTU)")

            # ── Class 0: key settings ──────────────────────
            print("\n[Class 0] Basic Settings")
            c0 = Class0(servo)
            c0.read()
            print(f"  Control Mode  : Pr0.01 = {c0.pr0_01}  (0=Pos|1=Vel|2=Torq|6=PR)")
            print(f"  Inertia Ratio : Pr0.04 = {c0.pr0_04} %")
            print(f"  Torque Limit  : Pr0.13 = {c0.pr0_13} %")
            print(f"  Pulse/Rev     : Pr0.08 = {c0.pr0_08}")

            # ── ClassB: real-time monitor loop ────────────
            print("\n[ClassB] Real-time Monitor (5 samples, 1s interval)")
            print(f"  {'Speed(rpm)':<12}{'Torque(%)':<11}{'Current(A)':<12}"
                  f"{'VBus(V)':<9}{'Temp(C)':<9}{'Overload%':<11}{'Alarm'}")
            print(f"  {'-'*70}")
            cB = ClassB(servo)
            for _ in range(5):
                cB.read()
                print(f"  {cB.motor_speed_rpm or 0:<12}"
                      f"{cB.motor_torque_pct or 0:<11}"
                      f"{cB.motor_current_a or 0:<12}"
                      f"{cB.dc_bus_voltage_v or 0:<9}"
                      f"{cB.driver_temp_c or 0:<9}"
                      f"{cB.overload_rate_pct or 0:<11}"
                      f"{cB.current_alarm or 0}")
                time.sleep(1.0)

            # ── DI/DO status ───────────────────────────────
            print("\n[ClassB] Digital I/O Status")
            for ch in range(1, 9):
                state = "ON " if cB.di_active(ch) else "off"
                print(f"  DI{ch} = {state}", end="   ")
            print()
            for ch in range(1, 6):
                state = "ON " if cB.do_active(ch) else "off"
                print(f"  DO{ch} = {state}", end="   ")
            print()

    except ConnectionError as e:
        print(f"\nConnection failed: {e}")
        print("Check: COM port | baud=57600 | slave_id=4 | RS485 wiring")
    except Exception as e:
        print(f"\nError: {e}")
        raise