import logging
import time
import json
from multiprocessing import Process, Event
from module.database.redis_client import RedisConnection
from module.connectors.EL7_Servo.ServoMonitor import ServoMonitor
from module.connectors.DELTA_C200.VfdMonitor import VfdMonitor

logging.getLogger('pymodbus').setLevel(logging.INFO)
# logging.getLogger().setLevel(logging.INFO)

class Drive(Process):
    def __init__(self,config,redis):
        super().__init__(name=config.get("dev").split("/")[-1])
        self.logger = logging.getLogger(f"{self.name}")
        self.redis = RedisConnection(redis,config.get("dev").split("/")[-1])
        self._stop_event = Event() 
        self.config = config
        self.start()
    def run(self):
        try:
            self.r = self.redis.connect()
            if self.name != 'spindle':
                self.servo = ServoMonitor(self.config)
            else:
                logging.info("calling vfd monitor")
                self.servo = VfdMonitor(self.config)

            # self.logger.info(self.servo.read_all_config())
            data = self.servo.read_all_config()
            if data:
                self.r.xadd(self.name,{'config': json.dumps(data)})

            while not self._stop_event.is_set():
                 try: 
                    #  self.logger.info(self.servo.read_status_only())
                    start_time = time.time()
                    data = self.servo.read_status_only()
                    if data :
                        self.r.xadd(self.name, {'monitor': json.dumps(data)})

                    while time.time()-start_time <= 1:
                        pass

                 except Exception as e:
                    time.sleep(1.0)  
        except KeyboardInterrupt:
            self.logger.warning("Received KeyboardInterrupt in run")
        except Exception as e:
            self.logger.error(f"{e}")
        finally:
            self.logger.info(f"Process {self.name} stopped cleanly")
            self.servo=ServoMonitor(self.config)

    def stop(self):
        self._stop_event.set()