from module.connectors.DELTA_C200._BaseGroup import _BaseGroup,ParamDef

# ═══════════════════════════════════════════════════════════════
#  GROUP 08 — PID Parameters  0x0800 ~ 0x0813
# ═══════════════════════════════════════════════════════════════
class Group08(_BaseGroup):
    GROUP_NAME = "Group 08 — PID Parameters"
    PARAMS = [
        ParamDef("Pr08-00","Input Terminal for PID Feedbac",   0x0801,16,"R/W",0,  "",  "0=No PID|1=Neg|2=Pos|3=Neg+target|4=Pos+target"),
        ParamDef("Pr08-01","PID Proportional Gain Kp",         0x0802,16,"R/W",80, "%", "★ 0~500%"),
        ParamDef("Pr08-02","PID Integral Time Ti",             0x0803,16,"R/W",10, "s", "★ 0.0~100.0s | 0=Disable"),
        ParamDef("Pr08-03","Derivative Control ",              0x0804,16,"R/W",0,  "s"),
        ParamDef("Pr08-04","Upper limit Integral Control",     0x0805,16,"R/W",100,"%"),
        ParamDef("Pr08-05","PID Output Frequency Limit",       0x0806,16,"R/W",100,"%"),
        ParamDef("Pr08-07","PID Delay Time",                   0x0808,16,"R/W",0,  "s"),
        ParamDef("Pr08-08","PID Feedback Gain",                0x0809,16,"R/W",100,"%"),
        ParamDef("Pr08-09","Feedback Signal Fault Treatment",  0x080A,16,"R/W",100,"%"),
        ParamDef("Pr08-10","Sleep Function Frequency",         0x080B,16,"R/W",0,  "Hz"),
        ParamDef("Pr08-11","Wake-up Frequency",                0x080C,16,"R/W",0,  "Hz"),
        ParamDef("Pr08-12","Sleep Time",                       0x080D,16,"R/W",0,  "s"),
        ParamDef("Pr08-13","PID Deviation Level",              0x080E,16,"R/W",10, "%"),
        ParamDef("Pr08-14","PID Deviation Time",               0x080F,16,"R/W",5,  "s"),
        ParamDef("Pr08-15","Filter Time PID Feedback",         0x0810,16,"R/W",5,  "s"),
        ParamDef("Pr08-16","PID Detection Value (Read)",       0x0811,16,"R",  0,  "%", "★ Read-only PID feedback"),
        ParamDef("Pr08-17","PID Reference Value (Read)",       0x0812,16,"R",  0,  "%"),
        ParamDef("Pr08-18","PID Output Value (Read)",          0x0813,16,"R",  0,  "%"),
        ParamDef("Pr08-19","PID Filter Time",                  0x0814,16,"R/W",0,  "s"),
    ]