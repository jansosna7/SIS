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

def swap(splitters_positions, chosen_splitter, new_position):
    new_splitters_positions = list(splitters_positions)
    chosen_index = new_splitters_positions.index(chosen_splitter)
    new_splitters_positions[chosen_index] = new_position
    
    return new_splitters_positions

def optimize_splitters_with_reassignment(OLT, onups, num_splitters, max_iter, max_stagnation):
    ONU_positions = onups.copy()
    splitters_positions = random_initial_positions(num_splitters)
    
    ONU_positions = assign_ONU_to_splitters(splitters_positions, ONU_positions)
    
    total_length, mst = calculate_total_length(OLT, splitters_positions, ONU_positions)

    stagnation = 0

    
    for iteration in range(max_iter):
        #print(total_length)
        chosen_splitter = random.choice(splitters_positions)
        
        best_move = None
        best_length = total_length
        best_mst = mst
        best_ONU_positions = ONU_positions
        best_splitters_positions = splitters_positions
        
        for distance in [1,4,16]:
            for direction in ['up', 'down', 'left', 'right']:
                new_position = move_splitter(chosen_splitter, direction, distance)
                new_splitters_positions = swap(splitters_positions, chosen_splitter, new_position)            

                new_ONU_positions = assign_ONU_to_splitters(new_splitters_positions, ONU_positions)

                new_length, new_mst = calculate_total_length(OLT, new_splitters_positions, ONU_positions)
                
                if new_length < best_length:
                    best_length = new_length
                    best_mst = new_mst
                    best_move = True
                    best_ONU_positions = new_ONU_positions
                    best_splitters_positions = new_splitters_positions

        if best_move:
            stagnation = 0            
            total_length = best_length
            mst = best_mst
            ONU_positions = best_ONU_positions
            splitters_positions = best_splitters_positions
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
    
    for num_splitters in range(1, 2+int(len(ONU_positions)**0.5)):
        splitters,onus,dist,mst = optimize_splitters_with_reassignment(OLT, ONU_positions, num_splitters, max_iter, max_stagnation)
    
        '''best_dist = dist
        for i in range(4):
            c_splitters,c_onus,c_dist,c_mst = optimize_splitters_with_reassignment(OLT, ONU_positions, num_splitters, max_iter, max_stagnation)
            print(dist)
            if(c_dist < best_dist):
                splitters,onus,dist,mst = c_splitters,c_onus,c_dist,c_mst'''
        file_path = os.path.join("naive_img", str(num_splitters) + "_naive_fiber_network" + num + ".png")
        plot_network(OLT, splitters, mst, onus, file_path, int(dist))
        print(dist)

if __name__=="__main__":
    main()
