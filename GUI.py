import tkinter as tk
from tkinter import simpledialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from k_rand import calculate

df = pd.DataFrame(columns=['x', 'y'])

root = tk.Tk()
root.title("XY Plane with Points")

current_mode = "add"  # 'add' or 'remove'
plane_size = 0
canvas = None  

def ask_plane_size():
    size = simpledialog.askinteger("Plane Size", "Enter the size of the plane (positive integer):")
    if size is None or size <= 0:
        messagebox.showerror("Invalid Size", "Please enter a valid positive integer.")
        ask_plane_size()
    else:
        create_plane(size)

def create_plane(size):
    global plane_size
    plane_size = size
    update_plane_plot()

def update_plane_plot():
    global canvas
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-plane_size, plane_size)
    ax.set_ylim(-plane_size, plane_size)
    ax.set_title("XY Plane")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True)

    ax.scatter(df['x'], df['y'], color='green', zorder=5)

    if canvas is not None:
        canvas.get_tk_widget().destroy()  
    canvas = FigureCanvasTkAgg(fig, master=frame_plot) 
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    canvas.mpl_connect('button_press_event', on_canvas_click)

def on_canvas_click(event):
    global df  
    if event.inaxes is not None:
        x = int(round(event.xdata))
        y = int(round(event.ydata))
        
        if -plane_size <= x <= plane_size and -plane_size <= y <= plane_size:
            if current_mode == "add":
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

def toggle_mode():
    global current_mode
    if current_mode == "add":
        current_mode = "remove"
        btn_toggle.config(text="Switch to Add Mode")
    else:
        current_mode = "add"
        btn_toggle.config(text="Switch to Remove Mode")

def call_calculate():
    max_splitters = simpledialog.askinteger("Max Splitters", "Enter the maximum number of splitters:")
    if max_splitters is None or max_splitters <= 0:
        messagebox.showerror("Invalid Input", "Please enter a valid positive integer for max_splitters.")
    else:
        calculate(df, max_splitters)

frame_controls = tk.Frame(root)
frame_controls.pack(side=tk.LEFT, padx=10, pady=10)

frame_plot = tk.Frame(root)
frame_plot.pack(side=tk.RIGHT, padx=10, pady=10)

btn_toggle = tk.Button(frame_controls, text="Switch to Remove Mode", command=toggle_mode)
btn_toggle.pack(fill=tk.X, pady=5)

btn_calculate = tk.Button(frame_controls, text="Calculate", command=call_calculate)
btn_calculate.pack(fill=tk.X, pady=5)

ask_plane_size()

root.mainloop()

