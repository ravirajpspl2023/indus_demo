from typing import Any, List, Optional
from module.connectors.DELTA_C200.VFDClient import VFDClient

import logging


log = logging.getLogger(__name__)

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

        # log.debug("DriveMonitor read complete")

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