from module.connectors.DELTA_C200._BaseGroup import _BaseGroup,ParamDef
# ═══════════════════════════════════════════════════════════════
#  GROUP 06 — Protection Parameters  0x0600 ~ 0x0649
# ═══════════════════════════════════════════════════════════════
class Group06(_BaseGroup):
    GROUP_NAME = "Group 06 — Protection Parameters"
    PARAMS = [
        ParamDef("Pr06-00","Low Voltage Level",                0x0601,16,"R/W",190, "V"),
        ParamDef("Pr06-01","Over-voltage Stall Prevention",    0x0602,16,"R/W",380, "V"),
        ParamDef("Pr06-03","Over-current Stall Prevention Accel",0x0604,16,"R/W",150,"%"),
        ParamDef("Pr06-04","Over-current Stall Prevention Oper",0x0605,16,"R/W",150,"%"),
        ParamDef("Pr06-06","Over-torque Detection Selection 1",0x0607,16,"R/W",0,  ""),
        ParamDef("Pr06-07","Over-torque Detection Level 1",    0x0608,16,"R/W",150,"%"),
        ParamDef("Pr06-08","Over-torque Detection Time 1",     0x0609,16,"R/W",0,  "s"),
        ParamDef("Pr06-09","Over-torque Detection Selection 2",0x060A,16,"R/W",0,  ""),
        ParamDef("Pr06-10","Over-torque Detection Level 2",    0x060B,16,"R/W",150,"%"),
        ParamDef("Pr06-11","Over-torque Detection Time 2",     0x060C,16,"R/W",0,  "s"),
        ParamDef("Pr06-12","Current Limit",                    0x060D,16,"R/W",170,"%",  "0~250%"),
        ParamDef("Pr06-13","Electronic Thermal Relay Selection",0x060E,16,"R/W",2,  ""),
        ParamDef("Pr06-14","Electronic Thermal Relay Level",   0x060F,16,"R/W",0,  "%"),
        ParamDef("Pr06-17","Fault Record 1 (Recent)",          0x0612,16,"R",  0,  "",  "★ 0=No fault|1=OCA|7=OVA|16=OH1|21=OL"),
        ParamDef("Pr06-18","Fault Record 2",                   0x0613,16,"R",  0,  ""),
        ParamDef("Pr06-19","Fault Record 3",                   0x0614,16,"R",  0,  ""),
        ParamDef("Pr06-20","Fault Record 4",                   0x0615,16,"R",  0,  ""),
        ParamDef("Pr06-21","Fault Record 5",                   0x0616,16,"R",  0,  ""),
        ParamDef("Pr06-22","Fault Record 6 (Oldest)",          0x0617,16,"R",  0,  ""),
        ParamDef("Pr06-25","Fault Output Option 1",            0x061A,16,"R/W",0,  ""),
        ParamDef("Pr06-28","Motor Thermal Relay",              0x061D,16,"R/W",0,  ""),
        ParamDef("Pr06-29","PTC Thermistor Detection Level",   0x061E,16,"R/W",0,  ""),
        ParamDef("Pr06-63","Fault Record 1 Day",               0x0640,16,"R",  0,  "day"),
        ParamDef("Pr06-64","Fault Record 1 Min",               0x0641,16,"R",  0,  "min"),
        ParamDef("Pr06-65","Fault Record 2 Day",               0x0642,16,"R",  0,  "day"),
        ParamDef("Pr06-66","Fault Record 2 Min",               0x0643,16,"R",  0,  "min"),
        ParamDef("Pr06-67","Fault Record 3 Day",               0x0644,16,"R",  0,  "day"),
        ParamDef("Pr06-68","Fault Record 3 Min",               0x0645,16,"R",  0,  "min"),
        ParamDef("Pr06-73","Fault Record 6 Min",               0x064A,16,"R",  0,  "min"),
    ]