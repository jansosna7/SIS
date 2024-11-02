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

from fiber_lib import *

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
        print(dist)

if __name__=="__main__":
    main()
