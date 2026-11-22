import re
import sys
from pathlib import Path

# --- PARCHE PARA STREAMLIT CLOUD ---
# Añade la carpeta raíz al PATH para que encuentre la carpeta 'src'
root_path = Path(__file__).resolve().parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))
# -----------------------------------

import numpy as np
import pandas as pd
import streamlit as st

from src import tests as T
from src import viz as V
from src import styles

st.set_page_config(page_title="Calculadora de Hipotesis", page_icon="🧮", layout="wide")
styles.inyectar_css()

st.markdown(
    '<div class="titulo-app">'
    '<h1>🧮 Calculadora de Contraste de Hipotesis</h1>'
    '<p>Elige el contraste, pega tus valores y el resultado aparece al instante.</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ---------- Barra lateral ----------
with st.sidebar:
    st.markdown("### ⚙️ Parametros")
    alpha = st.select_slider(
        "Nivel de significacion (α)",
        options=[0.001, 0.01, 0.05, 0.10],
        value=0.05,
    )
    st.caption(f"α = {alpha}  ·  Convencional: 0.05")

    st.markdown("---")
    st.markdown("### 📖 Como usar")
    st.markdown(
        "1. Elige el tipo de contraste.\n"
        "2. Pega los valores en los campos.\n"
        "3. El resultado se actualiza solo.\n\n"
        "**Separadores validos:** coma, punto y coma, espacio o salto de linea."
    )

# ---------- Parser de numeros ----------
NUM_RE = re.compile(r"-?\d+(?:[.,]\d+)?")

def parsear(texto):
    if not texto or not texto.strip():
        return np.array([])
    nums = NUM_RE.findall(texto)
    try:
        return np.array([float(n.replace(",", ".")) for n in nums])
    except ValueError:
        return None

def valido(x):
    return x is not None and len(x) > 0

# ---------- Helpers UI ----------
def dos_textareas(label_a="Grupo A", label_b="Grupo B", pref="x",
                  ph_a=None, ph_b=None):
    c1, c2 = st.columns(2)
    with c1:
        txt_a = st.text_area(label_a, height=100, key=f"{pref}_a",
                             placeholder=ph_a or "Ej: 12.3, 14.5, 11.8, 13.0")
    with c2:
        txt_b = st.text_area(label_b, height=100, key=f"{pref}_b",
                             placeholder=ph_b or "Ej: 15.1, 16.0, 14.7, 15.3")
    return parsear(txt_a), parsear(txt_b)

def mostrar_resultado(r, detalle=None, figuras=None):
    st.markdown("---")
    
    # 1. PRIMERO: La decisión (El cartel de Se Rechaza o No)
    if r.p_valor < alpha:
        st.error(
            f"### 🔴 Se RECHAZA H₀\n"
            f"**p = {r.p_valor:.6f} < α = {alpha}** — Existe evidencia estadística suficiente contra H₀."
        )
    else:
        st.success(
            f"### 🟢 NO se rechaza H₀\n"
            f"**p = {r.p_valor:.6f} ≥ α = {alpha}** — No hay evidencia suficiente contra H₀."
        )

    # 2. SEGUNDO: Las métricas principales
    m1, m2, m3 = st.columns(3)
    m1.metric("Estadistico", f"{r.estadistico:.4f}")
    m2.metric("p-valor", f"{r.p_valor:.6f}")
    if r.tamano_efecto is not None:
        m3.metric(f"Tamano del efecto ({r.nombre_efecto})", f"{r.tamano_efecto:.4f}")
    else:
        m3.empty()

    st.subheader(f"Detalles del análisis: {r.test}")

    # 3. TERCERO: Las hipótesis
    if detalle:
        h1, h2 = st.columns(2)
        h1.markdown(f"**H₀ (Nula):** {detalle.get('h0', '—')}")
        h2.markdown(f"**H₁ (Alternativa):** {detalle.get('h1', '—')}")

    if r.gl is not None:
        st.caption(f"Grados de libertad: {r.gl:.2f}")

    if r.supuestos:
        with st.expander("🔍 Verificación de Supuestos (Shapiro-Wilk)"):
            for k, v in r.supuestos.items():
                if isinstance(v, (int, float)) and not np.isnan(v):
                    ok = v > alpha
                    st.write(f"**{k}:** p = {v:.4f} → {'✅ normal' if ok else '⚠️ no normal'}")
            st.caption("Si p < α en Shapiro-Wilk, considera un test no parametrico.")

    # 4. AL FINAL: Los gráficos
    if figuras:
        st.markdown("### 📊 Gráficos de apoyo")
        cols = st.columns(min(2, len(figuras)))
        for i, fig in enumerate(figuras):
            with cols[i % len(cols)]:
                st.pyplot(fig)

# ---------- Selector de test ----------
st.markdown("### 🧪 Tipo de contraste")
tipo = st.selectbox("Selecciona el test", [
    "t de Student — 2 grupos independientes",
    "t de Student — 1 muestra",
    "t pareada (antes / despues)",
    "Mann-Whitney U — 2 grupos independientes",
    "Wilcoxon — pareado",
    "ANOVA — >2 grupos",
    "Kruskal-Wallis — >2 grupos",
    "Chi-cuadrado — independencia",
    "Correlacion — Pearson / Spearman",
    "Z — 2 proporciones",
    "Z — 1 media (sigma conocida)",
    "Z — 1 proporcion",
], label_visibility="collapsed")

# ---------- Render por tipo ----------
if tipo.startswith("t de Student — 2"):
    a, b = dos_textareas()
    var_iguales = st.checkbox("Asumir varianzas iguales", value=False,
                              help="Si dudas, dejalo desmarcado: Welch es mas robusto.")
    if valido(a) and valido(b):
        if len(a) < 2 or len(b) < 2:
            st.warning("Cada grupo necesita al menos 2 valores.")
        else:
            r = T.t_independiente(a, b, alpha, equal_var=var_iguales)
            mostrar_resultado(
                r,
                detalle={"h0": "μ_A = μ_B (medias iguales)",
                         "h1": "μ_A ≠ μ_B (medias distintas)"},
                figuras=[V.boxplot_dos_grupos(a, b), V.histogramas(a, b)],
            )
    else:
        st.info("Pega valores en ambos grupos para calcular.")

elif tipo.startswith("t de Student — 1"):
    c1, c2 = st.columns([2, 1])
    with c1:
        txt = st.text_area("Muestra", height=140, key="t1_x",
                           placeholder="Ej: 12.3, 14.5, 11.8, 13.0, 12.9")
    with c2:
        mu0 = st.number_input("μ₀ (media hipotetica)", value=0.0, step=0.1, key="t1_mu0")
    x = parsear(txt)
    if valido(x):
        if len(x) < 2:
            st.warning("Se necesitan al menos 2 valores.")
        else:
            r = T.t_una_muestra(x, mu0, alpha)
            mostrar_resultado(
                r,
                detalle={"h0": f"μ = {mu0}", "h1": f"μ ≠ {mu0}"},
                figuras=[V.histograma_uno(x), V.qqplot(x)],
            )
    else:
        st.info("Pega los valores de la muestra.")

elif tipo.startswith("t pareada"):
    a, b = dos_textareas("Antes", "Despues", "tp",
                         "Ej: 68, 72, 65, 70, 71",
                         "Ej: 75, 78, 72, 77, 80")
    if valido(a) and valido(b):
        if len(a) != len(b):
            st.warning(f"Deben tener el mismo numero de valores (Antes={len(a)}, Despues={len(b)}).")
        elif len(a) < 2:
            st.warning("Se necesitan al menos 2 pares.")
        else:
            r = T.t_pareada(a, b, alpha)
            mostrar_resultado(
                r,
                detalle={"h0": "μ_dif = 0 (sin cambio)",
                         "h1": "μ_dif ≠ 0 (hay cambio)"},
                figuras=[V.histogramas(a, b, ("Antes", "Despues")),
                         V.qqplot(a - b, "Q-Q — diferencias")],
            )
    else:
        st.info("Pega valores antes y despues (mismo numero).")

elif tipo.startswith("Mann-Whitney"):
    a, b = dos_textareas(pref="mw")
    if valido(a) and valido(b):
        if len(a) < 2 or len(b) < 2:
            st.warning("Cada grupo necesita al menos 2 valores.")
        else:
            r = T.mann_whitney(a, b, alpha)
            mostrar_resultado(
                r,
                detalle={"h0": "Las distribuciones de A y B son iguales",
                         "h1": "Las distribuciones de A y B difieren"},
                figuras=[V.boxplot_dos_grupos(a, b), V.histogramas(a, b)],
            )
    else:
        st.info("Pega valores en ambos grupos.")

elif tipo.startswith("Wilcoxon"):
    a, b = dos_textareas("Antes", "Despues", "wx")
    if valido(a) and valido(b):
        if len(a) != len(b):
            st.warning(f"Deben tener el mismo numero de valores ({len(a)} vs {len(b)}).")
        elif len(a) < 3:
            st.warning("Se necesitan al menos 3 pares.")
        else:
            r = T.wilcoxon(a, b, alpha)
            mostrar_resultado(
                r,
                detalle={"h0": "La mediana de las diferencias es 0",
                         "h1": "La mediana de las diferencias es ≠ 0"},
                figuras=[V.histogramas(a, b, ("Antes", "Despues"))],
            )
    else:
        st.info("Pega valores antes y despues.")

elif tipo.startswith("ANOVA") or tipo.startswith("Kruskal"):
    es_anova = tipo.startswith("ANOVA")
    n_g = st.number_input("Numero de grupos", min_value=2, max_value=10,
                          value=3, step=1, key=f"n_{tipo[:3]}")
    grupos = []
    cols = st.columns(min(int(n_g), 3))
    for i in range(int(n_g)):
        col = cols[i % len(cols)]
        with col:
            txt = st.text_area(f"Grupo {chr(65+i)}", height=120,
                               key=f"g_{tipo[:3]}_{i}",
                               placeholder="Ej: 10, 12, 11, 13...")
        grupos.append(parsear(txt))
    if all(valido(g) and len(g) >= 2 for g in grupos):
        if es_anova:
            r = T.anova(*grupos, alpha=alpha)
            h0, h1 = "Todas las medias son iguales", "Al menos una media difiere"
        else:
            r = T.kruskal(*grupos, alpha=alpha)
            h0, h1 = "Todas las distribuciones son iguales", "Al menos una distribucion difiere"
        dicc = {chr(65+i): g for i, g in enumerate(grupos)}
        mostrar_resultado(
            r,
            detalle={"h0": h0, "h1": h1},
            figuras=[V.boxplot_multiple(dicc)],
        )
    else:
        st.info("Pega valores en cada grupo (≥2 por grupo).")

elif tipo.startswith("Chi-cuadrado"):
    st.markdown("**Tabla de contingencia** — modifica celdas; añade/quita filas y columnas con los botones.")
    df_default = pd.DataFrame([[10, 20], [30, 15]],
                              columns=["Col 1", "Col 2"],
                              index=["Fila 1", "Fila 2"])
    tabla = st.data_editor(df_default, num_rows="dynamic",
                           use_container_width=True, key="chi_tabla")
    try:
        valores = tabla.values.astype(float)
        if np.isnan(valores).any() or (valores < 0).any():
            st.warning("La tabla contiene valores no validos.")
        elif valores.sum() == 0:
            st.info("Introduce frecuencias mayores que 0.")
        elif valores.shape[0] < 2 or valores.shape[1] < 2:
            st.warning("La tabla debe tener al menos 2 filas y 2 columnas.")
        else:
            r = T.chi_cuadrado(valores, alpha)
            bajas = int((valores < 5).sum())
            if bajas > 0.2 * valores.size:
                st.warning(f"⚠️ {bajas} celdas con frecuencia < 5. Chi-cuadrado puede no ser fiable.")
            mostrar_resultado(
                r,
                detalle={"h0": "Las variables son independientes",
                         "h1": "Las variables estan asociadas"},
            )
    except Exception as e:
        st.error(f"Error al procesar la tabla: {e}")

elif tipo.startswith("Correlacion"):
    a, b = dos_textareas("Variable X", "Variable Y", "co")
    metodo = st.radio("Coeficiente", ["Pearson", "Spearman"], horizontal=True)
    if valido(a) and valido(b):
        if len(a) != len(b):
            st.warning(f"X e Y deben tener el mismo numero de valores ({len(a)} vs {len(b)}).")
        elif len(a) < 3:
            st.warning("Se necesitan al menos 3 pares.")
        else:
            r = T.correlacion(a, b, alpha, metodo.lower())
            mostrar_resultado(
                r,
                detalle={"h0": "ρ = 0 (sin correlacion)",
                         "h1": "ρ ≠ 0 (hay correlacion)"},
                figuras=[V.dispersion_con_recta(a, b, "X", "Y")],
            )
    else:
        st.info("Pega valores de X e Y (mismo numero).")

elif tipo.startswith("Z — 2"):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Grupo 1**")
        x1 = st.number_input("Exitos (x₁)", min_value=0, value=20, step=1, key="z2_x1")
        n1 = st.number_input("Tamano (n₁)", min_value=1, value=100, step=1, key="z2_n1")
    with c2:
        st.markdown("**Grupo 2**")
        x2 = st.number_input("Exitos (x₂)", min_value=0, value=30, step=1, key="z2_x2")
        n2 = st.number_input("Tamano (n₂)", min_value=1, value=100, step=1, key="z2_n2")
    if x1 > n1 or x2 > n2:
        st.warning("Los exitos no pueden superar el tamano de muestra.")
    else:
        r = T.z_dos_proporciones(x1, n1, x2, n2, alpha)
        mostrar_resultado(r, detalle={"h0": "p₁ = p₂", "h1": "p₁ ≠ p₂"})

elif tipo.startswith("Z — 1 media"):
    c1, c2 = st.columns([2, 1])
    with c1:
        txt = st.text_area("Muestra", height=140, key="z1m_x",
                           placeholder="Ej: 12.3, 14.5, 11.8, 13.0...")
    with c2:
        mu0 = st.number_input("μ₀", value=0.0, step=0.1, key="z1m_mu0")
        sigma = st.number_input("σ (conocida)", min_value=0.0001, value=1.0,
                                step=0.1, key="z1m_sigma")
    x = parsear(txt)
    if valido(x) and len(x) >= 2:
        r = T.z_una_media(x, mu0, sigma, alpha)
        mostrar_resultado(
            r,
            detalle={"h0": f"μ = {mu0}", "h1": f"μ ≠ {mu0}"},
            figuras=[V.histograma_uno(x), V.qqplot(x)],
        )
    else:
        st.info("Pega la muestra y define μ₀ y σ.")

elif tipo.startswith("Z — 1 proporcion"):
    c1, c2, c3 = st.columns(3)
    x = c1.number_input("Exitos (x)", min_value=0, value=20, step=1, key="z1p_x")
    n = c2.number_input("Tamano (n)", min_value=1, value=100, step=1, key="z1p_n")
    p0 = c3.number_input("p₀", min_value=0.0001, max_value=0.9999,
                         value=0.5, step=0.01, key="z1p_p0")
    if x > n:
        st.warning("Los exitos no pueden superar n.")
    else:
        r = T.z_una_proporcion(x, n, p0, alpha)
        mostrar_resultado(
            r,
            detalle={"h0": f"p = {p0}", "h1": f"p ≠ {p0}"},
        )