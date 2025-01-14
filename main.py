import networkx as nx
import matplotlib.pyplot as plt
import heapq
import time
from timeout_decorator import timeout, TimeoutError
import tracemalloc

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

def BNB_TSP(graph, timeout=1800):
    '''Função para o algoritmo Branch and Bound Completo'''

    class Node:
        '''Nó para a árvore do bnb'''

        def __init__(self, level, path, cost, bound):
            self.level = level
            self.path = path
            self.cost = cost
            self.bound = bound

        def __lt__(self, other):
            return  self.level > other.level or (self.level == other.level and self.bound < other.bound)


    class BranchAndBoundTree:
        '''Árvore do algoritmo BNB'''

        def __init__(self, graph, timeout):
            self.graph = graph
            self.timeout = timeout
            self.n = graph.number_of_nodes()
            self.best_cost = float('inf')
            self.best_path = []

        def calculate_bound(self, node):
            bound = node.cost

            for i in range(self.n):
                if i not in node.path:
                    min_cost = float('inf')
                    for j in range(self.n):
                        if i != j and j not in node.path:
                            if self.graph.has_edge(i, j):
                                min_cost = min(min_cost, self.graph[i][j]['weight'])
                    if min_cost < float('inf'):
                        bound += min_cost

            return bound

        @timeout(1800)
        def branch_and_bound(self):
            '''Função que executa o Branch and Bound'''

            start_time = time.time() # início da coleta de uso de tempo 
            tracemalloc.start()  # Início da coleta de uso da memória

            pq = []  # Fila de Prioridades

            root = Node(0, [0], 0, 0)
            root.bound = self.calculate_bound(root)
            heapq.heappush(pq, root)

            while pq:

                node = heapq.heappop(pq)

                if node.bound < self.best_cost:
                    for i in range(self.n):
                        if i not in node.path:
                            if self.graph.has_edge(node.path[-1], i):
                                new_cost = node.cost + self.graph[node.path[-1]][i]['weight']
                                new_path = node.path + [i]

                                if len(new_path) == self.n:
                                    total_cost = new_cost + self.graph[new_path[-1]][0]['weight']
                                    if total_cost < self.best_cost:
                                        self.best_cost = total_cost
                                        self.best_path = new_path
                                else:
                                    child_node = Node(node.level + 1, new_path, new_cost, 0)
                                    child_node.bound = self.calculate_bound(child_node)

                                    if child_node.bound < self.best_cost:
                                        heapq.heappush(pq, child_node)
            
            current_memory, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            end_time = time.time()
            elapsed_time = end_time - start_time
            return self.best_cost, self.best_path, elapsed_time, current_memory, peak_memory
        
    bnb = BranchAndBoundTree(graph, timeout)
    min_cost, optimal_path, elapsed_time, current_memory, peak_memory = bnb.branch_and_bound()
    return min_cost, optimal_path, elapsed_time, current_memory, peak_memory    

@timeout(1800)
def twiceAroundTree(G : nx.Graph, start: int, toPlot=False):
    ''' Algoritmo Twice-Around-The-Tree 2-aproximado
    '''
    start_time = time.time() # início da coleta de uso de tempo 
    tracemalloc.start()  # Início da coleta de uso da memória

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
    
    current_memory, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    end_time = time.time()
    elapsed_time = end_time - start_time
    return H, cost, elapsed_time, current_memory, peak_memory

@timeout(1800)
def christofides(G : nx.Graph, start: int, toPlot=False):
    ''' Algoritmo de Christofides 1.5-aproximado
    '''
    start_time = time.time() # início da coleta de uso de tempo 
    tracemalloc.start()  # Início da coleta de uso da memória

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
    
    current_memory, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    end_time = time.time()
    elapsed_time = end_time - start_time
    return C, cost, elapsed_time, current_memory, peak_memory
    
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

'''Instâncias para o TSP e seus respectivos valores ótimos'''
data = [
("eil51", 426), 
("berlin52", 7542), 
("st70", 675), 
("eil76", 538), 
("pr76", 108159), 
("rat99", 1211), 
("kroA100", 21282), 
("kroB100", 22141), 
("kroC100", 20749), 
("kroD100", 21294), 
("kroE100", 22068), 
("rd100", 7910), 
("eil101", 629), 
("lin105", 14379), 
("pr107", 44303), 
("pr124", 59030), 
("bier127", 118282), 
("ch130", 6110), 
("pr136", 96772), 
("pr144", 58537), 
("ch150", 6528), 
("kroA150", 26524), 
("kroB150", 26130), 
("pr152", 73682), 
("u159", 42080), 
("rat195", 2323), 
("d198", 15780), 
("kroA200", 29368), 
("kroB200", 29437), 
("ts225", 126643), 
("tsp225", 3919), 
("pr226", 80369), 
("gil262", 2378), 
("pr264", 49135), 
("a280", 2579), 
("pr299", 48191), 
("lin318", 42029),  
("rd400", 15281), 
("fl417", 11861), 
("pr439", 107217), 
("pcb442", 50778), 
("d493", 35002), 
("u574", 36905), 
("rat575", 6773), 
("p654", 34643), 
("d657", 48912), 
("u724", 41910), 
("rat783", 8806), 
("pr1002", 259045), 
("u1060", 224094), 
("vm1084", 239297), 
("pcb1173", 56892), 
("d1291", 50801), 
("rl1304", 252948), 
("rl1323", 270199), 
("nrw1379", 56638), 
("fl1400", 20127), 
("u1432", 152970), 
("fl1577", 22249), 
("d1655", 62128), 
("vm1748", 336556), 
("u1817", 57201), 
("rl1889", 316536), 
("d2103", 80450), 
("u2152", 64253), 
("u2319", 234256),
("pr2392", 378032), 
("pcb3038", 137694),  
("fl3795", 28772), 
("fnl4461", 182566), 
("rl5915", 565530), 
("rl5934", 556045), 
("rl11849", 923368), 
("usa13509", 19982889),
("brd14051", 469445), 
("d15112", 1573152), 
("d18512", 645488)
]

def main():

    # Executa os 3 algoritmos para todas as instâncias do TSP
    for tsp_file, optimum in data:

        # Leitura dos dados e construção do grafo
        positions = readInputFile(f"input/{tsp_file}.tsp")
        G = buildGraph(positions)
        
        # Execução da função Twice Around The Tree
        try:
            C, cost, elapsed_time, current_memory, peak_memory = twiceAroundTree(G, 0, False)
            
            # Salvar os resultados em arquivo de saída
            with open(f'output/{tsp_file}_twice.txt', 'w') as f:
                f.write(f"Instancia: {tsp_file}\n")
                f.write(f"Algoritmo: Twice Around The Tree\n")
                f.write(f"Custo Otimo da Instancia: {optimum}\n")
                f.write(f"Custo Encontrado: {cost}\n")
                f.write(f"Tempo Decorrido: {elapsed_time:.2f} segundos\n")
                f.write(f"Memoria Atual: {current_memory / 10**6:.2f} MB\n")
                f.write(f"Memoria de Pico: {peak_memory / 10**6:.2f} MB\n")
                
            print(f"Resultados para {tsp_file} salvos em {f'output/{tsp_file}_twice.txt'}")

        except TimeoutError:
            with open(f'output/{tsp_file}_twice.txt', 'w') as f:
                f.write(f"Instancia: {tsp_file}\n")
                f.write("Timeout, 30 minutos foram alcançados\n")
            
            print(f"Timeout ao processar {tsp_file} com Twice Around The Tree")
        
        # Execução da função Christofides
        try:
            C, cost, elapsed_time, current_memory, peak_memory = christofides(G, 0, False)
            
            # Salvar os resultados em arquivo de saída
            with open(f'output/{tsp_file}_chris.txt', 'w') as f:
                f.write(f"Instancia: {tsp_file}\n")
                f.write(f"Algoritmo: Christofides\n")
                f.write(f"Custo Otimo da Instancia: {optimum}\n")
                f.write(f"Custo Encontrado: {cost}\n")
                f.write(f"Tempo Decorrido: {elapsed_time:.2f} segundos\n")
                f.write(f"Memoria Atual: {current_memory / 10**6:.2f} MB\n")
                f.write(f"Memoria de Pico: {peak_memory / 10**6:.2f} MB\n")
                
            print(f"Resultados para {tsp_file} salvos em {f'output/{tsp_file}_chris.txt'}")

        except TimeoutError:
            with open(f'output/{tsp_file}_chris.txt', 'w') as f:
                f.write(f"Instancia: {tsp_file}\n")
                f.write("Timeout, 30 minutos foram alcançados\n")
            
            print(f"Timeout ao processar {tsp_file} com Christofides")

        # Execução da função Branch and Bound
        try:
            min_cost, optimal_path, elapsed_time, current_memory, peak_memory = BNB_TSP(G)
            
            # Salvar os resultados em arquivo de saída
            with open(f'output/{tsp_file}_bnb.txt', 'w') as f:
                f.write(f"Instância: {tsp_file}\n")
                f.write(f"Algoritmo: Branch and Bound\n")
                f.write(f"Custo Ótimo da Instância: {optimum}\n")
                f.write(f"Custo Encontrado: {min_cost}\n")
                f.write(f"Caminho Encontrado: {optimal_path}\n")
                f.write(f"Tempo Decorrido: {elapsed_time:.2f} segundos\n")
                f.write(f"Memória Atual: {current_memory / 10**6:.2f} MB\n")
                f.write(f"Memória de Pico: {peak_memory / 10**6:.2f} MB\n")
                
            print(f"Resultados para {tsp_file} salvos em {f'output/{tsp_file}_bnb.txt'}")

        except TimeoutError:
            with open(f'output/{tsp_file}_bnb.txt', 'w') as f:
                f.write(f"Instancia: {tsp_file}\n")
                f.write("Timeout, 30 minutos foram alcançados\n")
            
            print(f"Timeout ao processar {tsp_file} com Branch and Bound")

def main():
    G = buildGraph(readInputFile("input/berlin52.tsp"))
    # G = getExampleGraph()
    C, cost, elapsed_time, current_memory, peak_memory = twiceAroundTree(G, 0, False)
    print(f"Custo TwiceAroundTree: {cost}")
    C, cost, elapsed_time, current_memory, peak_memory = christofides(G, 0, False)
    print(f"Custo Christofides: {cost}")
    
    
main()

'''
TODO: Branch and Bound
TODO: Pegar estatísticas

'''
