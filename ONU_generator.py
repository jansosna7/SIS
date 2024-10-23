import numpy as np
import pandas as pd

# Parameters for ONU points
num_onu = 100
center = (0, 0)
spread = 100  # Controls the spread of points around the center

# Generate ONU points randomly around the center
onu_points = np.random.normal(loc=center, scale=spread, size=(num_onu, 2))
onu_points = np.round(onu_points).astype(int)
# Create a DataFrame to store the points
df_onu = pd.DataFrame(onu_points, columns=['x', 'y'])

# Save the DataFrame to an Excel file
file_path = "onu_points.xlsx"
df_onu.to_excel(file_path, index=False)

print(f"ONU points saved to {file_path}")
