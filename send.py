import paho.mqtt.client as mqtt
import time
from simulator import Simulator
import math
import random


class MQTTDataPublisher:
    def __init__(self, broker_address, topic):
        self.broker_address = broker_address
        self.topic = topic
       
        self.client = mqtt.Client()
        self.client.connect(self.broker_address)
    
    def next_time_interval(self, l):
        n = random.random()
        inter_event_time = -math.log(1.0 - n) / l
        return inter_event_time
    
    def publish_data(self, data_set, l, NbreMessages):
        Time = 0
        
        for data in data_set:
            tt = self.next_time_interval(l)
            print("Publishing Time:", Time)
            time.sleep(tt)
            Time += tt
            self.client.publish(self.topic, str(data))
            print(f"Published data: {data} to topic: {self.topic}")

            NbreMessages -= 1
            
            if NbreMessages == 0:
                break
            

# Usage
if __name__ == "__main__":
    broker_address = "192.168.168.128" 
    topic = "sensor/data"  
    
    sim = Simulator(seed=12345, mean=20, standard_deviation=5)
    data_set = [sim.calculate_next_value() for _ in range(100000)]
    
    publisher = MQTTDataPublisher(broker_address, topic)
    publisher.publish_data(data_set, l=10, NbreMessages=10000)
