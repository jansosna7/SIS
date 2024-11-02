import random
import numpy as np
import pandas as pd

from scipy.spatial.distance import euclidean
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial import distance_matrix
import matplotlib.pyplot as plt
import os
from sklearn.cluster import KMeans

from fiber_lib import *

def optimize_splitters_with_kmeans(OLT, ONU_positions, num_splitters):
    # Extract ONU positions as numpy array
    onu_positions = ONU_positions[['x', 'y']].to_numpy()
    
    # Apply K-means clustering
    kmeans = KMeans(n_clusters=num_splitters, random_state=0)
    kmeans.fit(onu_positions)
    
    # Get the cluster centers (splitter positions)
    splitters_positions = np.round(kmeans.cluster_centers_).astype(int)
    
    # Assign each ONU to the nearest splitter
    #distances = kmeans.transform(onu_positions)
    #ONU_positions['splitter_id'] = np.argmin(distances, axis=1)
    
    ONU_positions = assign_ONU_to_splitters(splitters_positions, ONU_positions)
    

    total_distance,mst = calculate_total_length(OLT, splitters_positions, ONU_positions)
    
    return splitters_positions, ONU_positions, total_distance, mst

def main():
    OLT = (0,0)
    file_path = "onu_points" + num + ".xlsx"
    ONU_positions =  pd.read_excel(file_path)
    ONU_positions['splitter_id'] = -1

    for num_splitters in range(1, 2+int(len(ONU_positions)**0.5)):
        splitters,onus,dist,mst = optimize_splitters_with_kmeans(OLT, ONU_positions, num_splitters)
        print(dist)
        file_path = os.path.join("k-means_img", str(num_splitters) + "_kmean_fiber_network" + num + ".png")
        plot_network(OLT, splitters, mst, onus, file_path, int(dist))

if __name__=="__main__":
    main()
