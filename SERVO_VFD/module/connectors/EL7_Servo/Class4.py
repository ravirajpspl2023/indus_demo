from module.connectors.EL7_Servo._BaseParamClass import _BaseParamClass,ParamDef

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
        # ParamDef("Pr4.64","AO1 Output Function",                0x0481,16,"R/W",0,    ""),
        # ParamDef("Pr4.65","AO1 Signal Selection",               0x0483,16,"R/W",0x04, ""),
        # ParamDef("Pr4.66","AO1 Amplification",                  0x0485,16,"R/W",100,  "%"),
        # ParamDef("Pr4.67","AO1 Communication Output Value",     0x0487,16,"R/W",0,    ""),
        # ParamDef("Pr4.68","AO1 Output Offset",                  0x0489,16,"R/W",0,    ""),
    ]

