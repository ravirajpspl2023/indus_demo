from module.connectors.DELTA_C200._BaseGroup import _BaseGroup,ParamDef

class Group04(_BaseGroup):
    GROUP_NAME = "Group 04 — Multi-step Speed"
    PARAMS = [
        ParamDef("Pr04-00","1st Step Speed Frequency",         0x0401,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-01","2nd Step Speed Frequency",         0x0402,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-02","3rd Step Speed Frequency",         0x0403,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-03","4th Step Speed Frequency",         0x0404,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-04","5th Step Speed Frequency",         0x0405,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-05","6th Step Speed Frequency",         0x0406,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-06","7th Step Speed Frequency",         0x0407,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-07","8th Step Speed Frequency",         0x0408,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-08","9th Step Speed Frequency",         0x0409,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-09","10th Step Speed Frequency",        0x040A,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-10","11th Step Speed Frequency",        0x040B,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-11","12th Step Speed Frequency",        0x040C,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-12","13th Step Speed Frequency",        0x040D,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-13","14th Step Speed Frequency",        0x040E,16,"R/W",0,  "Hz"),
        ParamDef("Pr04-14","15th Step Speed Frequency",        0x040F,16,"R/W",0,  "Hz"),
    ]
