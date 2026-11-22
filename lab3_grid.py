"""ЛР3, варіант 26: кластер №26, решітчаста (2D) міжкластерна топологія.

Кластер №26 (7 вузлів, 10 зв'язків): трикутник 0-1-2 зверху, зв'язки 1-3 і 2-3,
два трикутники 3-4-5 і 4-5-6 знизу. Власні ступені: 0:2, 1:3, 2:3, 3:4, 4:3, 5:3, 6:2 (S = 4).
Кластер з координатами (row, col) має номер a = row * COLS + col. Глобальний номер вузла = 7a + b.

Регулярні зв'язки (сусіди по решітці):
    праворуч: (a, 2) -> (a+1, 1),   (a, 6) -> (a+1, 5)
    донизу:   (a, 6) -> (a+COLS, 0)
Нерегулярні зв'язки:
  1) діагональ донизу-праворуч: (a, 4) -> (a+COLS+1, 0)
  2) замикання решітки в тор: усі три правила (праворуч, донизу, діагональ) застосовуються
     і для крайніх кластерів, з індексами за модулем: (row, col) -> ((row+dr) mod R, (col+dc) mod C).
     Крайні кластери використовують порти, які в решітці простоювали, тому S не зростає.
Усього кластер має рівно 8 вільних портів до ступеня 4 (0:2, 1:1, 2:1, 4:1, 5:1, 6:2),
і всі вони зайняті цими зв'язками, тому S = 4.
"""
import common as c
from draw import draw_topology, scaling_plots, RESULTS

CL = c.CLUSTER_26
GRIDS = [(2, 2), (3, 3), (4, 4), (6, 6), (8, 8), (10, 10), (12, 12)]   # N = 7*R*C, до 1008

REGULAR = {'right': (0, 1, ((2, 1), (6, 5))), 'bottom': (1, 0, ((6, 0),))}
IRREGULAR = {'diag': (1, 1, ((4, 0),))}


def inter_cluster_edges(rows, cols, direction, wrap=False):
    """wrap=False — лише зв'язки всередині решітки; wrap=True — лише замикаючі (торові) зв'язки."""
    e = []
    for row in range(rows):
        for col in range(cols):
            a = row * cols + col
            for dr, dc, pairs in direction.values():
                inside = row + dr < rows and col + dc < cols
                if inside == wrap:
                    continue
                a_n = ((row + dr) % rows) * cols + (col + dc) % cols
                e += [(CL.node(a, v_from), CL.node(a_n, v_to)) for v_from, v_to in pairs]
    return e


def all_irregular(rows, cols):
    """Діагоналі всередині решітки + замикання всіх напрямків у тор."""
    return (inter_cluster_edges(rows, cols, IRREGULAR)
            + inter_cluster_edges(rows, cols, {**REGULAR, **IRREGULAR}, wrap=True))


def positions(rows, cols):
    return {CL.node(row * cols + col, v): (x + 6.5 * col, y - 7 * row)
            for row in range(rows) for col in range(cols) for v, (x, y) in CL.pos.items()}


def main():
    draw_topology(CL, 1, [], [], CL.pos, 'Кластер №26: нумерація вузлів', 'lab3_cluster.png', figsize=(3, 4))
    draw_topology(CL, 9, inter_cluster_edges(3, 3, REGULAR), [], positions(3, 3),
                  'ЛР3: решітка 3×3 кластери, регулярні зв’язки', 'lab3_regular_3x3.png', figsize=(10, 11))
    draw_topology(CL, 9, inter_cluster_edges(3, 3, REGULAR), all_irregular(3, 3), positions(3, 3),
                  'ЛР3: решітка 3×3 + діагоналі + замикання в тор', 'lab3_modified_3x3.png', figsize=(10, 11), rad=0.1)

    reg_rows, mod_rows = [], []
    for rows, cols in GRIDS:
        n = rows * cols
        reg_e = inter_cluster_edges(rows, cols, REGULAR)
        irr_e = all_irregular(rows, cols)
        reg = c.metrics(c.build_topology(CL, n, reg_e))
        mod = c.metrics(c.build_topology(CL, n, reg_e + irr_e))
        reg_rows.append({'grid': f'{rows}x{cols}', 'n': n, **reg})
        mod_rows.append({'grid': f'{rows}x{cols}', 'n': n, **mod})

    c.print_table(reg_rows, 'Решітка, лише регулярні зв’язки')
    c.print_table(mod_rows, 'Решітка + діагоналі + тор')
    c.save_csv(reg_rows, f'{RESULTS}/lab3_regular.csv')
    c.save_csv(mod_rows, f'{RESULTS}/lab3_modified.csv')
    scaling_plots({'регулярна': reg_rows, 'модифікована': mod_rows}, 'lab3', 'ЛР3 решітка')
    return reg_rows, mod_rows


if __name__ == '__main__':
    main()
