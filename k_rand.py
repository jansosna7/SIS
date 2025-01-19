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
import k_means

from fiber_lib import *


def optimize_splitters_with_krand(ONU_positions, num_splitters, max_iter, max_stagnation):
    #k-means version
    splitters_positions, ONU_positions, total_distance, mst = k_means.optimize_splitters_with_kmeans(ONU_positions, num_splitters)
    splitters_positions = splitters_positions

    #random noise version
    splitters_positions, ONU_positions, total_length, mst = random_noise.optimize_splitters_with_random_noise(ONU_positions, splitters_positions, max_iter, max_stagnation)
    
    #naive version
    splitters_positions, ONU_positions, total_length, mst = naive.optimize_splitters_with_reassignment(ONU_positions, splitters_positions, max_iter, max_stagnation)
    
    return splitters_positions, ONU_positions, total_length, mst


def calculate(ONU_positions, max_splitters, close=True, size=25):
    file_path = "onu_points" + num + ".xlsx"
    
    ONU_positions['splitter_id'] = -1
    max_iter = 5000
    max_stagnation = 50

    best_splitters,best_onus,best_dist,best_mst = optimize_splitters_with_krand(ONU_positions, 1, max_iter, max_stagnation)

    for num_splitters in range(3, min(len(ONU_positions)+1,max_splitters+1)):
        c_splitters,c_onus,c_dist,c_mst = optimize_splitters_with_krand(ONU_positions, num_splitters, max_iter, max_stagnation)
        print(num_splitters, c_dist)
        
        if c_dist<best_dist:
            best_splitters = c_splitters
            best_onus = c_onus
            best_dist = c_dist
            best_mst = c_mst
        
    file_path = os.path.join("krand_fiber_network" + ".png")
    plot_network(best_splitters, best_mst, best_onus, file_path, best_dist, close, size)
    print("final", best_dist)
    print(best_splitters)
    print(best_onus)

