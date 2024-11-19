import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate sample data
# Dataset 1
timestamps1 = pd.date_range(start="2024-01-01", periods=50, freq='D')
data1 = np.random.rand(50)

# Dataset 2 (different length)
timestamps2 = pd.date_range(start="2024-02-01", periods=30, freq='D')
data2 = np.random.rand(30)

# Plot on Figure 2
plt.figure(2)

# Plot Dataset 1
plt.plot(timestamps1, data1, label="Dataset 1", marker='o')

# Plot Dataset 2
plt.plot(timestamps2, data2, label="Dataset 2", marker='x')

# Format and display
plt.xlabel('Timestamp')
plt.ylabel('Value')
plt.title('Plot of Two Datasets with Different Timestamps')
plt.legend()
plt.grid()
plt.xticks(rotation=45)  # Rotate timestamps for better readability
plt.tight_layout()       # Adjust layout to prevent clipping

# Show plot
plt.show()
