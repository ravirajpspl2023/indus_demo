import logging
import time

log = logging.getLogger(__name__)

from module.connectors.DELTA_C200.VFDClient import VFDClient
from module.connectors.DELTA_C200.Group00 import Group00
from module.connectors.DELTA_C200.Group01 import Group01
from module.connectors.DELTA_C200.Group02 import Group02
from module.connectors.DELTA_C200.Group03 import Group03
from module.connectors.DELTA_C200.Group04 import Group04
from module.connectors.DELTA_C200.Group05 import Group05
from module.connectors.DELTA_C200.Group06 import Group06
from module.connectors.DELTA_C200.Group07 import Group07
from module.connectors.DELTA_C200.Group08 import Group08
from module.connectors.DELTA_C200.Group09 import Group09
from module.connectors.DELTA_C200.Group10 import Group10
from module.connectors.DELTA_C200.Group11 import Group11
from module.connectors.DELTA_C200.DriveMonitor import DriveMonitor




class VfdMonitor:
    """
    One-stop wrapper — creates all class objects and reads them.

    Example:
        with ServoMonitor('COM3', slave_id=4) as mon:
            mon.read_all()
            print(mon.status.motor_speed_rpm)
            print(mon.status.current_alarm)
            print(mon.comm.pr5_31)      # slave ID

            mon.status.read()           # quick re-read of status only
    """
    def __init__(self, config):
        self.config = config
        self.client  = VFDClient(port=self.config.get('dev'),baudrate=self.config.get("baudrate",9600),
                             bytesize=self.config.get('databits',8),parity=self.config.get('parity',"N"),stopbits=self.config.get('stopbits',1))
        while self.client == None :
            time.sleep(10)
            self.client = VFDClient(port=self.config.get('dev'),baudrate=self.config.get("baudrate",9600),
                             bytesize=self.config.get('databits',8),parity=self.config.get('parity',"N"),stopbits=self.config.get('stopbits',1))
        self.g00     = Group00(self.client)
        self.g01     = Group01(self.client)
        self.g02     = Group02(self.client)
        self.g03     = Group03(self.client)
        self.g04     = Group04(self.client)
        self.g05     = Group05(self.client)
        self.g06     = Group06(self.client)
        self.g07     = Group07(self.client)
        self.g08     = Group08(self.client)
        self.comm    = Group09(self.client)   # RS485 settings
        self.g10     = Group10(self.client)
        self.g11     = Group11(self.client)
        self.monitor = DriveMonitor(self.client)
        self._all_groups = [
            self.g00, self.g01, self.g02, self.g03,
            self.g04, self.g05, self.g06, self.g07,
            self.g08, self.comm, self.g10, self.g11,
        ]

    def read_all_config(self):
        data = {}
        for cls in self._all_groups:
            try:    
                cls.read()
                data.update(cls.to_dict())
            except Exception as e:
                log.error(f"Failed {cls.CLASS_NAME}: {e}")
        return data

    def read_status_only(self):
        """Fastest — only ClassB real-time registers."""
        self.monitor.read()
        return self.monitor.to_dict()
    def close(self): self.client.close()
    def __enter__(self): return self
    def __exit__(self, *_): self.close()