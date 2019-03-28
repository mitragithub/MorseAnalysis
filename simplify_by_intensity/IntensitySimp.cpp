//============================================================================
// Name        : IntensitySimp.cpp
// Author      : Dingkang Wang
// Version     :
// Copyright   : Your copyright notice
// Description : Remove Branches with low average intensity.
//============================================================================

#include "Point.h"

#include <fstream>
#include <unordered_map>
#include <algorithm>
#include <cmath>

using namespace std;

//#define DEBUG true

typedef pair<int, int> iipair;

// original image, intensity of pixels.
unordered_map<Point, int> map_intensity;

// Output new set of v & e, record existing vertices & its index.
unordered_map<Point, int> index_v;

// new vertices & edges;
vector<Point> new_vertices;
vector<iipair> new_edges;

// original vertices & edges;
vector<Point> vertices;
vector<iipair> edges;

int w = 0, h = 0;
double filter_threshold = 2;
string ifile_path = ""; 	// input image grid path.
string vfile_path = "", efile_path = ""; // input file paths.
string ovfile_path = "", oefile_path = ""; // output file paths.

// read in intensity;
void ReadIntensity(string filepath) {
	cout << "Read Intensity..." << endl;
	ifstream fin;
	fin.open(filepath.c_str());
	int density;
	int y, x;

	while (fin >> x >> y >> density) {
		map_intensity[Point(y, x, density)] = density;
	}
	fin.close();
}

// read in vertices, edges;
void ReadInEdge(string vpath, string epath) {
	cout << "Read in vertices and edges..." << endl;
	ifstream fin;
	int x, y;
	double den;
	fin.open(vpath.c_str());
	// x y density
	while (fin >> x >> y >> den) {
		vertices.push_back(Point(y, x, 0));
	}
	fin.close();

	int u, v, i;
	fin.open(epath.c_str());
	// u v i (u, v) starting from 0.
	while (fin >> u >> v >> i) {
		edges.push_back(make_pair(u, v));
	}
	fin.close();
}

double GetDistance(int px, int py, int ux, int uy, int vx, int vy) {
	int A = px - ux;
	int B = px - uy;
	int C = vx - ux;
	int D = vy - uy;

	int dot = A * C + B * D;
	int len_sq = C * C + D * D;
	int param = -1;
	if (len_sq != 0) //in case of 0 length line
		param = dot / len_sq;

	int xx, yy;

	if (param < 0) {
		xx = ux;
		yy = uy;
	} else if (param > 1) {
		xx = vx;
		yy = vy;
	} else {
		xx = ux + param * C;
		yy = uy + param * D;
	}
	int dx = px - xx;
	int dy = py - yy;
	return sqrt(dx * dx + dy * dy);
}


// get x, y coordinates of all pixels on an edge. (Bresenham's line algorithm)
vector<Point> bresenham_line(Point &u, Point &v) {
	vector<Point> points;

	int x1 = u.x, y1 = u.y;
	int x2 = v.x, y2 = v.y;
	const bool steep = (abs(y2 - y1) >= abs(x2 - x1));
	if (steep) {
		swap(x1, y1);
		swap(x2, y2);
	}

	if (x1 > x2) {
		swap(x1, x2);
		swap(y1, y2);
	}

	const int dx = x2 - x1;
	const int dy = abs(y2 - y1);
	double error = (double) dx / 2;
	const int ystep = (y1 < y2) ? 1 : -1;
	int y = y1;
	const int max_x = x2;
	for (int x = x1; x <= max_x; x++) {
		if (steep)
			points.push_back(Point(y, x, 0));
		else
			points.push_back(Point(x, y, 0));
		error -= dy;
		if (error < 0) {
			y += ystep;
			error += dx;
		}
	}
	return points;
}

// rewrite it. use the new bresenham alg.
double GetUnitEdgeIntensity(iipair &edge) {
	Point u = vertices[edge.first];
	Point v = vertices[edge.second];

	vector<Point> pixels = bresenham_line(u, v);

	double tot_intensity = 0.0;
	for(auto p: pixels) {
		if(map_intensity.count(p))
			tot_intensity += map_intensity[p];
	}
	return tot_intensity / pixels.size();
}


// filter out edges with low (bottom percentage%) intensity;
void Filter(double threshold) {
	cout << "Filtering..." << endl;
	vector<double> edge_intensities(edges.size(), 0);
	// double max_intensity = 0.0;

	for (int i = 0; i < (int) edges.size(); ++i) {
		if (i % 100000 == 0)
			cout << i << endl;
		double intensity = GetUnitEdgeIntensity(edges[i]);
		edge_intensities[i] = intensity;

	}

	int cnt = 0;
	for (int i = 0; i < (int) edges.size(); ++i) {
		if (edge_intensities[i] > threshold) {
			Point u = vertices[edges[i].first];
			Point v = vertices[edges[i].second];

			int iu, iv;

			if (!index_v.count(u)) {
				index_v[u] = cnt++;
				new_vertices.push_back(u);
			}
			if (!index_v.count(v)) {
				index_v[v] = cnt++;
				new_vertices.push_back(v);
			}
			iu = index_v[u], iv = index_v[v];
			new_edges.push_back(make_pair(iu, iv));

		}
	}

}

void OutputNewGraph(string ovfile_path, string oefile_path) {
	cout << "Writing..." << endl;
	ofstream fout;
	fout.open(ovfile_path.c_str());
	for (auto &p : new_vertices) {
		fout << p.x << " " << p.y << " " << p.s << endl;
	}
	fout.close();

	fout.open(oefile_path.c_str());
	for (auto &e : new_edges) {
		fout << e.first << " " << e.second << " " << endl;
	}
	fout.close();
}

int main(int argc, char **argv) {

	if (argc < 4) {
		cout
				<< "We need three parameters, folder path, and (l, w), length(left to right) and width of the image."
				<< endl;
		exit(0);
	}
	string folder_path = argv[1];

	string ifile_path = folder_path + "/grid.txt"; // input image grid path.
	string vfile_path = folder_path + "/vert.txt", efile_path = folder_path
			+ "/edge.txt"; // input file paths.
	string ovfile_path = folder_path + "/new_vert.txt", oefile_path =
			folder_path + "/new_edge.txt"; //output file path, in the same folder as input.

	w = atoi(argv[2]);
	h = atoi(argv[3]);

	if (argc > 4)
		filter_threshold = atof(argv[4]);

	ReadIntensity(ifile_path);
	ReadInEdge(vfile_path, efile_path);
	cout << "We have " << vertices.size() << " vertices, and "
			<< edges.size() << " edges." << endl;
	Filter(filter_threshold);

	cout << "Now we have " << new_vertices.size() << " vertices, and "
			<< new_edges.size() << " edges." << endl;
	OutputNewGraph(ovfile_path, oefile_path);

	return 0;
}
