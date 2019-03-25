from PIL import Image, ImageDraw
import os
import sys

def make_png(verts, edges, path, l, w, linestroke=1):
    im = Image.new('L', (l, w), color=0)
    draw = ImageDraw.Draw(im)
    for e in edges:
        u, v = verts[e[0]], verts[e[1]]
        draw.line((u[0], u[1], v[0], v[1]), fill=255, width=linestroke)
    im.save(path, format='png')



if __name__ == '__main__':

    input_folder, l, w = sys.argv[1], sys.argv[2], sys.argv[3]
    input_vert = os.path.join(input_folder, 'new_vert.txt')
    input_edge = os.path.join(input_folder, 'new_edge.txt')
    # input_edge = os.path.join(input_folder, 'no_hole_edge.txt')
    l, w = int(l), int(w)
    verts, edges = [], []

    with open(input_vert) as vfile:
        for line in vfile:
            v = line.strip().split()
            verts.append((int(v[0]), int(v[1])))

    with open(input_edge) as efile:
        for line in efile:
            e = line.strip().split()
            edges.append((int(e[0]), int(e[1])))

    dirpath = os.path.dirname(input_vert)
    path = os.path.join(dirpath, 'output_image.png')
    make_png(verts, edges, path, l, w)