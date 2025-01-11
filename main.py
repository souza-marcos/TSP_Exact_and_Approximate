import networkx as nx
import matplotlib.pyplot as plt

limDigits = 6

def readInputFile(filename: str) -> list[tuple[float, float]]:
    ''' Lê um arquivo de entrada no formato .tsp e retorna uma lista de tuplas (x, y) com as posições dos pontos
    '''
    with open(filename, 'r') as f:
        lines = f.readlines()
        positions = []
        for line in lines[6:]:
            if line == "EOF\n": 
                break
            _, x, y = line.split()
            positions.append((float(x), float(y)))
    
    return positions
    
    
def distance(p1, p2) -> float:
    ''' Calcula a distância euclidiana entre dois pontos
    '''
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

def buildGraph(positions: list[tuple[float, float]]):
    ''' Constrói um grafo completo com os vértices nas posições dadas
    '''
    G = nx.Graph()
    for i in range(len(positions)):
        for j in range(i+1, len(positions)):
            G.add_edge(i, j, weight=distance(positions[i], positions[j]))
    return G
    
def plotGraph(G : nx.Graph, axis : plt.Axes, title=""):
    ''' Plota um grafo G em um eixo axis
    '''
    pos=nx.spring_layout(G, seed=7)
    axis.set_title(title)
    nx.draw_networkx_nodes(G, pos, node_size=400, ax=axis)
    nx.draw_networkx_edges(G, pos, width=1, ax=axis)
    nx.draw_networkx_labels(G, pos, font_size=12, font_family="sans-serif", ax=axis)
    
    weightLabels = nx.get_edge_attributes(G, 'weight')
    weightLabels = {k: round(v, limDigits) for k, v in weightLabels.items()}
    nx.draw_networkx_edge_labels(G, pos, weightLabels, ax=axis)
    
    
def twiceAroundTree(G : nx.Graph, start: int, toPlot=False):
    ''' Algoritmo Twice-Around-The-Tree 2-aproximado
    '''
    T = nx.minimum_spanning_tree(G)

    if toPlot:
        fig, axs = plt.subplots(1, 3, figsize=(15, 5))
        subax1, subax2, subax3 = axs
        plotGraph(G, subax1, "Original Graph")
        plotGraph(T, subax2, "Minimum Spanning Tree")
    
    
    # Caminhamento pre-ordem em T
    walk = list(nx.dfs_preorder_nodes(T, start))
    
    # Adiciona o nó inicial ao final do caminho => ciclo hamiltoniano
    walk.append(start)
    
    # Calcula o custo do ciclo hamiltoniano
    cost = 0
    for i in range(len(walk)-1):
        cost += G[walk[i]][walk[i+1]]['weight']
        
    # Seja H o grafo induzido pelo ciclo hamiltoniano
    H = nx.Graph()
    for i in range(len(walk)-1):
        H.add_edge(walk[i], walk[i+1], weight=G[walk[i]][walk[i+1]]['weight'])
    
    # Plota o ciclo hamiltoniano
    if toPlot:
        plotGraph(H, subax3, "Hamiltonian Cycle")
        plt.show()
    
    return H, cost

def christofides(G : nx.Graph, start: int, toPlot=False):
    ''' Algoritmo de Christofides 1.5-aproximado
    '''
    # MST de G
    T = nx.minimum_spanning_tree(G)
    
    # Subgrafo de G induzido pelas arestas de grau ímpar em T
    degrees = dict(nx.degree(T))
    nodes = [node for node in degrees if degrees[node] % 2 == 1]
    
    I = nx.Graph(nx.subgraph(G, nodes))
    
    if toPlot:
        fig, axs = plt.subplots(1, 4, figsize=(25, 10))
        subax1, subax2, subax3, subax4 = axs
        plotGraph(G, subax1, "Original Graph")
        plotGraph(T, subax2, "Minimum Spanning Tree")
        plotGraph(I, subax3, "Subgraph of odd degree vertices")
    
    # Emparelhamento perfeito de peso mínimo em I
    M = nx.min_weight_matching(I)
    
    # Circuito euleriano em H = T + M
    H = nx.MultiGraph(T)
    H.add_edges_from(M)
    
    euler_walk = list(nx.eulerian_circuit(H, source=start))
    
    # Transforma o circuito euleriano em um ciclo hamiltoniano
    hamiltonian_walk = [start]
    visited = [False for _ in range(G.number_of_nodes())]
    for u, v in euler_walk:
        if not visited[v]:
            hamiltonian_walk.append(v)
            visited[v] = True
            
    # Seja C o grafo induzido pelo ciclo hamiltoniano
    C = nx.Graph()
    for i in range(len(hamiltonian_walk)-1):
        C.add_edge(hamiltonian_walk[i], hamiltonian_walk[i+1], weight=G[hamiltonian_walk[i]][hamiltonian_walk[i+1]]['weight'])        
    
    # Calcula o custo do ciclo hamiltoniano
    cost = 0
    for i in range(len(hamiltonian_walk)-1):
        cost += G[hamiltonian_walk[i]][hamiltonian_walk[i+1]]['weight']

    # Plota o ciclo hamiltoniano
    if toPlot:
        plotGraph(C, subax4, "Hamiltonian Cycle")
        plt.show()
    
    return C, cost
    
def getExampleGraph():
    ''' Retorna o grafo usado nos slides da aula
    '''
    G = nx.Graph()
    G.add_edge(0, 1, weight=4)
    G.add_edge(0, 2, weight=8)
    G.add_edge(0, 3, weight=9)
    G.add_edge(0, 4, weight=12)
    G.add_edge(1, 2, weight=6)
    G.add_edge(1, 3, weight=8)
    G.add_edge(1, 4, weight=9)
    G.add_edge(2, 3, weight=10)
    G.add_edge(2, 4, weight=11)
    G.add_edge(3, 4, weight=7)
    return G    

def main():
    # G = buildGraph(readInputFile("input/berlin52.tsp"))
    G = getExampleGraph()
    C, cost = twiceAroundTree(G, 0, False)
    print(f"Custo TwiceAroundTree: {cost}")
    C, cost = christofides(G, 0, False)
    print(f"Custo Christofides: {cost}")
    
    
main()

'''
TODO: Branch and Bound
TODO: Pegar estatísticas

'''
