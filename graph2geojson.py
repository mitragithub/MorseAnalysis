import os
import sys
from geojson import Feature, FeatureCollection, LineString
import geojson as gjson


def make_geojson(vertices, edges, output_path):
    dir_path = os.path.dirname(output_path)
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
    features = []
    for i in range(len(edges)):
        e = edges[i]
        u, v = vertices[e[0]], vertices[e[1]]
        features.append(Feature(id=i, geometry=LineString([(u[0], u[1]), (v[0], v[1])]),
                                    properties={"stroke-width": 1}))
    with open(output_path, 'w') as file:
        file.write(gjson.dumps(FeatureCollection(features), sort_keys=True))


if __name__ == '__main__':
    id = int(sys.argv[1])
    input_folder = sys.argv[2]
    output_folder = sys.argv[3]
    input_vertices = os.path.join(input_folder, 'new_vert.txt')
    input_edges = os.path.join(input_folder, 'new_edge.txt')
    # input_vertices = sys.argv[1]
    # input_edges = sys.argv[2]
    neuron_name = sys.argv[4]
    vertices =[]
    edges = []
    with open(input_vertices) as input_v:
        for line in input_v:
            data = line.strip().split()[:2]
            v = [int(x) for x in data]
            v[1] = -v[1] # flip y axis
            vertices.append(v)

    with open(input_edges) as input_e:
        for line in input_e:
            data = line.strip().split()
            e = [int(x) for x in data]
            edges.append(e)

    output_path = os.path.join(output_folder, neuron_name+ '_' + '{0:04d}'.format(id) + '.json')
    make_geojson(vertices, edges, output_path)