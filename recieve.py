import paho.mqtt.client as mqtt
import time
from statistics import mean
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class DataAggregator:
    def __init__(self, edge_broker_address, cloud_broker_address, topic_edge, topic_cloud, 
                 sampling_interval=5, use_moving_average=False, window_size=5):
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
        
 
        self.moving_window = deque(maxlen=window_size)
        
 
        self.edge_client = mqtt.Client()
        self.cloud_client = mqtt.Client()
        

        self.edge_client.connect(self.edge_broker_address)
        self.cloud_client.connect(self.cloud_broker_address)
        
  
        self.edge_client.on_message = self.on_message_received
        self.edge_client.subscribe(self.topic_edge)
        

        plt.style.use('seaborn')
        self.fig, self.ax = plt.subplots()
        self.line_data, = self.ax.plot([], [], label='Data', color='blue')
        self.line_avg, = self.ax.plot([], [], label='Average', color='red')
        self.ax.set_title('Real-Time Data Plotting')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Value')
        self.ax.legend()
        
    def on_message_received(self, client, userdata, message):
        try:
            # Decode and convert message payload to float
            data = float(message.payload.decode())
            self.data_list.append(data)
            self.moving_window.append(data)  # Add data to the moving window
            self.time_stamps.append(time.time())
            print(f"Received data from Edge broker: {data}")
        except ValueError:
            print("Received non-numeric data, ignoring.")
    
    def calculate_moving_average(self):
        # Calculate the moving average using the sliding window
        if len(self.moving_window) > 0:
            return mean(self.moving_window)
        return 0
    
    def publish_to_cloud(self):
        if self.data_list:
            if self.use_moving_average:
                avg_data = self.calculate_moving_average()
                print(f"Calculated Moving Average: {avg_data}")
            else:
                avg_data = mean(self.data_list)
                print(f"Calculated Simple Mean: {avg_data}")
            
            # Publish average data to the cloud
            self.cloud_client.publish(self.topic_cloud, str(avg_data))
            self.avg_data_list.append(avg_data)
            print(f"Published average data to Cloud broker: {avg_data}")
            
            # Clear the list of collected data
            self.data_list.clear()
    
    def update_plot(self, frame):
        # Update the plot with new data
        if len(self.time_stamps) > 0:
            current_time = self.time_stamps[-1]
            start_time = current_time - 60  # Display last 60 seconds of data
            
            # Trim data for the last 60 seconds
            time_window = [t for t in self.time_stamps if t >= start_time]
            data_window = self.data_list[-len(time_window):]
            avg_window = self.avg_data_list[-len(time_window):]
            
            self.line_data.set_data(time_window, data_window)
            self.line_avg.set_data(time_window, avg_window)
            
            # Update plot limits
            self.ax.set_xlim(start_time, current_time)
            self.ax.set_ylim(min(data_window + avg_window) - 5, max(data_window + avg_window) + 5)
        
        return self.line_data, self.line_avg

    def start(self):
        # Start the MQTT client loop
        self.edge_client.loop_start()
        
        # Start Matplotlib animation
        ani = animation.FuncAnimation(self.fig, self.update_plot, blit=True, interval=1000)
        plt.show()
        
        try:
            while True:
                # Wait for the specified sampling interval
                time.sleep(self.sampling_interval)
                self.publish_to_cloud()
        except KeyboardInterrupt:
            print("Stopping application.")
        finally:
        
            self.edge_client.loop_stop()
            self.edge_client.disconnect()
            self.cloud_client.disconnect()

# Usage
if __name__ == "__main__":
    edge_broker_address = "169.254.248.120"
    cloud_broker_address = "localhost"
    topic_edge = "sensor/data"
    topic_cloud = "sensor/average"
    sampling_interval = 5
    use_moving_average = True  # Set this to True to use moving average
    window_size = 5            # Size of the moving window
    
    aggregator = DataAggregator(edge_broker_address, cloud_broker_address, topic_edge, topic_cloud, 
                                sampling_interval, use_moving_average, window_size)
    aggregator.start()
