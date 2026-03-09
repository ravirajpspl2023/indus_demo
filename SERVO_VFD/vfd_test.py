"""
============================================================
Delta VFD-C200 Series AC Drive — Modbus RTU/ASCII Client
============================================================
Library  : pymodbus >= 3.x
Protocol : Modbus RTU or ASCII over RS-485 (RJ45 / terminal)
Default  : Baud=9600, 7N2 ASCII (Pr09-04=1), Slave ID=1

Delta C200 Address formula:
  Parameter Pr.GG-NN → Modbus Hex = GGNNh
  Example : Pr.01-12  → 0x010C  → decimal 268

Special registers:
  2000H — Command (Run/Stop/FWD/REV)    Write only
  2001H — Frequency command (×0.01 Hz)  Write only
  2002H — Control (EF / Reset / BB)     Write only
  2100H — Fault code                    Read only
  2101H — Drive status bits             Read only
  2102H — Frequency command F  (×0.01)  Read only
  2103H — Output frequency H   (×0.01)  Read only
  2104H — Output current A     (×0.1)   Read only
  2105H — DC bus voltage U     (×0.1)   Read only
  2106H — Output voltage E     (×0.1)   Read only
  210BH — Output torque %      (×0.1)   Read only
  210CH — Motor speed rpm               Read only
  220EH — IGBT temperature °C           Read only
  220FH — Capacitor temperature °C      Read only
  2210H — DI input status bits          Read only
  2211H — DO output status bits         Read only

Design:
  - Each parameter Group (00~11) is a Python class
  - read()  → ONE bulk Modbus call (start_addr → end_addr)
  - Parameters auto-mapped from bulk response by address offset
  - 32-bit param = two consecutive registers (Hi+Lo)
  - write() → single register write (Fn06)
  - DriveControl class — Run/Stop/Freq/Reset commands
  - DriveMonitor  class — real-time 2100H~2211H registers

Usage:
    from delta_c200_modbus import VFDClient, Group09, Group00, DriveMonitor, DriveControl

    vfd = VFDClient(port='COM3', slave_id=1)

    # RS485 settings
    g09 = Group09(vfd)
    g09.read()
    print(g09.pr09_00)   # slave address
    print(g09.pr09_01)   # baud rate

    # Real-time monitor
    mon = DriveMonitor(vfd)
    mon.read()
    print(mon.output_freq_hz)
    print(mon.output_current_a)
    print(mon.dc_bus_voltage_v)
    print(mon.fault_code)

    # Control
    ctrl = DriveControl(vfd)
    ctrl.set_frequency(50.0)
    ctrl.run_fwd()
    ctrl.stop()
    ctrl.reset_fault()

    vfd.close()
============================================================
"""

from dataclasses import dataclass
from typing import Any, List, Optional
import logging
import time

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
    code   : str          # "Pr09-04"
    name   : str
    addr   : int          # Modbus address (decimal)
    bits   : int  = 16    # 16 or 32
    rw     : str  = "R/W" # "R" | "R/W"
    default: Any  = 0
    unit   : str  = ""
    note   : str  = ""


# ─────────────────────────────────────────────────────────────
#  Modbus Serial Client Wrapper
# ─────────────────────────────────────────────────────────────
class VFDClient:
    """
    RS-485 Modbus connection to Delta VFD-C200.

    Parameters
    ----------
    port     : Serial port  e.g. 'COM3' or '/dev/ttyUSB0'
    slave_id : Pr09-00, default=1
    baudrate : Pr09-01, default=9600
    mode     : 'RTU' or 'ASCII' (Pr09-04)
               RTU  → bytesize=8, default 8N1 (Pr09-04=12)
               ASCII→ bytesize=7, default 7N2 (Pr09-04=1)
    timeout  : seconds
    """
    BAUD_MAP = {
        4.8:  4800,  6.0:  6000,  9.6:  9600,
        19.2: 19200, 38.4: 38400, 57.6: 57600,
        76.8: 76800, 115.2:115200,
    }

    def __init__(
        self,
        port     : str,
        slave_id : int   = 1,
        baudrate : int   = 9600,
        mode     : str   = 'RTU',
        timeout  : float = 1.0,
    ):
        self.slave_id = slave_id
        self.mode     = mode.upper()

        # Delta C200 ASCII default: 7-bit, N parity, 2 stop
        # Delta C200 RTU  default: 8-bit, N parity, 1 stop
        if self.mode == 'ASCII':
            bs, par, sb = 7, 'N', 2
        else:
            bs, par, sb = 8, 'N', 1

        self._client = ModbusSerialClient(
            port=port, baudrate=baudrate,
            bytesize=bs, parity=par, stopbits=sb, timeout=timeout,
        )
        if not self._client.connect():
            raise ConnectionError(f"Cannot open {port}")
        log.info(f"Connected  port={port}  slave={slave_id}  baud={baudrate}  mode={mode}")

    def read_registers(self, start_addr: int, count: int) -> List[int]:
        """Read `count` holding registers from start_addr (Fn 03)."""
        resp = self._client.read_holding_registers(
            address=start_addr, count=count, slave=self.slave_id)
        if resp.isError():
            raise ModbusException(
                f"Read error  addr=0x{start_addr:04X}  count={count}")
        return list(resp.registers)

    def write_register(self, addr: int, value: int) -> None:
        """Write single 16-bit register (Fn 06)."""
        resp = self._client.write_register(
            address=addr, value=int(value) & 0xFFFF, slave=self.slave_id)
        if resp.isError():
            raise ModbusException(f"Write error  addr=0x{addr:04X}")
        log.debug(f"Written  0x{addr:04X} = {value}")

    def write_registers(self, start_addr: int, values: List[int]) -> None:
        """Write multiple 16-bit registers (Fn 16)."""
        resp = self._client.write_registers(
            address=start_addr,
            values=[v & 0xFFFF for v in values],
            slave=self.slave_id)
        if resp.isError():
            raise ModbusException(f"Multi-write error  addr=0x{start_addr:04X}")

    def close(self):
        self._client.close()

    def __enter__(self): return self
    def __exit__(self, *_): self.close()


# ─────────────────────────────────────────────────────────────
#  Base Parameter Group
# ─────────────────────────────────────────────────────────────
class _BaseGroup:
    """
    Base for all C200 parameter groups.

    Subclass defines:
        GROUP_NAME : str
        PARAMS     : List[ParamDef]  — ordered list

    Delta C200 address formula:
        Pr.GG-NN → addr = GG*256 + NN  (= 0xGGNN decimal)

    read()  → ONE bulk Modbus call  start_addr → end_addr
    write() → single register write via Fn06
    """
    GROUP_NAME: str = "Base"
    PARAMS: List[ParamDef] = []

    def __init__(self, client: VFDClient):
        self._client = client
        # code → attribute name:  "Pr09-04" → "pr09_04"
        self._attr_map = {
            p.code: p.code.lower().replace('-', '_').replace('.', '_')
            for p in self.PARAMS
        }
        for attr in self._attr_map.values():
            setattr(self, attr, None)

    @property
    def start_addr(self) -> int:
        return min(p.addr for p in self.PARAMS)

    @property
    def end_addr(self) -> int:
        return max(p.addr + (1 if p.bits == 32 else 0) for p in self.PARAMS)

    @property
    def read_count(self) -> int:
        return self.end_addr - self.start_addr + 1

    # ── BULK READ ──────────────────────────────────────────
    def read(self) -> None:
        """
        ONE Modbus call reads all registers for this group
        (start_addr to end_addr), then maps each param
        to its attribute automatically by address offset.
        """
        log.info(
            f"[{self.GROUP_NAME}]  "
            f"0x{self.start_addr:04X} ~ 0x{self.end_addr:04X}  "
            f"({self.read_count} regs)"
        )
        regs = self._client.read_registers(self.start_addr, self.read_count)

        for p in self.PARAMS:
            offset = p.addr - self.start_addr
            if offset < 0 or offset >= len(regs):
                continue
            if p.bits == 32:
                hi  = regs[offset]
                lo  = regs[offset + 1] if (offset + 1) < len(regs) else 0
                val = (hi << 16) | lo
                if val >= 0x80000000:
                    val -= 0x100000000
            else:
                val = regs[offset]
                if val >= 0x8000:
                    val -= 0x10000

            setattr(self, self._attr_map[p.code], val)

        log.info(f"  -> {len(self.PARAMS)} params mapped")

    # ── WRITE ──────────────────────────────────────────────
    def write(self, attr_name: str) -> None:
        """Write a single parameter back to drive."""
        code = next(
            (c for c, a in self._attr_map.items() if a == attr_name), None)
        if code is None:
            raise ValueError(f"Unknown attribute: {attr_name}")
        p = next(x for x in self.PARAMS if x.code == code)
        if p.rw == 'R':
            raise PermissionError(f"{code} is read-only!")
        value = getattr(self, attr_name)
        if value is None:
            raise ValueError(f"{attr_name} is None — set a value first")
        if p.bits == 32:
            v = int(value) & 0xFFFFFFFF
            self._client.write_registers(p.addr, [(v >> 16) & 0xFFFF, v & 0xFFFF])
        else:
            self._client.write_register(p.addr, int(value) & 0xFFFF)
        log.info(f"Written  {code}  0x{p.addr:04X}  = {value}")

    # ── PRINT ──────────────────────────────────────────────
    def print_all(self) -> None:
        print(f"\n{'='*74}")
        print(f"  {self.GROUP_NAME}")
        print(f"  Bulk read: 0x{self.start_addr:04X}~0x{self.end_addr:04X}  ({self.read_count} regs)")
        print(f"{'='*74}")
        print(f"  {'Code':<12} {'Hex':<8} {'Name':<40} {'Value':<10} {'Unit'}")
        print(f"  {'-'*74}")
        for p in self.PARAMS:
            v = getattr(self, self._attr_map[p.code])
            print(f"  {p.code:<12} 0x{p.addr:04X}   {p.name:<40} {str(v):<10} {p.unit}")
        print(f"{'='*74}\n")

    def to_dict(self) -> dict:
        return {
            p.code: {
                "name" : p.name,
                "addr" : f"0x{p.addr:04X}",
                "value": getattr(self, self._attr_map[p.code]),
                "unit" : p.unit,
            }
            for p in self.PARAMS
        }

    def __repr__(self):
        return (f"<{self.__class__.__name__} "
                f"0x{self.start_addr:04X}~0x{self.end_addr:04X} "
                f"{len(self.PARAMS)} params>")


# ═══════════════════════════════════════════════════════════════
#  GROUP 00 — Drive Parameters  0x0000 ~ 0x0032
# ═══════════════════════════════════════════════════════════════
class Group00(_BaseGroup):
    GROUP_NAME = "Group 00 — Drive Parameters"
    PARAMS = [
        ParamDef("Pr00-00","Identity Code of AC Drive",        0x0000,16,"R",   0,    "",    "Read-only model ID"),
        ParamDef("Pr00-01","Rated Current Display",            0x0001,16,"R",   0,    "A"),
        ParamDef("Pr00-02","Parameter Reset",                  0x0002,16,"R/W", 0,    "",    "9: Reset all to defaults"),
        ParamDef("Pr00-03","Start-up Display Selection",       0x0003,16,"R/W", 0,    "",    "0=Hz|1=A|2=RPM|3=User"),
        ParamDef("Pr00-04","Content of Multi-function Display",0x0004,16,"R/W", 0,    ""),
        ParamDef("Pr00-05","User-defined Value",               0x0005,16,"R/W", 0,    ""),
        ParamDef("Pr00-06","Firmware Version",                 0x0006,16,"R",   0,    ""),
        ParamDef("Pr00-07","Parameter Protection Password",    0x0007,16,"R/W", 0,    ""),
        ParamDef("Pr00-08","Keypad Mode",                      0x0008,16,"R/W", 0,    ""),
        ParamDef("Pr00-10","Control Mode",                     0x000A,16,"R/W", 0,    "",    "0=V/F|1=V/F+PG|2=SVC|3=FOC"),
        ParamDef("Pr00-11","Speed Control Mode",               0x000B,16,"R/W", 0,    ""),
        ParamDef("Pr00-12","Reserved",                         0x000C,16,"R/W", 0,    ""),
        ParamDef("Pr00-13","Digital Keypad STOP/RESET",        0x000D,16,"R/W", 1,    "",    "0=Disable STOP|1=Enable STOP"),
        ParamDef("Pr00-14","Carrier Frequency",                0x000E,16,"R/W", 6,    "kHz", "2~15kHz"),
        ParamDef("Pr00-15","Lead-Lag Function",                0x000F,16,"R/W", 0,    ""),
        ParamDef("Pr00-16","Auto-tuning for Rotating Motor",   0x0010,16,"R/W", 0,    ""),
        ParamDef("Pr00-17","Carrier Frequency Reduction",      0x0011,16,"R/W", 0,    ""),
        ParamDef("Pr00-18","Slip Compensation for V/F Control",0x0012,16,"R/W", 0,    ""),
        ParamDef("Pr00-19","Control Signal Selection",         0x0013,16,"R/W", 0,    ""),
        ParamDef("Pr00-20","Source of Frequency Command AUTO", 0x0014,16,"R/W", 0,    "",    "★ 0=Keypad|1=RS485|2=Analog|..."),
        ParamDef("Pr00-21","Source of Operation Command AUTO", 0x0015,16,"R/W", 0,    "",    "★ 0=Keypad|1=External|2=RS485"),
        ParamDef("Pr00-22","Stop Method",                      0x0016,16,"R/W", 0,    "",    "0=Ramp|1=Coast"),
        ParamDef("Pr00-23","Auto-restart after Fault",         0x0017,16,"R/W", 0,    "times"),
        ParamDef("Pr00-24","Auto-restart Interval Time",       0x0018,16,"R/W", 60,   "s"),
        ParamDef("Pr00-25","Motor Speed Display",              0x0019,16,"R/W", 0,    ""),
        ParamDef("Pr00-26","Max User-defined Value",           0x001A,16,"R/W", 0,    ""),
        ParamDef("Pr00-27","User-defined Coefficient K",       0x001B,16,"R/W", 0,    ""),
        ParamDef("Pr00-28","Display Coefficient C",            0x001C,16,"R/W", 0,    ""),
        ParamDef("Pr00-29","Decimal Places",                   0x001D,16,"R/W", 0,    ""),
        ParamDef("Pr00-30","Software Version",                 0x001E,16,"R",   0,    ""),
        ParamDef("Pr00-32","Energy-saving Control",            0x0020,16,"R/W", 0,    ""),
        ParamDef("Pr00-40","HAND Mode Source of Freq Command", 0x0028,16,"R/W", 0,    ""),
        ParamDef("Pr00-41","HAND Mode Source of Operation Cmd",0x0029,16,"R/W", 0,    ""),
        ParamDef("Pr00-48","Display Filter",                   0x0030,16,"R/W", 0,    ""),
        ParamDef("Pr00-50","Serial Comm. Freq. Command",       0x0032,16,"R/W", 0,    "×0.01Hz","RS485 frequency last written"),
    ]


# ═══════════════════════════════════════════════════════════════
#  GROUP 01 — Basic Parameters  0x0100 ~ 0x012E
# ═══════════════════════════════════════════════════════════════
class Group01(_BaseGroup):
    GROUP_NAME = "Group 01 — Basic Parameters"
    PARAMS = [
        ParamDef("Pr01-00","Max Operation Frequency",          0x0100,16,"R/W",60,   "Hz",  "★"),
        ParamDef("Pr01-01","Output Frequency at Max Voltage",  0x0101,16,"R/W",60,   "Hz"),
        ParamDef("Pr01-02","Output Voltage at Max Freq (V/F)", 0x0102,16,"R/W",220,  "V"),
        ParamDef("Pr01-03","Mid Frequency for V/F Curve",      0x0103,16,"R/W",0,    "Hz"),
        ParamDef("Pr01-04","Mid Voltage for V/F Curve",        0x0104,16,"R/W",0,    "V"),
        ParamDef("Pr01-05","Min Output Frequency",             0x0105,16,"R/W",0,    "Hz"),
        ParamDef("Pr01-06","Min Output Voltage",               0x0106,16,"R/W",0,    "V"),
        ParamDef("Pr01-07","Upper Limit of Output Frequency",  0x0107,16,"R/W",120,  "Hz",  "Max allowed frequency"),
        ParamDef("Pr01-08","Lower Limit of Output Frequency",  0x0108,16,"R/W",0,    "Hz",  "Min allowed frequency"),
        ParamDef("Pr01-09","Output Freq for Zero Speed",       0x0109,16,"R/W",0,    "Hz"),
        ParamDef("Pr01-10","Output Voltage for Zero Speed",    0x010A,16,"R/W",0,    "V"),
        ParamDef("Pr01-11","V/F Curve Selection",              0x010B,16,"R/W",0,    ""),
        ParamDef("Pr01-12","Acceleration Time 1",              0x010C,16,"R/W",10,   "s",   "★ ×0.01s (write 1000 = 10.00s)"),
        ParamDef("Pr01-13","Deceleration Time 1",              0x010D,16,"R/W",10,   "s",   "★ ×0.01s"),
        ParamDef("Pr01-14","Acceleration Time 2",              0x010E,16,"R/W",10,   "s"),
        ParamDef("Pr01-15","Deceleration Time 2",              0x010F,16,"R/W",10,   "s"),
        ParamDef("Pr01-16","Acceleration Time 3",              0x0110,16,"R/W",10,   "s"),
        ParamDef("Pr01-17","Deceleration Time 3",              0x0111,16,"R/W",10,   "s"),
        ParamDef("Pr01-18","Acceleration Time 4",              0x0112,16,"R/W",10,   "s"),
        ParamDef("Pr01-19","Deceleration Time 4",              0x0113,16,"R/W",10,   "s"),
        ParamDef("Pr01-20","JOG Acceleration Time",            0x0114,16,"R/W",10,   "s"),
        ParamDef("Pr01-21","JOG Deceleration Time",            0x0115,16,"R/W",10,   "s"),
        ParamDef("Pr01-22","JOG Frequency",                    0x0116,16,"R/W",6,    "Hz",  "★"),
        ParamDef("Pr01-23","1st/4th Accel/Decel Switching Freq",0x0117,16,"R/W",0,   "Hz"),
        ParamDef("Pr01-24","S-curve Accel Begin",              0x0118,16,"R/W",0,    "s"),
        ParamDef("Pr01-25","S-curve Accel End",                0x0119,16,"R/W",0,    "s"),
        ParamDef("Pr01-26","S-curve Decel Begin",              0x011A,16,"R/W",0,    "s"),
        ParamDef("Pr01-27","S-curve Decel End",                0x011B,16,"R/W",0,    "s"),
        ParamDef("Pr01-28","Skip Frequency 1 Upper Limit",     0x011C,16,"R/W",0,    "Hz"),
        ParamDef("Pr01-29","Skip Frequency 1 Lower Limit",     0x011D,16,"R/W",0,    "Hz"),
        ParamDef("Pr01-30","Skip Frequency 2 Upper Limit",     0x011E,16,"R/W",0,    "Hz"),
        ParamDef("Pr01-31","Skip Frequency 2 Lower Limit",     0x011F,16,"R/W",0,    "Hz"),
        ParamDef("Pr01-32","Skip Frequency 3 Upper Limit",     0x0120,16,"R/W",0,    "Hz"),
        ParamDef("Pr01-33","Skip Frequency 3 Lower Limit",     0x0121,16,"R/W",0,    "Hz"),
        ParamDef("Pr01-34","Zero Speed Operation",             0x0122,16,"R/W",0,    ""),
        ParamDef("Pr01-43","V/F Curve Selection",              0x012B,16,"R/W",0,    ""),
        ParamDef("Pr01-46","Voltage Recovery Rate",            0x012E,16,"R/W",0,    ""),
    ]


# ═══════════════════════════════════════════════════════════════
#  GROUP 02 — Digital I/O Parameters  0x0200 ~ 0x0237
# ═══════════════════════════════════════════════════════════════
class Group02(_BaseGroup):
    GROUP_NAME = "Group 02 — Digital Input / Output"
    PARAMS = [
        ParamDef("Pr02-00","2/3-Wire Operation Control",       0x0200,16,"R/W",0,  "",  "0=2-wire|1=3-wire"),
        ParamDef("Pr02-01","Multi-function Input MI1",         0x0201,16,"R/W",1,  "",  "1=FWD/STOP|6=JOG|19=UP|20=DOWN"),
        ParamDef("Pr02-02","Multi-function Input MI2",         0x0202,16,"R/W",2,  "",  "2=REV/STOP"),
        ParamDef("Pr02-03","Multi-function Input MI3",         0x0203,16,"R/W",3,  ""),
        ParamDef("Pr02-04","Multi-function Input MI4",         0x0204,16,"R/W",4,  ""),
        ParamDef("Pr02-05","Multi-function Input MI5",         0x0205,16,"R/W",0,  ""),
        ParamDef("Pr02-06","Multi-function Input MI6",         0x0206,16,"R/W",0,  ""),
        ParamDef("Pr02-07","Multi-function Input MI7",         0x0207,16,"R/W",0,  ""),
        ParamDef("Pr02-08","Multi-function Input MI8",         0x0208,16,"R/W",0,  ""),
        ParamDef("Pr02-09","Digital Input Debounce Time",      0x0209,16,"R/W",1,  "×2ms"),
        ParamDef("Pr02-10","DI Signal Level Detection",        0x020A,16,"R/W",0,  ""),
        ParamDef("Pr02-11","Digital Input Filter",             0x020B,16,"R/W",1,  ""),
        ParamDef("Pr02-12","Digital Input Status",             0x020C,16,"R",  0,  "",  "Read-only bit status"),
        ParamDef("Pr02-13","Multi-function Output RY1",        0x020D,16,"R/W",11, "",  "★ 0=No func|1=Run|2=At-speed|11=Fault"),
        ParamDef("Pr02-14","Multi-function Output RY2",        0x020E,16,"R/W",1,  ""),
        ParamDef("Pr02-15","Output Signal Level RY1",          0x020F,16,"R/W",0,  ""),
        ParamDef("Pr02-16","Multi-function Output MO1",        0x0210,16,"R/W",0,  ""),
        ParamDef("Pr02-17","Multi-function Output MO2",        0x0211,16,"R/W",0,  ""),
        ParamDef("Pr02-18","Digital Output Status",            0x0212,16,"R",  0,  "",  "Read-only bit status"),
        ParamDef("Pr02-36","Digital Input Invert",             0x0224,16,"R/W",0,  ""),
        ParamDef("Pr02-50","DI Current Status (read-only)",    0x0232,16,"R",  0,  "",  "★ Current DI state bits"),
        ParamDef("Pr02-51","DO Current Status (read-only)",    0x0233,16,"R",  0,  "",  "★ Current DO state bits"),
    ]


# ═══════════════════════════════════════════════════════════════
#  GROUP 03 — Analog Input / Output  0x0300 ~ 0x0332
# ═══════════════════════════════════════════════════════════════
class Group03(_BaseGroup):
    GROUP_NAME = "Group 03 — Analog Input / Output"
    PARAMS = [
        ParamDef("Pr03-00","AVI Analog Input Selection",       0x0300,16,"R/W",1,  "",   "0=No func|1=Freq cmd|2=Torque|4=PID target|5=PID feedback"),
        ParamDef("Pr03-01","ACI Analog Input Selection",       0x0301,16,"R/W",0,  ""),
        ParamDef("Pr03-02","AUI Analog Input Selection",       0x0302,16,"R/W",0,  ""),
        ParamDef("Pr03-03","AVI Positive Bias",                0x0303,16,"R/W",0,  "%",  "-100~100"),
        ParamDef("Pr03-04","ACI Positive Bias",                0x0304,16,"R/W",0,  "%"),
        ParamDef("Pr03-05","AUI Positive Bias",                0x0305,16,"R/W",0,  "%"),
        ParamDef("Pr03-07","AVI Negative Bias",                0x0307,16,"R/W",0,  "%"),
        ParamDef("Pr03-11","AVI Gain",                         0x030B,16,"R/W",100,"",   "-500~500"),
        ParamDef("Pr03-12","ACI Gain",                         0x030C,16,"R/W",100,""),
        ParamDef("Pr03-13","AUI Gain",                         0x030D,16,"R/W",100,""),
        ParamDef("Pr03-15","AVI Filter Time",                  0x030F,16,"R/W",50, "×0.01s"),
        ParamDef("Pr03-16","ACI Filter Time",                  0x0310,16,"R/W",50, "×0.01s"),
        ParamDef("Pr03-17","AUI Filter Time",                  0x0311,16,"R/W",50, "×0.01s"),
        ParamDef("Pr03-20","AFM1 Output Function",             0x0314,16,"R/W",0,  ""),
        ParamDef("Pr03-21","AFM1 Output Gain",                 0x0315,16,"R/W",100,"%"),
        ParamDef("Pr03-23","AFM2 Output Function",             0x0317,16,"R/W",0,  ""),
        ParamDef("Pr03-24","AFM2 Output Gain",                 0x0318,16,"R/W",100,"%"),
        ParamDef("Pr03-28","AVI Input Type",                   0x031C,16,"R/W",0,  "",   "0=0-10V|1=0-20mA|2=4-20mA"),
        ParamDef("Pr03-29","ACI Input Type",                   0x031D,16,"R/W",2,  "",   "0=0-10V|1=0-20mA|2=4-20mA"),
        ParamDef("Pr03-50","AVI Analog Monitor",               0x0332,16,"R",  0,  "%",  "Read-only current AVI value"),
    ]


# ═══════════════════════════════════════════════════════════════
#  GROUP 04 — Multi-step Speed  0x0400 ~ 0x040E
# ═══════════════════════════════════════════════════════════════
class Group04(_BaseGroup):
    GROUP_NAME = "Group 04 — Multi-step Speed"
    PARAMS = [
        ParamDef("Pr04-00","1st Step Speed Frequency",         0x0400,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-01","2nd Step Speed Frequency",         0x0401,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-02","3rd Step Speed Frequency",         0x0402,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-03","4th Step Speed Frequency",         0x0403,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-04","5th Step Speed Frequency",         0x0404,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-05","6th Step Speed Frequency",         0x0405,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-06","7th Step Speed Frequency",         0x0406,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-07","8th Step Speed Frequency",         0x0407,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-08","9th Step Speed Frequency",         0x0408,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-09","10th Step Speed Frequency",        0x0409,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-10","11th Step Speed Frequency",        0x040A,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-11","12th Step Speed Frequency",        0x040B,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-12","13th Step Speed Frequency",        0x040C,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-13","14th Step Speed Frequency",        0x040D,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-14","15th Step Speed Frequency",        0x040E,16,"R/W",0,  "Hz"),
    ]


# ═══════════════════════════════════════════════════════════════
#  GROUP 05 — Motor Parameters  0x0500 ~ 0x052C
# ═══════════════════════════════════════════════════════════════
class Group05(_BaseGroup):
    GROUP_NAME = "Group 05 — Motor Parameters"
    PARAMS = [
        ParamDef("Pr05-00","Motor Auto-tuning",                0x0500,16,"R/W",0,  "",  "0=Off|1=Rolling IM|2=Static IM|4=Rolling PM"),
        ParamDef("Pr05-01","Motor Rated Current",              0x0501,16,"R/W",0,  "A", "★ From nameplate"),
        ParamDef("Pr05-02","Motor Rated Power",                0x0502,16,"R/W",0,  "kW","★ From nameplate"),
        ParamDef("Pr05-03","Motor Rated Speed",                0x0503,16,"R/W",1710,"RPM","★ From nameplate"),
        ParamDef("Pr05-04","Motor Rated Frequency",            0x0504,16,"R/W",60, "Hz"),
        ParamDef("Pr05-05","Motor No-load Current",            0x0505,16,"R/W",0,  "A", "Auto-set after tuning"),
        ParamDef("Pr05-06","Motor Stator Resistance R1",       0x0506,16,"R/W",0,  "Ω"),
        ParamDef("Pr05-07","Motor Rotor Resistance R2",        0x0507,16,"R/W",0,  "Ω"),
        ParamDef("Pr05-08","Motor Magnetizing Inductance Lm",  0x0508,16,"R/W",0,  "mH"),
        ParamDef("Pr05-09","Motor Stator Inductance Lx",       0x0509,16,"R/W",0,  "mH"),
        ParamDef("Pr05-11","Motor Number of Poles",            0x050B,16,"R/W",4,  "",  "★ From nameplate"),
        ParamDef("Pr05-12","Motor 1/2 Selection",              0x050C,16,"R/W",0,  "",  "0=Motor1|1=Motor2"),
        ParamDef("Pr05-13","Motor 2 Rated Current",            0x050D,16,"R/W",0,  "A"),
        ParamDef("Pr05-14","Motor 2 Rated Power",              0x050E,16,"R/W",0,  "kW"),
        ParamDef("Pr05-15","Motor 2 Rated Speed",              0x050F,16,"R/W",1710,"RPM"),
        ParamDef("Pr05-22","Induction Motor Slip Compensation",0x0516,16,"R/W",0,  ""),
        ParamDef("Pr05-26","Energy Consumption Accumulate",    0x051A,16,"R",  0,  "kWh","Read-only"),
        ParamDef("Pr05-28","Run Counter (Total)",              0x051C,16,"R",  0,  ""),
        ParamDef("Pr05-29","Total Operation Time",             0x051D,16,"R",  0,  "min"),
    ]


# ═══════════════════════════════════════════════════════════════
#  GROUP 06 — Protection Parameters  0x0600 ~ 0x0649
# ═══════════════════════════════════════════════════════════════
class Group06(_BaseGroup):
    GROUP_NAME = "Group 06 — Protection Parameters"
    PARAMS = [
        ParamDef("Pr06-00","Low Voltage Level",                0x0600,16,"R/W",190, "V"),
        ParamDef("Pr06-01","Over-voltage Stall Prevention",    0x0601,16,"R/W",380, "V"),
        ParamDef("Pr06-03","Over-current Stall Prevention Accel",0x0603,16,"R/W",150,"%"),
        ParamDef("Pr06-04","Over-current Stall Prevention Oper",0x0604,16,"R/W",150,"%"),
        ParamDef("Pr06-06","Over-torque Detection Selection 1",0x0606,16,"R/W",0,  ""),
        ParamDef("Pr06-07","Over-torque Detection Level 1",    0x0607,16,"R/W",150,"%"),
        ParamDef("Pr06-08","Over-torque Detection Time 1",     0x0608,16,"R/W",0,  "s"),
        ParamDef("Pr06-09","Over-torque Detection Selection 2",0x0609,16,"R/W",0,  ""),
        ParamDef("Pr06-10","Over-torque Detection Level 2",    0x060A,16,"R/W",150,"%"),
        ParamDef("Pr06-11","Over-torque Detection Time 2",     0x060B,16,"R/W",0,  "s"),
        ParamDef("Pr06-12","Current Limit",                    0x060C,16,"R/W",170,"%",  "0~250%"),
        ParamDef("Pr06-13","Electronic Thermal Relay Selection",0x060D,16,"R/W",2,  ""),
        ParamDef("Pr06-14","Electronic Thermal Relay Level",   0x060E,16,"R/W",0,  "%"),
        ParamDef("Pr06-17","Fault Record 1 (Recent)",          0x0611,16,"R",  0,  "",  "★ 0=No fault|1=OCA|7=OVA|16=OH1|21=OL"),
        ParamDef("Pr06-18","Fault Record 2",                   0x0612,16,"R",  0,  ""),
        ParamDef("Pr06-19","Fault Record 3",                   0x0613,16,"R",  0,  ""),
        ParamDef("Pr06-20","Fault Record 4",                   0x0614,16,"R",  0,  ""),
        ParamDef("Pr06-21","Fault Record 5",                   0x0615,16,"R",  0,  ""),
        ParamDef("Pr06-22","Fault Record 6 (Oldest)",          0x0616,16,"R",  0,  ""),
        ParamDef("Pr06-25","Fault Output Option 1",            0x0619,16,"R/W",0,  ""),
        ParamDef("Pr06-28","Motor Thermal Relay",              0x061C,16,"R/W",0,  ""),
        ParamDef("Pr06-29","PTC Thermistor Detection Level",   0x061D,16,"R/W",0,  ""),
        ParamDef("Pr06-63","Fault Record 1 Day",               0x063F,16,"R",  0,  "day"),
        ParamDef("Pr06-64","Fault Record 1 Min",               0x0640,16,"R",  0,  "min"),
        ParamDef("Pr06-65","Fault Record 2 Day",               0x0641,16,"R",  0,  "day"),
        ParamDef("Pr06-66","Fault Record 2 Min",               0x0642,16,"R",  0,  "min"),
        ParamDef("Pr06-67","Fault Record 3 Day",               0x0643,16,"R",  0,  "day"),
        ParamDef("Pr06-68","Fault Record 3 Min",               0x0644,16,"R",  0,  "min"),
        ParamDef("Pr06-73","Fault Record 6 Min",               0x0649,16,"R",  0,  "min"),
    ]


# ═══════════════════════════════════════════════════════════════
#  GROUP 07 — Special Parameters  0x0700 ~ 0x071F
# ═══════════════════════════════════════════════════════════════
class Group07(_BaseGroup):
    GROUP_NAME = "Group 07 — Special Parameters"
    PARAMS = [
        ParamDef("Pr07-00","Software Brake Level",             0x0700,16,"R/W",380, "V",  "DC bus level to activate brake"),
        ParamDef("Pr07-01","DC Brake Current Level",           0x0701,16,"R/W",0,   "%"),
        ParamDef("Pr07-02","DC Brake Time at Start-up",        0x0702,16,"R/W",0,   "s"),
        ParamDef("Pr07-03","DC Brake Time at Stop",            0x0703,16,"R/W",0,   "s"),
        ParamDef("Pr07-04","DC Brake Starting Frequency",      0x0704,16,"R/W",0,   "Hz"),
        ParamDef("Pr07-06","Speed Search at Start",            0x0706,16,"R/W",0,   ""),
        ParamDef("Pr07-09","Speed Search Level",               0x0709,16,"R/W",150, "%"),
        ParamDef("Pr07-11","Auto Energy-saving Mode",          0x070B,16,"R/W",0,   "",  "0=Disable|1=Enable"),
        ParamDef("Pr07-12","Speed Search during Power Loss",   0x070C,16,"R/W",0,   ""),
        ParamDef("Pr07-19","Fan Cooling Control",              0x0713,16,"R/W",0,   "",  "0=Always ON|1=Auto OFF|2=Always OFF"),
        ParamDef("Pr07-20","Emergency Stop Time",              0x0714,16,"R/W",0,   "s"),
        ParamDef("Pr07-21","Auto-restart Times",               0x0715,16,"R/W",0,   "times"),
        ParamDef("Pr07-22","Auto-restart Interval",            0x0716,16,"R/W",60,  "s"),
        ParamDef("Pr07-27","Slip Compensation Gain",           0x071B,16,"R/W",0,   "%"),
        ParamDef("Pr07-28","ASR P Gain",                       0x071C,16,"R/W",10,  ""),
        ParamDef("Pr07-29","ASR I Gain",                       0x071D,16,"R/W",100, "ms"),
        ParamDef("Pr07-30","Slip Compensation Time",           0x071E,16,"R/W",1,   "s"),
        ParamDef("Pr07-31","Torque Compensation Gain",         0x071F,16,"R/W",0,   ""),
    ]


# ═══════════════════════════════════════════════════════════════
#  GROUP 08 — PID Parameters  0x0800 ~ 0x0813
# ═══════════════════════════════════════════════════════════════
class Group08(_BaseGroup):
    GROUP_NAME = "Group 08 — PID Parameters"
    PARAMS = [
        ParamDef("Pr08-00","PID Feedback Terminal Select",     0x0800,16,"R/W",0,  "",  "0=No PID|1=Neg|2=Pos|3=Neg+target|4=Pos+target"),
        ParamDef("Pr08-01","PID Proportional Gain Kp",         0x0801,16,"R/W",80, "%", "★ 0~500%"),
        ParamDef("Pr08-02","PID Integral Time Ti",             0x0802,16,"R/W",10, "s", "★ 0.0~100.0s | 0=Disable"),
        ParamDef("Pr08-03","PID Derivative Time Td",           0x0803,16,"R/W",0,  "s"),
        ParamDef("Pr08-04","PID Integral Upper Limit",         0x0804,16,"R/W",100,"%"),
        ParamDef("Pr08-05","PID Output Upper Limit",           0x0805,16,"R/W",100,"%"),
        ParamDef("Pr08-06","PID Primary Low-pass Filter",      0x0806,16,"R/W",0,  "s"),
        ParamDef("Pr08-07","PID Secondary Low-pass Filter",    0x0807,16,"R/W",0,  "s"),
        ParamDef("Pr08-08","PID Feedback Gain",                0x0808,16,"R/W",100,"%"),
        ParamDef("Pr08-10","Sleep Function Frequency",         0x080A,16,"R/W",0,  "Hz"),
        ParamDef("Pr08-11","Wake-up Frequency",                0x080B,16,"R/W",0,  "Hz"),
        ParamDef("Pr08-12","Sleep Time",                       0x080C,16,"R/W",0,  "s"),
        ParamDef("Pr08-13","PID Deviation Level",              0x080D,16,"R/W",10, "%"),
        ParamDef("Pr08-14","PID Deviation Time",               0x080E,16,"R/W",5,  "s"),
        ParamDef("Pr08-16","PID Detection Value (Read)",       0x0810,16,"R",  0,  "%", "★ Read-only PID feedback"),
        ParamDef("Pr08-17","PID Reference Value (Read)",       0x0811,16,"R",  0,  "%"),
        ParamDef("Pr08-18","PID Output Value (Read)",          0x0812,16,"R",  0,  "%"),
        ParamDef("Pr08-19","PID Filter Time",                  0x0813,16,"R/W",0,  "s"),
    ]


# ═══════════════════════════════════════════════════════════════
#  GROUP 09 — Communication Parameters  0x0900 ~ 0x092E
#  ★ RS485 setup lives here
# ═══════════════════════════════════════════════════════════════
class Group09(_BaseGroup):
    GROUP_NAME = "Group 09 — Communication Parameters  [RS485 here!]"
    PARAMS = [
        ParamDef("Pr09-00","COM1 Slave Address",               0x0900,16,"R/W",1,    "",  "★ 1~254 | Default=1"),
        ParamDef("Pr09-01","COM1 Baud Rate",                   0x0901,16,"R/W",9600, "bps","★ 4800~115200"),
        ParamDef("Pr09-02","COM1 Transmission Fault Treatment", 0x0902,16,"R/W",3,   "",  "0=Warn+run|1=Warn+ramp|2=Warn+coast|3=No warn"),
        ParamDef("Pr09-03","COM1 Time-out Detection",          0x0903,16,"R/W",0,    "s",  "0=Disable|0.1~100.0"),
        ParamDef("Pr09-04","COM1 Communication Protocol",      0x0904,16,"R/W",1,    "",  "★ 1=7N2 ASCII|12=8N1 RTU|13=8N2 RTU|14=8E1 RTU"),
        ParamDef("Pr09-09","Response Delay Time",              0x0909,16,"R/W",2,    "ms", "0.0~200.0ms"),
        ParamDef("Pr09-10","Serial Comm. Freq. Command",       0x090A,16,"R/W",60,   "Hz"),
        ParamDef("Pr09-11","Block Transfer 1",                 0x090B,16,"R/W",0,    ""),
        ParamDef("Pr09-12","Block Transfer 2",                 0x090C,16,"R/W",0,    ""),
        ParamDef("Pr09-13","Block Transfer 3",                 0x090D,16,"R/W",0,    ""),
        ParamDef("Pr09-14","Block Transfer 4",                 0x090E,16,"R/W",0,    ""),
        ParamDef("Pr09-15","Block Transfer 5",                 0x090F,16,"R/W",0,    ""),
        ParamDef("Pr09-16","Block Transfer 6",                 0x0910,16,"R/W",0,    ""),
        ParamDef("Pr09-17","Block Transfer 7",                 0x0911,16,"R/W",0,    ""),
        ParamDef("Pr09-18","Block Transfer 8",                 0x0912,16,"R/W",0,    ""),
        ParamDef("Pr09-19","Block Transfer 9",                 0x0913,16,"R/W",0,    ""),
        ParamDef("Pr09-20","Block Transfer 10",                0x0914,16,"R/W",0,    ""),
        ParamDef("Pr09-21","Block Transfer 11",                0x0915,16,"R/W",0,    ""),
        ParamDef("Pr09-22","Block Transfer 12",                0x0916,16,"R/W",0,    ""),
        ParamDef("Pr09-23","Block Transfer 13",                0x0917,16,"R/W",0,    ""),
        ParamDef("Pr09-24","Block Transfer 14",                0x0918,16,"R/W",0,    ""),
        ParamDef("Pr09-25","Block Transfer 15",                0x0919,16,"R/W",0,    ""),
        ParamDef("Pr09-26","Block Transfer 16",                0x091A,16,"R/W",0,    ""),
        ParamDef("Pr09-30","Communication Decoding Method",    0x091E,16,"R/W",1,    "",  "0=Decoding 20xx|1=Decoding 60xx"),
        ParamDef("Pr09-31","Internal Communication Protocol",  0x091F,16,"R/W",0,    "",  "0=Modbus 485"),
        ParamDef("Pr09-35","PLC Address",                      0x0923,16,"R/W",2,    ""),
        ParamDef("Pr09-36","CANopen Slave Address",            0x0924,16,"R/W",0,    ""),
        ParamDef("Pr09-37","CANopen Speed",                    0x0925,16,"R/W",0,    ""),
        ParamDef("Pr09-38","CANopen Frequency Gain",           0x0926,16,"R/W",100,  "×0.01"),
        ParamDef("Pr09-46","CANopen Master Function",          0x092E,16,"R/W",0,    ""),
    ]


# ═══════════════════════════════════════════════════════════════
#  GROUP 10 — Speed Feedback Control  0x0A01 ~ 0x0A30
# ═══════════════════════════════════════════════════════════════
class Group10(_BaseGroup):
    GROUP_NAME = "Group 10 — Speed Feedback Control (PG)"
    PARAMS = [
        ParamDef("Pr10-01","Encoder Pulse Number",             0x0A01,16,"R/W",1024,"PPR", "★ Pulses per revolution"),
        ParamDef("Pr10-02","Encoder Type",                     0x0A02,16,"R/W",0,   "",   "0=ABZ|1=AB|2=A"),
        ParamDef("Pr10-03","Encoder Input Type",               0x0A03,16,"R/W",0,   "",   "0=Line driver|1=Open collector"),
        ParamDef("Pr10-05","Position Lock P Gain",             0x0A05,16,"R/W",10,  ""),
        ParamDef("Pr10-06","Position Lock I Gain",             0x0A06,16,"R/W",100, ""),
        ParamDef("Pr10-07","Feedback Gain",                    0x0A07,16,"R/W",100, ""),
        ParamDef("Pr10-08","Speed Feedback Filter",            0x0A08,16,"R/W",0,   "ms"),
        ParamDef("Pr10-17","ASR Low-speed P Gain",             0x0A11,16,"R/W",10,  ""),
        ParamDef("Pr10-18","ASR Low-speed I Gain",             0x0A12,16,"R/W",100, "ms"),
        ParamDef("Pr10-24","APR P Gain",                       0x0A18,16,"R/W",10,  ""),
        ParamDef("Pr10-25","Feed Forward for APR",             0x0A19,16,"R/W",0,   ""),
        ParamDef("Pr10-26","PDFF Gain for APR",                0x0A1A,16,"R/W",0,   ""),
        ParamDef("Pr10-38","Low-pass Filter Time",             0x0A26,16,"R/W",0,   "ms"),
        ParamDef("Pr10-39","V/F to Vector Switch Level",       0x0A27,16,"R/W",0,   "Hz"),
        ParamDef("Pr10-40","Vector to V/F Switch Level",       0x0A28,16,"R/W",0,   "Hz"),
    ]


# ═══════════════════════════════════════════════════════════════
#  GROUP 11 — Advanced Parameters  0x0B00 ~ 0x0B2A
# ═══════════════════════════════════════════════════════════════
class Group11(_BaseGroup):
    GROUP_NAME = "Group 11 — Advanced Parameters"
    PARAMS = [
        ParamDef("Pr11-00","System Control Flags",             0x0B00,16,"R/W",0,   ""),
        ParamDef("Pr11-01","ASR 1 P Gain",                     0x0B01,16,"R/W",10,  ""),
        ParamDef("Pr11-02","ASR 1 I Gain",                     0x0B02,16,"R/W",100, "ms"),
        ParamDef("Pr11-03","ASR 2 P Gain",                     0x0B03,16,"R/W",10,  ""),
        ParamDef("Pr11-04","ASR 2 I Gain",                     0x0B04,16,"R/W",100, "ms"),
        ParamDef("Pr11-05","ASR Integral Limit",               0x0B05,16,"R/W",100, "%"),
        ParamDef("Pr11-06","ASR Control P1",                   0x0B06,16,"R/W",10,  ""),
        ParamDef("Pr11-07","ASR Control I1",                   0x0B07,16,"R/W",100, "ms"),
        ParamDef("Pr11-08","ASR Control P2",                   0x0B08,16,"R/W",10,  ""),
        ParamDef("Pr11-09","ASR Control I2",                   0x0B09,16,"R/W",100, "ms"),
        ParamDef("Pr11-12","Flux Weakening Curve",             0x0B0C,16,"R/W",0,   ""),
        ParamDef("Pr11-13","Motor Flux",                       0x0B0D,16,"R/W",100, "%"),
        ParamDef("Pr11-14","Max Iq Current Limit",             0x0B0E,16,"R/W",100, "%"),
        ParamDef("Pr11-15","Notch Filter Depth",               0x0B0F,16,"R/W",0,   ""),
        ParamDef("Pr11-16","Notch Filter Frequency",           0x0B10,16,"R/W",0,   "Hz"),
        ParamDef("Pr11-17","Torque Limit FWD Motor",           0x0B11,16,"R/W",200, "%"),
        ParamDef("Pr11-18","Torque Limit REV Motor",           0x0B12,16,"R/W",200, "%"),
        ParamDef("Pr11-19","Torque Limit FWD Regen",           0x0B13,16,"R/W",200, "%"),
        ParamDef("Pr11-20","Torque Limit REV Regen",           0x0B14,16,"R/W",200, "%"),
        ParamDef("Pr11-27","Torque Command Source",            0x0B1B,16,"R/W",0,   ""),
        ParamDef("Pr11-28","Torque Offset",                    0x0B1C,16,"R/W",0,   "%"),
        ParamDef("Pr11-29","Torque Digital Command",           0x0B1D,16,"R/W",0,   "%"),
        ParamDef("Pr11-36","Speed Limit Selection (Torque Mode)",0x0B24,16,"R/W",0, ""),
        ParamDef("Pr11-37","FWD Speed Limit in Torque Mode",   0x0B25,16,"R/W",100, "%"),
        ParamDef("Pr11-38","REV Speed Limit in Torque Mode",   0x0B26,16,"R/W",100, "%"),
        ParamDef("Pr11-42","System Control Flags 2",           0x0B2A,16,"R/W",0,   ""),
    ]


# ═══════════════════════════════════════════════════════════════
#  DriveMonitor — Real-time status registers (2100H ~ 2224H)
#  ★ ONE bulk read for all live data
# ═══════════════════════════════════════════════════════════════
class DriveMonitor:
    """
    Reads all real-time status/monitor registers in ONE bulk call.

    After read():
        mon.fault_code        → 2100H  error code (0=OK)
        mon.drive_status      → 2101H  status bits
        mon.freq_cmd_hz       → 2102H  ÷100 = Hz
        mon.output_freq_hz    → 2103H  ÷100 = Hz
        mon.output_current_a  → 2104H  ÷10  = A
        mon.dc_bus_voltage_v  → 2105H  ÷10  = V
        mon.output_voltage_v  → 2106H  ÷10  = V
        mon.output_torque_pct → 210BH  ÷10  = %
        mon.motor_speed_rpm   → 210CH
        mon.igbt_temp_c       → 220EH
        mon.cap_temp_c        → 220FH
        mon.di_status         → 2210H  bit field
        mon.do_status         → 2211H  bit field
    """

    # ── first block: 2100H ~ 210DH  (14 regs)
    BLOCK1_START = 0x2100
    BLOCK1_COUNT = 14    # 2100~210D

    # ── second block: 220EH ~ 2211H  (4 regs)
    BLOCK2_START = 0x220E
    BLOCK2_COUNT = 4     # 220E,220F,2210,2211

    def __init__(self, client: VFDClient):
        self._client = client
        # raw 16-bit reads
        self.fault_code       : Optional[int] = None
        self.drive_status     : Optional[int] = None
        self.freq_cmd_raw     : Optional[int] = None   # ×0.01 Hz
        self.output_freq_raw  : Optional[int] = None   # ×0.01 Hz
        self.output_current_raw: Optional[int]= None   # ×0.1 A
        self.dc_bus_raw       : Optional[int] = None   # ×0.1 V
        self.output_voltage_raw: Optional[int]= None   # ×0.1 V
        self.multi_step_no    : Optional[int] = None
        self.counter_value    : Optional[int] = None
        self.power_factor_raw : Optional[int] = None   # ×0.1 deg
        self.torque_raw       : Optional[int] = None   # ×0.1 %
        self.motor_speed_rpm  : Optional[int] = None
        self.pg_pulses        : Optional[int] = None
        self.power_output_raw : Optional[int] = None   # ×0.001 kW
        self.igbt_temp_c      : Optional[int] = None
        self.cap_temp_c       : Optional[int] = None
        self.di_status        : Optional[int] = None
        self.do_status        : Optional[int] = None

    def read(self) -> None:
        """
        TWO bulk reads cover all monitor registers.
        (2100H block + 220EH block)
        """
        # ── Block 1: 2100H ~ 210DH ──────────────────────
        regs1 = self._client.read_registers(self.BLOCK1_START, self.BLOCK1_COUNT)
        self.fault_code        = regs1[0x2100 - self.BLOCK1_START]  # 2100H
        self.drive_status      = regs1[0x2101 - self.BLOCK1_START]  # 2101H
        self.freq_cmd_raw      = regs1[0x2102 - self.BLOCK1_START]  # 2102H
        self.output_freq_raw   = regs1[0x2103 - self.BLOCK1_START]  # 2103H
        self.output_current_raw= regs1[0x2104 - self.BLOCK1_START]  # 2104H
        self.dc_bus_raw        = regs1[0x2105 - self.BLOCK1_START]  # 2105H
        self.output_voltage_raw= regs1[0x2106 - self.BLOCK1_START]  # 2106H
        self.multi_step_no     = regs1[0x2107 - self.BLOCK1_START]  # 2107H
        # 2108H reserved
        self.counter_value     = regs1[0x2109 - self.BLOCK1_START]  # 2109H
        self.power_factor_raw  = regs1[0x210A - self.BLOCK1_START]  # 210AH
        self.torque_raw        = regs1[0x210B - self.BLOCK1_START]  # 210BH signed
        self.motor_speed_rpm   = regs1[0x210C - self.BLOCK1_START]  # 210CH
        self.pg_pulses         = regs1[0x210D - self.BLOCK1_START]  # 210DH

        # ── Block 2: 220EH ~ 2211H ──────────────────────
        regs2 = self._client.read_registers(self.BLOCK2_START, self.BLOCK2_COUNT)
        self.igbt_temp_c = regs2[0x220E - self.BLOCK2_START]        # 220EH
        self.cap_temp_c  = regs2[0x220F - self.BLOCK2_START]        # 220FH
        self.di_status   = regs2[0x2210 - self.BLOCK2_START]        # 2210H
        self.do_status   = regs2[0x2211 - self.BLOCK2_START]        # 2211H

        log.debug("DriveMonitor read complete")

    # ── Scaled property helpers ───────────────────────────
    @property
    def freq_cmd_hz(self) -> Optional[float]:
        return self.freq_cmd_raw / 100.0 if self.freq_cmd_raw is not None else None

    @property
    def output_freq_hz(self) -> Optional[float]:
        return self.output_freq_raw / 100.0 if self.output_freq_raw is not None else None

    @property
    def output_current_a(self) -> Optional[float]:
        return self.output_current_raw / 10.0 if self.output_current_raw is not None else None

    @property
    def dc_bus_voltage_v(self) -> Optional[float]:
        return self.dc_bus_raw / 10.0 if self.dc_bus_raw is not None else None

    @property
    def output_voltage_v(self) -> Optional[float]:
        return self.output_voltage_raw / 10.0 if self.output_voltage_raw is not None else None

    @property
    def output_torque_pct(self) -> Optional[float]:
        if self.torque_raw is None: return None
        v = self.torque_raw
        if v >= 0x8000: v -= 0x10000   # signed
        return v / 10.0

    # ── Status bit helpers ────────────────────────────────
    @property
    def is_running(self) -> bool:
        if self.drive_status is None: return False
        return (self.drive_status & 0x03) == 0x03

    @property
    def is_stopped(self) -> bool:
        if self.drive_status is None: return False
        return (self.drive_status & 0x03) == 0x00

    @property
    def is_forward(self) -> bool:
        if self.drive_status is None: return False
        return (self.drive_status & 0x18) == 0x00

    @property
    def is_reverse(self) -> bool:
        if self.drive_status is None: return False
        return (self.drive_status & 0x18) == 0x10

    def di_active(self, ch: int) -> bool:
        """Check if DI channel (1~8) is active. ch=1~8."""
        if self.di_status is None: return False
        return bool((self.di_status >> (ch - 1)) & 1)

    def do_active(self, ch: int) -> bool:
        """Check if DO channel (1~5) is active."""
        if self.do_status is None: return False
        return bool((self.do_status >> (ch - 1)) & 1)

    def print_status(self) -> None:
        print(f"\n{'='*56}")
        print(f"  Delta C200 — Real-time Drive Status")
        print(f"{'='*56}")
        print(f"  Fault Code        : {self.fault_code}  (0=No fault)")
        print(f"  Drive Status bits : 0b{self.drive_status:016b}" if self.drive_status is not None else "  Drive Status: None")
        print(f"  Running           : {self.is_running}")
        print(f"  Direction         : {'REV' if self.is_reverse else 'FWD'}")
        print(f"  Freq Command      : {self.freq_cmd_hz} Hz")
        print(f"  Output Frequency  : {self.output_freq_hz} Hz")
        print(f"  Output Current    : {self.output_current_a} A")
        print(f"  DC Bus Voltage    : {self.dc_bus_voltage_v} V")
        print(f"  Output Voltage    : {self.output_voltage_v} V")
        print(f"  Output Torque     : {self.output_torque_pct} %")
        print(f"  Motor Speed       : {self.motor_speed_rpm} RPM")
        print(f"  IGBT Temperature  : {self.igbt_temp_c} °C")
        print(f"  Capacitor Temp    : {self.cap_temp_c} °C")
        print(f"  DI Status bits    : 0b{self.di_status:08b}" if self.di_status is not None else "  DI Status: None")
        print(f"  DO Status bits    : 0b{self.do_status:08b}" if self.do_status is not None else "  DO Status: None")
        print(f"{'='*56}\n")

    def to_dict(self):
        data ={}
        data['Fault Code'] = self.fault_code
        data['Drive Status bits'] = f"0b{self.drive_status:016b}" if self.drive_status is not None else "  Drive Status: None"
        data['Running'] = self.is_running
        data['Direction'] = self.is_reverse
        data ['Freq Command'] = self.freq_cmd_hz
        data['Output Frequency'] = self.output_freq_hz
        data['Output Current'] = self.output_current_a
        data['DC Bus Voltage'] = self.dc_bus_voltage_v
        data['Output Voltage'] = self.output_voltage_v
        data['Output Torque'] = self.output_torque_pct
        data['Motor Speed'] = self.motor_speed_rpm
        data['IGBT Temperature'] = self.igbt_temp_c
        data['Capacitor Temp'] = self.cap_temp_c
        data ['DI Status bits'] = self.di_status
        data['DO Status bits'] = self.do_status
        return data

# ═══════════════════════════════════════════════════════════════
#  DriveControl — Run / Stop / Frequency / Reset
# ═══════════════════════════════════════════════════════════════
class DriveControl:
    """
    Controls drive via 2000H (command) and 2001H (frequency).

    IMPORTANT: Pr00-20 must = 1 (RS485 freq source)
               Pr00-21 must = 2 (RS485 operation source)

    2000H command word:
      Bit 0-3 : 0=No func | 1=Stop | 2=Run | 3=JOG+Run
      Bit 4-5 : 01=FWD | 10=REV | 11=Change direction
      Bit 6-7 : accel/decel group select

    2001H frequency:
      Value = Hz × 100  (e.g. 50.00 Hz → write 5000)

    2002H control:
      Bit 0: External Fault (EF)
      Bit 1: Reset
      Bit 2: Base Block (BB)
    """

    CMD_ADDR  = 0x2000
    FREQ_ADDR = 0x2001
    CTRL_ADDR = 0x2002

    def __init__(self, client: VFDClient):
        self._client = client

    def run_fwd(self) -> None:
        """Run in Forward direction."""
        # Bit0-3=2 (Run), Bit4-5=01 (FWD)
        self._client.write_register(self.CMD_ADDR, 0x0012)
        log.info("Command: RUN FWD")

    def run_rev(self) -> None:
        """Run in Reverse direction."""
        # Bit0-3=2 (Run), Bit4-5=10 (REV)
        self._client.write_register(self.CMD_ADDR, 0x0022)
        log.info("Command: RUN REV")

    def stop(self) -> None:
        """Ramp to stop."""
        # Bit0-3=1 (Stop)
        self._client.write_register(self.CMD_ADDR, 0x0001)
        log.info("Command: STOP")

    def jog_fwd(self) -> None:
        """JOG Forward (uses Pr01-22 JOG frequency)."""
        self._client.write_register(self.CMD_ADDR, 0x0013)
        log.info("Command: JOG FWD")

    def set_frequency(self, hz: float) -> None:
        """
        Set target frequency.
        hz : float  e.g. 50.0
        Writes hz × 100 to 2001H.
        """
        raw = int(round(hz * 100))
        if not 0 <= raw <= 60000:
            raise ValueError(f"Frequency {hz}Hz out of range (0~600Hz)")
        self._client.write_register(self.FREQ_ADDR, raw)
        log.info(f"Frequency set: {hz} Hz  (raw={raw})")

    def reset_fault(self) -> None:
        """Reset drive fault (bit1 of 2002H)."""
        self._client.write_register(self.CTRL_ADDR, 0x0002)
        time.sleep(0.2)
        self._client.write_register(self.CTRL_ADDR, 0x0000)
        log.info("Fault reset command sent")

    def external_fault(self, on: bool) -> None:
        """Set/clear External Fault (EF) — bit0 of 2002H."""
        self._client.write_register(self.CTRL_ADDR, 0x0001 if on else 0x0000)

    def run_at_freq(self, hz: float, direction: str = 'FWD') -> None:
        """Convenience: set frequency and run in one call."""
        self.set_frequency(hz)
        if direction.upper() == 'REV':
            self.run_rev()
        else:
            self.run_fwd()


# ═══════════════════════════════════════════════════════════════
#  VFDManager — all groups + monitor + control in one place
# ═══════════════════════════════════════════════════════════════
class VFDManager:
    """
    One-stop wrapper for complete C200 access.

    Example:
        with VFDManager('COM3', slave_id=1) as vfd:
            vfd.read_all()
            print(vfd.monitor.output_freq_hz)
            print(vfd.comm.pr09_00)       # slave address
            vfd.ctrl.run_at_freq(40.0)
            time.sleep(5)
            vfd.ctrl.stop()
    """
    def __init__(self, port: str, slave_id: int = 1,
                 baudrate: int = 9600, mode: str = 'RTU'):
        self.client  = VFDClient(port, slave_id, baudrate, mode)
        self.g00     = Group00(self.client)
        self.g01     = Group01(self.client)
        self.g02     = Group02(self.client)
        self.g03     = Group03(self.client)
        self.g04     = Group04(self.client)
        self.g05     = Group05(self.client)
        self.g06     = Group06(self.client)
        self.g07     = Group07(self.client)
        self.g08     = Group08(self.client)
        self.comm    = Group09(self.client)   # RS485 settings
        self.g10     = Group10(self.client)
        self.g11     = Group11(self.client)
        self.monitor = DriveMonitor(self.client)
        self.ctrl    = DriveControl(self.client)
        self._all_groups = [
            self.g00, self.g01, self.g02, self.g03,
            self.g04, self.g05, self.g06, self.g07,
            self.g08, self.comm, self.g10, self.g11,
        ]

    def read_all(self) -> None:
        """Read all parameter groups + monitor registers."""
        for g in self._all_groups:
            try:    g.read()
            except Exception as e:
                log.error(f"Failed {g.GROUP_NAME}: {e}")
        try:    self.monitor.read()
        except Exception as e:
            log.error(f"Failed DriveMonitor: {e}")

    def read_monitor_only(self) -> None:
        """Fast — only live status registers."""
        self.monitor.read()

    def close(self): self.client.close()
    def __enter__(self): return self
    def __exit__(self, *_): self.close()


# ─────────────────────────────────────────────────────────────
#  Quick demo / test
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")

    PORT     = sys.argv[1] if len(sys.argv) > 1 else "COM3"
    SLAVE_ID = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    MODE     = sys.argv[3] if len(sys.argv) > 3 else "RTU"

    print(f"\n{'='*60}")
    print(f"  Delta VFD-C200  port={PORT}  slave={SLAVE_ID}  mode={MODE}")
    print(f"{'='*60}")

    try:
        with VFDClient(PORT, slave_id=SLAVE_ID, mode=MODE) as vfd:

            # ── Group 09: check RS485 settings ─────────
            print("\n[Group 09] Communication Settings")
            g09 = Group09(vfd)
            g09.read()
            print(f"  Slave Address   : Pr09-00 = {g09.pr09_00}")
            print(f"  Baud Rate       : Pr09-01 = {g09.pr09_01} bps")
            print(f"  Protocol        : Pr09-04 = {g09.pr09_04}  (1=7N2 ASCII | 12=8N1 RTU)")
            print(f"  Response Delay  : Pr09-09 = {g09.pr09_09} ms")

            # ── Group 00: operation source ─────────────
            print("\n[Group 00] Key Settings")
            g00 = Group00(vfd)
            g00.read()
            print(f"  Freq Source     : Pr00-20 = {g00.pr00_20}  (★ Set to 1 for RS485)")
            print(f"  Oper Source     : Pr00-21 = {g00.pr00_21}  (★ Set to 2 for RS485)")
            print(f"  Control Mode    : Pr00-10 = {g00.pr00_10}  (0=V/F|2=SVC|3=FOC)")
            print(f"  Carrier Freq    : Pr00-14 = {g00.pr00_14} kHz")

            # ── Group 06: fault records ─────────────────
            print("\n[Group 06] Fault Records")
            g06 = Group06(vfd)
            g06.read()
            print(f"  Fault Record 1  : Pr06-17 = {g06.pr06_17}")
            print(f"  Fault Record 2  : Pr06-18 = {g06.pr06_18}")
            print(f"  Fault Record 3  : Pr06-19 = {g06.pr06_19}")

            # ── DriveMonitor: real-time data ────────────
            print("\n[Monitor] Real-time Status (5 samples)")
            print(f"  {'Fault':<7} {'FreqCmd(Hz)':<14} {'OutFreq(Hz)':<14} "
                  f"{'Current(A)':<12} {'VBus(V)':<10} {'Torque(%)':<11} {'RPM'}")
            print(f"  {'-'*80}")
            mon = DriveMonitor(vfd)
            for _ in range(5):
                mon.read()
                print(
                    f"  {mon.fault_code or 0:<7} "
                    f"{str(mon.freq_cmd_hz):<14} "
                    f"{str(mon.output_freq_hz):<14} "
                    f"{str(mon.output_current_a):<12} "
                    f"{str(mon.dc_bus_voltage_v):<10} "
                    f"{str(mon.output_torque_pct):<11} "
                    f"{mon.motor_speed_rpm or 0}"
                )
                time.sleep(1.0)

            # ── DI/DO status ────────────────────────────
            print("\n[Monitor] Digital I/O Status")
            for ch in range(1, 9):
                state = "ON " if mon.di_active(ch) else "off"
                print(f"  DI{ch}={state}", end="  ")
            print()
            for ch in range(1, 6):
                state = "ON " if mon.do_active(ch) else "off"
                print(f"  DO{ch}={state}", end="  ")
            print()

            # ── Example: Run at 40Hz FWD ────────────────
            # UNCOMMENT ONLY WHEN Pr00-20=1, Pr00-21=2 are set!
            # ctrl = DriveControl(vfd)
            # ctrl.run_at_freq(40.0, 'FWD')
            # time.sleep(5)
            # ctrl.stop()

    except ConnectionError as e:
        print(f"\nConnection failed: {e}")
        print("Check: COM port | baud=9600 | slave_id=1 | RS485 wiring")
    except Exception as e:
        print(f"\nError: {e}")
        raise