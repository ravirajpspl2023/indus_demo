from module.connectors.DELTA_C200._BaseGroup import _BaseGroup,ParamDef

# ═══════════════════════════════════════════════════════════════
#  GROUP 00 — Drive Parameters  0x0000 ~ 0x0032
# ═══════════════════════════════════════════════════════════════
class Group00(_BaseGroup):
    GROUP_NAME = "Group 00 — Drive Parameters"
    PARAMS = [
        ParamDef("Pr00-00","Identity Code of AC Drive",        0x0001,16,"R",   0,    "",    "Read-only model ID"),
        ParamDef("Pr00-01","Rated Current Display",            0x0002,16,"R",   0,    "A"),
        ParamDef("Pr00-02","Parameter Reset",                  0x0003,16,"R/W", 0,    "",    "9: Reset all to defaults"),
        ParamDef("Pr00-03","Start-up Display Selection",       0x0004,16,"R/W", 0,    "",    "0=Hz|1=A|2=RPM|3=User"),
        ParamDef("Pr00-04","Content of Multi-function Display",0x0005,16,"R/W", 0,    ""),
        ParamDef("Pr00-05","Coeffi Gain Actual Output Freq",   0x0006,16,"R/W", 0,    ""),
        ParamDef("Pr00-06","Software Version",                 0x0007,16,"R",   0,    ""),
        ParamDef("Pr00-07","Parameter Protection Password",    0x0008,16,"R/W", 0,    ""),
        ParamDef("Pr00-08","Param Prote Password Setting",     0x0009,16,"R/W", 0,    ""),
        ParamDef("Pr00-10","Control Mode",                     0x000B,16,"R/W", 0,    "",    "0=V/F|1=V/F+PG|2=SVC|3=FOC"),
        ParamDef("Pr00-11","Speed Control Mode",               0x000C,16,"R/W", 0,    ""),
        ParamDef("Pr00-13","Control of Torque Mode",           0x000E,16,"R/W", 1,    "",    "0=Disable STOP|1=Enable STOP"),
        ParamDef("Pr00-14","High Speed Mode Setting",          0x000F,16,"R/W", 6,    "kHz", "2~15kHz"),
        ParamDef("Pr00-16","Load Selection ",                  0x0011,16,"R/W", 0,    ""),
        ParamDef("Pr00-17","Carrier Frequency Reduction",      0x0012,16,"R/W", 0,    ""),
        ParamDef("Pr00-18","Single or Three-phase setting",    0x0013,16,"R/W", 0,    ""),
        ParamDef("Pr00-19","PLC Command Mask",                 0x0014,16,"R/W", 0,    ""),
        ParamDef("Pr00-20","Source of Frequency Command AUTO", 0x0015,16,"R/W", 0,    "",    "★ 0=Keypad|1=RS485|2=Analog|..."),
        ParamDef("Pr00-21","Source of Operation Command AUTO", 0x0016,16,"R/W", 0,    "",    "★ 0=Keypad|1=External|2=RS485"),
        ParamDef("Pr00-22","Stop Method",                      0x0017,16,"R/W", 0,    "",    "0=Ramp|1=Coast"),
        ParamDef("Pr00-23","Control of Motor Direction",       0x0018,16,"R/W", 0,    "times"),
        ParamDef("Pr00-24","Memory of Frequency Command",      0x0019,16,"R/W", 60,   "s"),
        ParamDef("Pr00-25","User Defined Characteristics",     0x001A,16,"R/W", 0,    ""),
        ParamDef("Pr00-26","Max User-defined Value",           0x001B,16,"R/W", 0,    ""),
        ParamDef("Pr00-27","User-defined Coefficient K",       0x001C,16,"R/W", 0,    ""),
        ParamDef("Pr00-29","LOCAL/REMOTE Selection",           0x001E,16,"R/W", 0,    ""),
        ParamDef("Pr00-30","Source Master Frequency Command",  0x001F,16,"R",   0,    ""),
        ParamDef("Pr00-31","Source Operation Command",         0x0020,16,"R",   0,    ""),
        ParamDef("Pr00-32","Digital Keypad STOP Function",     0x0021,16,"R/W", 0,    ""),
        ParamDef("Pr00-48","Display Filter (curr)",            0x0031,16,"R/W", 0,    ""),
        ParamDef("Pr00-49","Display Filter Time (Keypad",      0x0032,16,"R/W", 0,    ""),
        ParamDef("Pr00-50","Software Version (date)",          0x0033,16,"R/W", 0,    ""),
    ]