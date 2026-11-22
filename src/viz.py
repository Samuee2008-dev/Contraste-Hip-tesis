"""Gráficos para la comprobación de hipótesis.

Todas las funciones devuelven un matplotlib.figure.Figure.
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


def boxplot_dos_grupos(a, b, etiquetas=("A", "B")):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.boxplot([a, b], tick_labels=list(etiquetas))
    ax.set_ylabel("Valor")
    ax.set_title("Comparación de grupos (boxplot)")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def histogramas(a, b, etiquetas=("A", "B")):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(a, bins=20, alpha=0.55, label=etiquetas[0], density=True, edgecolor="black")
    ax.hist(b, bins=20, alpha=0.55, label=etiquetas[1], density=True, edgecolor="black")
    ax.set_xlabel("Valor")
    ax.set_ylabel("Densidad")
    ax.set_title("Distribuciones superpuestas")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def qqplot(x, titulo="Q-Q plot"):
    fig, ax = plt.subplots(figsize=(5, 4))
    stats.probplot(np.asarray(x, dtype=float), dist="norm", plot=ax)
    ax.set_title(titulo)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def dispersion_con_recta(x, y, xlabel="X", ylabel="Y"):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(x, y, alpha=0.7, edgecolor="black", linewidth=0.3)
    if len(x) >= 2:
        m, b = np.polyfit(x, y, 1)
        xs = np.linspace(x.min(), x.max(), 100)
        ax.plot(xs, m * xs + b, color="crimson", label=f"y = {m:.2f}x + {b:.2f}")
        ax.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title("Dispersión con recta ajustada")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def boxplot_multiple(grupos: dict):
    """grupos: dict {etiqueta: array} para >2 niveles."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.boxplot(list(grupos.values()), tick_labels=list(grupos.keys()))
    ax.set_ylabel("Valor")
    ax.set_title("Comparación de >2 grupos (boxplot)")
    ax.grid(True, axis="y", alpha=0.3)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    fig.tight_layout()
    return fig


def heatmap_correlacion(df, columnas):
    """Matriz de correlación (Pearson) entre las columnas seleccionadas."""
    corr = df[columnas].corr()
    fig, ax = plt.subplots(figsize=(5 + 0.4 * len(columnas), 4 + 0.4 * len(columnas)))
    im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(columnas)))
    ax.set_yticks(range(len(columnas)))
    ax.set_xticklabels(columnas, rotation=45, ha="right")
    ax.set_yticklabels(columnas)
    for i in range(len(columnas)):
        for j in range(len(columnas)):
            ax.text(j, i, f"{corr.values[i, j]:.2f}",
                    ha="center", va="center", color="black", fontsize=9)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title("Matriz de correlación")
    fig.tight_layout()
    return fig


def histograma_uno(x, titulo="Distribucion de la muestra"):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(np.asarray(x, dtype=float), bins=20, alpha=0.7,
            edgecolor="black", density=True)
    ax.set_xlabel("Valor")
    ax.set_ylabel("Densidad")
    ax.set_title(titulo)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig
