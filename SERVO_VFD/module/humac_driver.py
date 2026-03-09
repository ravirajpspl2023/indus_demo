import logging
from module.connectors.Drive import Drive
from module.config.config import config
from module.servo_publish import ServoPublisher


class humac_driver:
    def __init__(self):
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.config = config("./module/config/config.json")
        self.modbus_connectors = []
        self.servo_publishers = []
    def start(self):
        redis = self.config.get_redis_config()
        for modbus in self.config.get_modbus_config():
            modbus_connector = Drive(modbus,redis)
            self.modbus_connectors.append(modbus_connector)
        
        for servo in self.config.get_servo_list():
            servo_publisher = ServoPublisher(servo,redis,self.config.get_mqtt_config())
            servo_publisher.start()
            self.servo_publishers.append(servo_publisher)

        try:
            while True:
                pass
            for modbus_connector in self.modbus_connectors:
                modbus_connector.join()

            for servo_publisher in self.servo_publishers:
                servo_publisher.join()
        except KeyboardInterrupt:
            for modbus_connector in self.modbus_connectors:
                modbus_connector.stop()
            for servo_publisher in self.servo_publishers:
                servo_publisher.stop()
            return