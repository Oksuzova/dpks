"""Експеримент: порівняння власних топологій ЛР1-3 з декартовим добутком «кластер × міжкластерна топологія».

Декартовий добуток G × H: на місце кожної вершини графа H ставиться копія кластера G,
і КОЖЕН вузол v кластера a з'єднується з тим самим вузлом v у кожному кластері,
сусідньому з a у графі H. Властивості: S = S_G + S_H, D = D_G + D_H.

Варіанти, що порівнюються:
    1. Строгий добуток — з'єднуються всі вузли кластера (0-0, 1-1, ..., v-v).
    2. Добуток на вільних портах — з'єднуються лише вузли, власний ступінь яких
       менший за ступінь кластера (ті самі вузли, що використано у власній топології).
    3. Власна топологія (з регулярними та нерегулярними зв'язками), де кожен напрямок
       обслуговує окремий вузол кластера, тому ступінь не зростає.
"""
import os

import matplotlib.pyplot as plt

import common as c
import draw
import lab1_linear as l1
import lab2_tree as l2
import lab3_grid as l3
from draw import RESULTS


# ---------- міжкластерні графи H ----------

def path_h(n):
    return [(a, a + 1) for a in range(n - 1)]


def tree_h(n):
    return [(p, ch) for p in range(n) for ch in (2 * p + 1, 2 * p + 2) if ch < n]


def grid_h(r, k, torus=False):
    e = []
    for row in range(r):
        for col in range(k):
            a = row * k + col
            if col + 1 < k or torus:
                e.append((a, row * k + (col + 1) % k))
            if row + 1 < r or torus:
                e.append((a, ((row + 1) % r) * k + col))
    return list({tuple(sorted(x)) for x in e})


# ---------- добуток ----------

def free_nodes(cl):
    g = cl.graph()
    s = max(d for _, d in g.degree())
    return [v for v, d in g.degree() if d < s]


def product_edges(cl, h_edges, nodes=None):
    nodes = range(cl.size) if nodes is None else nodes
    return [(cl.node(a, v), cl.node(b, v)) for a, b in h_edges for v in nodes]


def product_graph(cl, n, h_edges, nodes=None):
    return c.build_topology(cl, n, product_edges(cl, h_edges, nodes))


# ---------- експерименти ----------

def experiment(cl, configs, own_builder, label_key):
    """configs: список (мітка, n, h_edges, параметр для own_builder)."""
    rows = []
    free = free_nodes(cl)
    for label, n, h_edges, own_param in configs:
        variants = {
            'строгий добуток': product_graph(cl, n, h_edges),
            'добуток на вільних портах': product_graph(cl, n, h_edges, free),
            'власна топологія': own_builder(own_param),
        }
        for name, g in variants.items():
            rows.append({label_key: label, 'варіант': name, **c.metrics(g)})
    return rows


def lab1():
    cl = l1.CL
    sizes = [4, 16, 64, 143]
    configs = [(n, n, path_h(n), n) for n in sizes]
    own = lambda n: c.build_topology(cl, n, l1.regular_edges(n) + l1.irregular_edges(n))
    return experiment(cl, configs, own, 'n')


def lab2():
    cl = l2.CL
    levels = [3, 5, 7]
    configs = [(L, l2.n_clusters(L), tree_h(l2.n_clusters(L)), L) for L in levels]
    own = lambda L: c.build_topology(cl, l2.n_clusters(L), l2.regular_edges(L) + l2.irregular_edges(L))
    return experiment(cl, configs, own, 'L')


def lab3():
    cl = l3.CL
    sides = [3, 6, 12]
    configs = [(f'{r}x{r}', r * r, grid_h(r, r, torus=True), r) for r in sides]
    own = lambda r: c.build_topology(cl, r * r, l3.inter_cluster_edges(r, r, l3.REGULAR) + l3.all_irregular(r, r))
    return experiment(cl, configs, own, 'grid')


def draw_product(cl, n, h_edges, h_pos, title, filename, g_pos=None, figsize=(8, 9.5), labels=None):
    """Малює строгий добуток «кластер × H».

    Положення вузла (a, v) = h_pos[a] + g_pos[v]: копії кластера стоять у вершинах графа H,
    а H розміщено так, щоб зв'язки між однойменними вузлами (сині) не накладалися
    на зв'язки всередині кластерів (сірі) і не проходили через інші вузли.
    """
    g_pos = g_pos or cl.pos
    pos = {cl.node(a, v): (h_pos[a][0] + x, h_pos[a][1] + y) for a in range(n) for v, (x, y) in g_pos.items()}
    fig, ax = plt.subplots(figsize=figsize)
    for u, v in product_edges(cl, h_edges):
        ax.plot(*zip(pos[u], pos[v]), color='#1f6fd1', lw=1.6, zorder=1)
    for u, v in c.intra_cluster_edges(cl, n):
        ax.plot(*zip(pos[u], pos[v]), color='#777777', lw=1.8, zorder=2)
    for k, (x, y) in pos.items():
        ax.scatter(x, y, s=400, c='white', edgecolors='black', zorder=3)
        ax.text(x, y, str(k), ha='center', va='center', fontsize=8, zorder=4)
    for a, (x, y, text) in (labels or {}).items():
        ax.text(x, y, text, fontsize=10, color='#777777', ha='center', va='center')
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title + '\nсірі — зв’язки всередині кластерів, сині — кожен вузол b з’єднаний з вузлом b сусіднього кластера',
                 fontsize=11, pad=22)
    path = os.path.join(RESULTS, filename)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    draw._show(fig)
    return path


# Кластер №16, «покладений на бік»: листки 0, 1 ліворуч, центри 2, 3, листки 4, 5 праворуч
CLUSTER_16_SIDEWAYS = {0: (0, 0.7), 1: (0, -0.7), 2: (1.1, 0.25), 3: (2.2, -0.25), 4: (3.3, 0.7), 5: (3.3, -0.7)}


def pictures():
    # ЛР1: копії кластера зсунуті вгору-праворуч
    n = 4
    h1 = {a: (0.7 * a, 2.7 * a) for a in range(n)}
    draw_product(l1.CL, n, path_h(n), h1, 'Строгий декартовий добуток: кластер №6 × лінійка з 4 вершин', 'cart_lab1.png',
                 labels={a: (h1[a][0] + 7.1, h1[a][1] + 0.2, f'кластер {a}') for a in range(n)})

    # ЛР2: дерево кластерів, кластер «на боці», рівні дерева зсунуті по горизонталі
    n = 7
    h2 = {}
    for a in range(n):
        lvl = (a + 1).bit_length() - 1
        idx = a - (2 ** lvl - 1)
        width = 20
        h2[a] = (width / 2 ** lvl * (idx + 0.5) + 1.2 * lvl, -4.2 * lvl)
    draw_product(l2.CL, n, tree_h(n), h2, 'Строгий декартовий добуток: кластер №16 × двійкове дерево з 7 вершин',
                 'cart_lab2.png', g_pos=CLUSTER_16_SIDEWAYS, figsize=(12, 8),
                 labels={a: (h2[a][0] + 1.65, h2[a][1] + 1.25, f'кластер {a}') for a in range(n)})

    # ЛР3: решітка кластерів, «скошена», щоб рядки й стовпці не збігалися з рядами вузлів кластера
    r = 3
    h3 = {row * r + col: (8.0 * col - 3.4 * row, 2.4 * col - 7.6 * row) for row in range(r) for col in range(r)}
    draw_product(l3.CL, r * r, grid_h(r, r), h3, 'Строгий декартовий добуток: кластер №26 × решітка 3×3', 'cart_lab3.png',
                 figsize=(12, 11),
                 labels={a: (h3[a][0] + 1.8, h3[a][1] + 5.3, f'кластер {a}') for a in range(r * r)})


def main():
    pictures()
    results = {}
    for name, fn in (('lab1', lab1), ('lab2', lab2), ('lab3', lab3)):
        rows = fn()
        c.print_table(rows, f'{name}: декартовий добуток vs власна топологія')
        c.save_csv(rows, f'{RESULTS}/cart_{name}.csv')
        results[name] = rows
    return results


if __name__ == '__main__':
    main()
