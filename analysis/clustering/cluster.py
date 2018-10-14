#!/usr/bin/env python3

import numpy as np
import queue
from subprocess import call

def dist(x, y):
    return np.linalg.norm(x-y)


def avg_dist(x, s):
    return np.average([dist(x, y) for y in s])


def in_set(x, s):
    for y in s:
        if np.array_equal(x, y):
            return True
    return False


def k_centers(points, k):
    """ Assigns k centers from the provided
        list of points
    """
    centers = []
    # Choose a random point as cluster center
    centers.append(points[0])
    # Choose n-1 new cluster centers as max distance
    # to existing cluster centers
    for i in range(k-1):
        # Sort points in priority queue accoring to
        # their average distance to n-1 cluster centers
        q = queue.PriorityQueue()
        for point in points:
            d = avg_dist(point, centers)
            # Horrible HACK: the minus is for getting
            # the largest distance first
            q.put((-d, point))
        centers.append(q.get()[1])
    return centers


def k_medoids(points, k):
    pass


def assign_cluster(points, centers):
    """ Returns a list of indeces representing the
        cluster center index of each point
        (e.g. index 0 means the first element in
        the centers list
    """
    cluster_ids = []
    for point in points:
        cluster_ids.append(np.argmin([dist(point, y) for y in centers]))
    return cluster_ids


def rand_sphere(n, dim=2, center=None, r=1):
    """ Returns n random points in a sphere
        of dimension dim around the provided center
        (default center is the origin)
    """
    if center is None:
        center = np.zeros(dim)

    points = np.zeros(dim)
    while points.shape[0] <= n:
        new_point = np.random.uniform(-1, 1, size=dim)
        if np.linalg.norm(new_point) <= 1:
            points = np.vstack((points, new_point))

    points = np.delete(points, 0, 0)
    return r * points + center

n = 600
m = 5
points = np.zeros(2)
for i in range(m):
    r = np.random.uniform(0.5, 2)
    points = np.vstack((points, rand_sphere(n, center=np.random.uniform(-5, 5, size=(1, 2)), r=r) ))

k = m
centers = k_centers(points, k)
cluster_ids = assign_cluster(points, centers)

with open('cluster.data', 'w') as f:
    for point, cluster_id in zip(points, cluster_ids):
        f.write('{} {}\n'.format(' '.join(map(str, point)), cluster_id))
call(['gnuplot', 'draw.gp'])
call(['eog', 'cluster.png'])
