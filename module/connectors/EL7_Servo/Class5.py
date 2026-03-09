from module.connectors.EL7_Servo._BaseParamClass import _BaseParamClass,ParamDef

# ═══════════════════════════════════════════════════════════════
#  CLASS 5 — Extension Settings  (RS485 setup lives here!)
#  Address range: 0x0500 ~ 0x0549
# ═══════════════════════════════════════════════════════════════
class Class5(_BaseParamClass):
    CLASS_NAME = "Class 5 — Extension Settings  [RS485 here!]"
    PARAMS = [
        ParamDef("Pr5.00","2nd Pulse Count/Revolution",         0x0500,32,"R/W",10000,"pulse/rev"),
        ParamDef("Pr5.01","2nd Cmd Freq Divider Numerator",     0x0502,32,"R/W",1,    ""),
        ParamDef("Pr5.02","2nd Cmd Freq Divider Denominator",   0x0504,32,"R/W",1,    ""),
        ParamDef("Pr5.04","Driver Prohibition Input",           0x0509,16,"R/W",0,    ""),
        ParamDef("Pr5.06","Servo-off Mode",                     0x050D,16,"R/W",0,    ""),
        ParamDef("Pr5.08","DC Bus Undervoltage Alarm",          0x0513,16,"R/W",50,   "V"),
        ParamDef("Pr5.09","Main Power-off Detection Time",      0x0515,16,"R/W",0,    "ms"),
        ParamDef("Pr5.10","Servo-off due to Alarm Mode",        0x0517,16,"R/W",0,    ""),
        ParamDef("Pr5.11","Servo Braking Torque",               0x0519,16,"R/W",0,    "%"),
        ParamDef("Pr5.12","Overload Level Setting",             0x051B,16,"R/W",0,    "%"),
        ParamDef("Pr5.15","I/O Digital Filter",                 0x051F,16,"R/W",3,    "x0.1ms"),
        ParamDef("Pr5.17","Counter Clearing Input Mode",        0x0523,16,"R/W",1,    ""),
        ParamDef("Pr5.20","Position Unit Settings",             0x0529,16,"R/W",0,    ""),
        ParamDef("Pr5.21","Torque Limit Selection",             0x052B,16,"R/W",0,    ""),
        ParamDef("Pr5.22","2nd Torque Limit",                   0x052D,16,"R/W",300,  "%"),
        ParamDef("Pr5.23","+ve Torque Warning Threshold",       0x052F,16,"R/W",0,    "%"),
        ParamDef("Pr5.24","-ve Torque Warning Threshold",       0x0531,16,"R/W",0,    "%"),
        ParamDef("Pr5.28","LED Initial Status",                 0x0539,16,"R/W",1,    ""),
        ParamDef("Pr5.29","RS485 Communication Mode",           0x053B,16,"R/W",0,    "",   "0=Modbus RTU"),
        ParamDef("Pr5.30","RS485 Baud Rate",                    0x053D,16,"R/W",5,    "",   "0=2400|1=4800|2=9600|3=19200|4=38400|5=57600|6=115200"),
        ParamDef("Pr5.31","RS485 Slave Address",                0x053F,16,"R/W",4,    "",   "1~247"),
        ParamDef("Pr5.32","Max Cmd Pulse Input Frequency",      0x0541,16,"R/W",0,    ""),
        ParamDef("Pr5.35","Front Panel Lock Setting",           0x0547,16,"R/W",0,    ""),
        ParamDef("Pr5.37","Torque Saturation Alarm Time",       0x0549,16,"R/W",500,  "ms"),
    ]
