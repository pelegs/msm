#!/usr/bin/env python3

import numpy as np
import queue

def dist(x, y):
    return np.linalg.norm(x-y)

def avg_dist(x, s):
    return np.average([dist(x, y) for y in s])

def in_set(x, s):
    for y in s:
        if np.array_equal(x, y):
            return True
    return False

def k_centers(points, n):
    centers = []

    # Choose a random point as cluster center
    centers.append(points[0])

    # Choose n-1 new cluster centers as max distance
    # to existing cluster centers
    for i in range(n):
        # Sort points in priority queue accoring to
        # their average distance to n-1 cluster centers
        q = queue.PriorityQueue()
        for point in points:
            d = avg_dist(point, centers)
            # Minus is for getting the largest distance first
            q.put((-d, point))
        centers.append(q.get()[1])
    return centers

def assign_cluster(points, centers):
    cluster_ids = []
    for point in points:
        cluster_ids.append(np.argmin([dist(point, y) for y in centers]))
    return cluster_ids

n = 10000
points = np.random.uniform(-10, 10, size=(n, 2))
k = 10
centers = k_centers(points, k)
cluster_ids = assign_cluster(points, centers)

for point, cluster_id in zip(points, cluster_ids):
    out = ' '.join(map(str, point))
    print(out, cluster_id)
