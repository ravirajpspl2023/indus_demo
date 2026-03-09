import logging
import json

class config:
    def __init__(self,config_file):
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.config_file = config_file
        with open(self.config_file, 'r') as f:
            self.config_data = f.read()
            self.config_data = json.loads(self.config_data)
        self.logger.info(f"Configuration loaded from {self.config_file}")

    def get_mqtt_config(self):
        return self.config_data.get("mqtt", {})
    
    def get_modbus_config(self):
        return self.config_data.get("modbus", {})
    
    def get_redis_config(self):
        return self.config_data.get("redis", {})
    def get_socket_config(self,):
        return self.config_data.get("socket",{})
    
    def get_servo_list(self,):
        streams=[]
        for modbus in self.config_data.get("modbus"):
            streams.append(modbus.get("dev").split("/")[-1])
        return streams
        
