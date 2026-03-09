from module.connectors.EL7_Servo._BaseParamClass import _BaseParamClass,ParamDef


# ═══════════════════════════════════════════════════════════════
#  CLASS 0 — Basic Settings   0x0001 ~ 0x006B
# ═══════════════════════════════════════════════════════════════

class Class0(_BaseParamClass):
    CLASS_NAME = "Class 0 — Basic Settings"
    PARAMS = [
        ParamDef("Pr0.00","Model-following/ZTC Bandwidth",      0x0001,16,"R/W",1,    "0.1Hz"),
        ParamDef("Pr0.01","Control Mode Settings",              0x0003,16,"R/W",0,    "",    "0=Pos|1=Vel|2=Torque|6=PR"),
        ParamDef("Pr0.02","Real-time Auto Gain Adjusting",      0x0005,16,"R/W",0x1,  ""),
        ParamDef("Pr0.03","Real-time Auto Stiffness Adjusting", 0x0007,16,"R/W",11,   "",    "0~31"),
        ParamDef("Pr0.04","Inertia Ratio",                      0x0009,16,"R/W",250,  "%"),
        ParamDef("Pr0.05","Command Pulse Input Selection",       0x000B,16,"R/W",0,    "",    "0=200kHz|1=4MHz"),
        ParamDef("Pr0.06","Command Pulse Polarity Inversion",   0x000D,16,"R/W",0,    ""),
        ParamDef("Pr0.07","Command Pulse Input Mode",           0x000F,16,"R/W",3,    "",    "0=CW/CCW|1=Pulse+Dir|3=AB×4"),
        ParamDef("Pr0.08","1st Cmd Pulse Count/Revolution",     0x0010,32,"R/W",10000,"pulse/rev"),
        ParamDef("Pr0.09","1st Cmd Freq Divider Numerator",     0x0012,32,"R/W",1,    ""),
        ParamDef("Pr0.10","1st Cmd Freq Divider Denominator",   0x0014,32,"R/W",1,    ""),
        ParamDef("Pr0.11","Encoder Output Pulse Count/Rev",     0x0017,16,"R/W",2500, "pulse/rev"),
        ParamDef("Pr0.12","Pulse Output Logic Inversion",       0x0019,16,"R/W",0,    ""),
        ParamDef("Pr0.13","1st Torque Limit",                   0x001B,16,"R/W",350,  "%"),
        ParamDef("Pr0.14","Excessive Position Deviation",       0x001D,16,"R/W",30,   "x10k pulse"),
        ParamDef("Pr0.15","Absolute Encoder Settings",          0x001F,16,"R/W",0,    "",    "0=Inc|1=Abs single|2=Abs multi"),
        ParamDef("Pr0.16","Regenerative Resistance",            0x0021,16,"R/W",100,  "Ohm"),
        ParamDef("Pr0.17","Regenerative Resistor Power Rating", 0x0023,16,"R/W",50,   "W"),
        ParamDef("Pr0.22","PR and P/S/T Mode Switching",        0x002D,16,"R/W",0,    ""),
        ParamDef("Pr0.25","Auxiliary Function",                 0x0033,16,"R/W",0,    ""),
        ParamDef("Pr0.26","Simulated I/O",                      0x0035,16,"R/W",0,    ""),
        ParamDef("Pr0.30","Encoder Feedback Mode",              0x0037,16,"R/W",0,    ""),
        ParamDef("Pr0.31","External Encoder Type",              0x0039,16,"R/W",0,    ""),
        ParamDef("Pr0.32","External Encoder Direction",         0x003B,16,"R/W",0,    ""),
        ParamDef("Pr0.33","Excessive Hybrid Deviation",         0x0043,16,"R/W",16000,""),
        ParamDef("Pr0.34","Clear Hybrid Control Deviation",     0x0045,16,"R/W",0,    ""),
        ParamDef("Pr0.35","Ext Encoder Divider Numerator",      0x0047,16,"R/W",0,    ""),
        ParamDef("Pr0.36","Ext Encoder Divider Denominator",    0x0049,16,"R/W",10000,""),
        ParamDef("Pr0.37","Ext Encoder Feedback Pulse/Rev",     0x004B,16,"R/W",0,    "pulse/rev"),
        ParamDef("Pr0.38","Z-signal Pulse Input Source",        0x004D,16,"R/W",0,    ""),
        ParamDef("Pr0.40","Mapping Parameter 1",                0x0050,32,"R/W",0,    ""),
        ParamDef("Pr0.41","Mapping Parameter 2",                0x0052,32,"R/W",0,    ""),
        ParamDef("Pr0.42","Mapping Parameter 3",                0x0054,32,"R/W",0,    ""),
        ParamDef("Pr0.43","Mapping Parameter 4",                0x0056,32,"R/W",0,    ""),
        ParamDef("Pr0.50","Mapping Param 1 Indicator",          0x0064,32,"R/W",0x49, ""),
        ParamDef("Pr0.51","Mapping Param 2 Indicator",          0x0066,32,"R/W",0x49, ""),
        ParamDef("Pr0.52","Mapping Param 3 Indicator",          0x0068,32,"R/W",0x49, ""),
        ParamDef("Pr0.53","Mapping Param 4 Indicator",          0x006A,32,"R/W",0x49, ""),
    ]
