from module.connectors.DELTA_C200._BaseGroup import _BaseGroup,ParamDef

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