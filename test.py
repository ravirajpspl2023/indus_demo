"""
Leadshine EL7-RS Series AC Servo Drive — Modbus RTU Python Library
===================================================================
- प्रत्येक Class साठी एक Python Object
- Class च्या पहिल्या address पासून शेवटच्या address पर्यंत
  एकाच Modbus request मध्ये सगळे registers read करतो
- Response मधून प्रत्येक parameter ची value काढतो

Requirements:
    pip install pymodbus

Usage:
    drive = EL7RSDrive(port='COM3', slave_id=4, baudrate=57600)
    drive.read_class0()          # Basic Settings
    drive.read_class_status()    # Class B — live monitor
    print(drive.class0.control_mode)
    print(drive.classB.motor_speed_rpm)
"""

from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
from dataclasses import dataclass, field
from typing import Optional
import time
import struct


# ─────────────────────────────────────────────────────────────────────────────
# Helper: 16-bit signed
# ─────────────────────────────────────────────────────────────────────────────
def to_signed16(val: int) -> int:
    """Unsigned 16-bit → Signed 16-bit"""
    if val >= 0x8000:
        val -= 0x10000
    return val


def to_signed32(hi: int, lo: int) -> int:
    """Two 16-bit registers → Signed 32-bit integer"""
    raw = (hi << 16) | lo
    if raw >= 0x80000000:
        raw -= 0x100000000
    return raw


# ─────────────────────────────────────────────────────────────────────────────
# Parameter Descriptor
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class ParamInfo:
    """एका parameter ची माहिती"""
    code: str           # e.g. "Pr0.01"
    name: str           # e.g. "Control Mode Settings"
    address: int        # Modbus address (hex number)
    bits: int           # 16 or 32
    default: int        # Factory default
    unit: str = ""      # e.g. "rpm", "%", "Hz"
    value: Optional[int] = None  # Read केलेली value


# ─────────────────────────────────────────────────────────────────────────────
# Base Class — एका Class Group साठी
# ─────────────────────────────────────────────────────────────────────────────
class ServoParamGroup:
    """
    एका Class Group साठी base.
    start_addr ते end_addr पर्यंत एकाच request मध्ये read करतो.
    """
    # Subclass मध्ये PARAMS define करायचे
    PARAMS: list[ParamInfo] = []
    CLASS_NAME: str = "Base"

    def __init__(self):
        # प्रत्येक param ची value None initialize
        self._param_map: dict[int, ParamInfo] = {}
        for p in self.PARAMS:
            self._param_map[p.address] = p

    @property
    def start_address(self) -> int:
        """Group मधील सर्वात कमी address"""
        return min(p.address for p in self.PARAMS)

    @property
    def end_address(self) -> int:
        """Group मधील सर्वात जास्त address
        (32-bit params दोन registers वापरतात)
        """
        last = max(p.address for p in self.PARAMS)
        # last param 32-bit असेल तर +1
        last_param = self._param_map[last]
        return last + (1 if last_param.bits == 32 else 0)

    @property
    def register_count(self) -> int:
        """एका request मध्ये किती registers read करायचे"""
        return self.end_address - self.start_address + 1

    def parse_response(self, registers: list[int]):
        """
        Read केलेले registers → प्रत्येक param ला value assign करतो.
        registers[0] = start_address ची value
        registers[1] = start_address + 1 ची value
        ...
        """
        base = self.start_address

        for param in self.PARAMS:
            offset = param.address - base
            if offset < 0 or offset >= len(registers):
                param.value = None
                continue

            if param.bits == 16:
                param.value = to_signed16(registers[offset])
            elif param.bits == 32:
                if offset + 1 < len(registers):
                    param.value = to_signed32(registers[offset], registers[offset + 1])
                else:
                    param.value = None

        # Subclass मध्ये named attributes update करतो
        self._update_attributes()

    def _update_attributes(self):
        """Subclass मध्ये override करायचे — named properties set करतो"""
        pass

    def print_all(self):
        """सगळ्या parameters ची value print करतो"""
        print(f"\n{'='*60}")
        print(f"  {self.CLASS_NAME}")
        print(f"  Address Range: 0x{self.start_address:04X} → 0x{self.end_address:04X}")
        print(f"  Registers to read: {self.register_count}")
        print(f"{'='*60}")
        for p in self.PARAMS:
            val_str = str(p.value) if p.value is not None else "---"
            print(f"  {p.code:<12} 0x{p.address:04X}  {p.name:<45} = {val_str} {p.unit}")


# ─────────────────────────────────────────────────────────────────────────────
# CLASS 0 — Basic Settings
# ─────────────────────────────────────────────────────────────────────────────
class Class0_BasicSettings(ServoParamGroup):
    CLASS_NAME = "Class 0 - Basic Settings"
    PARAMS = [
        ParamInfo("Pr0.00", "Model-following Bandwidth",       0x0001, 16,  1,    "0.1Hz"),
        ParamInfo("Pr0.01", "Control Mode Settings",           0x0003, 16,  0,    ""),
        ParamInfo("Pr0.02", "Real-time Auto Gain Adjusting",   0x0005, 16,  0x1,  ""),
        ParamInfo("Pr0.03", "Real-time Auto Stiffness",        0x0007, 16,  11,   ""),
        ParamInfo("Pr0.04", "Inertia Ratio",                   0x0009, 16,  250,  "%"),
        ParamInfo("Pr0.05", "Command Pulse Input Selection",   0x000B, 16,  0,    ""),
        ParamInfo("Pr0.06", "Command Pulse Polarity Inversion",0x000D, 16,  0,    ""),
        ParamInfo("Pr0.07", "Command Pulse Input Mode",        0x000F, 16,  3,    ""),
        ParamInfo("Pr0.08", "1st Cmd Pulse Count/Revolution",  0x0010, 32,  10000,"pulse/rev"),
        ParamInfo("Pr0.09", "1st Freq Divider Numerator",      0x0012, 32,  1,    ""),
        ParamInfo("Pr0.10", "1st Freq Divider Denominator",    0x0014, 32,  1,    ""),
        ParamInfo("Pr0.11", "Encoder Output Pulse Count/Rev",  0x0017, 16,  2500, "pulse/rev"),
        ParamInfo("Pr0.12", "Pulse Output Logic Inversion",    0x0019, 16,  0,    ""),
        ParamInfo("Pr0.13", "1st Torque Limit",                0x001B, 16,  350,  "%"),
        ParamInfo("Pr0.14", "Excessive Position Deviation",    0x001D, 16,  30,   "×10000 pulse"),
        ParamInfo("Pr0.15", "Absolute Encoder Settings",       0x001F, 16,  0,    ""),
        ParamInfo("Pr0.16", "Regenerative Resistance",         0x0021, 16,  100,  "Ω"),
        ParamInfo("Pr0.17", "Regenerative Resistor Power",     0x0023, 16,  50,   "W"),
    ]

    def __init__(self):
        super().__init__()
        # Named attributes
        self.model_following_bandwidth: Optional[int] = None
        self.control_mode: Optional[int] = None
        self.auto_gain_mode: Optional[int] = None
        self.stiffness: Optional[int] = None
        self.inertia_ratio: Optional[int] = None
        self.pulse_input_selection: Optional[int] = None
        self.pulse_polarity_inversion: Optional[int] = None
        self.pulse_input_mode: Optional[int] = None
        self.pulse_count_per_rev: Optional[int] = None
        self.gear_numerator: Optional[int] = None
        self.gear_denominator: Optional[int] = None
        self.encoder_output_pulse: Optional[int] = None
        self.pulse_output_inversion: Optional[int] = None
        self.torque_limit_pct: Optional[int] = None
        self.pos_deviation_limit: Optional[int] = None
        self.abs_encoder_setting: Optional[int] = None
        self.regen_resistance: Optional[int] = None
        self.regen_power: Optional[int] = None

    def _update_attributes(self):
        m = {p.address: p.value for p in self.PARAMS}
        self.model_following_bandwidth = m.get(0x0001)
        self.control_mode              = m.get(0x0003)
        self.auto_gain_mode            = m.get(0x0005)
        self.stiffness                 = m.get(0x0007)
        self.inertia_ratio             = m.get(0x0009)
        self.pulse_input_selection     = m.get(0x000B)
        self.pulse_polarity_inversion  = m.get(0x000D)
        self.pulse_input_mode          = m.get(0x000F)
        self.pulse_count_per_rev       = m.get(0x0010)
        self.gear_numerator            = m.get(0x0012)
        self.gear_denominator          = m.get(0x0014)
        self.encoder_output_pulse      = m.get(0x0017)
        self.pulse_output_inversion    = m.get(0x0019)
        self.torque_limit_pct          = m.get(0x001B)
        self.pos_deviation_limit       = m.get(0x001D)
        self.abs_encoder_setting       = m.get(0x001F)
        self.regen_resistance          = m.get(0x0021)
        self.regen_power               = m.get(0x0023)

    @property
    def control_mode_name(self) -> str:
        names = {0:"Position", 1:"Velocity", 2:"Torque",
                 3:"Pos+Vel", 4:"Pos+Torque", 5:"Vel+Torque", 6:"PR"}
        return names.get(self.control_mode, "Unknown") if self.control_mode is not None else "---"


# ─────────────────────────────────────────────────────────────────────────────
# CLASS 1 — Gain Adjustment
# ─────────────────────────────────────────────────────────────────────────────
class Class1_GainAdjustment(ServoParamGroup):
    CLASS_NAME = "Class 1 – Gain Adjustment"
    PARAMS = [
        ParamInfo("Pr1.00", "1st Position Loop Gain",             0x0101, 16, 320,   "0.1/s"),
        ParamInfo("Pr1.01", "1st Velocity Loop Gain",             0x0103, 16, 180,   "Hz"),
        ParamInfo("Pr1.02", "1st Integral Time Constant Vel Loop",0x0105, 16, 310,   "0.1ms"),
        ParamInfo("Pr1.03", "1st Velocity Detection Filter",      0x0107, 16, 15,    ""),
        ParamInfo("Pr1.04", "1st Torque Filter Time Constant",    0x0109, 16, 126,   "0.1ms"),
        ParamInfo("Pr1.05", "2nd Position Loop Gain",             0x010B, 16, 380,   "0.1/s"),
        ParamInfo("Pr1.06", "2nd Velocity Loop Gain",             0x010D, 16, 180,   "Hz"),
        ParamInfo("Pr1.07", "2nd Integral Time Constant Vel Loop",0x010F, 16, 10000, "0.1ms"),
        ParamInfo("Pr1.08", "2nd Velocity Detection Filter",      0x0111, 16, 15,    ""),
        ParamInfo("Pr1.09", "2nd Torque Filter Time Constant",    0x0113, 16, 126,   "0.1ms"),
        ParamInfo("Pr1.10", "Velocity Feed Forward Gain",         0x0115, 16, 300,   "%"),
        ParamInfo("Pr1.11", "Velocity FF Filter Time Constant",   0x0117, 16, 50,    "0.1ms"),
        ParamInfo("Pr1.12", "Torque Feed Forward Gain",           0x0119, 16, 0,     "%"),
        ParamInfo("Pr1.13", "Torque FF Filter Time Constant",     0x011B, 16, 0,     "0.1ms"),
        ParamInfo("Pr1.15", "Position Gain Switching Mode",       0x011F, 16, 0,     ""),
        ParamInfo("Pr1.17", "Position Gain Switching Level",      0x0123, 16, 50,    ""),
        ParamInfo("Pr1.18", "Hysteresis at Gain Switching",       0x0125, 16, 33,    ""),
        ParamInfo("Pr1.19", "Position Control Switching Time",    0x0127, 16, 33,    "0.1ms"),
    ]

    def __init__(self):
        super().__init__()
        self.pos_loop_gain_1: Optional[int] = None
        self.vel_loop_gain_1: Optional[int] = None
        self.vel_integral_time_1: Optional[int] = None
        self.vel_detect_filter_1: Optional[int] = None
        self.torque_filter_1: Optional[int] = None
        self.pos_loop_gain_2: Optional[int] = None
        self.vel_loop_gain_2: Optional[int] = None
        self.vel_integral_time_2: Optional[int] = None
        self.vel_detect_filter_2: Optional[int] = None
        self.torque_filter_2: Optional[int] = None
        self.vel_ff_gain: Optional[int] = None
        self.vel_ff_filter: Optional[int] = None
        self.torque_ff_gain: Optional[int] = None
        self.torque_ff_filter: Optional[int] = None
        self.gain_switch_mode: Optional[int] = None
        self.gain_switch_level: Optional[int] = None
        self.gain_switch_hysteresis: Optional[int] = None
        self.gain_switch_time: Optional[int] = None

    def _update_attributes(self):
        m = {p.address: p.value for p in self.PARAMS}
        self.pos_loop_gain_1      = m.get(0x0101)
        self.vel_loop_gain_1      = m.get(0x0103)
        self.vel_integral_time_1  = m.get(0x0105)
        self.vel_detect_filter_1  = m.get(0x0107)
        self.torque_filter_1      = m.get(0x0109)
        self.pos_loop_gain_2      = m.get(0x010B)
        self.vel_loop_gain_2      = m.get(0x010D)
        self.vel_integral_time_2  = m.get(0x010F)
        self.vel_detect_filter_2  = m.get(0x0111)
        self.torque_filter_2      = m.get(0x0113)
        self.vel_ff_gain          = m.get(0x0115)
        self.vel_ff_filter        = m.get(0x0117)
        self.torque_ff_gain       = m.get(0x0119)
        self.torque_ff_filter     = m.get(0x011B)
        self.gain_switch_mode     = m.get(0x011F)
        self.gain_switch_level    = m.get(0x0123)
        self.gain_switch_hysteresis = m.get(0x0125)
        self.gain_switch_time     = m.get(0x0127)


# ─────────────────────────────────────────────────────────────────────────────
# CLASS 3 — Velocity / Torque Control
# ─────────────────────────────────────────────────────────────────────────────
class Class3_VelocityTorque(ServoParamGroup):
    CLASS_NAME = "Class 3 – Velocity / Torque Control"
    PARAMS = [
        ParamInfo("Pr3.00", "Velocity Internal/External Switching", 0x0301, 16, 1,   ""),
        ParamInfo("Pr3.01", "Velocity Cmd Direction Selection",      0x0303, 16, 0,   ""),
        ParamInfo("Pr3.02", "Velocity Cmd Input Gain",               0x0305, 16, 500, "rpm/V"),
        ParamInfo("Pr3.03", "Velocity Cmd Input Inversion",          0x0307, 16, 0,   ""),
        ParamInfo("Pr3.04", "1st Internal Speed",                    0x0309, 16, 0,   "rpm"),
        ParamInfo("Pr3.05", "2nd Internal Speed",                    0x030B, 16, 0,   "rpm"),
        ParamInfo("Pr3.06", "3rd Internal Speed",                    0x030D, 16, 0,   "rpm"),
        ParamInfo("Pr3.07", "4th Internal Speed",                    0x030F, 16, 0,   "rpm"),
        ParamInfo("Pr3.08", "5th Internal Speed",                    0x0311, 16, 0,   "rpm"),
        ParamInfo("Pr3.09", "6th Internal Speed",                    0x0313, 16, 0,   "rpm"),
        ParamInfo("Pr3.10", "7th Internal Speed",                    0x0315, 16, 0,   "rpm"),
        ParamInfo("Pr3.11", "8th Internal Speed",                    0x0317, 16, 0,   "rpm"),
        ParamInfo("Pr3.12", "Acceleration Time",                     0x0319, 16, 100, "ms"),
        ParamInfo("Pr3.13", "Deceleration Time",                     0x031B, 16, 100, "ms"),
        ParamInfo("Pr3.14", "Sigmoid Accel/Decel",                   0x031D, 16, 0,   "ms"),
        ParamInfo("Pr3.15", "Zero Speed Clamp Selection",            0x031F, 16, 0,   ""),
        ParamInfo("Pr3.16", "Zero Speed Clamp Level",                0x0321, 16, 30,  "rpm"),
        ParamInfo("Pr3.17", "Torque Internal/External Switching",    0x0323, 16, 0,   ""),
        ParamInfo("Pr3.18", "Torque Cmd Direction Selection",        0x0325, 16, 0,   ""),
        ParamInfo("Pr3.19", "Torque Cmd Input Gain",                 0x0327, 16, 30,  "%/V"),
        ParamInfo("Pr3.20", "Torque Cmd Input Inversion",            0x0329, 16, 0,   ""),
        ParamInfo("Pr3.21", "Velocity Limit in Torque Mode",         0x032B, 16, 0,   "rpm"),
        ParamInfo("Pr3.22", "Torque Command (RS485)",                0x032D, 16, 0,   "%"),
        ParamInfo("Pr3.23", "Zero Speed Delay Time",                 0x032F, 16, 0,   "ms"),
        ParamInfo("Pr3.24", "Maximum Motor Speed",                   0x0331, 16, 0,   "rpm"),
    ]

    def __init__(self):
        super().__init__()
        self.vel_source: Optional[int] = None
        self.vel_direction: Optional[int] = None
        self.vel_input_gain: Optional[int] = None
        self.vel_input_inversion: Optional[int] = None
        self.speed_1: Optional[int] = None
        self.speed_2: Optional[int] = None
        self.speed_3: Optional[int] = None
        self.speed_4: Optional[int] = None
        self.speed_5: Optional[int] = None
        self.speed_6: Optional[int] = None
        self.speed_7: Optional[int] = None
        self.speed_8: Optional[int] = None
        self.accel_time_ms: Optional[int] = None
        self.decel_time_ms: Optional[int] = None
        self.sigmoid_time: Optional[int] = None
        self.zero_clamp_select: Optional[int] = None
        self.zero_clamp_level_rpm: Optional[int] = None
        self.torque_source: Optional[int] = None
        self.torque_direction: Optional[int] = None
        self.torque_input_gain: Optional[int] = None
        self.torque_input_inversion: Optional[int] = None
        self.vel_limit_torque_mode: Optional[int] = None
        self.torque_command_pct: Optional[int] = None  # RS485 torque setpoint
        self.zero_speed_delay_ms: Optional[int] = None
        self.max_speed_rpm: Optional[int] = None

    def _update_attributes(self):
        m = {p.address: p.value for p in self.PARAMS}
        self.vel_source           = m.get(0x0301)
        self.vel_direction        = m.get(0x0303)
        self.vel_input_gain       = m.get(0x0305)
        self.vel_input_inversion  = m.get(0x0307)
        self.speed_1              = m.get(0x0309)
        self.speed_2              = m.get(0x030B)
        self.speed_3              = m.get(0x030D)
        self.speed_4              = m.get(0x030F)
        self.speed_5              = m.get(0x0311)
        self.speed_6              = m.get(0x0313)
        self.speed_7              = m.get(0x0315)
        self.speed_8              = m.get(0x0317)
        self.accel_time_ms        = m.get(0x0319)
        self.decel_time_ms        = m.get(0x031B)
        self.sigmoid_time         = m.get(0x031D)
        self.zero_clamp_select    = m.get(0x031F)
        self.zero_clamp_level_rpm = m.get(0x0321)
        self.torque_source        = m.get(0x0323)
        self.torque_direction     = m.get(0x0325)
        self.torque_input_gain    = m.get(0x0327)
        self.torque_input_inversion = m.get(0x0329)
        self.vel_limit_torque_mode= m.get(0x032B)
        self.torque_command_pct   = m.get(0x032D)
        self.zero_speed_delay_ms  = m.get(0x032F)
        self.max_speed_rpm        = m.get(0x0331)

    @property
    def speed_list(self) -> list[int]:
        """सगळ्या 8 internal speeds list मध्ये"""
        return [self.speed_1, self.speed_2, self.speed_3, self.speed_4,
                self.speed_5, self.speed_6, self.speed_7, self.speed_8]


# ─────────────────────────────────────────────────────────────────────────────
# CLASS 4 — I/O Monitoring Settings
# ─────────────────────────────────────────────────────────────────────────────
class Class4_IOSettings(ServoParamGroup):
    CLASS_NAME = "Class 4 – I/O Monitoring Settings"
    PARAMS = [
        ParamInfo("Pr4.00", "DI1 Function Assignment",        0x0401, 16, 0x1,  ""),
        ParamInfo("Pr4.01", "DI2 Function Assignment",        0x0403, 16, 0x2,  ""),
        ParamInfo("Pr4.02", "DI3 Function Assignment",        0x0405, 16, 0x8,  ""),
        ParamInfo("Pr4.03", "DI4 Function Assignment",        0x0407, 16, 0x4,  ""),
        ParamInfo("Pr4.04", "DI5 Function Assignment",        0x0409, 16, 0x3,  ""),
        ParamInfo("Pr4.05", "DI6 Function Assignment",        0x040B, 16, 0x0,  ""),
        ParamInfo("Pr4.06", "DI7 Function Assignment",        0x040D, 16, 0x0,  ""),
        ParamInfo("Pr4.07", "DI8 Function Assignment",        0x040F, 16, 0x27, ""),
        ParamInfo("Pr4.10", "DO1 Function Assignment",        0x0415, 16, 0x2,  ""),
        ParamInfo("Pr4.11", "DO2 Function Assignment",        0x0417, 16, 0x4,  ""),
        ParamInfo("Pr4.12", "DO3 Function Assignment",        0x0419, 16, 0x3,  ""),
        ParamInfo("Pr4.13", "DO4 Function Assignment",        0x041B, 16, 0x1,  ""),
        ParamInfo("Pr4.14", "DO5 Function Assignment",        0x041D, 16, 0x22, ""),
        ParamInfo("Pr4.31", "Positioning Complete Range",     0x0445, 16, 50,   "pulse"),
        ParamInfo("Pr4.33", "INP Positioning Delay Time",     0x0449, 16, 1000, "ms"),
        ParamInfo("Pr4.34", "Zero Speed Detection Level",     0x044B, 16, 150,  "rpm"),
        ParamInfo("Pr4.35", "Velocity Coincidence Range",     0x044D, 16, 0,    "rpm"),
        ParamInfo("Pr4.36", "Arrival Velocity",               0x044F, 16, 30,   "rpm"),
        ParamInfo("Pr4.43", "Emergency Stop Function",        0x0457, 16, 0,    ""),
    ]

    def __init__(self):
        super().__init__()
        self.di1 = self.di2 = self.di3 = self.di4 = None
        self.di5 = self.di6 = self.di7 = self.di8 = None
        self.do1 = self.do2 = self.do3 = self.do4 = self.do5 = None
        self.in_position_range: Optional[int] = None
        self.inp_delay_ms: Optional[int] = None
        self.zero_speed_rpm: Optional[int] = None
        self.vel_coincidence_rpm: Optional[int] = None
        self.arrival_vel_rpm: Optional[int] = None
        self.estop_mode: Optional[int] = None

    def _update_attributes(self):
        m = {p.address: p.value for p in self.PARAMS}
        self.di1 = m.get(0x0401); self.di2 = m.get(0x0403)
        self.di3 = m.get(0x0405); self.di4 = m.get(0x0407)
        self.di5 = m.get(0x0409); self.di6 = m.get(0x040B)
        self.di7 = m.get(0x040D); self.di8 = m.get(0x040F)
        self.do1 = m.get(0x0415); self.do2 = m.get(0x0417)
        self.do3 = m.get(0x0419); self.do4 = m.get(0x041B)
        self.do5 = m.get(0x041D)
        self.in_position_range = m.get(0x0445)
        self.inp_delay_ms      = m.get(0x0449)
        self.zero_speed_rpm    = m.get(0x044B)
        self.vel_coincidence_rpm = m.get(0x044D)
        self.arrival_vel_rpm   = m.get(0x044F)
        self.estop_mode        = m.get(0x0457)


# ─────────────────────────────────────────────────────────────────────────────
# CLASS 5 — Extension Settings (RS485 config येथे आहे)
# ─────────────────────────────────────────────────────────────────────────────
class Class5_Extension(ServoParamGroup):
    CLASS_NAME = "Class 5 – Extension Settings"
    PARAMS = [
        ParamInfo("Pr5.04", "Driver Prohibition Input",       0x0509, 16, 0,    ""),
        ParamInfo("Pr5.06", "Servo-off Mode",                 0x050D, 16, 0,    ""),
        ParamInfo("Pr5.08", "DC Bus Undervoltage Level",      0x0513, 16, 50,   "V"),
        ParamInfo("Pr5.09", "Main Power-off Detection Time",  0x0515, 16, 0,    "ms"),
        ParamInfo("Pr5.10", "Servo-off due to Alarm Mode",    0x0517, 16, 0,    ""),
        ParamInfo("Pr5.11", "Servo Braking Torque",           0x0519, 16, 0,    "%"),
        ParamInfo("Pr5.12", "Overload Level Setting",         0x051B, 16, 0,    "%"),
        ParamInfo("Pr5.20", "Position Unit Settings",         0x0529, 16, 0,    ""),
        ParamInfo("Pr5.21", "Torque Limit Selection",         0x052B, 16, 0,    ""),
        ParamInfo("Pr5.22", "2nd Torque Limit",               0x052D, 16, 300,  "%"),
        ParamInfo("Pr5.28", "LED Initial Display Status",     0x0539, 16, 1,    ""),
        ParamInfo("Pr5.29", "RS485 Communication Mode",       0x053B, 16, 0,    ""),
        ParamInfo("Pr5.30", "RS485 Baud Rate",                0x053D, 16, 5,    ""),
        ParamInfo("Pr5.31", "RS485 Axis Address (Slave ID)",  0x053F, 16, 4,    ""),
        ParamInfo("Pr5.35", "Front Panel Lock",               0x0547, 16, 0,    ""),
        ParamInfo("Pr5.37", "Torque Saturation Alarm Time",   0x0549, 16, 500,  "ms"),
    ]

    BAUD_MAP = {0: 2400, 1: 4800, 2: 9600, 3: 19200,
                4: 38400, 5: 57600, 6: 115200}

    def __init__(self):
        super().__init__()
        self.prohibition_input: Optional[int] = None
        self.servo_off_mode: Optional[int] = None
        self.undervoltage_level_v: Optional[int] = None
        self.power_off_detect_ms: Optional[int] = None
        self.alarm_servo_off_mode: Optional[int] = None
        self.braking_torque_pct: Optional[int] = None
        self.overload_level_pct: Optional[int] = None
        self.position_unit: Optional[int] = None
        self.torque_limit_select: Optional[int] = None
        self.torque_limit_2_pct: Optional[int] = None
        self.led_display: Optional[int] = None
        self.rs485_mode: Optional[int] = None
        self.rs485_baudrate_code: Optional[int] = None
        self.rs485_slave_id: Optional[int] = None
        self.panel_lock: Optional[int] = None
        self.torque_sat_alarm_ms: Optional[int] = None

    def _update_attributes(self):
        m = {p.address: p.value for p in self.PARAMS}
        self.prohibition_input     = m.get(0x0509)
        self.servo_off_mode        = m.get(0x050D)
        self.undervoltage_level_v  = m.get(0x0513)
        self.power_off_detect_ms   = m.get(0x0515)
        self.alarm_servo_off_mode  = m.get(0x0517)
        self.braking_torque_pct    = m.get(0x0519)
        self.overload_level_pct    = m.get(0x051B)
        self.position_unit         = m.get(0x0529)
        self.torque_limit_select   = m.get(0x052B)
        self.torque_limit_2_pct    = m.get(0x052D)
        self.led_display           = m.get(0x0539)
        self.rs485_mode            = m.get(0x053B)
        self.rs485_baudrate_code   = m.get(0x053D)
        self.rs485_slave_id        = m.get(0x053F)
        self.panel_lock            = m.get(0x0547)
        self.torque_sat_alarm_ms   = m.get(0x0549)

    @property
    def rs485_baudrate_value(self) -> int:
        return self.BAUD_MAP.get(self.rs485_baudrate_code, 0)


# ─────────────────────────────────────────────────────────────────────────────
# CLASS B — Status / Monitor Registers (Read Only) ← सर्वात जास्त वापर
# ─────────────────────────────────────────────────────────────────────────────
class ClassB_Status(ServoParamGroup):
    CLASS_NAME = "Class B – Status / Monitor Registers (Read Only)"
    PARAMS = [
        ParamInfo("PrB.00", "Software Version DSP",          0x0B00, 16, 0, ""),
        ParamInfo("PrB.01", "Software Version CPLD",         0x0B01, 16, 0, ""),
        ParamInfo("PrB.02", "Software Version Others",       0x0B02, 16, 0, ""),
        ParamInfo("PrB.03", "Current Alarm Code",            0x0B03, 16, 0, ""),
        ParamInfo("PrB.04", "Motor Not Rotating Cause",      0x0B04, 16, 0, ""),
        ParamInfo("PrB.05", "Driver Operation Status",       0x0B05, 16, 0, "bits"),
        ParamInfo("PrB.06", "Motor Speed (Before Filter)",   0x0B06, 16, 0, "rpm"),
        ParamInfo("PrB.07", "Motor Torque",                  0x0B07, 16, 0, "%"),
        ParamInfo("PrB.08", "Motor Current",                 0x0B08, 16, 0, "×0.1A"),
        ParamInfo("PrB.09", "Motor Speed (After Filter)",    0x0B09, 16, 0, "rpm"),
        ParamInfo("PrB.10", "DC Bus Voltage",                0x0B0A, 16, 0, "V"),
        ParamInfo("PrB.11", "Driver Temperature",            0x0B0B, 16, 0, "°C"),
        ParamInfo("PrB.12", "Analog Input AI-1",             0x0B0C, 16, 0, "mV"),
        ParamInfo("PrB.13", "Analog Input AI-2",             0x0B0D, 16, 0, "mV"),
        ParamInfo("PrB.14", "Analog Input AI-3",             0x0B0E, 16, 0, "mV"),
        ParamInfo("PrB.15", "Motor Overload Rate",           0x0B0F, 16, 0, "%"),
        ParamInfo("PrB.16", "Drive Overload Rate",           0x0B10, 16, 0, "%"),
        ParamInfo("PrB.17", "Digital Input Status",          0x0B11, 16, 0, "bits"),
        ParamInfo("PrB.18", "Digital Output Status",         0x0B12, 16, 0, "bits"),
        # 32-bit registers — 0x0B14 & 0x0B15, 0x0B16 & 0x0B17, etc.
        ParamInfo("PrB.20", "Command Position",              0x0B14, 32, 0, "cmd unit"),
        ParamInfo("PrB.21", "Motor Position",                0x0B16, 32, 0, "cmd unit"),
        ParamInfo("PrB.22", "Position Deviation",            0x0B18, 32, 0, "cmd unit"),
    ]

    def __init__(self):
        super().__init__()
        self.fw_version_dsp: Optional[int] = None
        self.fw_version_cpld: Optional[int] = None
        self.alarm_code: Optional[int] = None
        self.no_rotate_cause: Optional[int] = None
        self.drive_status: Optional[int] = None
        self.motor_speed_rpm: Optional[int] = None
        self.motor_torque_pct: Optional[int] = None
        self.motor_current_a: Optional[float] = None
        self.motor_speed_filtered_rpm: Optional[int] = None
        self.dc_bus_voltage_v: Optional[int] = None
        self.drive_temp_c: Optional[int] = None
        self.analog_input_1_mv: Optional[int] = None
        self.analog_input_2_mv: Optional[int] = None
        self.analog_input_3_mv: Optional[int] = None
        self.motor_overload_pct: Optional[int] = None
        self.drive_overload_pct: Optional[int] = None
        self.di_status: Optional[int] = None
        self.do_status: Optional[int] = None
        self.command_position: Optional[int] = None
        self.motor_position: Optional[int] = None
        self.position_deviation: Optional[int] = None

    def _update_attributes(self):
        m = {p.address: p.value for p in self.PARAMS}
        self.fw_version_dsp          = m.get(0x0B00)
        self.fw_version_cpld         = m.get(0x0B01)
        self.alarm_code              = m.get(0x0B03)
        self.no_rotate_cause         = m.get(0x0B04)
        self.drive_status            = m.get(0x0B05)
        self.motor_speed_rpm         = m.get(0x0B06)
        self.motor_torque_pct        = m.get(0x0B07)
        raw_curr = m.get(0x0B08)
        self.motor_current_a         = raw_curr / 10.0 if raw_curr is not None else None
        self.motor_speed_filtered_rpm= m.get(0x0B09)
        self.dc_bus_voltage_v        = m.get(0x0B0A)
        self.drive_temp_c            = m.get(0x0B0B)
        self.analog_input_1_mv       = m.get(0x0B0C)
        self.analog_input_2_mv       = m.get(0x0B0D)
        self.analog_input_3_mv       = m.get(0x0B0E)
        self.motor_overload_pct      = m.get(0x0B0F)
        self.drive_overload_pct      = m.get(0x0B10)
        self.di_status               = m.get(0x0B11)
        self.do_status               = m.get(0x0B12)
        self.command_position        = m.get(0x0B14)
        self.motor_position          = m.get(0x0B16)
        self.position_deviation      = m.get(0x0B18)

    @property
    def is_alarm(self) -> bool:
        return self.alarm_code is not None and self.alarm_code != 0

    @property
    def di_bits(self) -> dict[str, bool]:
        """DI1~DI8 प्रत्येकाची ON/OFF state"""
        if self.di_status is None:
            return {}
        return {f"DI{i+1}": bool(self.di_status & (1 << i)) for i in range(8)}

    @property
    def do_bits(self) -> dict[str, bool]:
        """DO1~DO5 प्रत्येकाची ON/OFF state"""
        if self.do_status is None:
            return {}
        return {f"DO{i+1}": bool(self.do_status & (1 << i)) for i in range(5)}

    def print_live(self):
        """Live monitor display"""
        print(f"\n{'─'*50}")
        print(f"  🔵 Speed     : {self.motor_speed_rpm} rpm")
        print(f"  🟡 Torque    : {self.motor_torque_pct} %")
        print(f"  🟢 Current   : {self.motor_current_a} A")
        print(f"  🔋 DC Bus    : {self.dc_bus_voltage_v} V")
        print(f"  🌡  Temp      : {self.drive_temp_c} °C")
        print(f"  ⚠️  Alarm     : {self.alarm_code} {'← FAULT!' if self.is_alarm else '(OK)'}")
        print(f"  📥 DI Status : {bin(self.di_status or 0)}")
        print(f"  📤 DO Status : {bin(self.do_status or 0)}")
        print(f"  📍 Position  : cmd={self.command_position}  motor={self.motor_position}")
        print(f"  📐 Deviation : {self.position_deviation} pulse")
        print(f"{'─'*50}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN DRIVE CLASS — सगळ्या classes एकत्र
# ─────────────────────────────────────────────────────────────────────────────
class EL7RSDrive:
    """
    Leadshine EL7-RS Servo Drive — Complete Modbus Interface

    Usage:
        drive = EL7RSDrive(port='COM3', slave_id=4, baudrate=57600)
        drive.read_class0()
        drive.read_class_status()
        print(drive.class0.control_mode_name)
        print(drive.classB.motor_speed_rpm)
    """

    def __init__(self, port: str, slave_id: int = 4,
                 baudrate: int = 57600, timeout: float = 1.0):
        self.port      = port
        self.slave_id  = slave_id
        self.baudrate  = baudrate
        self.timeout   = timeout

        # प्रत्येक Class चा object
        self.class0  = Class0_BasicSettings()
        self.class1  = Class1_GainAdjustment()
        self.class3  = Class3_VelocityTorque()
        self.class4  = Class4_IOSettings()
        self.class5  = Class5_Extension()
        self.classB  = ClassB_Status()

        self._client: Optional[ModbusSerialClient] = None

    # ── Connection ───────────────────────────────────────────────────────────
    def connect(self) -> bool:
        self._client = ModbusSerialClient(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=self.timeout
        )
        ok = self._client.connect()
        print(f"{'✅ Connected' if ok else '❌ Connection FAILED'} → {self.port} | "
              f"ID={self.slave_id} | {self.baudrate}bps")
        return ok

    def disconnect(self):
        if self._client:
            self._client.close()
            print("🔌 Disconnected")

    # ── Core Read Method ─────────────────────────────────────────────────────
    def _read_group(self, group: ServoParamGroup) -> bool:
        """
        group च्या start → end address पर्यंत एकाच request मध्ये read करतो.
        response मधून प्रत्येक parameter ची value काढतो.
        """
        if not self._client or not self._client.is_socket_open():
            print("❌ Not connected!")
            return False

        start = group.start_address
        count = group.register_count

        print(f"📡 Reading {group.CLASS_NAME}")
        print(f"   Start: 0x{start:04X} | Count: {count} registers | "
              f"End: 0x{start+count-1:04X}")

        try:
            result = self._client.read_holding_registers(
                address=start,
                count=count,
                slave=self.slave_id
            )

            if result.isError():
                print(f"   ❌ Modbus Error: {result}")
                return False

            registers = result.registers
            print(f"   ✅ Received {len(registers)} registers")

            # Parse करतो — प्रत्येक param ला value assign
            group.parse_response(registers)
            return True

        except ModbusException as e:
            print(f"   ❌ Exception: {e}")
            return False

    # ── Public Read Methods ───────────────────────────────────────────────────
    def read_class0(self) -> bool:
        """Class 0 – Basic Settings read करतो"""
        return self._read_group(self.class0)

    def read_class1(self) -> bool:
        """Class 1 – Gain Adjustment read करतो"""
        return self._read_group(self.class1)

    def read_class3(self) -> bool:
        """Class 3 – Velocity/Torque Control read करतो"""
        return self._read_group(self.class3)

    def read_class4(self) -> bool:
        """Class 4 – I/O Settings read करतो"""
        return self._read_group(self.class4)

    def read_class5(self) -> bool:
        """Class 5 – Extension/RS485 Settings read करतो"""
        return self._read_group(self.class5)

    def read_class_status(self) -> bool:
        """Class B – Live Status read करतो (सर्वात जास्त वापर)"""
        return self._read_group(self.classB)

    def read_all(self) -> dict[str, bool]:
        """सगळ्या classes एकत्र read करतो"""
        return {
            "class0":   self.read_class0(),
            "class1":   self.read_class1(),
            "class3":   self.read_class3(),
            "class4":   self.read_class4(),
            "class5":   self.read_class5(),
            "classB":   self.read_class_status(),
        }

    # ── Write Method ─────────────────────────────────────────────────────────
    def write_param(self, address: int, value: int) -> bool:
        """
        एका parameter ला value write करतो (Function Code 06)
        """
        if not self._client:
            return False
        try:
            result = self._client.write_register(
                address=address, value=value, slave=self.slave_id
            )
            ok = not result.isError()
            status = "✅" if ok else "❌"
            print(f"   {status} Write → 0x{address:04X} = {value}")
            return ok
        except ModbusException as e:
            print(f"   ❌ Write Exception: {e}")
            return False

    # ── Context Manager ───────────────────────────────────────────────────────
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()


# ─────────────────────────────────────────────────────────────────────────────
# DEMO — Simulation (actual drive शिवाय test करायला)
# ─────────────────────────────────────────────────────────────────────────────
def demo_simulation():
    """
    Actual drive नसताना logic test करायला —
    fake registers generate करतो आणि parse करतो.
    """
    print("=" * 60)
    print("  DEMO MODE — Simulated Register Values")
    print("=" * 60)

    # ── Class 0 simulation ───────────────────────────────────────
    c0 = Class0_BasicSettings()
    print(f"\n📦 {c0.CLASS_NAME}")
    print(f"   Start Addr : 0x{c0.start_address:04X}")
    print(f"   End Addr   : 0x{c0.end_address:04X}")
    print(f"   Reg Count  : {c0.register_count}")

    # Fake registers — start address (0x0001) पासून end address पर्यंत
    # 0x0001=1, 0x0002=0(padding), 0x0003=1(velocity mode), ...
    base = c0.start_address
    regs = [0] * c0.register_count
    # Pr0.00 @ offset 0x0001-0x0001=0 → value=1
    regs[0x0001 - base] = 1        # MFC bandwidth
    regs[0x0003 - base] = 1        # Control mode = 1 (Velocity)
    regs[0x0005 - base] = 0x01     # Auto gain
    regs[0x0007 - base] = 13       # Stiffness
    regs[0x0009 - base] = 300      # Inertia ratio
    regs[0x000B - base] = 0        # Pulse selection
    regs[0x000F - base] = 3        # Pulse mode
    # 32-bit: Pr0.08 @ 0x0010 & 0x0011
    regs[0x0010 - base] = 0        # High word
    regs[0x0011 - base] = 10000    # Low word → 10000 pulses/rev
    regs[0x001B - base] = 300      # Torque limit 300%

    c0.parse_response(regs)
    print(f"\n   ✅ Parsed Values:")
    print(f"   control_mode       = {c0.control_mode} → '{c0.control_mode_name}'")
    print(f"   stiffness          = {c0.stiffness}")
    print(f"   inertia_ratio      = {c0.inertia_ratio} %")
    print(f"   pulse_count_per_rev= {c0.pulse_count_per_rev} pulse/rev")
    print(f"   torque_limit_pct   = {c0.torque_limit_pct} %")

    # ── Class B simulation ───────────────────────────────────────
    cB = ClassB_Status()
    print(f"\n📊 {cB.CLASS_NAME}")
    print(f"   Start Addr : 0x{cB.start_address:04X}")
    print(f"   End Addr   : 0x{cB.end_address:04X}")
    print(f"   Reg Count  : {cB.register_count}")

    base = cB.start_address
    regs = [0] * cB.register_count
    regs[0x0B00 - base] = 0x0125   # FW version DSP
    regs[0x0B03 - base] = 0        # No alarm
    regs[0x0B05 - base] = 0b0000_0011  # Drive ready + servo on
    regs[0x0B06 - base] = 1450     # Motor speed 1450 rpm
    regs[0x0B07 - base] = 35       # Torque 35%
    regs[0x0B08 - base] = 42       # Current 4.2A (×0.1)
    regs[0x0B0A - base] = 310      # DC bus 310V
    regs[0x0B0B - base] = 45       # Temp 45°C
    regs[0x0B0F - base] = 20       # Overload 20%
    regs[0x0B11 - base] = 0b0001_0111  # DI1,DI2,DI3,DI5 active
    regs[0x0B12 - base] = 0b0000_0110  # DO2,DO3 active
    # Position 32-bit
    regs[0x0B14 - base] = 0        # Cmd pos H
    regs[0x0B15 - base] = 50000    # Cmd pos L
    regs[0x0B16 - base] = 0        # Motor pos H
    regs[0x0B17 - base] = 49980    # Motor pos L
    regs[0x0B18 - base] = 0        # Deviation H
    regs[0x0B19 - base] = 20       # Deviation L = 20 pulse

    cB.parse_response(regs)
    cB.print_live()

    print("\n   DI Status breakdown:")
    for name, state in cB.di_bits.items():
        print(f"   {name}: {'🟢 ON' if state else '⚪ OFF'}")

    # ── Class 3 simulation ───────────────────────────────────────
    c3 = Class3_VelocityTorque()
    print(f"\n⚙️  {c3.CLASS_NAME}")
    print(f"   Start Addr : 0x{c3.start_address:04X}")
    print(f"   End Addr   : 0x{c3.end_address:04X}")
    print(f"   Reg Count  : {c3.register_count}")

    base = c3.start_address
    regs = [0] * c3.register_count
    regs[0x0301 - base] = 1        # Internal speed source
    regs[0x0305 - base] = 500      # Gain 500 rpm/V
    regs[0x0309 - base] = 300      # Speed 1 = 300 rpm
    regs[0x030B - base] = 600      # Speed 2 = 600 rpm
    regs[0x030D - base] = 1000     # Speed 3 = 1000 rpm
    regs[0x0319 - base] = 500      # Accel 500ms
    regs[0x031B - base] = 500      # Decel 500ms

    c3.parse_response(regs)
    print(f"\n   ✅ Internal Speeds: {c3.speed_list}")
    print(f"   Accel Time: {c3.accel_time_ms} ms")
    print(f"   Decel Time: {c3.decel_time_ms} ms")

    print("\n" + "=" * 60)
    print("  ✅ Demo complete! Actual drive साठी EL7RSDrive वापरा.")
    print("=" * 60)


# ─────────────────────────────────────────────────────────────────────────────
# REAL DRIVE USAGE EXAMPLE
# ─────────────────────────────────────────────────────────────────────────────
def real_drive_example():
    """
    Actual drive शी connect होण्याचा example.
    PORT आणि SLAVE_ID बदलायचे.
    """
    PORT     = 'COM3'    # Windows: 'COM3' | Linux: '/dev/ttyUSB0'
    SLAVE_ID = 4         # Pr5.31 default = 4
    BAUD     = 57600     # Pr5.30 = 5 → 57600

    with EL7RSDrive(port=PORT, slave_id=SLAVE_ID, baudrate=BAUD) as drive:

        # ── Class 0 read (एकच request)
        drive.read_class0()
        print(f"Control Mode : {drive.class0.control_mode_name}")
        print(f"Inertia Ratio: {drive.class0.inertia_ratio} %")
        print(f"Torque Limit : {drive.class0.torque_limit_pct} %")

        # ── Gain settings
        drive.read_class1()
        print(f"Vel Loop Gain: {drive.class1.vel_loop_gain_1} Hz")

        # ── Live status polling loop
        print("\n📡 Live Monitor (5 seconds)...")
        for _ in range(5):
            drive.read_class_status()
            drive.classB.print_live()
            time.sleep(1.0)

        # ── Write example: internal speed 1 = 500 rpm
        drive.write_param(address=0x0309, value=500)

        # ── Read back to verify
        drive.read_class3()
        print(f"Speed 1 after write: {drive.class3.speed_1} rpm")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Leadshine EL7-RS Modbus Library\n")
    print("1) Demo (simulation)  2) Real drive")
    choice = input("Choice [1/2]: ").strip()

    if choice == "2":
        real_drive_example()
    else:
        demo_simulation()