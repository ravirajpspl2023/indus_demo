from module.connectors.EL7_Servo._BaseParamClass import _BaseParamClass,ParamDef


# ═══════════════════════════════════════════════════════════════
#  CLASS 9 — Position Control (PR Parameters)
# ═══════════════════════════════════════════════════════════════

class Class9(_BaseParamClass):
    CLASS_NAME = "Class 9 — Position Control (PR Parameters)"
    PARAMS = [
        # PR0 Parameters
        ParamDef("Pr9.00", "PR0 mode",                    0x0200, 16, "R/W", 0,   ""),
        ParamDef("Pr9.01", "PR0 position H",              0x0201, 16, "R/W", 0,   ""),
        ParamDef("Pr9.02", "PR0 position(L)",             0x0202, 16, "R/W", 0,   ""),
        ParamDef("Pr9.03", "PR0 velocity",                0x0203, 16, "R/W", 60,  ""),
        ParamDef("Pr9.04", "PR0 acceleration time",       0x0204, 16, "R/W", 100, ""),
        ParamDef("Pr9.05", "PR0 deceleration time",       0x0205, 16, "R/W", 100, ""),
        ParamDef("Pr9.06", "PR0 pause time",              0x0206, 16, "R/W", 0,   ""),
        ParamDef("Pr9.07", "PR0 special parameter",       0x0207, 16, "R/W", 0,   ""),
        
        # PR1 Parameters
        ParamDef("Pr9.08", "PR1 mode",                    0x0208, 16, "R/W", 0,   ""),
        ParamDef("Pr9.09", "PR1 position H",              0x0209, 16, "R/W", 0,   ""),
        ParamDef("Pr9.10", "PR1 position(L)",             0x020A, 16, "R/W", 0,   ""),
        ParamDef("Pr9.11", "PR1 velocity",                0x020B, 16, "R/W", 60,  ""),
        ParamDef("Pr9.12", "PR1 acceleration time",       0x020C, 16, "R/W", 100, ""),
        ParamDef("Pr9.13", "PR1 deceleration time",       0x020D, 16, "R/W", 100, ""),
        ParamDef("Pr9.14", "PR1 pause time",              0x020E, 16, "R/W", 0,   ""),
        ParamDef("Pr9.15", "PR1 special parameter",       0x020F, 16, "R/W", 0,   ""),
        
        # PR2 Parameters
        ParamDef("Pr9.16", "PR2 mode",                    0x0210, 16, "R/W", 0,   ""),
        ParamDef("Pr9.17", "PR2 position H",              0x0211, 16, "R/W", 0,   ""),
        ParamDef("Pr9.18", "PR2 position(L)",             0x0212, 16, "R/W", 0,   ""),
        ParamDef("Pr9.19", "PR2 velocity",                0x0213, 16, "R/W", 60,  ""),
        ParamDef("Pr9.20", "PR2 acceleration time",       0x0214, 16, "R/W", 100, ""),
        ParamDef("Pr9.21", "PR2 deceleration time",       0x0215, 16, "R/W", 100, ""),
        ParamDef("Pr9.22", "PR2 pause time",              0x0216, 16, "R/W", 0,   ""),
        ParamDef("Pr9.23", "PR2 special parameter",       0x0217, 16, "R/W", 0,   ""),
        
        # PR3 Parameters
        ParamDef("Pr9.24", "PR3 mode",                    0x0218, 16, "R/W", 0,   ""),
        ParamDef("Pr9.25", "PR3 position H",              0x0219, 16, "R/W", 0,   ""),
        ParamDef("Pr9.26", "PR3 position(L)",             0x021A, 16, "R/W", 0,   ""),
        ParamDef("Pr9.27", "PR3 velocity",                0x021B, 16, "R/W", 60,  ""),
        ParamDef("Pr9.28", "PR3 acceleration time",       0x021C, 16, "R/W", 100, ""),
        ParamDef("Pr9.29", "PR3 deceleration time",       0x021D, 16, "R/W", 100, ""),
        ParamDef("Pr9.30", "PR3 pause time",              0x021E, 16, "R/W", 0,   ""),
        ParamDef("Pr9.31", "PR3 special parameter",       0x021F, 16, "R/W", 0,   ""),
        
        # PR4 Parameters
        ParamDef("Pr9.32", "PR4 mode",                    0x0220, 16, "R/W", 0,   ""),
        ParamDef("Pr9.33", "PR4 position H",              0x0221, 16, "R/W", 0,   ""),
        ParamDef("Pr9.34", "PR4 position(L)",             0x0222, 16, "R/W", 0,   ""),
        ParamDef("Pr9.35", "PR4 velocity",                0x0223, 16, "R/W", 60,  ""),
        ParamDef("Pr9.36", "PR4 acceleration time",       0x0224, 16, "R/W", 100, ""),
        ParamDef("Pr9.37", "PR4 deceleration time",       0x0225, 16, "R/W", 100, ""),
        ParamDef("Pr9.38", "PR4 pause time",              0x0226, 16, "R/W", 0,   ""),
        ParamDef("Pr9.39", "PR4 special parameter",       0x0227, 16, "R/W", 0,   ""),
        
        # PR5 Parameters
        ParamDef("Pr9.40", "PR5 mode",                    0x0228, 16, "R/W", 0,   ""),
        ParamDef("Pr9.41", "PR5 position H",              0x0229, 16, "R/W", 0,   ""),
        ParamDef("Pr9.42", "PR5 position(L)",             0x022A, 16, "R/W", 0,   ""),
        ParamDef("Pr9.43", "PR5 velocity",                0x022B, 16, "R/W", 60,  ""),
        ParamDef("Pr9.44", "PR5 acceleration time",       0x022C, 16, "R/W", 100, ""),
        ParamDef("Pr9.45", "PR5 deceleration time",       0x022D, 16, "R/W", 100, ""),
        ParamDef("Pr9.46", "PR5 pause time",              0x022E, 16, "R/W", 0,   ""),
        ParamDef("Pr9.47", "PR5 special parameter",       0x022F, 16, "R/W", 0,   ""),
        
        # PR6 Parameters
        ParamDef("Pr9.48", "PR6 mode",                    0x0230, 16, "R/W", 0,   ""),
        ParamDef("Pr9.49", "PR6 position H",              0x0231, 16, "R/W", 0,   ""),
        ParamDef("Pr9.50", "PR6 position(L)",             0x0232, 16, "R/W", 0,   ""),
        ParamDef("Pr9.51", "PR6 velocity",                0x0233, 16, "R/W", 60,  ""),
        ParamDef("Pr9.52", "PR6 acceleration time",       0x0234, 16, "R/W", 100, ""),
        ParamDef("Pr9.53", "PR6 deceleration time",       0x0235, 16, "R/W", 100, ""),
        ParamDef("Pr9.54", "PR6 pause time",              0x0236, 16, "R/W", 0,   ""),
        ParamDef("Pr9.55", "PR6 special parameter",       0x0237, 16, "R/W", 0,   ""),
        
        # PR7 Parameters
        ParamDef("Pr9.56", "PR7 mode",                    0x0238, 16, "R/W", 0,   ""),
        ParamDef("Pr9.57", "PR7 position H",              0x0239, 16, "R/W", 0,   ""),
        ParamDef("Pr9.58", "PR7 position(L)",             0x023A, 16, "R/W", 0,   ""),
        ParamDef("Pr9.59", "PR7 velocity",                0x023B, 16, "R/W", 60,  ""),
        ParamDef("Pr9.60", "PR7 acceleration time",       0x023C, 16, "R/W", 100, ""),
        ParamDef("Pr9.61", "PR7 deceleration time",       0x023D, 16, "R/W", 100, ""),
        ParamDef("Pr9.62", "PR7 pause time",              0x023E, 16, "R/W", 0,   ""),
        ParamDef("Pr9.63", "PR7 special parameter",       0x023F, 16, "R/W", 0,   ""),
        
        # PR8 Parameters
        ParamDef("Pr9.64", "PR8 mode",                    0x0240, 16, "R/W", 0,   ""),
        ParamDef("Pr9.65", "PR8 position H",              0x0241, 16, "R/W", 0,   ""),
        ParamDef("Pr9.66", "PR8 position(L)",             0x0242, 16, "R/W", 0,   ""),
        ParamDef("Pr9.67", "PR8 velocity",                0x0243, 16, "R/W", 60,  ""),
        ParamDef("Pr9.68", "PR8 acceleration time",       0x0244, 16, "R/W", 100, ""),
        ParamDef("Pr9.69", "PR8 deceleration time",       0x0245, 16, "R/W", 100, ""),
        ParamDef("Pr9.70", "PR8 pause time",              0x0246, 16, "R/W", 0,   ""),
        ParamDef("Pr9.71", "PR8 special parameter",       0x0247, 16, "R/W", 0,   ""),
        
        # PR9 Parameters
        ParamDef("Pr9.72", "PR9 mode",                    0x0248, 16, "R/W", 0,   ""),
        ParamDef("Pr9.73", "PR9 position H",              0x0249, 16, "R/W", 0,   ""),
        ParamDef("Pr9.74", "PR9 position(L)",             0x024A, 16, "R/W", 0,   ""),
        ParamDef("Pr9.75", "PR9 velocity",                0x024B, 16, "R/W", 60,  ""),
        ParamDef("Pr9.76", "PR9 acceleration time",       0x024C, 16, "R/W", 100, ""),
        ParamDef("Pr9.77", "PR9 deceleration time",       0x024D, 16, "R/W", 100, ""),
        ParamDef("Pr9.78", "PR9 pause time",              0x024E, 16, "R/W", 0,   ""),
        ParamDef("Pr9.79", "PR9 special parameter",       0x024F, 16, "R/W", 0,   ""),
        
        # PR10 Parameters
        ParamDef("Pr9.80", "PR10 mode",                   0x0250, 16, "R/W", 0,   ""),
        ParamDef("Pr9.81", "PR10 position H",             0x0251, 16, "R/W", 0,   ""),
        ParamDef("Pr9.82", "PR10 position(L)",            0x0252, 16, "R/W", 0,   ""),
        ParamDef("Pr9.83", "PR10 velocity",               0x0253, 16, "R/W", 60,  ""),
        ParamDef("Pr9.84", "PR10 acceleration time",      0x0254, 16, "R/W", 100, ""),
        ParamDef("Pr9.85", "PR10 deceleration time",      0x0255, 16, "R/W", 100, ""),
        ParamDef("Pr9.86", "PR10 pause time",             0x0256, 16, "R/W", 0,   ""),
        ParamDef("Pr9.87", "PR10 special parameter",      0x0257, 16, "R/W", 0,   ""),
        
        # PR11 Parameters
        ParamDef("Pr9.88", "PR11 mode",                   0x0258, 16, "R/W", 0,   ""),
        ParamDef("Pr9.89", "PR11 position H",             0x0259, 16, "R/W", 0,   ""),
        ParamDef("Pr9.90", "PR11 position(L)",            0x025A, 16, "R/W", 0,   ""),
        ParamDef("Pr9.91", "PR11 velocity",               0x025B, 16, "R/W", 60,  ""),
        ParamDef("Pr9.92", "PR11 acceleration time",      0x025C, 16, "R/W", 100, ""),
        ParamDef("Pr9.93", "PR11 deceleration time",      0x025D, 16, "R/W", 100, ""),
        ParamDef("Pr9.94", "PR11 pause time",             0x025E, 16, "R/W", 0,   ""),
        ParamDef("Pr9.95", "PR11 special parameter",      0x025F, 16, "R/W", 0,   ""),
        
        # PR12 Parameters
        ParamDef("Pr9.96",  "PR12 mode",                  0x0260, 16, "R/W", 0,   ""),
        ParamDef("Pr9.97",  "PR12 position H",            0x0261, 16, "R/W", 0,   ""),
        ParamDef("Pr9.98",  "PR12 position(L)",           0x0262, 16, "R/W", 0,   ""),
        ParamDef("Pr9.99",  "PR12 velocity",              0x0263, 16, "R/W", 60,  ""),
        ParamDef("Pr9.100", "PR12 acceleration time",     0x0264, 16, "R/W", 100, ""),
        ParamDef("Pr9.101", "PR12 deceleration time",     0x0265, 16, "R/W", 100, ""),
        ParamDef("Pr9.102", "PR12 pause time",            0x0266, 16, "R/W", 0,   ""),
        ParamDef("Pr9.103", "PR12 special parameter",     0x0267, 16, "R/W", 0,   ""),
        
        # PR13 Parameters
        ParamDef("Pr9.104", "PR13 mode",                  0x0268, 16, "R/W", 0,   ""),
        ParamDef("Pr9.105", "PR13 position H",            0x0269, 16, "R/W", 0,   ""),
        ParamDef("Pr9.106", "PR13 position(L)",           0x026A, 16, "R/W", 0,   ""),
        ParamDef("Pr9.107", "PR13 velocity",              0x026B, 16, "R/W", 60,  ""),
        ParamDef("Pr9.108", "PR13 acceleration time",     0x026C, 16, "R/W", 100, ""),
        ParamDef("Pr9.109", "PR13 deceleration time",     0x026D, 16, "R/W", 100, ""),
        ParamDef("Pr9.110", "PR13 pause time",            0x026E, 16, "R/W", 0,   ""),
        ParamDef("Pr9.111", "PR13 special parameter",     0x026F, 16, "R/W", 0,   ""),
        
        # PR14 Parameters
        ParamDef("Pr9.112", "PR14 mode",                  0x0270, 16, "R/W", 0,   ""),
        ParamDef("Pr9.113", "PR14 position H",            0x0271, 16, "R/W", 0,   ""),
        ParamDef("Pr9.114", "PR14 position(L)",           0x0272, 16, "R/W", 0,   ""),
        ParamDef("Pr9.115", "PR14 velocity",              0x0273, 16, "R/W", 60,  ""),
        ParamDef("Pr9.116", "PR14 acceleration time",     0x0274, 16, "R/W", 100, ""),
        ParamDef("Pr9.117", "PR14 deceleration time",     0x0275, 16, "R/W", 100, ""),
        ParamDef("Pr9.118", "PR14 pause time",            0x0276, 16, "R/W", 0,   ""),
        ParamDef("Pr9.119", "PR14 special parameter",     0x0277, 16, "R/W", 0,   ""),
        
        # PR15 Parameters
        ParamDef("Pr9.120", "PR15 mode",                  0x0278, 16, "R/W", 0,   ""),
        ParamDef("Pr9.121", "PR15 position H",            0x0279, 16, "R/W", 0,   ""),
        ParamDef("Pr9.122", "PR15 position(L)",           0x027A, 16, "R/W", 0,   ""),
        ParamDef("Pr9.123", "PR15 velocity",              0x027B, 16, "R/W", 60,  ""),
        ParamDef("Pr9.124", "PR15 acceleration time",     0x027C, 16, "R/W", 100, ""),
        # ParamDef("Pr9.125", "PR15 deceleration time",     0x027D, 16, "R/W", 100, ""),
        # ParamDef("Pr9.126", "PR15 pause time",            0x027E, 16, "R/W", 0,   ""),
        # ParamDef("Pr9.127", "PR15 special parameter",     0x027F, 16, "R/W", 0,   ""),
    ]

    def get_path(self, n):
        """Get dict for PR path n (0~15)."""
        b = n * 8
        keys = ['mode','pos_hi','pos_lo','velocity','accel_ms','decel_ms','pause_ms','special']
        return {k: getattr(self, self._attr_map[self.PARAMS[b+i].code])
                for i, k in enumerate(keys)}

    def position_32bit(self, n):
        """Combine pos_hi + pos_lo into signed 32-bit integer."""
        d = self.get_path(n)
        if d['pos_hi'] is None: return None
        v = ((d['pos_hi'] & 0xFFFF) << 16) | (d['pos_lo'] & 0xFFFF)
        return v - 0x100000000 if v >= 0x80000000 else v