from module.connectors.EL7_Servo._BaseParamClass import _BaseParamClass,ParamDef

# ═══════════════════════════════════════════════════════════════
#  CLASS 8 — PR-Control Parameters   0x6000 ~ 0x602F
# ═══════════════════════════════════════════════════════════════
class Class8(_BaseParamClass):
    CLASS_NAME = "Class 8 — PR-Control Parameters"
    PARAMS = [
        ParamDef("Pr8.00","PR Control Enable",                  0x6000,16,"R/W",0,  "",  "0=Off|1=On"),
        ParamDef("Pr8.01","PR Path Count",                      0x6001,16,"R/W",16, ""),
        ParamDef("Pr8.02","PR Control Operation",               0x6002,16,"R/W",0,  ""),
        ParamDef("Pr8.06","Software Positive Limit Hi",         0x6006,16,"R/W",0,  ""),
        ParamDef("Pr8.07","Software Positive Limit Lo",         0x6007,16,"R/W",0,  ""),
        ParamDef("Pr8.08","Software Negative Limit Hi",         0x6008,16,"R/W",0,  ""),
        ParamDef("Pr8.09","Software Negative Limit Lo",         0x6009,16,"R/W",0,  ""),
        ParamDef("Pr8.10","Homing Mode",                        0x600A,16,"R/W",0,  "",  "0=None|1=Z|2=DI"),
        ParamDef("Pr8.11","Homing Zero Position Hi",            0x600B,16,"R/W",0,  ""),
        ParamDef("Pr8.12","Homing Zero Position Lo",            0x600C,16,"R/W",0,  ""),
        ParamDef("Pr8.13","Home Position Offset Hi",            0x600D,16,"R/W",0,  ""),
        ParamDef("Pr8.14","Home Position Offset Lo",            0x600E,16,"R/W",0,  ""),
        ParamDef("Pr8.15","High Homing Velocity",               0x600F,16,"R/W",200,"rpm"),
        ParamDef("Pr8.16","Low Homing Velocity",                0x6010,16,"R/W",50, "rpm"),
        ParamDef("Pr8.17","Homing Acceleration",                0x6011,16,"R/W",100,"ms"),
        ParamDef("Pr8.18","Homing Deceleration",                0x6012,16,"R/W",100,"ms"),
        ParamDef("Pr8.19","Homing Torque Holding Time",         0x6013,16,"R/W",100,"ms"),
        ParamDef("Pr8.20","Homing Torque",                      0x6014,16,"R/W",100,"%"),
        ParamDef("Pr8.21","Homing Overtravel Alarm Range",      0x6015,16,"R/W",0,  "rev"),
        ParamDef("Pr8.22","Emergency Stop at Limit Decel",      0x6016,16,"R/W",10, "ms"),
        ParamDef("Pr8.23","STP Emergency Stop Decel",           0x6017,16,"R/W",50, "ms"),
        ParamDef("Pr8.24","IO Combination Trigger Mode",        0x601A,16,"R/W",0,  ""),
        ParamDef("Pr8.25","IO Combination Filter",              0x601B,16,"R/W",5,  "ms"),
        ParamDef("Pr8.26","S-code Current Output",              0x601C,16,"R/W",0,  ""),
        ParamDef("Pr8.27","PR Warning Status",                  0x601D,16,"R/W",0,  ""),
        ParamDef("Pr8.39","JOG Velocity",                       0x6027,16,"R/W",100,"rpm"),
        ParamDef("Pr8.40","JOG Acceleration",                   0x6028,16,"R/W",100,"ms"),
        ParamDef("Pr8.41","JOG Deceleration",                   0x6029,16,"R/W",100,"ms"),
        ParamDef("Pr8.42","Command Position Hi (Read)",         0x602A,16,"R",  0,  ""),
        ParamDef("Pr8.43","Command Position Lo (Read)",         0x602B,16,"R",  0,  ""),
        ParamDef("Pr8.44","Motor Position Hi (Read)",           0x602C,16,"R",  0,  ""),
        ParamDef("Pr8.45","Motor Position Lo (Read)",           0x602D,16,"R",  0,  ""),
        ParamDef("Pr8.46","Input IO Status",                    0x602E,16,"R",  0,  ""),
        ParamDef("Pr8.47","Output IO Status",                   0x602F,16,"R",  0,  ""),
    ]
