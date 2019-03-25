import sys
import os, os.path
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Delaunay
from PIL import Image
from scipy.ndimage import gaussian_filter

def build_vert_by_th(im_cube,threshold):
    vertex = []
    [nx,ny,nz] = im_cube.shape
    ind_vert = 0
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                if im_cube[i,j,k]>threshold:
                    vertex.append([i,j,k,im_cube[i,j,k]])
    vertex = np.asarray(vertex)
    return vertex

def buildTriFromTetra(tetra):
    tri = {}

    nTe = tetra.shape[0]
    tri_index = 0

    for i in range(nTe):
        for j in range(4):
            # Four triangles
            newTri = []
            for k in range(4):
                # Triangles' three vertices
                if k != j:
                    newTri.append(tetra[i, k])
            newTri = tuple(newTri)
            if newTri not in tri:
                # Add new triangles
                tri[newTri] = tri_index
                tri_index = tri_index + 1

    # Convert everythin into list
    nTri = len(tri)
    tri_array = np.zeros([nTri, 3])
    for key, value in tri.items():
        tri_array[value, :] = list(key)

    return tri_array

def builEdgeFromTri(tri):
    edge = {}
    edge_index = 0

    nTri = len(tri)

    for i in range(nTri):
        for j in range(3):
            # 3 edges
            newEdge = []
            for k in range(3):
                if k != j:
                    newEdge.append(tri[i, k])
            newEdge = tuple(newEdge)
            if newEdge not in edge:
                edge[newEdge] = edge_index
                edge_index = edge_index + 1

    nEdge = len(edge)
    edge_array = np.zeros([nEdge, 2])
    for key, value in edge.items():
        edge_array[value, :] = list(key)

    return edge_array

def outBinary(vert, edge, triangle, nV, nE, nT,file_name):
    open(file_name, 'wb').close()
    with open(file_name, 'wb') as f:
        nV.astype(np.int32).tofile(f)
        vert.astype('d').tofile(f)
        nE.astype(np.int32).tofile(f)
        edge.astype(np.int32).tofile(f)
        nT.astype(np.int32).tofile(f)
        triangle.astype(np.int32).tofile(f)
    f.close()

def threshold_im(i_im,i_th):
    size_x,size_y = i_im.shape[0],i_im.shape[1]
    o_vert = []
    for i in range(size_x):
        for j in range(size_y):
            if i_im[i,j]>i_th:
                o_vert.append([i,j,i_im[i,j]])
    o_vert = np.asarray(o_vert)
    return o_vert

# read in image
Image.MAX_IMAGE_PIXELS = None
FIG_NAME = sys.argv[1]
im = plt.imread(FIG_NAME)
#out_dir = 'output'
out_dir = sys.argv[2]
GAUSSIAN = 1
if len(sys.argv) >= 4:
    GAUSSIAN = (int)(sys.argv[3])


im = gaussian_filter(im, sigma=GAUSSIAN)

print(np.min(im),np.max(im),np.percentile(im,99))

# threshold
threshold_vert = threshold_im(im,1)
print("len vert after threshold:",len(threshold_vert))
sys.stdout.flush()

print("Triangulation")
tri = Delaunay(threshold_vert[:,:2])
tri.simplices.sort()
print(tri.simplices.shape)

print("Build edge from tri.")
edge = builEdgeFromTri(tri.simplices)

np.savetxt(os.path.join(out_dir, "edge_list.txt"), edge, fmt='%d')
np.savetxt(os.path.join(out_dir, "tri_list.txt"), tri.simplices, fmt='%d')
np.savetxt(os.path.join(out_dir, "vert_list.txt"), threshold_vert, fmt='%s')

