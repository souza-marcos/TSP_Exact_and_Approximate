import networkx as nx
import matplotlib.pyplot as plt
import logging

_l = logging.getLogger("networkx")
_l.addHandler(_h := logging.StreamHandler())
_h.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
_l.setLevel(logging.DEBUG)

G = nx.Graph()

H = nx.path_graph(10)
G.add_nodes_from(H)
G.add_edges_from(H.edges())

P = nx.petersen_graph()
ER = nx.erdos_renyi_graph(10, 0.5)

import matplotlib.pyplot as plt
subax1 = plt.subplot(121)
nx.draw(G, with_labels=True, ax=subax1)

subax2 = plt.subplot(122)
nx.draw(ER, ax=subax2)

plt.show()