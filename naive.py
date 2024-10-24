import pandas as pd
import numpy as np
import random
from scipy.spatial.distance import euclidean
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial import distance_matrix
import matplotlib.pyplot as plt
import os

FIG_SIZE = 250
num = "_3"

def calculate_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def random_initial_positions(num_splitters):
    angles = np.random.uniform(0, 2 * np.pi, num_splitters)
    distances = np.random.uniform(0, 200, num_splitters)
    
    splitters_positions = [(int(d * np.cos(a)), int(d * np.sin(a))) for a, d in zip(angles, distances)]
    
    return splitters_positions

def assign_ONU_to_splitters(splitters_positions, ONU_positions):
    """
    Parametry:
    splitters_positions: Lista krotek (x, y) z pozycjami splitterów.
    ONU_positions: DataFrame z kolumnami ['x', 'y'] zawierającymi pozycje ONU.
    
    Zwraca:
    DataFrame: Zaktualizowany DataFrame ONU_positions z nową kolumną 'splitter_id'.
    """
    ONU_positions['splitter_id'] = -1
    
    splitter_capacity = {i: 0 for i in range(len(splitters_positions))}
    
    for index, onu in ONU_positions.iterrows():
        onu_position = (onu['x'], onu['y'])
        
        min_distance = float('inf')
        closest_splitter_id = -1
        
        for i, splitter in enumerate(splitters_positions):
            distance = calculate_distance(onu_position, splitter)

            if distance < min_distance:
                min_distance = distance
                closest_splitter_id = i

        if closest_splitter_id != -1:
            ONU_positions.at[index, 'splitter_id'] = closest_splitter_id
            splitter_capacity[closest_splitter_id] += 1  
    
    return ONU_positions


def calculate_total_length(OLT, splitters_positions, ONU_positions):
    total_length = 0
    
    for index, onu in ONU_positions.iterrows():
        onu_position = (onu['x'], onu['y'])
        splitter_id = onu['splitter_id']
        splitter_position = splitters_positions[int(splitter_id)]
        total_length += calculate_distance(onu_position, splitter_position)
        
    all_nodes = [OLT] + splitters_positions
    dist_matrix = distance_matrix(all_nodes, all_nodes)
    mst = minimum_spanning_tree(dist_matrix).toarray()
    total_length += mst[mst > 0].sum()
    return total_length, mst

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

def plot_network(OLT, splitters_positions, mst, ONU_positions, title, dist):
    plt.figure(figsize=(10, 8))

    plt.plot(OLT[0], OLT[1], 'bo', markersize=10, label='OLT')

    for idx, splitter in enumerate(splitters_positions):
        plt.plot(splitter[0], splitter[1], 'ro', markersize=8, label='Splitter' if idx == 0 else "")  # Splitters in red

    for i in range(mst.shape[0]):
        for j in range(mst.shape[1]):
            if mst[i, j] > 0:  # There is a connection
                if i == 0:  # OLT is the first node (index 0)
                    plt.plot([OLT[0], splitters_positions[j-1][0]], 
                             [OLT[1], splitters_positions[j-1][1]], 'r-', linewidth=2)
                else:
                    plt.plot([splitters_positions[i-1][0], splitters_positions[j-1][0]], 
                             [splitters_positions[i-1][1], splitters_positions[j-1][1]], 'r-', linewidth=2)

    for _, onu in ONU_positions.iterrows():
        plt.plot(onu['x'], onu['y'], 'go', markersize=4)
        if onu.name == 0:  
            plt.plot(onu['x'], onu['y'], 'go', markersize=4, label='ONU')
        splitter_id = onu['splitter_id']  
        splitter_position = splitters_positions[splitter_id]
        plt.plot([splitter_position[0], onu['x']], [splitter_position[1], onu['y']], 'g-', linewidth=1) 


    plt.title('Fiber network ' + str(dist))
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

if __name__=="__main__":
    main()
