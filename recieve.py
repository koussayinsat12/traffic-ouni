import paho.mqtt.client as mqtt
import time
from statistics import mean
from collections import deque
import matplotlib.pyplot as plt

class DataAggregator:
    def __init__(self, edge_broker_address, cloud_broker_address, topic_edge, topic_cloud, 
                 sampling_interval=5, plot_interval=10, use_moving_average=False, window_size=5):
        self.edge_broker_address = edge_broker_address
        self.cloud_broker_address = cloud_broker_address
        self.topic_edge = topic_edge
        self.topic_cloud = topic_cloud
        self.sampling_interval = sampling_interval
    
        self.use_moving_average = use_moving_average
        self.window_size = window_size
        
        self.data_list = []
        self.avg_data_list = []
        self.time_stamps = []
        self.moving_window = []
        self.avg_timestamp = []
        self.moving_timestamps = []
        self.plot_interval = plot_interval
       
        self.edge_client = mqtt.Client()
        self.cloud_client = mqtt.Client()
        
        self.edge_client.connect(self.edge_broker_address)
        self.cloud_client.connect(self.cloud_broker_address)
        
      
        self.edge_client.on_message = self.on_message_received
        self.edge_client.subscribe(self.topic_edge)

        self.edge_client.loop_start()
        self.cloud_client.loop_start()

    def on_message_received(self, client, userdata, message):
        try:
            data = float(message.payload.decode())
            self.data_list.append(data)
            self.moving_window.append(data)
            self.time_stamps.append(time.time())
            self.moving_timestamps.append(time.time())
            print(f"Received data from Edge broker: {data}")
        except ValueError:
            print("Received non-numeric data, ignoring.")
    
    def calculate_moving_average(self, arr):
        moving_averages = []
        i=0
        while i < len(arr) - self.window_size + 1:
        
            window = arr[i : i + self.window_size]
            window_average = round(sum(window) / self.window_size, 2)
            moving_averages.append(window_average)
            i += 1
        return moving_averages
    
    def publish_to_cloud(self):
        
        
        
        
        if self.use_moving_average:
            
       
            
            avg_data = self.calculate_moving_average(self.moving_window)
            self.avg_timestamp= self.avg_timestamp + self.calculate_moving_average(self.moving_timestamps )
            
            self.moving_window = []
            self.moving_timestamps = [] 
            if avg_data is None:
                print("Insufficient data for moving average calculation.")
                return
           
        else:
            
            self.avg_timestamp= self.avg_timestamp + [time.time()]
            
            avg_data = [round(mean(self.data_list), 2)]
           
        
     
        self.cloud_client.publish(self.topic_cloud, str(avg_data))
        self.avg_data_list= self.avg_data_list +avg_data
 
        print(f"Published average data to Cloud broker")

    def plot_data(self):
        plt.style.use('ggplot')
        fig, ax = plt.subplots()
        ax.set_title('Data and Moving Average/Mean Plot')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Value')
        
        avg_label = 'Moving Average' if self.use_moving_average else 'Simple Mean'
        
        if len(self.time_stamps) > 0 and len(self.avg_timestamp) > 0:
            time_deltas = [t - self.time_stamps[0] for t in self.time_stamps]
            time_deltas_avg = [t - self.avg_timestamp[0] for t in self.avg_timestamp]
            ax.plot(time_deltas, self.data_list, label='Received Data', color='blue')
            ax.plot(time_deltas_avg, self.avg_data_list, label=avg_label, color='red', linestyle='--')
            ax.legend()
            plt.show()

    def start(self):
        try:
            start_time = time.time()
            

            print(f"Collecting data and publishing every {self.sampling_interval} seconds... Press Ctrl+C to stop.")
            while True:
                time.sleep(self.sampling_interval)
                self.publish_to_cloud()
                
                exec_time = time.time()-start_time
                
                if exec_time > self.plot_interval:
                    break
                
                
                
        except KeyboardInterrupt:
            print("Stopping application due to keyboard interrupt.")
        finally:
            print("Stopping MQTT clients and disconnecting...")
            self.edge_client.loop_stop()
            self.cloud_client.loop_stop()
            self.edge_client.disconnect()
            self.cloud_client.disconnect()
            print("Generating plot of collected data...")
            self.plot_data()

# Usage
# Usage
if __name__ == "__main__":
    # Define broker addresses and topics
    edge_broker_address = "192.168.168.128"
    cloud_broker_address = "192.168.168.1"
    topic_edge = "sensor/data"
    topic_cloud = "sensor/average"
    
    # Define parameters
    sampling_interval = 1  
    plot_interval = 40      
    use_moving_average = False
    window_size = 5            

    # Create and start the DataAggregator
    aggregator = DataAggregator(
        edge_broker_address, 
        cloud_broker_address, 
        topic_edge, 
        topic_cloud, 
        sampling_interval,     
        plot_interval,         
        use_moving_average, 
        window_size
    )
    aggregator.start()

