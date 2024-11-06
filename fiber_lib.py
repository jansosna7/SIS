import random
import numpy as np
import pandas as pd

from scipy.spatial.distance import euclidean
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial import distance_matrix
import matplotlib.pyplot as plt
import os

FIG_SIZE = 250
num = "_3"

def calculate_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def calculate_total_length(splitters_positions, ONU_positions):
    total_length = 0
    
    for index, onu in ONU_positions.iterrows():
        onu_position = (onu['x'], onu['y'])
        splitter_id = onu['splitter_id']
        splitter_position = splitters_positions[int(splitter_id)]
        total_length += calculate_distance(onu_position, splitter_position)
        
    all_nodes = splitters_positions
    dist_matrix = distance_matrix(all_nodes, all_nodes)
    mst = minimum_spanning_tree(dist_matrix).toarray()
    total_length += mst[mst > 0].sum()
    return total_length, mst


def random_initial_positions(num_splitters):
    angles = np.random.uniform(0, 2 * np.pi, num_splitters)
    distances = np.random.uniform(0, FIG_SIZE, num_splitters)
    
    splitters_positions = [(int(d * np.cos(a)), int(d * np.sin(a))) for a, d in zip(angles, distances)]
    
    return splitters_positions

def assign_ONU_to_splitters(splitters_positions, onus):

    ONU_positions = onus.copy()
    
    ONU_positions['splitter_id'] = -1
    ONU_positions['distance'] = -1

    for index, onu in ONU_positions.iterrows():
        onu_position = (onu['x'], onu['y'])
        
        min_distance = float('inf')
        closest_splitter_id = -1
        
        for ids, splitter in enumerate(splitters_positions):
            if(ids > 0):
                distance = calculate_distance(onu_position, splitter)

                if distance < min_distance:
                    min_distance = distance
                    closest_splitter_id = ids

        ONU_positions.at[index, 'splitter_id'] = closest_splitter_id
        ONU_positions.at[index, 'distance'] = int(min_distance)

    
    return ONU_positions.copy()

def plot_network(splitters_positions, mst, ONU_positions, title, dist):
    plt.figure(figsize=(10, 8))

    for idx, splitter in enumerate(splitters_positions):
        plt.plot(splitter[0], splitter[1], 'ro', markersize=8, label='Splitter' if idx == 0 else "")  # Splitters in red

    plt.plot(splitters_positions[0][0], splitters_positions[0][1], 'bo', markersize=10, label='OLT')

    for i in range(mst.shape[0]):
        for j in range(mst.shape[1]):
            if mst[i, j] > 0:  # There is a connection
                    plt.plot([splitters_positions[i][0], splitters_positions[j][0]], 
                             [splitters_positions[i][1], splitters_positions[j][1]], 'r-', linewidth=2)

    for _, onu in ONU_positions.iterrows():
        plt.plot(onu['x'], onu['y'], 'go', markersize=4)
        if onu.name == 0:  
            plt.plot(onu['x'], onu['y'], 'go', markersize=4, label='ONU')
            
        splitter_id = onu['splitter_id']  
        splitter_position = splitters_positions[splitter_id]
        plt.plot([splitter_position[0], onu['x']], [splitter_position[1], onu['y']], 'g-', linewidth=1) 


    plt.title('Fiber network distance: ' + str(dist))
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.xlim(-FIG_SIZE, FIG_SIZE)
    plt.ylim(-FIG_SIZE, FIG_SIZE)
    plt.axhline(0, color='gray', lw=0.5)
    plt.axvline(0, color='gray', lw=0.5)
    plt.grid()
    plt.legend()
    plt.savefig(title)
    plt.close()

    
