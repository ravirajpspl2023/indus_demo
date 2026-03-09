import logging
from dataclasses import dataclass
from typing import Any, List, Optional
from module.connectors.DELTA_C200.VFDClient import VFDClient

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


log = logging.getLogger(__name__)
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
        
        try:
            regs = self._client.read_registers(self.start_addr, self.read_count)
        except Exception as e:
            log.error(f"[{self.GROUP_NAME}] Bulk read failed: {e}")
            # Fallback: read individual parameters
            self._read_individual_params()
            return

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
    
    def _read_individual_params(self):
        """Fallback: read parameters individually when bulk read fails"""
        log.warning(f"[{self.GROUP_NAME}] Using individual parameter reads")
        
        for p in self.PARAMS:
            try:
                if p.bits == 32:
                    regs = self._client.read_registers(p.addr, 2)
                    val = (regs[0] << 16) | regs[1]
                    if val >= 0x80000000:
                        val -= 0x100000000
                else:
                    regs = self._client.read_registers(p.addr, 1)
                    val = regs[0]
                    if val >= 0x8000:
                        val -= 0x10000
                
                setattr(self, self._attr_map[p.code], val)
                log.debug(f"  {p.code} -> {val}")
                
            except Exception as e:
                log.error(f"  {p.code} failed: {e}")
                setattr(self, self._attr_map[p.code], None)

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
            p.name: {
                # "name" : p.name,
                # "addr" : f"0x{p.addr:04X}",
                "value": getattr(self, self._attr_map[p.code]),
                # "unit" : p.unit,
            }
            for p in self.PARAMS
        }

    def __repr__(self):
        return (f"<{self.__class__.__name__} "
                f"0x{self.start_addr:04X}~0x{self.end_addr:04X} "
                f"{len(self.PARAMS)} params>")
