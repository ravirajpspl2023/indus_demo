from module.connectors.EL7_Servo._BaseParamClass import _BaseParamClass,ParamDef

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