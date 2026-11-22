"""ЛР1, варіант 6: кластер №6, лінійна міжкластерна топологія.

Кластер №6 (7 вузлів, 11 зв'язків): верхній ряд 0-1-2, нижній ряд 3-4-5-6, зигзаг 3-0-4-1-5-2-6.
Вузол позначаємо (a, b): a — номер кластера зліва направо, b — номер вузла в кластері.
Глобальний номер = 7a + b.

Регулярні зв'язки (сусідні кластери, верхнім рядом):
    (a, 2) -> (a+1, 0)
Нерегулярні зв'язки (два рівні «експрес-ліній» нижнім рядом):
    (a, 6) -> (a+k1, 3),  k1 = max(2, round(sqrt(n)))       — «середній» крок
    (a, 6) -> (a+k2, 3),  k2 = max(k1 + 1, n // 4)          — «далекий» крок
Вузли 3 і 6 мають власний ступінь 2, тож кожен приймає рівно два нерегулярні зв'язки,
а вузли 0 і 2 (ступінь 3) — один регулярний. Ступінь топології S = 4, як у кластера.
"""
import math

import common as c
from draw import draw_topology, scaling_plots, RESULTS

CL = c.CLUSTER_6
SIZES = [2, 4, 8, 16, 32, 64, 100, 143]     # кількість кластерів n (N = 7n, до 1001)
CLUSTER_STEP = 8                            # відстань між кластерами на малюнку


def steps(n):
    k1 = max(2, round(math.sqrt(n)))
    return k1, max(k1 + 1, n // 4)


def regular_edges(n):
    e = []
    for a in range(n - 1):
        e.append((CL.node(a, 2), CL.node(a + 1, 0)))
    return e


def irregular_edges(n):
    e = []
    for k in steps(n):
        e += [(CL.node(a, 6), CL.node(a + k, 3)) for a in range(n - k)]
    return e


def positions(n):
    return {CL.node(a, v): (x + CLUSTER_STEP * a, y) for a in range(n) for v, (x, y) in CL.pos.items()}


def main():
    draw_topology(CL, 1, [], [], CL.pos, 'Кластер №6: нумерація вузлів', 'lab1_cluster.png', figsize=(5, 2.5))
    draw_topology(CL, 4, regular_edges(4), [], positions(4),
                  'ЛР1: лінійка з 4 кластерів, регулярні зв’язки', 'lab1_regular_n4.png', figsize=(12, 3))
    draw_topology(CL, 8, regular_edges(8), irregular_edges(8), positions(8),
                  'ЛР1: лінійка з 8 кластерів + нерегулярні зв’язки (k1 = 3, k2 = 4)', 'lab1_modified_n8.png',
                  figsize=(20, 7), rad=0.3)

    reg_rows, mod_rows = [], []
    for n in SIZES:
        reg = c.metrics(c.build_topology(CL, n, regular_edges(n)))
        mod = c.metrics(c.build_topology(CL, n, regular_edges(n) + irregular_edges(n)))
        reg_rows.append({'n': n, **reg})
        k1, k2 = steps(n)
        mod_rows.append({'n': n, 'k1': k1, 'k2': k2, **mod})

    c.print_table(reg_rows, 'Лінійка, лише регулярні зв’язки')
    c.print_table(mod_rows, 'Лінійка + нерегулярні зв’язки')
    c.save_csv(reg_rows, f'{RESULTS}/lab1_regular.csv')
    c.save_csv(mod_rows, f'{RESULTS}/lab1_modified.csv')
    scaling_plots({'регулярна': reg_rows, 'модифікована': mod_rows}, 'lab1', 'ЛР1 лінійка')
    return reg_rows, mod_rows


if __name__ == '__main__':
    main()
