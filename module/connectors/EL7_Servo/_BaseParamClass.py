

from module.connectors.EL7_Servo.ServoClient import ServoClient
from dataclasses import dataclass
from typing import Optional, Any, List, Dict
import logging

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
        self.log = logging.getLogger(client.port.split("/")[-1])
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
        # log.info(f"[{self.CLASS_NAME}]  "
        #          f"0x{self.start_addr:04X} ~ 0x{self.end_addr:04X}  "
        #          f"({self.read_count} registers)")
        try: 
            regs = self._client.read_registers(self.start_addr, self.read_count)
        except Exception as e:
            self.log.info(f'error to read resigster {self.CLASS_NAME}')

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

        self.log.info(f"  -> {len(self.PARAMS)} params mapped")

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

        self.log.info(f"Written  {code}  (0x{p.addr:04X})  = {value}")

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
            p.name: {
                # "name": p.name,
                # "addr": f"0x{p.addr:04X}",
                "value": getattr(self, self._attr_map[p.code]),
                # "unit": p.unit,
            }
            for p in self.PARAMS
        }

        # return {
        #     p.code: {
        #         "name": p.name,
        #         "addr": f"0x{p.addr:04X}",
        #         "value": getattr(self, self._attr_map[p.code]),
        #         "unit": p.unit,
        #     }
        #     for p in self.PARAMS
        # }

    def __repr__(self):
        return (f"<{self.__class__.__name__} "
                f"0x{self.start_addr:04X}~0x{self.end_addr:04X} "
                f"{len(self.PARAMS)} params>")