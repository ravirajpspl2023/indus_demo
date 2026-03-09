from module.connectors.DELTA_C200._BaseGroup import _BaseGroup,ParamDef
# ═══════════════════════════════════════════════════════════════
#  GROUP 07 — Special Parameters  0x0700 ~ 0x071F
# ═══════════════════════════════════════════════════════════════

class Group07(_BaseGroup):
    GROUP_NAME = "Group 07 — Special Parameters"
    PARAMS = [
        ParamDef("Pr07-00","Software Brake Level",             0x0701,16,"R/W",380, "V",  "DC bus level to activate brake"),
        ParamDef("Pr07-01","DC Brake Current Level",           0x0702,16,"R/W",0,   "%"),
        ParamDef("Pr07-02","DC Brake Time at Start-up",        0x0703,16,"R/W",0,   "s"),
        ParamDef("Pr07-03","DC Brake Time at Stop",            0x0704,16,"R/W",0,   "s"),
        ParamDef("Pr07-04","Start-Point for DC Brake",         0x0705,16,"R/W",0,   "Hz"),
        ParamDef("Pr07-06","Speed Search at Start",            0x0707,16,"R/W",0,   ""),
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
