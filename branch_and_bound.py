import heapq
import networkx as nx
import time
import tracemalloc

class ExecutionTimeoutError(Exception):
    '''Erro lançado caso o programa demore mais que 30min'''
    pass

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

        def branch_and_bound(self):
            '''Função que executa o Branch and Bound'''

            start_time = time.time() # início da coleta de uso de tempo 
            tracemalloc.start()  # Início da coleta de uso da memória

            pq = []  # Fila de Prioridades

            root = Node(0, [0], 0, 0)
            root.bound = self.calculate_bound(root)
            heapq.heappush(pq, root)

            while pq:

                if time.time() - start_time > self.timeout:
                    raise ExecutionTimeoutError("Execução excedeu o tempo limite de 30 minutos.")

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

# Funções fornecidas

def readInputFile(filename: str) -> list[tuple[float, float]]:
    ''' Lê um arquivo de entrada no formato .tsp e retorna uma lista de tuplas (x, y) com as posições dos pontos '''
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
    ''' Calcula a distância euclidiana entre dois pontos '''
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5


def buildGraph(positions: list[tuple[float, float]]):
    ''' Constrói um grafo completo com os vértices nas posições dadas '''
    G = nx.Graph()
    for i in range(len(positions)):
        for j in range(i+1, len(positions)):
            G.add_edge(i, j, weight=distance(positions[i], positions[j]))
    return G

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

# Construir o grafo e resolver o problema
# positions = readInputFile('input/berlin52.tsp')  # Substitua pelo caminho do seu arquivo
# G = buildGraph(positions)
G = getExampleGraph()
try:
    min_cost, optimal_path, elapsed_time, current_memory, peak_memory = BNB_TSP(G)
    print("Custo Mínimo:", min_cost)
    print("Caminho Ótimo:", optimal_path)
    print("Tempo Decorrido:", elapsed_time)
    print(f"Memória Atual: {current_memory / 10**6:.2f} MB")
    print(f"Memória de Pico: {peak_memory / 10**6:.2f} MB")
except ExecutionTimeoutError as e:
    print(e)