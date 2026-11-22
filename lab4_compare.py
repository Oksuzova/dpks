"""ЛР4: порівняльний аналіз топологій ЛР1-3 за методикою кафедри.

Топології (модифіковані, з нерегулярними зв'язками):
    1 — лінійка на кластері №6 (ЛР1)
    2 — дерево на кластері №16 (ЛР2)
    3 — решітка-тор на кластері №26 (ЛР3)

Порядок:
1. Щільні серії масштабування (N ≈ 28 … 1008) для кожної топології.
2. П'ять графіків D, D_ave, S, C, T від N, на кожному — 3 криві.
3. Діапазон N ділиться на зони за точками перетину кривих.
4. У кожній зоні — середні значення характеристик, нормалізація
   (мінімальне серед трьох топологій = 1, інші — відношення до нього;
   якщо T < 1, використовується 2 − T) та інтегральна оцінка — сума
   нормалізованих значень (оптимум = 5).
5. Гістограма інтегральних оцінок по зонах.
"""
import os

import matplotlib.pyplot as plt
import numpy as np

import common as c
import draw
import lab1_linear as l1
import lab2_tree as l2
import lab3_grid as l3
from draw import RESULTS

KEYS = ['D', 'D_ave', 'S', 'C', 'T']
LABELS = {'D': 'D', 'D_ave': 'D̄', 'S': 'S', 'C': 'C', 'T': 'T'}
TITLES = {'D': 'Діаметр D', 'D_ave': 'Середній діаметр D̄', 'S': 'Ступінь S',
          'C': 'Вартість C (кількість зв’язків)', 'T': 'Топологічний трафік T'}

# Розміри підібрані так, щоб N у трьох топологій були близькими (від ~28 до ~1008)
LINE_SIZES = [4, 6, 8, 11, 16, 22, 30, 40, 45, 55, 60, 72, 90, 110, 130, 144]
TREE_SIZES = [5, 7, 9, 13, 19, 26, 35, 47, 55, 64, 75, 84, 105, 128, 152, 168]
GRID_SIZES = [(2, 2), (2, 3), (3, 3), (3, 4), (4, 4), (4, 5), (5, 5), (5, 6), (6, 6), (6, 7), (7, 7), (7, 8),
              (8, 8), (9, 9), (10, 10), (11, 11), (12, 12)]

# Межі зон — за точками перетину кривих D_ave (див. графік):
# решітка сходиться з лінійкою при N ≈ 250, дерево перетинає решітку при N ≈ 450
ZONES = [(1, 250), (251, 450), (451, 1010)]


def series():
    return {
        'Лінійка (ЛР1)': [c.metrics(c.build_topology(l1.CL, n, l1.regular_edges(n) + l1.irregular_edges(n)))
                          for n in LINE_SIZES],
        'Дерево (ЛР2)': [c.metrics(c.build_topology(l2.CL, n, l2.regular_edges(n=n) + l2.irregular_edges(n=n)))
                         for n in TREE_SIZES],
        'Решітка (ЛР3)': [c.metrics(c.build_topology(l3.CL, r * k, l3.inter_cluster_edges(r, k, l3.REGULAR)
                                                     + l3.all_irregular(r, k)))
                          for r, k in GRID_SIZES],
    }


def plot_metric(data, key, filename):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for name, rows in data.items():
        ax.plot([r['N'] for r in rows], [r[key] for r in rows], marker='o', markersize=4, label=name)
    for lo, hi in ZONES[1:]:
        ax.axvline(lo, color='gray', linestyle=':', linewidth=1)
    if key == 'T':
        ax.axhline(1, color='gray', linestyle='--', linewidth=1, label='T = 1 (оптимум)')
    ax.set_xlabel('N, кількість процесорів')
    ax.set_ylabel(LABELS[key])
    ax.set_title(f'Залежність {LABELS[key]} від N')
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, filename), dpi=150)
    draw._show(fig)


def zone_tables(data):
    """Середні значення, нормалізовані значення та інтегральна оцінка для кожної зони."""
    result = []
    for lo, hi in ZONES:
        avg = {}
        for name, rows in data.items():
            in_zone = [r for r in rows if lo <= r['N'] <= hi]
            avg[name] = {k: float(np.mean([r[k] for r in in_zone])) for k in KEYS}
            avg[name]['points'] = len(in_zone)
        # трафік: якщо T < 1, використовуємо 2 - T (відхилення від оптимуму 1)
        t_eff = {name: (2 - a['T'] if a['T'] < 1 else a['T']) for name, a in avg.items()}
        norm = {}
        for name, a in avg.items():
            norm[name] = {k: a[k] / min(b[k] for b in avg.values()) for k in KEYS if k != 'T'}
            norm[name]['T'] = t_eff[name] / min(t_eff.values())
            norm[name]['sum'] = sum(norm[name][k] for k in KEYS)
        result.append({'zone': (lo, hi), 'avg': avg, 'norm': norm})
    return result


def print_zones(zones):
    for z in zones:
        lo, hi = z['zone']
        print(f'\nЗона {lo} – {hi}')
        rows = [{'топологія': name, 'точок': a['points'], **{LABELS[k]: round(a[k], 3) for k in KEYS}}
                for name, a in z['avg'].items()]
        c.print_table(rows, 'Середні значення')
        rows = [{'топологія': name, **{LABELS[k]: round(n[k], 3) for k in KEYS}, 'Σ': round(n['sum'], 3)}
                for name, n in z['norm'].items()]
        c.print_table(rows, 'Нормалізовані значення')


def histogram(zones, filename):
    names = list(zones[0]['norm'].keys())
    x = np.arange(len(names))
    width = 0.26
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for i, z in enumerate(zones):
        lo, hi = z['zone']
        vals = [z['norm'][n]['sum'] for n in names]
        bars = ax.bar(x + (i - 1) * width, vals, width, label=f'Зона {i + 1} ({lo}–{min(hi, 1008)})')
        ax.bar_label(bars, fmt='%.2f', fontsize=7)
    ax.axhline(5, color='gray', linestyle='--', linewidth=1, label='оптимум = 5')
    ax.set_xticks(x, names)
    ax.set_ylabel('Інтегральна оцінка Σ')
    ax.set_ylim(4, max(z['norm'][n]['sum'] for z in zones for n in names) + 0.4)
    ax.set_title('Порівняння сум нормалізованих результатів')
    ax.grid(alpha=0.3, axis='y')
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, filename), dpi=150)
    draw._show(fig)


def main():
    data = series()
    for name, rows in data.items():
        c.print_table(rows, name)
        c.save_csv(rows, f'{RESULTS}/lab4_series_{name.split()[0]}.csv')
    for key in KEYS:
        plot_metric(data, key, f'lab4_{key}.png')
    zones = zone_tables(data)
    print_zones(zones)
    histogram(zones, 'lab4_integral.png')
    return data, zones


if __name__ == '__main__':
    main()
