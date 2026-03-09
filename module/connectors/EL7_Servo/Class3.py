from module.connectors.EL7_Servo._BaseParamClass import _BaseParamClass,ParamDef

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

