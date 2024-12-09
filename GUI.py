import tkinter as tk
from tkinter import simpledialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import k_rand_lib  # Assuming you have this module

# Initialize the DataFrame to store points
df = pd.DataFrame(columns=['x', 'y'])

# Create the main application window
root = tk.Tk()
root.title("XY Plane with Points")

# Variable to track the mode (add or remove)
current_mode = "add"  # 'add' or 'remove'
plane_size = 0
canvas = None  # We will initialize the canvas here

# Function to ask for the size of the plane
def ask_plane_size():
    size = simpledialog.askinteger("Plane Size", "Enter the size of the plane (positive integer):")
    if size is None or size <= 0:
        messagebox.showerror("Invalid Size", "Please enter a valid positive integer.")
        ask_plane_size()
    else:
        create_plane(size)

# Function to create the plane based on user input
def create_plane(size):
    global plane_size
    plane_size = size
    update_plane_plot()

# Function to update the plot with points
def update_plane_plot():
    global canvas
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-plane_size, plane_size)
    ax.set_ylim(-plane_size, plane_size)
    ax.set_title("XY Plane")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True)

    # Plot all points
    ax.scatter(df['x'], df['y'], color='red', zorder=5)

    # If canvas exists, update it; otherwise, create a new one
    if canvas is not None:
        canvas.get_tk_widget().destroy()  # Destroy the previous canvas
    canvas = FigureCanvasTkAgg(fig, master=frame_plot)  # Recreate the canvas with the updated plot
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Bind mouse click event to add/remove point
    canvas.mpl_connect('button_press_event', on_canvas_click)

# Function to handle mouse click on the canvas
def on_canvas_click(event):
    global df  # Ensure we're modifying the global df variable
    if event.inaxes is not None:
        x = int(round(event.xdata))
        y = int(round(event.ydata))
        
        # Ensure coordinates are within bounds
        if -plane_size <= x <= plane_size and -plane_size <= y <= plane_size:
            if current_mode == "add":
                # Add point using pd.concat() instead of append()
                new_point = pd.DataFrame({'x': [x], 'y': [y]})
                df = pd.concat([df, new_point], ignore_index=True)
                update_plane_plot()
            elif current_mode == "remove":
                # Remove point within a margin of error
                margin = 5
                index_to_remove = None
                for i, row in df.iterrows():
                    if abs(row['x'] - x) <= margin and abs(row['y'] - y) <= margin:
                        index_to_remove = i
                        break
                
                if index_to_remove is not None:
                    df.drop(index_to_remove, inplace=True)
                    update_plane_plot()
                else:
                    messagebox.showerror("Point Not Found", "No point found close to the clicked coordinates within the margin.")

# Function to toggle between 'add' and 'remove' mode
def toggle_mode():
    global current_mode
    if current_mode == "add":
        current_mode = "remove"
        btn_toggle.config(text="Switch to Add Mode")
    else:
        current_mode = "add"
        btn_toggle.config(text="Switch to Remove Mode")

# Function to ask the user for max_splitters and trigger the calculation
def calculate():
    max_splitters = simpledialog.askinteger("Max Splitters", "Enter the maximum number of splitters:")
    if max_splitters is None or max_splitters <= 0:
        messagebox.showerror("Invalid Input", "Please enter a valid positive integer for max_splitters.")
    else:
        # Pass both the df and max_splitters to the calculate function
        k_rand_lib.calculate(df, max_splitters)

# Add the main buttons and set up the interface
frame_controls = tk.Frame(root)
frame_controls.pack(side=tk.LEFT, padx=10, pady=10)

frame_plot = tk.Frame(root)
frame_plot.pack(side=tk.RIGHT, padx=10, pady=10)

# Button to toggle between add/remove mode
btn_toggle = tk.Button(frame_controls, text="Switch to Remove Mode", command=toggle_mode)
btn_toggle.pack(fill=tk.X, pady=5)

# Button to calculate/optimize
btn_calculate = tk.Button(frame_controls, text="Calculate", command=calculate)
btn_calculate.pack(fill=tk.X, pady=5)

# Ask for the plane size on launch
ask_plane_size()

# Start the Tkinter main loop
root.mainloop()

