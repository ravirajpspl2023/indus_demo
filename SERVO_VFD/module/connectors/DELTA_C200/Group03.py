from module.connectors.DELTA_C200._BaseGroup import _BaseGroup,ParamDef
# ═══════════════════════════════════════════════════════════════
#  GROUP 03 — Analog Input / Output  0x0300 ~ 0x0332
# ═══════════════════════════════════════════════════════════════
class Group03(_BaseGroup):
    GROUP_NAME = "Group 03 — Analog Input / Output"
    PARAMS = [
        ParamDef("Pr03-00","AVI Analog Input Selection",       0x0301,16,"R/W",1,  "",   "0=No func|1=Freq cmd|2=Torque|4=PID target|5=PID feedback"),
        ParamDef("Pr03-01","ACI Analog Input Selection",       0x0302,16,"R/W",0,  ""),
        ParamDef("Pr03-02","AUI Analog Input Selection",       0x0303,16,"R/W",0,  ""),
        ParamDef("Pr03-03","Analog Input Bias AVI",            0x0304,16,"R/W",0,  "%",  "-100~100"),
        ParamDef("Pr03-04","Analog Input Bias ACI",            0x0305,16,"R/W",0,  "%"),
        ParamDef("Pr03-05","Analog Voltage Input Bias AUI",    0x0306,16,"R/W",0,  "%"),
        ParamDef("Pr03-07","Positive/negative Bias Mode AVI",  0x0308,16,"R/W",0,  "%"),
        ParamDef("Pr03-08","Positive/negative Bias Mode ACI",  0x0309,16,"R/W",0,  "%"),
        ParamDef("Pr03-09","Positive/negative Bias Mode AUI",  0x030A,16,"R/W",0,  "%"),
        ParamDef("Pr03-10","Analog Frequency Command Reverse Run", 0x030B,16,"R/W",0,  "%"),
        ParamDef("Pr03-11","Analog input AVI Gain",            0x030C,16,"R/W",100,"",   "-500~500"),
        ParamDef("Pr03-12","Analog Input Gain ACI",            0x030D,16,"R/W",100,""),
        ParamDef("Pr03-13","Analog Positive Input Gain AUI",   0x030E,16,"R/W",100,""),
        ParamDef("Pr03-14","Analog Negative Input Gain AUI",   0x030F,16,"R/W",100,""),
        ParamDef("Pr03-15","AVI Filter Time",                  0x0310,16,"R/W",50, "×0.01s"),
        ParamDef("Pr03-16","ACI Filter Time",                  0x0311,16,"R/W",50, "×0.01s"),
        ParamDef("Pr03-17","AUI Filter Time",                  0x0312,16,"R/W",50, "×0.01s"),
        ParamDef("Pr03-18","Addition Function Analog Input",   0x0313,16,"R/W",50, "×0.01s"),
        ParamDef("Pr03-19","4-20mA Analog Input Signal Loss",  0x0314,16,"R/W",50, "×0.01s"),
        ParamDef("Pr03-20","AFM1 Output Function",             0x0315,16,"R/W",0,  ""),
        ParamDef("Pr03-21","AFM1 Output Gain",                 0x0316,16,"R/W",100,"%"),
        ParamDef("Pr03-22","Analog Output 1 REV Direction AFM1",0x0317,16,"R/W",100,"%"),
        ParamDef("Pr03-23","AFM2 Output Function",             0x0318,16,"R/W",0,  ""),
        ParamDef("Pr03-24","AFM2 Output Gain",                 0x0319,16,"R/W",100,"%"),
        ParamDef("Pr03-28","AVI Input Type",                   0x031D,16,"R/W",0,  "",   "0=0-10V|1=0-20mA|2=4-20mA"),
        ParamDef("Pr03-29","ACI Input Type",                   0x031E,16,"R/W",2,  "",   "0=0-10V|1=0-20mA|2=4-20mA"),
        ParamDef("Pr03-31","AFM2 0-20mA Output Selection",     0x0320,16,"R/W",0,  ""),
        ParamDef("Pr03-32","AFM1 DC Output Setting Level",     0x0321,16,"R/W",0,  ""),
        ParamDef("Pr03-33","AFM2 DC Output Setting Level",     0x0322,16,"R/W",0,  ""),
        ParamDef("Pr03-44","MO by AI Level",                   0x032D,16,"R/W",0,  ""),
        ParamDef("Pr03-45","AI Upper Level",                   0x032E,16,"R/W",0,  ""),
        ParamDef("Pr03-46","AI Lower Level",                   0x032F,16,"R/W",0,  ""),
        ParamDef("Pr03-50","AVI Analog Monitor",               0x0333,16,"R",  0,  "%",  "Read-only current AVI value"),
    ]
