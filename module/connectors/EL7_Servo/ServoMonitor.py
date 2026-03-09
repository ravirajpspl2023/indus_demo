import logging
import time

log = logging.getLogger(__name__)

from module.connectors.EL7_Servo.ServoClient import ServoClient
from module.connectors.EL7_Servo.Class0 import Class0
from module.connectors.EL7_Servo.Class1 import Class1
from module.connectors.EL7_Servo.Class2 import Class2
from module.connectors.EL7_Servo.Class3 import Class3
from module.connectors.EL7_Servo.Class4 import Class4
from module.connectors.EL7_Servo.Class5 import Class5
from module.connectors.EL7_Servo.Class6 import Class6
from module.connectors.EL7_Servo.Class8 import Class8
from module.connectors.EL7_Servo.Class9 import Class9
from module.connectors.EL7_Servo.ClassB import ClassB



class ServoMonitor:
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
        self.client  = ServoClient(port=self.config.get('dev'),baudrate=self.config.get("baudrate",9600),
                             bytesize=self.config.get('databits',8),parity=self.config.get('parity',"N"),stopbits=self.config.get('stopbits',1))
        
        log.debug(f'client information {self.client._client.connect()}')

        while not self.client._client.connect():
            time.sleep(10)

        # while self.client == None :
        #     time.sleep(10)
        #     self.client = ServoClient(port=self.config.get('dev'),baudrate=self.config.get("baudrate",9600),
        #                      bytesize=self.config.get('databits',8),parity=self.config.get('parity',"N"),stopbits=self.config.get('stopbits',1))
        self.basic   = Class0(self.client)
        self.gain    = Class1(self.client)
        self.vib     = Class2(self.client)
        self.veltrq  = Class3(self.client)
        self.io      = Class4(self.client)
        self.comm    = Class5(self.client)
        self.other   = Class6(self.client)
        self.status  = ClassB(self.client)
        self.pr_ctrl = Class8(self.client)
        self.pr_path = Class9(self.client)
        self._all    = [self.basic, self.gain, self.vib, self.veltrq,
                        self.io, self.comm, self.other,self.pr_ctrl, self.pr_path]

    def read_all_config(self):
        data = {}
        for cls in self._all:
            try:    
                cls.read()
                data.update(cls.to_dict())
            except Exception as e:
                log.error(f"Failed {cls.CLASS_NAME}: {e}")
        return data

    def read_status_only(self):
        """Fastest — only ClassB real-time registers."""
        self.status.read()
        return self.status.to_dict()
    def close(self): self.client.close()
    def __enter__(self): return self
    def __exit__(self, *_): self.close()