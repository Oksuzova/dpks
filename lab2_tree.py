"""ЛР2, варіант 16: кластер №16, деревоподібна (двійкове дерево) міжкластерна топологія.

Кластер №16 (6 вузлів, 5 зв'язків): листки 0, 1 — центр 2 — центр 3 — листки 4, 5.
Верхні листки 0, 1 — «вхід» від батька, нижні листки 4, 5 — «виходи» до дітей.
Кластери нумеруються як у двійковій купі: корінь 0, діти кластера p — l = 2p+1 та r = 2p+2.
Глобальний номер вузла = 6a + b.

Регулярні зв'язки (кожна дитина з'єднана з ОБОМА нижніми листками батька, «перехресно»):
    (p, 4) -> (l, 0),   (p, 5) -> (l, 1)      лівий нащадок
    (p, 4) -> (r, 1),   (p, 5) -> (r, 0)      правий нащадок
Нерегулярні зв'язки:
  1) кільце в межах кожного рівня дерева, починаючи з 1-го:
    (a, 1) -> (наступний кластер того ж рівня, 0); останній кластер рівня замикається на перший
  2) зв'язки між листовими кластерами (їхні нижні листки 4, 5 інакше простоюють).
     Листові кластери нумеруються зліва направо: i = 0 .. Lf-1, h = Lf // 2, q = Lf // 4:
    (лист i, 4) -> (лист (i+h) mod Lf, 5)     — «через корінь», у протилежне піддерево
    (лист i, 5) -> (лист (i+q) mod Lf, 4)     — у сусіднє піддерево
Ступінь топології S = 3 — такий самий, як у кластера.
"""
import common as c
from draw import draw_topology, scaling_plots, RESULTS

CL = c.CLUSTER_16
LEVELS = [2, 3, 4, 5, 6, 7]       # рівнів дерева; кластерів n = 2^L - 1 (N = 6n, до 762)


def n_clusters(levels):
    return 2 ** levels - 1


def regular_edges(levels=None, n=None):
    """Зв'язки для повного дерева з levels рівнів або для довільних n кластерів (неповне дерево)."""
    n = n if n is not None else n_clusters(levels)
    e = []
    for p in range(n):
        left, right = 2 * p + 1, 2 * p + 2
        if left < n:
            e += [(CL.node(p, 4), CL.node(left, 0)), (CL.node(p, 5), CL.node(left, 1))]
        if right < n:
            e += [(CL.node(p, 4), CL.node(right, 1)), (CL.node(p, 5), CL.node(right, 0))]
    return e


def irregular_edges(levels=None, n=None):
    n = n if n is not None else n_clusters(levels)
    e = []
    for lvl in range(1, n.bit_length()):
        level = list(range(2 ** lvl - 1, min(2 ** (lvl + 1) - 1, n)))
        pairs = list(zip(level, level[1:]))
        if len(level) > 2:
            pairs.append((level[-1], level[0]))
        e += [(CL.node(a, 1), CL.node(b, 0)) for a, b in pairs]
    e += leaf_edges(n)
    return e


def leaf_edges(n):
    leaves = [a for a in range(n) if 2 * a + 1 >= n]
    lf = len(leaves)
    e = []
    for step, (u, v) in ((lf // 2, (4, 5)), (lf // 4, (5, 4))):
        if step < 1 or step % lf == 0:
            continue
        e += [(CL.node(leaves[i], u), CL.node(leaves[(i + step) % lf], v)) for i in range(lf)]
    return e


def positions(levels):
    pos = {}
    width = 2 ** (levels - 1) * 4.5
    for a in range(n_clusters(levels)):
        lvl = (a + 1).bit_length() - 1
        idx = a - (2 ** lvl - 1)
        step = width / 2 ** lvl
        x0 = step * idx + step / 2 - 1
        for v, (x, y) in CL.pos.items():
            pos[CL.node(a, v)] = (x0 + x, y - 5.5 * lvl)
    return pos


def main():
    draw_topology(CL, 1, [], [], CL.pos, 'Кластер №16: нумерація вузлів', 'lab2_cluster.png', figsize=(2.5, 3.5))
    draw_topology(CL, 7, regular_edges(3), [], positions(3),
                  'ЛР2: дерево з 3 рівнів (7 кластерів), регулярні зв’язки', 'lab2_regular_L3.png', figsize=(12, 9))
    draw_topology(CL, 7, regular_edges(3), irregular_edges(3), positions(3),
                  'ЛР2: дерево з 3 рівнів + кільця по рівнях + зв’язки між листками', 'lab2_modified_L3.png', figsize=(12, 9), rad=0.15)

    reg_rows, mod_rows = [], []
    for levels in LEVELS:
        n = n_clusters(levels)
        reg = c.metrics(c.build_topology(CL, n, regular_edges(levels)))
        mod = c.metrics(c.build_topology(CL, n, regular_edges(levels) + irregular_edges(levels)))
        reg_rows.append({'L': levels, 'n': n, **reg})
        mod_rows.append({'L': levels, 'n': n, **mod})

    c.print_table(reg_rows, 'Дерево, лише регулярні зв’язки')
    c.print_table(mod_rows, 'Дерево + нерегулярні зв’язки')
    c.save_csv(reg_rows, f'{RESULTS}/lab2_regular.csv')
    c.save_csv(mod_rows, f'{RESULTS}/lab2_modified.csv')
    scaling_plots({'регулярна': reg_rows, 'модифікована': mod_rows}, 'lab2', 'ЛР2 дерево')
    return reg_rows, mod_rows


if __name__ == '__main__':
    main()
