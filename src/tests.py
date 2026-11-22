"""Lógica de contrastes de hipótesis.

Cada función devuelve un objeto Resultado con:
- estadístico de contraste
- p-valor
- grados de libertad (si aplica)
- tamaño del efecto y su nombre
- supuestos comprobados (p. ej. Shapiro-Wilk)
- interpretación textual lista para mostrar en la interfaz
"""
from dataclasses import dataclass, field
import numpy as np
from scipy import stats


@dataclass
class Resultado:
    test: str
    estadistico: float
    p_valor: float
    gl: float | None = None
    tamano_efecto: float | None = None
    nombre_efecto: str = ""
    supuestos: dict = field(default_factory=dict)
    interpretacion: str = ""


# ---------- Helpers internos ----------
def _interp(p: float, alpha: float) -> str:
    if p < alpha:
        return f"Se RECHAZA H₀ (p = {p:.4f} < α = {alpha})"
    return f"NO se rechaza H₀ (p = {p:.4f} ≥ α = {alpha})"


def _cohen_d(a, b) -> float:
    n1, n2 = len(a), len(b)
    s = np.sqrt(((n1 - 1) * np.var(a, ddof=1) + (n2 - 1) * np.var(b, ddof=1)) / (n1 + n2 - 2))
    return float((np.mean(a) - np.mean(b)) / s) if s > 0 else 0.0


def _shapiro(x) -> float:
    return float(stats.shapiro(x)[1]) if len(x) >= 3 else float("nan")


# ---------- 2 grupos independientes ----------
def t_independiente(a, b, alpha=0.05, equal_var=False) -> Resultado:
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    t, p = stats.ttest_ind(a, b, equal_var=equal_var)
    return Resultado(
        test="t de Student (Welch)" if not equal_var else "t de Student (varianzas iguales)",
        estadistico=float(t),
        p_valor=float(p),
        gl=float(len(a) + len(b) - 2),
        tamano_efecto=_cohen_d(a, b),
        nombre_efecto="Cohen's d",
        supuestos={"Shapiro p (grupo A)": _shapiro(a), "Shapiro p (grupo B)": _shapiro(b)},
        interpretacion=_interp(p, alpha),
    )


def mann_whitney(a, b, alpha=0.05) -> Resultado:
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    n1, n2 = len(a), len(b)
    r = 1 - (2 * u) / (n1 * n2)  # rank-biserial
    return Resultado(
        test="Mann-Whitney U",
        estadistico=float(u),
        p_valor=float(p),
        tamano_efecto=float(r),
        nombre_efecto="r (rank-biserial)",
        interpretacion=_interp(p, alpha),
    )


# ---------- 2 grupos pareados ----------
def t_pareada(a, b, alpha=0.05) -> Resultado:
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    t, p = stats.ttest_rel(a, b)
    dif = a - b
    sd = np.std(dif, ddof=1)
    d = float(np.mean(dif) / sd) if sd > 0 else 0.0
    return Resultado(
        test="t pareada",
        estadistico=float(t),
        p_valor=float(p),
        gl=float(len(a) - 1),
        tamano_efecto=d,
        nombre_efecto="Cohen's d (pareado)",
        supuestos={"Shapiro p (diferencias)": _shapiro(dif)},
        interpretacion=_interp(p, alpha),
    )


def wilcoxon(a, b, alpha=0.05) -> Resultado:
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    s, p = stats.wilcoxon(a, b)
    return Resultado(
        test="Wilcoxon (rangos con signo)",
        estadistico=float(s),
        p_valor=float(p),
        interpretacion=_interp(p, alpha),
    )


# ---------- >2 grupos ----------
def anova(*grupos, alpha=0.05) -> Resultado:
    f, p = stats.f_oneway(*grupos)
    sup = {f"Shapiro p (grupo {i+1})": _shapiro(np.asarray(g)) for i, g in enumerate(grupos)}
    return Resultado(
        test="ANOVA de un factor",
        estadistico=float(f),
        p_valor=float(p),
        supuestos=sup,
        interpretacion=_interp(p, alpha),
    )


def kruskal(*grupos, alpha=0.05) -> Resultado:
    h, p = stats.kruskal(*grupos)
    return Resultado(
        test="Kruskal-Wallis",
        estadistico=float(h),
        p_valor=float(p),
        interpretacion=_interp(p, alpha),
    )


# ---------- Categóricos ----------
def chi_cuadrado(tabla, alpha=0.05) -> Resultado:
    tabla = np.asarray(tabla)
    chi2, p, gl, _ = stats.chi2_contingency(tabla)
    n = tabla.sum()
    v = float(np.sqrt(chi2 / (n * (min(tabla.shape) - 1))))
    return Resultado(
        test="Chi-cuadrado de independencia",
        estadistico=float(chi2),
        p_valor=float(p),
        gl=float(gl),
        tamano_efecto=v,
        nombre_efecto="V de Cramér",
        interpretacion=_interp(p, alpha),
    )


# ---------- Correlación ----------
def correlacion(x, y, alpha=0.05, metodo="pearson") -> Resultado:
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if metodo == "pearson":
        r, p = stats.pearsonr(x, y)
        nombre, efecto = "Correlación de Pearson", "r"
    else:
        r, p = stats.spearmanr(x, y)
        nombre, efecto = "Correlación de Spearman", "ρ"
    return Resultado(
        test=nombre,
        estadistico=float(r),
        p_valor=float(p),
        tamano_efecto=float(r),
        nombre_efecto=efecto,
        interpretacion=_interp(p, alpha),
    )


# ---------- 1 muestra: t ----------
def t_una_muestra(x, mu0, alpha=0.05) -> Resultado:
    x = np.asarray(x, dtype=float)
    t, p = stats.ttest_1samp(x, mu0)
    sd = np.std(x, ddof=1)
    d = float((np.mean(x) - mu0) / sd) if sd > 0 else 0.0
    return Resultado(
        test="t de Student — 1 muestra",
        estadistico=float(t),
        p_valor=float(p),
        gl=float(len(x) - 1),
        tamano_efecto=d,
        nombre_efecto="Cohen's d",
        supuestos={"Shapiro p (muestra)": _shapiro(x)},
        interpretacion=_interp(p, alpha),
    )


# ---------- Z: 1 media (sigma conocida) ----------
def z_una_media(x, mu0, sigma, alpha=0.05) -> Resultado:
    x = np.asarray(x, dtype=float)
    n = len(x)
    z = (np.mean(x) - mu0) / (sigma / np.sqrt(n))
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    d = float((np.mean(x) - mu0) / sigma)
    return Resultado(
        test="Z — 1 media (sigma conocida)",
        estadistico=float(z),
        p_valor=float(p),
        tamano_efecto=d,
        nombre_efecto="Cohen's d",
        interpretacion=_interp(p, alpha),
    )


# ---------- Z: 2 proporciones ----------
def z_dos_proporciones(x1, n1, x2, n2, alpha=0.05) -> Resultado:
    p1 = x1 / n1
    p2 = x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se if se > 0 else 0.0
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    h = 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))
    return Resultado(
        test="Z — 2 proporciones",
        estadistico=float(z),
        p_valor=float(p),
        tamano_efecto=float(h),
        nombre_efecto="h de Cohen",
        interpretacion=_interp(p, alpha),
    )


# ---------- Z: 1 proporcion ----------
def z_una_proporcion(x, n, p0, alpha=0.05) -> Resultado:
    p_hat = x / n
    se = np.sqrt(p0 * (1 - p0) / n)
    z = (p_hat - p0) / se if se > 0 else 0.0
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    h = 2 * np.arcsin(np.sqrt(p_hat)) - 2 * np.arcsin(np.sqrt(p0))
    return Resultado(
        test="Z — 1 proporcion",
        estadistico=float(z),
        p_valor=float(p),
        tamano_efecto=float(h),
        nombre_efecto="h de Cohen",
        interpretacion=_interp(p, alpha),
    )
