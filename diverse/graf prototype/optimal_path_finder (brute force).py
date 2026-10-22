from graph import Graph, weighted_edge_list
import json
from itertools import permutations
from random import shuffle
from math import inf, factorial

from os import chdir
chdir("common/graf prototype")


G = Graph(weighted_edge_list)

simple_graph_nodes = ["START", "1", "2", "W1", "W2", "W3", "W4", "W5", "R1", "R2", "R3", "R4", "R5"]

simple_graph_adj = {}

for n in simple_graph_nodes:
    simple_graph_adj[n] = {}
    for adj_n in simple_graph_nodes:
        if adj_n != n:
            path = G.dijkstra(n, adj_n)
            simple_graph_adj[n][adj_n] = (G.sum_edge_weights(path), path)

with open("simple_graph_adjacency_list.json", "w", encoding="utf-8") as f:
    json.dump(simple_graph_adj, f, indent=4, ensure_ascii=False)

print("graph generated")

drop_offs = ["W1", "W2", "W3", "W4", "W5", "R1", "R2", "R3", "R4", "R5"]

def get_complete_path(seq):
    
    seq_extended = []

    for i in seq:
        if i[0] == "W":
            seq_extended.append("1")
        elif i[0] == "R":
            seq_extended.append("2")
        seq_extended.append(i)

    seq_complete = [node for node in G.dijkstra("START", seq_extended[0])]
    seq_complete = seq_complete[:-1]

    for i in range(len(seq_extended)-1):
        sub_path = simple_graph_adj[seq_extended[i]][seq_extended[i+1]][1]
        if i < len(seq_extended)-2:
            sub_path = sub_path[:-1]
        for node in sub_path:
            seq_complete.append(node)

    return seq_complete



results = {
    "best paths": [],
    "best sequences": []
}

max_edge_weight_sum = 0
worst_path = None

min_edge_weight_sum = inf
iteration = 0

for seq in permutations(drop_offs):
    iteration += 1
    if iteration % 1000 == 0:
        print(f"iteration: {iteration}/{factorial(10)} min_sum: {min_edge_weight_sum}, number of paths within 1mm: {len(results["best paths"])}")

    path = get_complete_path(seq)
    edge_weight_sum = G.sum_edge_weights(path)

    if edge_weight_sum < min_edge_weight_sum:
        results["best paths"] = [path]
        results["best sequences"] = [seq]
        min_edge_weight_sum = edge_weight_sum

    elif edge_weight_sum < min_edge_weight_sum + 0.001:
        results["best paths"].insert(0, path)
        results["best sequences"].insert(0, seq)

        if len(results["best paths"]) > inf:
            results["best paths"].pop()
            results["best sequences"].pop()

    if edge_weight_sum > max_edge_weight_sum:
        worst_path = path
        max_edge_weight_sum = edge_weight_sum

print(f"\n\nWorst path: \n{worst_path}")


with open("optimal_paths_brute_force.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)