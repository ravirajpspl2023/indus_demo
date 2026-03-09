from module.connectors.EL7_Servo._BaseParamClass import _BaseParamClass,ParamDef

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
