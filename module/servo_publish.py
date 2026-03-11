from multiprocessing import Process, Event
from module.database.redis_client import RedisConnection
import paho.mqtt.client as mqtt
import logging
import time
import json
import socket

class ServoPublisher(Process):
    def __init__(self, servo_name, redis_config, mqtt_config ):
        super().__init__(name=servo_name)
        self.logger = logging.getLogger(f"{self.name}_pub")
        self.redis = RedisConnection(redis_config, servo_name)
        self.mqtt_config = mqtt_config
        self._stop_event = Event()
        self.servo_stream = servo_name
        self.machine_id = self.mqtt_config.get("machine", {}).get("machine_id", None)
        self.edge_id = self.mqtt_config.get("machine", {}).get("edge_id", None)
        self.mqtt_topic = f"humac/telemetry_cnc/indus/{self.edge_id}/servo/{self.name}"
        self.password = None
        self.client = None

    def _check_host_connectivity(self,):
        """Check if the host and port are connectable."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                result = sock.connect_ex((self.mqtt_config['host'], self.mqtt_config['port']))
                if result == 0:
                    return True
                else:
                    return False
        except socket.gaierror:
            return False
        except Exception as e:
            return False
    
    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            self.logger.info(f"{self.servo_stream} mqtt client connected {reason_code}")
        else:
            self.logger.error(f"{self.servo_stream} mqtt client failed to connect with code {reason_code}")
    
    def on_message(self, client, userdata, message, properties=None):
        self.logger.info(f"Received message on topic {message.topic}: {message.payload.decode()}")
    
    def on_disconnect(self, client, userdata, flags, reason_code, properties=None):
        # self.client.loop_stop()
        self.logger.warning(f"Disconnected from {self.client._host}:{self.client._port}")
        self.connected = False

    def _publish(self,payload):
        try:
            if self.client:
                result = self.client.publish(self.mqtt_topic, json.dumps(payload),qos=1)
                result.wait_for_publish()
                return True
        except Exception as e:
            self.logger.error(f"Failed to publish message: {e}")
            return False

    def _connect(self):
        try:
            self.client = mqtt.Client( mqtt.CallbackAPIVersion.VERSION2,
                                      client_id= self.servo_stream, clean_session=True,reconnect_on_failure=True)
            if self.mqtt_config.get("password"):
                self.password = self.mqtt_config.get("password").encode('utf-8')
            self.client.username_pw_set(self.edge_id, self.password)
            self.client.reconnect_delay_set(1,15)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_disconnect = self.on_disconnect
            try:
                self.client.connect(self.mqtt_config['host'], self.mqtt_config['port'],keepalive=15)
                self.client.loop_start()
            except Exception as e:
                logging.error(f"mqtt client connection error: {e}")   
        except Exception as e:
            self.logger.error(f"MQTT connection error: {e}")

    def run(self):
        try: 
            while not self._check_host_connectivity():
                time.sleep(10)
            self._connect()
            self.r = self.redis.connect()
            self.logger.info(f"{self.name} publisher started")
            while not self._stop_event.is_set():
                try:
                    if not self.r:
                        self.r = self.redis.connect()
                    msgs = self.r.xreadgroup(self.redis.group_name,f"{self.servo_stream}_consumer",{self.servo_stream: ">"},count=1,block=1000)
                    if msgs:
                        for stream, messages in msgs:
                            for msg_id, fields in messages:
                                # self.logger.info(f"{stream} - {msg_id}: {fields}")
                                timestamp = int(msg_id.split('-')[0])
                                if fields.get('config'):
                                    self.mqtt_topic = f"humac/telemetry_cnc/indus/{self.edge_id}/servo/{self.name}/config"
                                    config_data = json.loads(fields.get('config'))
                                    config_data['ts'] = timestamp
                                    config_data['edgeid'] = self.edge_id
                                    while not self._publish(config_data):
                                        time.sleep(10)
                                if fields.get('monitor'):
                                    self.mqtt_topic = f"humac/telemetry_cnc/indus/{self.edge_id}/servo/{self.name}/monitor"
                                    monitor_data = json.loads(fields.get('monitor'))
                                    monitor_data['ts'] = timestamp
                                    monitor_data['edgeid'] = self.edge_id
                                    while not self._publish(monitor_data):
                                        time.sleep(10)
                                self.r.xack(self.servo_stream, self.redis.group_name, msg_id)
                                self.r.xdel(self.servo_stream, msg_id)
                    else:
                        time.sleep(0.1)
                        
                except Exception as e:
                    self.logger.error(f"Error in read/publish loop: {e}")
                    time.sleep(1.0)

        except KeyboardInterrupt:
            self.logger.warning("Received KeyboardInterrupt in run")
        except Exception as e:
            self.logger.error(f"Critical error in {self.name}: {e}")
        finally:
            self.stop()
            self.logger.info(f"Process {self.name} stopped cleanly")

    def stop(self):
        self._stop_event.set()