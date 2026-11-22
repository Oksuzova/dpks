"""Спільні функції для ЛР1-4: кластери з варіантів, метрики, таблиці."""
import csv
from collections import deque
from dataclasses import dataclass

import networkx as nx
from networkx.classes import Graph


@dataclass(frozen=True)
class Cluster:
    number: int        # номер кластера з таблиці варіантів
    size: int          # кількість вузлів
    edges: tuple       # внутрішні зв'язки
    pos: dict          # координати для малювання

    def node(self, a: int, b: int) -> int:
        """Вузол (a, b): a — номер кластера в топології, b — номер вузла в кластері."""
        return self.size * a + b

    def graph(self) -> Graph:
        g = nx.Graph()
        g.add_nodes_from(range(self.size))
        g.add_edges_from(self.edges)
        return g


# Кластер №6 (ЛР1): верхній ряд 0-1-2, нижній ряд 3-4-5-6, зигзаг між рядами
CLUSTER_6 = Cluster(
    number=6, size=7,
    edges=((0, 1), (1, 2), (3, 4), (4, 5), (5, 6), (3, 0), (0, 4), (4, 1), (1, 5), (5, 2), (2, 6)),
    pos={0: (1, 1.6), 1: (3, 1.6), 2: (5, 1.6), 3: (0, 0), 4: (2, 0), 5: (4, 0), 6: (6, 0)},
)

# Кластер №16 (ЛР2): два «Y»: листки 0, 1 — центр 2 — центр 3 — листки 4, 5
CLUSTER_16 = Cluster(
    number=16, size=6,
    edges=((0, 2), (1, 2), (2, 3), (3, 4), (3, 5)),
    pos={0: (0, 3), 1: (2, 3), 2: (1, 2), 3: (1, 1), 4: (0, 0), 5: (2, 0)},
)

# Кластер №26 (ЛР3): трикутник 0-1-2 зверху, зв'язки 1-3 і 2-3, два трикутники 3-4-5 і 4-5-6 знизу
CLUSTER_26 = Cluster(
    number=26, size=7,
    edges=((0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5), (4, 6), (5, 6)),
    pos={0: (2.5, 4.5), 1: (0.5, 3.5), 2: (2.5, 2.8), 3: (0.3, 1.8), 4: (2.7, 1.8), 5: (1, 0), 6: (3.4, 0)},
)


def build_topology(cl: Cluster, n_clusters: int, inter_edges) -> Graph:
    g = nx.Graph()
    g.add_nodes_from(range(cl.size * n_clusters))
    g.add_edges_from(intra_cluster_edges(cl, n_clusters))
    g.add_edges_from(inter_edges)
    return g


def intra_cluster_edges(cl: Cluster, n_clusters: int):
    return [(cl.node(a, u), cl.node(a, v)) for a in range(n_clusters) for u, v in cl.edges]


# ---------- метрики ----------

def bfs(graph: Graph, node: int) -> dict:
    queue = deque([node])
    dist = {node: 0}
    while queue:
        cur = queue.popleft()
        for n in graph.neighbors(cur):
            if n not in dist:
                dist[n] = dist[cur] + 1
                queue.append(n)
    return dist


def adj_matrix(graph: Graph):
    size = len(graph)
    m = []
    for i in range(size):
        neis = set(graph.neighbors(i))
        m.append([1 if j in neis else 0 for j in range(size)])
    return m


def dist_matrix(graph: Graph):
    size = len(graph)
    m = []
    for n in range(size):
        d = bfs(graph, n)
        if len(d) != size:
            raise ValueError('Граф незв’язний')
        m.append([d[i] for i in range(size)])
    return m


def D(dm):
    return max(max(row) for row in dm)


def d_ave(dm):
    n = len(dm)
    return sum(sum(row) for row in dm) / (n * (n - 1))


def S(am):
    return max(sum(row) for row in am)


def E(am):
    return sum(sum(row) for row in am) // 2


def metrics(graph: Graph) -> dict:
    am, dm = adj_matrix(graph), dist_matrix(graph)
    n, s, d, da, e = len(graph), S(am), D(dm), d_ave(dm), E(am)
    return {
        'N': n, 'D': d, 'D_ave': round(da, 3), 'S': s,
        'C': e,                     # вартість = кількість зв'язків
        'C_NDS': n * d * s,         # вартість C = N*D*S
        'T': round(2 * da / s, 3),  # T = 2*D_ave/S
    }


def print_table(rows, title=''):
    if title:
        print(f'\n{title}')
    keys = list(rows[0].keys())
    widths = [max(len(str(k)), *(len(str(r[k])) for r in rows)) for k in keys]
    print(' | '.join(str(k).rjust(w) for k, w in zip(keys, widths)))
    print('-+-'.join('-' * w for w in widths))
    for r in rows:
        print(' | '.join(str(r[k]).rjust(w) for k, w in zip(keys, widths)))


def save_csv(rows, path):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
