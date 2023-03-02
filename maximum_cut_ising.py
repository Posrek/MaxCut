# Copyright 2019 D-Wave Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ------ Import necessary packages ----
from collections import defaultdict

from dwave.system.samplers import DWaveSampler
from dwave.system.samplers import LeapHybridSampler
from dwave.system.composites import EmbeddingComposite
from dwave.cloud import Client #mislim da tole tuki ni potrebno

#client = Client.from_config(token='DEV-1de686584ee14d956aada28aadfec01c650cc1b9')

from matplotlib import pyplot as plt
import networkx as nx

# ------- Set up our graph -------

# shranimo graf
tuples = []
for t in open('C:/Users/Uporabnik/Desktop/DIPLOM/maximum-cut/G1_brez_brez_py.txt').read().split():
    a, b = t.strip('()').split(',')
    tuples.append((int(a), int(b)))
[tuple(int(i) for i in t.strip('()').split(',')) for t in open('C:/Users/Uporabnik/Desktop/DIPLOM/maximum-cut/G1_brez_brez_py.txt').read().split()]

#print(tuples)

# Create empty graph
G = nx.Graph()

# Add edges to the graph (also adds nodes)
G.add_edges_from(tuples)

# ------- Set up our QUBO dictionary -------

# Initialize our h vector, J matrix
h = defaultdict(int)
J = defaultdict(int)

# Update J matrix for every edge in the graph
for i, j in G.edges:
    J[(i,j)]+= 1

# ------- Run our QUBO on the QPU -------
# Set up QPU parameters
chainstrength = 100000
numruns = 10

# Run the QUBO on the solver from your config file
sampler = EmbeddingComposite(LeapHybridSampler())
#sampler = EmbeddingComposite(DWaveSampler())  #tega si uporablu
response = sampler.sample_ising(h, J,
                                chain_strength=chainstrength,
                                num_reads=numruns,
                                label='Example - Maximum Cut Ising')

# ------- Print results to user -------
print('-' * 60)
print('{:>15s}{:>15s}{:^15s}{:^15s}'.format('Set 0','Set 1','Energy','Cut Size'))
print('-' * 60)
for sample, E in response.data(fields=['sample','energy']):
    S0 = [k for k,v in sample.items() if v == -1]
    S1 = [k for k,v in sample.items() if v == 1]
    print('{:>15s}{:>15s}{:^15s}{:^15s}'.format(str(S0),str(S1),str(E),str(int((6-E)/2))))

# ------- Display results to user -------
# Grab best result
# Note: "best" result is the result with the lowest energy
# Note2: the look up table (lut) is a dictionary, where the key is the node index
#   and the value is the set label. For example, lut[5] = 1, indicates that
#   node 5 is in set 1 (S1).
lut = response.first.sample

# Interpret best result in terms of nodes and edges
S0 = [node for node in G.nodes if lut[node]==-1]
S1 = [node for node in G.nodes if lut[node]==1]
cut_edges = [(u, v) for u, v in G.edges if lut[u]!=lut[v]]
uncut_edges = [(u, v) for u, v in G.edges if lut[u]==lut[v]]

# Display best result
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos, nodelist=S0, node_color='r')
nx.draw_networkx_nodes(G, pos, nodelist=S1, node_color='c')
nx.draw_networkx_edges(G, pos, edgelist=cut_edges, style='dashdot', alpha=0.5, width=3)
nx.draw_networkx_edges(G, pos, edgelist=uncut_edges, style='solid', width=3)
nx.draw_networkx_labels(G, pos)

filename = "maxcut_plot_ising.png"
plt.savefig(filename, bbox_inches='tight')
print("\nYour plot is saved to {}".format(filename))



