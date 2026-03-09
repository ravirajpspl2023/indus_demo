from module.connectors.DELTA_C200._BaseGroup import _BaseGroup,ParamDef

# ═══════════════════════════════════════════════════════════════
#  GROUP 09 — Communication Parameters  0x0900 ~ 0x092E
#  ★ RS485 setup lives here
# ═══════════════════════════════════════════════════════════════
class Group09(_BaseGroup):
    GROUP_NAME = "Group 09 — Communication Parameters  [RS485 here!]"
    PARAMS = [
        ParamDef("Pr09-00","COM1 Slave Address",               0x0901,16,"R/W",1,    "",  "★ 1~254 | Default=1"),
        ParamDef("Pr09-01","COM1 Baud Rate",                   0x0902,16,"R/W",9600, "bps","★ 4800~115200"),
        ParamDef("Pr09-02","COM1 Transmission Fault Treatment", 0x0903,16,"R/W",3,   "",  "0=Warn+run|1=Warn+ramp|2=Warn+coast|3=No warn"),
        ParamDef("Pr09-03","COM1 Time-out Detection",          0x0904,16,"R/W",0,    "s",  "0=Disable|0.1~100.0"),
        ParamDef("Pr09-04","COM1 Communication Protocol",      0x0905,16,"R/W",1,    "",  "★ 1=7N2 ASCII|12=8N1 RTU|13=8N2 RTU|14=8E1 RTU"),
        ParamDef("Pr09-09","Response Delay Time",              0x090A,16,"R/W",2,    "ms", "0.0~200.0ms"),
        ParamDef("Pr09-10","Serial Comm. Freq. Command",       0x090B,16,"R/W",60,   "Hz"),
        ParamDef("Pr09-11","Block Transfer 1",                 0x090C,16,"R/W",0,    ""),
        ParamDef("Pr09-12","Block Transfer 2",                 0x090D,16,"R/W",0,    ""),
        ParamDef("Pr09-13","Block Transfer 3",                 0x090E,16,"R/W",0,    ""),
        ParamDef("Pr09-14","Block Transfer 4",                 0x090F,16,"R/W",0,    ""),
        ParamDef("Pr09-15","Block Transfer 5",                 0x0910,16,"R/W",0,    ""),
        ParamDef("Pr09-16","Block Transfer 6",                 0x0911,16,"R/W",0,    ""),
        ParamDef("Pr09-17","Block Transfer 7",                 0x0912,16,"R/W",0,    ""),
        ParamDef("Pr09-18","Block Transfer 8",                 0x0913,16,"R/W",0,    ""),
        ParamDef("Pr09-19","Block Transfer 9",                 0x0914,16,"R/W",0,    ""),
        ParamDef("Pr09-20","Block Transfer 10",                0x0915,16,"R/W",0,    ""),
        ParamDef("Pr09-21","Block Transfer 11",                0x0916,16,"R/W",0,    ""),
        ParamDef("Pr09-22","Block Transfer 12",                0x0917,16,"R/W",0,    ""),
        ParamDef("Pr09-23","Block Transfer 13",                0x0918,16,"R/W",0,    ""),
        ParamDef("Pr09-24","Block Transfer 14",                0x0919,16,"R/W",0,    ""),
        ParamDef("Pr09-25","Block Transfer 15",                0x091A,16,"R/W",0,    ""),
        ParamDef("Pr09-26","Block Transfer 16",                0x091B,16,"R/W",0,    ""),
        ParamDef("Pr09-30","Communication Decoding Method",    0x091F,16,"R/W",1,    "",  "0=Decoding 20xx|1=Decoding 60xx"),
        ParamDef("Pr09-31","Internal Communication Protocol",  0x0920,16,"R/W",0,    "",  "0=Modbus 485"),
        ParamDef("Pr09-35","PLC Address",                      0x0924,16,"R/W",2,    ""),
        ParamDef("Pr09-36","CANopen Slave Address",            0x0925,16,"R/W",0,    ""),
        ParamDef("Pr09-37","CANopen Speed",                    0x0926,16,"R/W",0,    ""),
        ParamDef("Pr09-38","CANopen Frequency Gain",           0x0927,16,"R/W",100,  "×0.01"),
        ParamDef("Pr09-46","CANopen Master Function",          0x092F,16,"R/W",0,    ""),
    ]
