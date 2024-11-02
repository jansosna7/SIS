import random
import numpy as np
import pandas as pd

from fiber_lib import *

from scipy.spatial.distance import euclidean
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial import distance_matrix
import matplotlib.pyplot as plt
import os

def add_noise(splitters_positions, distance):
    new_positions = []
    
    for (x, y) in splitters_positions:
        # Generate a random number between 0 and 1
        rand_num = random.random()
        
        if rand_num < 0.5:  # 50% chance to stay
            new_positions.append((x, y))
        else:
            # 50% chance to move in one of the 8 directions
            direction = random.choice(['up', 'down', 'left', 'right'])
            
            if direction == 'up':
                new_positions.append((x, y + distance))
            elif direction == 'down':
                new_positions.append((x, y - distance))
            elif direction == 'left':
                new_positions.append((x - distance, y))
            elif direction == 'right':
                new_positions.append((x + distance, y))

    return new_positions

def optimize_splitters_with_random_noise(OLT, onups, num_splitters, max_iter, max_stagnation):
    ONU_positions = onups.copy()
    splitters_positions = random_initial_positions(num_splitters)
    
    ONU_positions = assign_ONU_to_splitters(splitters_positions, ONU_positions)
    
    total_length, mst = calculate_total_length(OLT, splitters_positions, ONU_positions)

    stagnation = 0

    distance = 16
    for iteration in range(max_iter):
        #print(total_length)

        
        best_move = None
        best_length = total_length
        best_mst = mst
        best_ONU_positions = ONU_positions
        best_splitters_positions = splitters_positions
        
        new_splitters_positions = add_noise(splitters_positions, distance)            

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
            distance = distance/2
        if distance < 1:
            break
        
    return splitters_positions, ONU_positions, total_length, mst


def main():
    OLT = (0,0)
    file_path = "onu_points" + num + ".xlsx"
    ONU_positions =  pd.read_excel(file_path)
    ONU_positions['splitter_id'] = -1
    #num_splitters = 10
    max_iter = 5000
    max_stagnation = 60
    
    for num_splitters in range(1, 2+int(len(ONU_positions)**0.5)):
        splitters,onus,dist,mst = optimize_splitters_with_random_noise(OLT, ONU_positions, num_splitters, max_iter, max_stagnation)
    
        best_dist = dist
        for i in range(3):
            c_splitters,c_onus,c_dist,c_mst = optimize_splitters_with_random_noise(OLT, ONU_positions, num_splitters, max_iter, max_stagnation)
            print(dist)
            if(c_dist < best_dist):
                splitters,onus,dist,mst = c_splitters,c_onus,c_dist,c_mst
                
        file_path = os.path.join("random_noise_img", str(num_splitters) + "_random_noise_fiber_network" + num + ".png")
        plot_network(OLT, splitters, mst, onus, file_path, int(dist))

if __name__=="__main__":
    main()
