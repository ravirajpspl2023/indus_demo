from module.connectors.EL7_Servo._BaseParamClass import _BaseParamClass,ParamDef

class ClassB(_BaseParamClass):
    CLASS_NAME = "Class B — Status Monitor (Read Only)"
    PARAMS = [
        ParamDef("PrB.00","Software Version DSP",              0x0B00,16,"R",0,""),
        ParamDef("PrB.01","Software Version CPLD",             0x0B01,16,"R",0,""),
        ParamDef("PrB.02","Software Version Others",           0x0B02,16,"R",0,""),
        ParamDef("PrB.03","Current Alarm Code",                0x0B03,16,"R",0,"",  "0=No alarm"),
        ParamDef("PrB.04","Motor Not Rotating Cause",          0x0B04,16,"R",0,""),
        ParamDef("PrB.05","Driver Operation Status",           0x0B05,16,"R",0,""),
        ParamDef("PrB.06","Motor Speed Before Filter",         0x0B06,16,"R",0,"rpm"),
        ParamDef("PrB.07","Motor Torque",                      0x0B07,16,"R",0,"%"),
        ParamDef("PrB.08","Motor Current",                     0x0B08,16,"R",0,"A"),
        ParamDef("PrB.09","Motor Speed After Filter",          0x0B09,16,"R",0,"rpm"),
        ParamDef("PrB.10","DC Bus Voltage",                    0x0B0A,16,"R",0,"V"),
        ParamDef("PrB.11","Driver Temperature",                0x0B0B,16,"R",0,"deg C"),
        ParamDef("PrB.12","External Analog Input 1 AI-1",      0x0B0C,16,"R",0,"mV"),
        ParamDef("PrB.13","External Analog Input 2 AI-2",      0x0B0D,16,"R",0,"mV"),
        ParamDef("PrB.14","External Analog Input 3 AI-3",      0x0B0E,16,"R",0,"mV"),
        ParamDef("PrB.15","Motor Overload Rate",               0x0B0F,16,"R",0,"%"),
        ParamDef("PrB.16","Vent Overload Rate",                0x0B10,16,"R",0,"%"),
        ParamDef("PrB.17","Physical DI Input Status",          0x0B11,16,"R",0,"", "Bit0=DI1...Bit7=DI8"),
        ParamDef("PrB.18","Physical DO Output Status",         0x0B12,16,"R",0,"", "Bit0=DO1...Bit4=DO5"),
        ParamDef("PrB.20","Command Position Cmd Unit 32bit",   0x0B14,32,"R",0,""),
        ParamDef("PrB.21","Motor Position Cmd Unit 32bit",     0x0B16,32,"R",0,""),
        ParamDef("PrB.22","Position Deviation Cmd Unit 32bit", 0x0B18,32,"R",0,""),
        ParamDef("PrB.23","Command Position Enc Unit 32bit",   0x0B1A,32,"R",0,""),
        ParamDef("PrB.24","Motor Position Enc Unit 32bit",     0x0B1C,32,"R",0,""),
        ParamDef("PrB.25","Position Deviation Enc Unit 32bit", 0x0B1D,32,"R",0,""),
    ]

    # ── Convenient named properties ──────────────────────────
    @property
    def motor_speed_rpm(self):    return self.prb_06
    @property
    def motor_torque_pct(self):   return self.prb_07
    @property
    def motor_current_a(self):    return self.prb_08
    @property
    def dc_bus_voltage_v(self):   return self.prb_10
    @property
    def driver_temp_c(self):      return self.prb_11
    @property
    def current_alarm(self):      return self.prb_03
    @property
    def overload_rate_pct(self):  return self.prb_16
    @property
    def di_status_bits(self):     return self.prb_17
    @property
    def do_status_bits(self):     return self.prb_18
    @property
    def position_cmd(self):       return self.prb_20   # 32-bit
    @property
    def position_actual(self):    return self.prb_24   # 32-bit
    @property
    def position_deviation(self): return self.prb_25   # 32-bit

    def di_active(self, ch):
        """Check if DI channel (1~8) is active. Returns bool."""
        if self.prb_11 is None: return False
        return bool((self.prb_11 >> (ch - 1)) & 1)

    def do_active(self, ch):
        """Check if DO channel (1~5) is active. Returns bool."""
        if self.prb_12 is None: return False
        return bool((self.prb_12 >> (ch - 1)) & 1)