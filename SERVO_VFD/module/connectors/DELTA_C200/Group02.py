from module.connectors.DELTA_C200._BaseGroup import _BaseGroup,ParamDef
# ═══════════════════════════════════════════════════════════════
#  GROUP 02 — Digital I/O Parameters  0x0200 ~ 0x0237
# ═══════════════════════════════════════════════════════════════
class Group02(_BaseGroup):
    GROUP_NAME = "Group 02 — Digital Input / Output"
    PARAMS = [
        ParamDef("Pr02-00","2/3-Wire Operation Control",       0x0201,16,"R/W",0,  "",  "0=2-wire|1=3-wire"),
        ParamDef("Pr02-01","Multi-function Input MI1",         0x0202,16,"R/W",1,  "",  "1=FWD/STOP|6=JOG|19=UP|20=DOWN"),
        ParamDef("Pr02-02","Multi-function Input MI2",         0x0203,16,"R/W",2,  "",  "2=REV/STOP"),
        ParamDef("Pr02-03","Multi-function Input MI3",         0x0204,16,"R/W",3,  ""),
        ParamDef("Pr02-04","Multi-function Input MI4",         0x0205,16,"R/W",4,  ""),
        ParamDef("Pr02-05","Multi-function Input MI5",         0x0206,16,"R/W",0,  ""),
        ParamDef("Pr02-06","Multi-function Input MI6",         0x0207,16,"R/W",0,  ""),
        ParamDef("Pr02-07","Multi-function Input MI7",         0x0208,16,"R/W",0,  ""),
        ParamDef("Pr02-08","Multi-function Input MI8",         0x0209,16,"R/W",0,  ""),
        ParamDef("Pr02-09","UP/DOWN Key Mode",                 0x020A,16,"R/W",1,  "×2ms"),
        ParamDef("Pr02-10","Con.The Accel./Decel.UP/DOWN Key", 0x020B,16,"R/W",0,  ""),
        ParamDef("Pr02-11","Digital Input Response Time",      0x020C,16,"R/W",1,  ""),
        ParamDef("Pr02-12","Digital Input Operation Direction",0x020D,16,"R",  0,  "",  "Read-only bit status"),
        ParamDef("Pr02-13","Multi-function Output RY1",        0x020E,16,"R/W",11, "",  "★ 0=No func|1=Run|2=At-speed|11=Fault"),
        ParamDef("Pr02-14","Multi-function Output RY2",        0x020F,16,"R/W",1,  ""),
        ParamDef("Pr02-16","Multi-function Output MO1",        0x0210,16,"R/W",0,  ""),
        ParamDef("Pr02-17","Multi-function Output MO2",        0x0212,16,"R/W",0,  ""),
        ParamDef("Pr02-18","Multi-function Output Direction",  0x0213,16,"R",  0,  "",  "Read-only bit status"),
        ParamDef("Pr02-36","Digital Input Invert",             0x0224,16,"R/W",0,  ""),
        ParamDef("Pr02-50","DI Current Status (read-only)",    0x0232,16,"R",  0,  "",  "★ Current DI state bits"),
        ParamDef("Pr02-51","DO Current Status (read-only)",    0x0233,16,"R",  0,  "",  "★ Current DO state bits"),
    ]

    
