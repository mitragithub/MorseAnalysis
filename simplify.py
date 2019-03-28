import csv
import math
from matplotlib import image as mpimg
import numpy as np
from os.path import join
from PIL import Image, ImageDraw
import PIL
import sys

PIL.Image.MAX_IMAGE_PIXELS = None

IMAGE_FILENAME = sys.argv[1]
INPUT_FOLDER = sys.argv[2]
ALGO_THRESH = float(sys.argv[3])
LEN_THRESH = float(sys.argv[4])

# Vars
arg_len = len(sys.argv)

if arg_len < 6:
    ALPHA = 0
else:
    ALPHA = float(sys.argv[5])

if arg_len < 7:
    PATH_RADIUS = 2
else:
    PATH_RADIUS = int(sys.argv[6])

if arg_len < 8:
    MAX_INT = 1.0
else:
    MAX_INT = float(sys.argv[7])

# Files
VERT_FILENAME = join(INPUT_FOLDER, 'vert.txt')
PATH_FILENAME = join(INPUT_FOLDER, 'paths.txt')
GT_FILENAME = join(INPUT_FOLDER, 'diffusion_gt.txt')
DOMAIN_FILENAME = join(INPUT_FOLDER, 'diffusion_domain.txt')
pe_filename = join(INPUT_FOLDER, 'simplify_edges.txt')


def compute_abs_cos_angle(v1, v2):
    v1_array = np.asarray(v1)
    v2_array = np.asarray(v2)

    if np.linalg.norm(v1_array) == 0 or np.linalg.norm(v2_array) == 0:
        return 0

    v1_unit = v1_array / np.linalg.norm(v1_array)
    v2_unit = v2_array / np.linalg.norm(v2_array)
    angle = np.arccos(np.clip(np.dot(v1_unit, v2_unit), -1.0, 1.0))
    cos = math.cos(angle)
    return abs(cos)


def compute_tangents(p):
    estimated_tangents = []
    for i in range(len(p)):
        left = max(0, i - PATH_RADIUS)
        right = min(i + PATH_RADIUS, len(p) - 1)
        lv = p[left]
        rv = p[right]
        vector = (lv[0] - rv[0], lv[1] - rv[1])
        estimated_tangents.append(vector)
    return estimated_tangents


def dist(p1, p2):
    return (((p2[0] - p1[0]) ** 2) + ((p2[1] - p1[1]) ** 2)) ** .5


def line_function(val, cos):
    capped_val = min(val, MAX_INT)
    return (ALPHA + cos) * capped_val


def length(p):
    sum = 0
    for i in range(len(p) - 1):
        i_dist = dist(p[i], p[i + 1])
        sum += i_dist
    return sum


def make_png(paths, output_path, st, lens):

    good_paths = []
    bad_paths = []
    bad_len = []

    for i in range(len(paths)):
        path = paths[i]

        if st[i] > ALGO_THRESH:
            good_paths.append(path)
        else:
            bad_paths.append(path)
            bad_len.append(lens[i])

    con_paths = []
    for i in range(len(bad_paths)):
        path = bad_paths[i]
        p_len = bad_len[i]
        start = path[0]
        end = path[len(path)-1]
        g_start = [pa for pa in good_paths if pa[0] == start or pa[len(pa)-1] == start]
        g_end = [pa for pa in good_paths if pa[0] == end or pa[len(pa)-1] == end]
        if p_len < LEN_THRESH and len(g_start) > 0 and len(g_end) > 0 and (len(g_start) == 1 or len(g_end) == 1):
            con_paths.append(path)

    with open(output_path, 'w') as output_file:
        for p in good_paths:
            for i in range(len(p) - 1):
                v1 = p[i]
                v2 = p[i + 1]
                output_file.write(str(v1) + ' ' + str(v2) + '\n')

        for p in con_paths:
            for i in range(len(p) - 1):
                v1 = p[i]
                v2 = p[i + 1]
                output_file.write(str(v1) + ' ' + str(v2) + '\n')

        output_file.close()


verts = []
print('reading in verts...')
with open(VERT_FILENAME, 'r') as vert_file:
    reader = csv.reader(vert_file, delimiter=' ')
    for line in reader:
        verts.append((int(line[0]), int(line[1])))
    vert_file.close()

intensity = {}
print('reading image...')
input_img = mpimg.imread(IMAGE_FILENAME)
max_val = np.max(input_img)
print('MAX', max_val)

scaled_input_img = input_img/max_val
filtered_img = scaled_input_img
# filtered_img = gaussian_filter(scaled_input_img, SIGMA)
for v in verts:
    x = v[0]
    y = v[1]
    f = filtered_img[x, y]
    # print('f', f)
    intensity[v] = f
del input_img
del scaled_input_img
del filtered_img

paths = []
print('reading in paths...')
lines = [line.rstrip('\n').split(' ') for line in open(PATH_FILENAME)]

for i in range(len(lines)):
    lines[i] = lines[i][:len(lines[i]) - 1]

for line in lines:
    paths.append([int(x) for x in line])

print('reading domain...')
domain = []
with open(DOMAIN_FILENAME, 'r') as domain_file:
    reader = csv.reader(domain_file, delimiter=' ')
    for line in reader:
        domain.append((int(line[0]), int(line[1])))
    domain_file.close()

print('reading vectors...')
vectors = []
with open(GT_FILENAME, 'r') as gt_file:
    reader = csv.reader(gt_file, delimiter=' ')
    for line in reader:
        vectors.append((float(line[0]), float(line[1])))
    gt_file.close()

assert(len(domain) == len(vectors))

gt_dict = {}
print('building dict...')
for i in range(len(verts)):
    gt_dict[verts[i]] = vectors[i]

del domain
del vectors

print('ready to go!')
scores = []
lengths = []
degree_dict = {}
for i in range(len(verts)):
    degree_dict[i] = 0

p_index = 0
for path in paths:
    p_index += 1
    # print('path:', p_index,'/',len(paths))
    v_path = [verts[i] for i in path]
    # print(v_path)
    p_len = length(v_path)

    degree_dict[path[0]] += 1
    degree_dict[path[len(path)-1]] += 1

    lengths.append(p_len)
    # print(p_len)
    f_vals = [intensity[v] for v in v_path]
    # print(f_vals)
    tangents = compute_tangents(v_path)
    abs_cosines = []
    for i in range(len(v_path)):
        v = v_path[i]
        gt = gt_dict[v]
        tangent = tangents[i]
        abs_cosines.append(compute_abs_cos_angle(gt, tangent))

    score = 0
    vec_score = 0
    for i in range(len(v_path) - 1):
        b1 = line_function(f_vals[i], abs_cosines[i])
        b2 = line_function(f_vals[i+1], abs_cosines[i+1])
        h = dist(v_path[i], v_path[i+1])
        area = h * (b1 + b2) / 2
        score += area

        b3 = abs_cosines[i]
        b4 = abs_cosines[i+1]
        area2 = h*(b3+b4) / 2
        vec_score += area2
    scores.append(score/p_len)

print('outputting...')
min_len = min(lengths)
max_len = max(lengths)
normalized_lens = [(s - min_len) / (max_len - min_len) for s in lengths]
print('min len:', min(normalized_lens))
min_score = min(scores)
max_score = max(scores)
normalized_scores = [(s - min_score) / (max_score - min_score) for s in scores]
make_png(paths, pe_filename, normalized_scores, normalized_lens)
