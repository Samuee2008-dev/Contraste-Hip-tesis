"""CSS personalizado para la interfaz Streamlit.

Se inyecta con inyectar_css() al inicio de la app.
Los selectores usan data-testid de Streamlit (estables entre versiones).
"""
import streamlit as st

CSS = """
<style>
/* ---------- Tipografía ---------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* ---------- Título principal tipo "calculadora" ---------- */
.titulo-app {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: #ffffff;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 30px rgba(79, 70, 229, 0.25);
}
.titulo-app h1 {
    margin: 0;
    font-size: 1.6rem;
    font-weight: 700;
}
.titulo-app p {
    margin: 0.35rem 0 0 0;
    opacity: 0.9;
    font-size: 0.95rem;
}

/* ---------- Botón "Calcular" grande ---------- */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: #ffffff;
    border: none;
    border-radius: 12px;
    padding: 0.85rem 2rem;
    font-size: 1.05rem;
    font-weight: 600;
    width: 100%;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);
    transition: transform .15s ease, box-shadow .15s ease;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.45);
    color: #ffffff;
}

/* ---------- Tarjetas de resultado (métricas) ---------- */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}
[data-testid="stMetricLabel"] {
    color: #6b7280;
    font-weight: 500;
}
[data-testid="stMetricValue"] {
    color: #111827;
    font-weight: 700;
    font-size: 1.4rem;
}

/* ---------- Contenedores con borde (tarjetas de sección) ---------- */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-radius: 14px;
}

/* ---------- Barra lateral ---------- */
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e5e7eb;
}

/* ---------- Cajas de código / avisos ---------- */
[data-testid="stAlert"] {
    border-radius: 10px;
}

/* ---------- Inputs ---------- */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div,
[data-testid="stNumberInput"] > div > div {
    border-radius: 10px;
}

/* ---------- Ocultar footer por defecto ---------- */
footer {visibility: hidden;}
</style>
"""


def inyectar_css():
    """Inyecta el CSS custom. Llamar al inicio de app.py."""
    st.markdown(CSS, unsafe_allow_html=True)
