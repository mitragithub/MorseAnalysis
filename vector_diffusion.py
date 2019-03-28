import csv
from math import exp
from matplotlib import image as mpimg
import numpy as np
import PIL
import sys

PIL.Image.MAX_IMAGE_PIXELS = None


input_filename = sys.argv[1]
directory = sys.argv[2]
SIGMA = int(sys.argv[3])
if len(sys.argv) == 4:
    MAX_INT = 1.0
else:
    MAX_INT = float(sys.argv[4])

PC_MULT_FACTOR = 10

center_filename = directory + "centers.txt"
pc_filename = directory + "pc.txt"
vert_filename = directory + "diffusion_centers_vert.txt"
edge_filename = directory + "diffusion_centers_edge.txt"
vector_filename = directory + "diffusion_gt.txt"
domain_filename = directory + "diffusion_domain.txt"

directory = input_filename[:input_filename.rfind('/') + 1]
input_img = mpimg.imread(input_filename)
max_val = np.max(input_img)
scaled_input_img = input_img/max_val
filtered_img = scaled_input_img

nr, nc = filtered_img.shape


def distance(pt1, pt2):
    return ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** .5


def compute_vector_diffuison(x, y, dicti, grid):
    keys = dicti.keys()
    pt = (x, y)
    vector = [0, 0]
    x_min = max(0, x - 3 * SIGMA)
    x_max = min(nr + 1, x + 3 * SIGMA + 1)
    y_min = max(0, y - 3 * SIGMA)
    y_max = min(nc + 1, y + 3 * SIGMA + 1)
    for i in range(x_min, x_max):
        for j in range(y_min, y_max):
            dist = distance(pt, (i,j))
            if dist > 3*SIGMA:
                continue
            if (i,j) not in keys:
                continue
            value = dicti[(i, j)]
            f_val = grid[i, j]
            f_val = min(f_val, MAX_INT)
            factor = exp(-dist/SIGMA)
            factor *= f_val
            vector[0] += factor * value[0]
            vector[1] += factor * value[1]
    magnitude = (vector[0] ** 2 + vector[1] ** 2) ** .5
    if magnitude == 0:
        print('0!')
        return [0,0]
    normalized = (vector[0] / magnitude, vector[1] / magnitude)
    return normalized


print('loading centers...')
centers = []
wpcs = []
center_wpca_dict = {}
with open(center_filename, 'r') as center_file:
    reader = csv.reader(center_file, delimiter=' ')
    for x in reader:
        centers.append((int(x[0]), int(x[1])))
    center_file.close()

print('loading vectors...')
with open(pc_filename, 'r') as pc_file:
    reader = csv.reader(pc_file, delimiter=' ')
    for x in reader:
        x_axis_component = float(x[0])
        if x_axis_component >= 0:
            wpcs.append((float(x[0]), float(x[1])))
        else:
            wpcs.append((-float(x[0]), -float(x[1])))
    pc_file.close()
print('loaded')

assert(len(centers) == len(wpcs))

for i in range(len(centers)):
    center_wpca_dict[centers[i]] = wpcs[i]
diffusion_dict = {}
print('computing')
ctr = 0
for pt in centers:
    x = pt[0]
    y = pt[1]
    diffusion_vector = compute_vector_diffuison(x, y, center_wpca_dict, filtered_img)
    diffusion_dict[(x, y)] = diffusion_vector
    ctr += 1
    print('ctr:', ctr)
print('computed')
index = 0
with open(vert_filename, 'w') as vert_file:
    with open(edge_filename, 'w') as edge_file:
        with open(domain_filename, 'w') as domain_file:
            with open(vector_filename, 'w') as vector_file:
                for key in diffusion_dict.keys():
                    val = diffusion_dict[key]
                    vert_file.write(str(key[0]) + ' ' + str(key[1]) + '\n')
                    scaled_val = [PC_MULT_FACTOR * j for j in val]
                    pt2 = [key[j] + scaled_val[j] for j in range(len(key))]
                    vert_file.write(str(pt2[0]) + ' ' + str(pt2[1]) + '\n')
                    edge_file.write(str(2 * index) + ' ' + str(2 * index + 1) + '\n')
                    domain_file.write(str(key[0]) + ' ' + str(key[1]) + '\n')
                    vector_file.write(str(val[0]) + ' ' + str(val[1]) + '\n')

                    index += 1
        edge_file.close()
    vert_file.close()
