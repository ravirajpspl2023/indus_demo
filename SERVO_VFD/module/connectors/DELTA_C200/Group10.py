from module.connectors.DELTA_C200._BaseGroup import _BaseGroup,ParamDef

# ═══════════════════════════════════════════════════════════════
#  GROUP 10 — Speed Feedback Control  0x0A01 ~ 0x0A30
# ═══════════════════════════════════════════════════════════════
class Group10(_BaseGroup):
    GROUP_NAME = "Group 10 — Speed Feedback Control (PG)"
    PARAMS = [
        ParamDef("Pr10-01","Encoder Pulse",                    0x0A02,16,"R/W",1024,"PPR", "★ Pulses per revolution"),
        ParamDef("Pr10-02","Encoder Type",                     0x0A03,16,"R/W",0,   "",   "0=ABZ|1=AB|2=A"),
        ParamDef("Pr10-03","Encoder Input Type",               0x0A04,16,"R/W",0,   "",   "0=Line driver|1=Open collector"),
        ParamDef("Pr10-05","Position Lock P Gain",             0x0A06,16,"R/W",10,  ""),
        ParamDef("Pr10-06","Position Lock I Gain",             0x0A07,16,"R/W",100, ""),
        ParamDef("Pr10-07","Feedback Gain",                    0x0A08,16,"R/W",100, ""),
        ParamDef("Pr10-08","Speed Feedback Filter",            0x0A09,16,"R/W",0,   "ms"),
        ParamDef("Pr10-17","ASR Low-speed P Gain",             0x0A12,16,"R/W",10,  ""),
        ParamDef("Pr10-18","ASR Low-speed I Gain",             0x0A13,16,"R/W",100, "ms"),
        ParamDef("Pr10-24","APR P Gain",                       0x0A19,16,"R/W",10,  ""),
        ParamDef("Pr10-25","Feed Forward for APR",             0x0A1A,16,"R/W",0,   ""),
        ParamDef("Pr10-26","PDFF Gain for APR",                0x0A1B,16,"R/W",0,   ""),
        ParamDef("Pr10-38","Low-pass Filter Time",             0x0A27,16,"R/W",0,   "ms"),
        ParamDef("Pr10-39","V/F to Vector Switch Level",       0x0A28,16,"R/W",0,   "Hz"),
        ParamDef("Pr10-40","Vector to V/F Switch Level",       0x0A29,16,"R/W",0,   "Hz"),
    ]