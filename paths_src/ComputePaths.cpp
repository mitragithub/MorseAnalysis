//============================================================================
// Name        : ShowCandidates.cpp
// Author      : Dingkang Wang
// Version     :
// Copyright   : Your copyright notice
// Description : Show stats of each edge, there different stats
// 1. Average intensity throughout the edge.
// 2. gradient range (max - min).
// 3. different between it and its pc vector.
//============================================================================

#include "Point.h"

#include <iostream>
#include <iomanip>
#include <fstream>
#include <unordered_map>
#include <unordered_set>
#include <set>
using namespace std;

struct Path {

	vector<int> vertices;

	Path() {
		vertices = vector<int>();
	}

	Path(vector<int> _vers) {
		vertices = _vers;
	}

	void println() {
		cout << "Path: ";
		for (auto &i : vertices) {
			cout << i << " ";
		}
		cout << endl;
	}

};

typedef struct Path path;
typedef pair<int, int> iipair;
typedef pair<double, double> ddpair;

unordered_map<Point, int> map_intensity;
unordered_map<Point, double> map_vector;

vector<Point> new_vertices;
vector<iipair> new_edges;


// read in vertices, edges;
void ReadInEdge(string vpath, string epath) {
	cout << "Read in vertices and edges..." << endl;
	ifstream fin;
	int x, y;
	double den;
	fin.open(vpath.c_str());
	// x y density
	while (fin >> x >> y >> den) {
		new_vertices.push_back(Point(x, y, 0));
	}
	fin.close();

	int u, v, i;
	fin.open(epath.c_str());
	// u v i (u, v) starting from 0.
	while (fin >> u >> v >> i) {
		new_edges.push_back(make_pair(u, v));
	}
	fin.close();
}


void output_paths(string ofilepath, vector<path> &paths)
{
	cout << "Output...." << endl;
	ofstream fout;
	fout.open(ofilepath.c_str());
	fout << fixed << setprecision(4);
	for (int i = 0; i < (int) paths.size(); ++i) {
		for(auto id : paths[i].vertices) {
			fout << id << " ";
		}
		fout << endl;
	}

	fout.close();
}

void dfs(unordered_set<int> &used, vector<vector<iipair>> &edgelist, int temp,
		bool start, path &tpath, vector<path> &paths) {

	vector<iipair> edges = edgelist[temp];
	if (!start && edges.size() != 2) {
		// add path;
		paths.push_back(tpath);
	} else {
		for (auto &e : edges) {
			if (!used.count(e.second)) {
				used.insert(e.second);
				tpath.vertices.push_back(e.first);
				dfs(used, edgelist, e.first, false, tpath, paths);
				tpath.vertices.pop_back();
			}
		}
	}
}

vector<path> get_paths() {

	int n = new_vertices.size();

	vector<vector<iipair>> edgelist = vector<vector<iipair>>(n,
			vector<iipair>());

	set<iipair> used_edges;
	for (int i = 0; i < (int) new_edges.size(); ++i) {
		int u = new_edges[i].first;
		int v = new_edges[i].second;
		if (!used_edges.count(make_pair(min(u, v), max(u, v)))) {
			used_edges.insert(make_pair(min(u, v), max(u, v)));
			edgelist[u].push_back(make_pair(v, i));
			edgelist[v].push_back(make_pair(u, i));
		}
	}

	unordered_set<int> used;

	vector<path> rets;

	for (int i = 0; i < n; ++i) {
		if (edgelist[i].size() != 2) {
			path p;
			p.vertices.push_back(i);
			vector<path> paths;
			dfs(used, edgelist, i, true, p, paths);
			rets.insert(rets.end(), paths.begin(), paths.end());
		}
	}

	return rets;
}

int main(int argc, char** argv) {
	string vfile_path = argv[1], efile_path = argv[2]; // input file paths. path to vertice, edge files.

	string oefile_path = argv[3];

	ReadInEdge(vfile_path, efile_path);
	cout << "We have " << new_vertices.size() << " vertices, and "
			<< new_edges.size() << " edges." << endl;

	vector<path> paths = get_paths();
	cout << "There are " << paths.size() << " paths." << endl;
	output_paths(oefile_path, paths);

	return 0;
}
