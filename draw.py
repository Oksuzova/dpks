"""Малювання топологій: внутрішньокластерні, регулярні та нерегулярні зв'язки різними кольорами."""
import os

import matplotlib.pyplot as plt
import networkx as nx

import common as c

# True — показувати кожен малюнок у вікні (plt.show), як у звичайному запуску з PyCharm.
# Малюнки в будь-якому разі зберігаються в results/.
SHOW = True

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(RESULTS, exist_ok=True)


def draw_topology(cl, n_clusters, regular, irregular, pos, title, filename, figsize=(14, 5), rad=0.25):
    g = c.build_topology(cl, n_clusters, regular + irregular)
    fig, ax = plt.subplots(figsize=figsize)
    nx.draw_networkx_nodes(g, pos, node_size=260, node_color='white', edgecolors='black', ax=ax)
    nx.draw_networkx_labels(g, pos, font_size=7, ax=ax)
    nx.draw_networkx_edges(g, pos, edgelist=c.intra_cluster_edges(cl, n_clusters), edge_color='gray', ax=ax)
    nx.draw_networkx_edges(g, pos, edgelist=regular, edge_color='black', width=1.6, ax=ax)
    if irregular:
        nx.draw_networkx_edges(g, pos, edgelist=irregular, edge_color='tab:blue', width=1.3,
                               style='dashed', arrows=True, arrowstyle='-',
                               connectionstyle=f'arc3,rad={rad}', ax=ax)
    ax.set_aspect('equal')
    xs, ys = [p[0] for p in pos.values()], [p[1] for p in pos.values()]
    span = max((abs(pos[u][0] - pos[v][0]) + abs(pos[u][1] - pos[v][1]) for u, v in irregular), default=0)
    pad = max(2.5, abs(rad) * span / 2 + 1) if irregular else 0.6
    ax.set_xlim(min(xs) - 0.8, max(xs) + 0.8)
    ax.set_ylim(min(ys) - pad, max(ys) + pad)
    ax.set_title(title)
    ax.axis('off')
    fig.tight_layout()
    path = os.path.join(RESULTS, filename)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    _show(fig)
    return path


def plot_scaling(series: dict, metric: str, ylabel: str, title: str, filename: str):
    """series: {назва: rows}, rows — список словників з metrics()."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for name, rows in series.items():
        ax.plot([r['N'] for r in rows], [r[metric] for r in rows], marker='o', label=name)
    if metric == 'T':
        ax.axhline(1, color='gray', linestyle=':', label='T = 1 (оптимум)')
    ax.set_xlabel('N, кількість вузлів')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    path = os.path.join(RESULTS, filename)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    _show(fig)
    return path


def scaling_plots(series: dict, prefix: str, label: str):
    for metric, ylabel in [('D', 'Діаметр D'), ('D_ave', 'Середній діаметр D̄'), ('T', 'Трафік T')]:
        plot_scaling(series, metric, ylabel, f'{label}: {ylabel} від N', f'{prefix}_{metric}.png')


def _show(fig):
    if SHOW and plt.get_backend().lower() != 'agg':
        plt.show()
    plt.close(fig)
