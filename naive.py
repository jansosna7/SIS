import pandas as pd
import numpy as np
import random
from scipy.spatial.distance import euclidean
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial import distance_matrix
import matplotlib.pyplot as plt
import os

from fiber_lib import *

def move_splitter(splitter, direction, distance):  
    x, y = splitter  
    if direction == "up":
        y += distance
    elif direction == "down":
        y -= distance
    elif direction == "left":
        x -= distance
    elif direction == "right":
        x += distance
    return (x, y)

def swap(splitters_positions, chosen_splitter_index, new_position):
    new_splitters_positions = list(splitters_positions)
    new_splitters_positions[chosen_splitter_index] = new_position
    
    return new_splitters_positions

def optimize_splitters_with_reassignment(onups, splitters_positions, max_iter, max_stagnation):
    ONU_positions = onups.copy()  
    ONU_positions = assign_ONU_to_splitters(splitters_positions, ONU_positions)
    total_length, mst = calculate_total_length(splitters_positions, ONU_positions)

    if(len(splitters_positions) == 1):
        return splitters_positions, ONU_positions, total_length, mst

    stagnation = 0
    for iteration in range(max_iter):
        chosen_splitter_index = random.randint(1,len(splitters_positions)-1) #dont move OLT
        best_move = None
        best_length = total_length
        best_mst = mst
        best_ONU_positions = ONU_positions
        best_splitters_positions = splitters_positions
        
        for distance in [1,4,16]:
            for direction in ['up', 'down', 'left', 'right']:
                new_position = move_splitter(splitters_positions[chosen_splitter_index], direction, distance)
                new_splitters_positions = swap(splitters_positions, chosen_splitter_index, new_position)            
                new_ONU_positions = assign_ONU_to_splitters(new_splitters_positions, ONU_positions)
                new_length, new_mst = calculate_total_length(new_splitters_positions, ONU_positions)
                if new_length < best_length:
                    best_length = new_length.copy()
                    best_mst = new_mst.copy()
                    best_move = True
                    best_ONU_positions = new_ONU_positions.copy()
                    best_splitters_positions = new_splitters_positions.copy()

        if best_move:
            stagnation = 0            
            total_length = best_length.copy()
            mst = best_mst.copy()
            ONU_positions = best_ONU_positions.copy()
            splitters_positions = best_splitters_positions.copy()
        else:
            stagnation = stagnation + 1

        if stagnation > max_stagnation:
            break
        
    return splitters_positions, ONU_positions, total_length, mst

def main():
    OLT = (0,0)
    file_path = "onu_points" + num + ".xlsx"
    ONU_positions =  pd.read_excel(file_path)
    ONU_positions['splitter_id'] = -1
    num_splitters = 10
    max_iter = 3000
    max_stagnation = 33
    
    for num_splitters in range(1, 1+int(len(ONU_positions)**0.5)):
        splitters_positions = [OLT] + random_initial_positions(num_splitters)  
        splitters,onus,dist,mst = optimize_splitters_with_reassignment(ONU_positions, splitters_positions, max_iter, max_stagnation)
    
        file_path = os.path.join("naive_img", str(num_splitters) + "_naive_fiber_network" + num + ".png")
        plot_network(splitters, mst, onus, file_path, int(dist))
        print(dist)
        #check_assigment(onus,splitters)
        
if __name__=="__main__":
    main()
