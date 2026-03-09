from module.connectors.DELTA_C200._BaseGroup import _BaseGroup,ParamDef

# ═══════════════════════════════════════════════════════════════
#  GROUP 05 — Motor Parameters  0x0500 ~ 0x052C
# ═══════════════════════════════════════════════════════════════
class Group05(_BaseGroup):
    GROUP_NAME = "Group 05 — Motor Parameters"
    PARAMS = [
        ParamDef("Pr05-00","Motor Auto-tuning",                0x0501,16,"R/W",0,  "",  "0=Off|1=Rolling IM|2=Static IM|4=Rolling PM"),
        ParamDef("Pr05-01","Full-load Current Induction Motor 1",0x0502,16,"R/W",0,  "A", "★ From nameplate"),
        ParamDef("Pr05-02","Motor1 Rated Power",               0x0503,16,"R/W",0,  "kW","★ From nameplate"),
        ParamDef("Pr05-03","Motor1 Rated Speed",               0x0504,16,"R/W",1710,"RPM","★ From nameplate"),
        ParamDef("Pr05-04","Pole Number Induction Motor 1",    0x0505,16,"R/W",60, "Hz"),
        ParamDef("Pr05-05","Motor1 No-load Current",           0x0506,16,"R/W",0,  "A", "Auto-set after tuning"),
        ParamDef("Pr05-06","Motor1 Stator Resistance R1",      0x0507,16,"R/W",0,  "Ω"),
        ParamDef("Pr05-07","Motor1 Rotor Resistance R2",       0x0508,16,"R/W",0,  "Ω"),
        ParamDef("Pr05-08","Motor1 Magnetizing Inductance Lm", 0x0509,16,"R/W",0,  "mH"),
        ParamDef("Pr05-09","Motor1 Stator Inductance Lx",      0x050A,16,"R/W",0,  "mH"),
        ParamDef("Pr05-13","Motor 2 Rated Current",            0x050E,16,"R/W",0,  "A"),
        ParamDef("Pr05-14","Motor 2 Rated Power",              0x050F,16,"R/W",0,  "kW"),
        ParamDef("Pr05-15","Motor 2 Rated Speed",              0x0510,16,"R/W",1710,"RPM"),
        ParamDef("Pr05-16","Pole Number of Motor2",            0x0511,16,"R/W",0,  "kW"),
        ParamDef("Pr05-17","No-load Current Motor2",           0x0512,16,"R/W",0,  "kW"),
        ParamDef("Pr05-18","Stator Resistance Motor2",         0x0513,16,"R/W",0,  "kW"),
        ParamDef("Pr05-19","Rotor Resistance Motor2",          0x0514,16,"R/W",0,  "kW"),
        ParamDef("Pr05-20","Magnetizing Inductance Motor2 ",   0x0515,16,"R/W",0,  "kW"),
        ParamDef("Pr05-21","Stator Inductance Motor2 ",        0x0516,16,"R/W",0,  "kW"),
        ParamDef("Pr05-22","Motor 1/2 Selection",              0x0517,16,"R/W",0,  "kW"),
        ParamDef("Pr05-23","Frequency Y-connectio",            0x0518,16,"R/W",0,  "kW"),
        ParamDef("Pr05-25","Delay Time Y-connection",          0x051A,16,"R/W",0,  "kW"),
        ParamDef("Pr05-26","Accumulative Watt Per Second",     0x051B,16,"R",  0,  "kWh","Read-only"),
        ParamDef("Pr05-28","Accumulative Watt-hour Motor",     0x051D,16,"R",  0,  ""),
        ParamDef("Pr05-29","Accumulative w-h Motor Low Word", 0x051E,16,"R",  0,  "min"),
        ParamDef("Pr05-30","Accumulative w-h Motor High Word", 0x051F,16,"R",  0,  "min"),
        ParamDef("Pr05-31","Accumulative Motor Operation Time",0x0520,16,"R",  0,  "min"),
        ParamDef("Pr05-33","(IM)&Permanent Magnet M Selection",0x0522,16,"R",  0,  "min"),
        ParamDef("Pr05-34","Full-load current Permanent Magnet M",0x0523,16,"R",  0,  "min"),
        ParamDef("Pr05-35","Rated Power Permanent Magnet M",   0x0524,16,"R",  0,  "min"),
        ParamDef("Pr05-36","Rated speed Permanent Magnet M",   0x0525,16,"R",  0,  "min"),
        ParamDef("Pr05-37","Pole Permanent Magnet M",          0x0526,16,"R",  0,  "min"),
        ParamDef("Pr05-38","Inertia Permanent Magnet M",       0x0527,16,"R",  0,  "min"),
        ParamDef("Pr05-39","Stator Resistance of PM M",        0x0528,16,"R",  0,  "min"),
        ParamDef("Pr05-40","Permanent Magnet Motor Ld",        0x0529,16,"R",  0,  "min"),
        ParamDef("Pr05-42","PG Offset angle of PM M",          0x052B,16,"R",  0,  "min"),
        ParamDef("Pr05-43","Ke parameter of PM M",             0x052C,16,"R",  0,  "min"),
    ]