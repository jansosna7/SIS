import random
import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial import distance_matrix
import matplotlib.pyplot as plt
import os
from sklearn.cluster import KMeans
import random_noise
import naive

FIG_SIZE = 250
num = "_3"

def calculate_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


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



def optimize_splitters_with_krand(OLT, ONU_positions, num_splitters, max_iter, max_stagnation):
    onu_positions = ONU_positions[['x', 'y']].to_numpy()
    kmeans = KMeans(n_clusters=num_splitters, random_state=0)
    kmeans.fit(onu_positions)
    splitters_positions = np.round(kmeans.cluster_centers_).astype(int)
    splitters_positions = splitters_positions.tolist()  
    ONU_positions = assign_ONU_to_splitters(splitters_positions, ONU_positions)
    total_length,mst = calculate_total_length(OLT, splitters_positions, ONU_positions)
    
    #random noise version
    splitters_positions, ONU_positions, total_length, mst = random_noise.optimize_splitters_with_random_noise(OLT, ONU_positions, num_splitters, max_iter, max_stagnation)
    
    #naive version
    splitters_positions, ONU_positions, total_length, mst = naive.optimize_splitters_with_reassignment(OLT, ONU_positions, num_splitters, max_iter, max_stagnation)
    
    
    
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
    max_iter = 2000
    max_stagnation = 20

    for num_splitters in range(1, 2+int(len(ONU_positions)**0.5)):
        splitters,onus,dist,mst = optimize_splitters_with_krand(OLT, ONU_positions, num_splitters, max_iter, max_stagnation)
        
        file_path = os.path.join("k-rand_img", str(num_splitters) + "_krand_fiber_network" + num + ".png")
        plot_network(OLT, splitters, mst, onus, file_path, int(dist))

if __name__=="__main__":
    main()
