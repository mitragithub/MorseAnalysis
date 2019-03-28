import csv
from matplotlib import image as mpimg
# from multiprocessing import Pool as ThreadPool
import numpy as np
import os.path
import PIL
from wpca import WPCA
import sys


PIL.Image.MAX_IMAGE_PIXELS = None


input_filename = sys.argv[1]
PLOT_CENTERS_FILENAME = sys.argv[2]
HALF_SQUARE_SIDE = int(sys.argv[3])

# Just for Visualizing results, do not need to change
PC_MULT_FACTOR = 10
# POOLS = 6


def distance(p1, p2):
    return (((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2)) ** .5


out_dir = sys.argv[4]
output_centers_filename = out_dir + "centers.txt"
output_verts_filename = out_dir + "vec_vert.txt"
output_edges_filename = out_dir + "vec_edge.txt"
output_pc_filename = out_dir + "pc.txt"

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

print('loading image...')
# input_filename = 'img/PMD2055_ALL/PMD2055&2054-F1-2015.03.14-01.16.05_PMD2055_1_0001_lossless_reg.tif'
input_img = mpimg.imread(input_filename)
print('computing max val')
max_val = np.max(input_img)
print('max val:', max_val)
scaled_input_img = input_img/max_val
del input_img
filtered_img = scaled_input_img
del scaled_input_img
# filtered_img = gaussian_filter(scaled_input_img, SIGMA)
nr, nc = filtered_img.shape


def threaded(pt):
    x = pt[0]
    y = pt[1]
    x_min = max(0, x - HALF_SQUARE_SIDE)
    x_max = min(nr, x + HALF_SQUARE_SIDE + 1)
    y_min = max(0, y - HALF_SQUARE_SIDE)
    y_max = min(nc, y + HALF_SQUARE_SIDE + 1)
    neighborhood = []
    for i in range(x_min, x_max):
        for j in range(y_min, y_max):
            neighborhood.append([i,j,filtered_img[i,j]])
    nbhd_pts = [[n_pt[0], n_pt[1]] for n_pt in neighborhood]
    # print('n size:', len(neighborhood))
    coords = np.asarray(nbhd_pts)
    vals = [n_pt[2] for n_pt in neighborhood]
    weights = []
    for val in vals:
        weights.append([val, val])
    weights = np.asarray(weights)
    pca = WPCA(n_components=1)
    pca.fit(coords, weights=weights)
    component = pca.components_[0]
    return component


print('reading in plot centers...')
plot_centers = []
ctr = 0
with open(PLOT_CENTERS_FILENAME, 'r') as centers_file:
    reader = csv.reader(centers_file, delimiter=' ')
    for line in reader:
        pt = (int(line[0]), int(line[1]))
        ctr += 1
        print('center:', ctr)
        plot_centers.append(pt)
    centers_file.close()
print('centers read:', len(plot_centers))


index = 0
with open(output_verts_filename, 'w') as verts_file:
    with open(output_edges_filename, 'w') as edge_file:
        with open(output_pc_filename, 'w') as pc_file:
            with open(output_centers_filename, 'w') as center_file:

                results = []
                for i in range(len(plot_centers)):
                    # print('results', i)
                    pt = plot_centers[i]
                    results.append(threaded(pt))
                '''
                pool = ThreadPool(POOLS)
                results = pool.map(threaded, plot_centers)
                pool.close()
                pool.join()
                '''
                for i in range(len(plot_centers)):
                    pt = plot_centers[i]
                    component = results[i]
                    edge_file.write(str(2 * index) + ' ' + str(2 * index + 1) + '\n')
                    verts_file.write(str(pt[0]) + ' ' + str(pt[1]) + '\n')
                    pc_file.write(str(component[0]) + ' ' + str(component[1]) + '\n')
                    center_file.write(str(pt[0]) + ' ' + str(pt[1]) + '\n')

                    scaled_component = [PC_MULT_FACTOR * j for j in component]
                    pt2 = [pt[j] + scaled_component[j] for j in range(len(pt))]
                    verts_file.write(str(pt2[0]) + ' ' + str(pt2[1]) + '\n')
                    index += 1
                center_file.close()
            pc_file.close()
        edge_file.close()
    verts_file.close()
