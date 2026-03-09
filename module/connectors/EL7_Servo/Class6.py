from module.connectors.EL7_Servo._BaseParamClass import _BaseParamClass,ParamDef

# ═══════════════════════════════════════════════════════════════
#  CLASS 6 — Other Settings   0x0603 ~ 0x067F
# ═══════════════════════════════════════════════════════════════
class Class6(_BaseParamClass):
    CLASS_NAME = "Class 6 — Other Settings"
    PARAMS = [
        ParamDef("Pr6.01","Encoder Zero Position Compensation",  0x0603,16,"R/W",0,  ""),
        ParamDef("Pr6.03","JOG Torque Command",                  0x0607,16,"R/W",350,"%"),
        ParamDef("Pr6.04","JOG Velocity Command",                0x0609,16,"R/W",30, "rpm"),
        ParamDef("Pr6.05","Position 3rd Gain Valid Time",        0x060B,16,"R/W",0,  "ms"),
        ParamDef("Pr6.06","Position 3rd Gain Scale Factor",      0x060D,16,"R/W",100,"%"),
        ParamDef("Pr6.07","Torque Command Additional Value",     0x060F,16,"R/W",0,  "%", "Gravity compensation"),
        ParamDef("Pr6.08","+ve Direction Torque Compensation",   0x0611,16,"R/W",0,  "%"),
        ParamDef("Pr6.09","-ve Direction Torque Compensation",   0x0613,16,"R/W",0,  "%"),
        ParamDef("Pr6.11","Current Response Settings",           0x0617,16,"R/W",100,""),
        ParamDef("Pr6.14","Max Time to Stop After Disable",      0x061D,16,"R/W",500,"ms"),
        ParamDef("Pr6.20","Trial Run Distance",                  0x0629,16,"R/W",10, "rev"),
        ParamDef("Pr6.21","Trial Run Waiting Time",              0x062B,16,"R/W",300,"ms"),
        ParamDef("Pr6.22","Number of Trial Run Cycles",          0x062D,16,"R/W",5,  ""),
        ParamDef("Pr6.25","Trial Run Acceleration",              0x0633,16,"R/W",200,"ms"),
        ParamDef("Pr6.28","Observer Gain",                       0x0639,16,"R/W",0,  ""),
        ParamDef("Pr6.29","Observer Filter",                     0x063B,16,"R/W",0,  ""),
        ParamDef("Pr6.56","Blocked Rotor Alarm Torque",          0x0671,16,"R/W",300,"%"),
        ParamDef("Pr6.57","Blocked Rotor Alarm Delay Time",      0x0673,16,"R/W",400,"ms"),
        ParamDef("Pr6.63","Absolute Multiturn Data Limit",       0x067F,16,"R/W",0,  ""),
    ]


