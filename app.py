# -*- coding: utf-8 -*-
"""
Dashboard de Ventas - Streamlit
Autor: Angela Porres Cobb
Descripción: Dashboard de ventas con 4 secciones
"""

import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(
    page_title="Dashboard de Ventas",
    layout="wide",
    initial_sidebar_state="expanded"
)

#########################
## CARGA DE DATOS
#########################
# Carga de datos

@st.cache_data
def load_data():
    df1 = pd.read_csv("parte_1_sample.csv", parse_dates=["date"])
    df2 = pd.read_csv("parte_2_sample.csv", parse_dates=["date"])

    df = pd.concat([df1, df2], ignore_index=True)

    return df

df = load_data()

# Menú lateral
with st.sidebar:
    st.title("Menú")
    st.divider()
    
    # Selector de página/sección
    pagina = st.selectbox(
        "Selecciona una sección",
        [
            "Visión Global",
            "Análisis por Tienda",
            "Análisis por Estado",
            "Impacto de las promociones"
        ]
    )

    st.divider()
    st.caption("© 2026 - Dashboard de Ventas")

# Titulo principal
st.title("Dashboard de Ventas")
st.divider()

#########################
## PÁGINA 1: VISIÓN GLOBAL
#########################
if pagina == "Visión Global":
    st.header("Visión global de las ventas")
    st.info(
    "Con el dataset completo, los valores agregados serían mayores y "
    "las diferencias entre productos y tiendas se apreciarían con mayor claridad")

    # a) Conteo general con los siguientes datos
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tiendas", df["store_nbr"].nunique())
    col2.metric("Productos", df["family"].nunique())
    col3.metric("Estados", df["state"].nunique())
    col4.metric("Meses", df["month"].nunique())

    st.divider()

    # b) Análisis en términos medios de los siguientes datos
        # Top productos
    st.subheader("Top 10 productos más vendidos")
    top_products = (df.groupby("family")["sales"].mean().sort_values(ascending=False).head(10))
    st.bar_chart(top_products)

        # Ventas por tienda
    st.subheader("Distribución de ventas por tienda")
    sales_store = df.groupby("store_nbr")["sales"].mean()
    st.bar_chart(sales_store)

        # Promociones
    st.subheader("Top 10 tiendas con promociones")
    promo_store = (df[df["onpromotion"] > 0].groupby("store_nbr")["sales"].sum().sort_values(ascending=False).head(10)
    )
    st.bar_chart(promo_store)

    st.divider()

    # c) Análisis de la estacionalidad de las ventas
    st.subheader("Estacionalidad de las ventas")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("Ventas por dia")
        st.bar_chart(df.groupby("day_of_week")["sales"].mean())

    with col2:
        st.write("Ventas por semana")
        st.line_chart(df.groupby("week")["sales"].mean())

    with col3:
        st.write("Ventas por mes")
        st.line_chart(df.groupby("month")["sales"].mean())

#########################
## PÁGINA 2: ANÁLISIS POR TIENDA
#########################
elif pagina == "Análisis por Tienda":
    st.header("Análisis por tienda")
    st.info(
    "Con el dataset completo, los valores agregados serían mayores y "
    "las diferencias entre productos y tiendas se apreciarían con mayor claridad")
    store = st.selectbox(
        "Selecciona una tienda",
        sorted(df["store_nbr"].unique())
    )

    df_store = df[df["store_nbr"] == store]

    st.subheader("Ventas totales por año")
    st.bar_chart(df_store.groupby("year")["sales"].sum().sort_index())

    col1, col2 = st.columns(2)
    col1.metric("Productos vendidos", int(df_store["sales"].sum()))
    col2.metric("Productos en promoción",int(df_store[df_store["onpromotion"] > 0]["sales"].sum()))

#########################
## PÁGINA 3: ANÁLISIS POR ESTADO
#########################
elif pagina == "Análisis por Estado":
    st.header("Análisis por estado")
    st.info(
    "Con todos los datos disponibles, el ranking de tiendas podría variar "
    "y algunas tiendas cambiarían de posición")

    state = st.selectbox(
        "Selecciona un estado",
        sorted(df["state"].unique())
    )

    df_state = df[df["state"] == state]

    st.subheader("Transacciones por año")
    st.bar_chart(df_state.groupby("year")["transactions"].sum())

    st.subheader("Ranking de tiendas con más ventas")
    ranking = (
        df_state.groupby("store_nbr")["sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    st.bar_chart(ranking)

    st.subheader("Producto más vendido en la tienda")
    top_product = df_state.groupby("family")["sales"].sum().idxmax()
    st.success(f"Producto más vendido: **{top_product}**")

#########################
## PÁGINA 4: Análisis estratégico
#########################
elif pagina == "Impacto de las promociones":
    st.header("Impacto de las promociones en las ventas")
    st.info(
    "Con el conjunto completo de datos, el impacto porcentual de las "
    "promociones sería más estable y menos sensible a valores extremos")

    # Crear variable binaria de promoción
    df["promo_flag"] = df["onpromotion"] > 0

    # 1. Ventas medias con y sin promoción
    st.subheader("Ventas medias con y sin promoción")

    promo_mean = df.groupby("promo_flag")["sales"].mean()
    promo_mean.index = ["Sin promoción", "Con promoción"]

    st.bar_chart(promo_mean)
    st.divider()

    # 2. Ventas medias por tipo de tienda
    st.subheader("Ventas medias por tipo de tienda")

    ventas_tipo_tienda = (df.groupby("store_type")["sales"].mean().sort_values(ascending=False))
    st.bar_chart(ventas_tipo_tienda)

    st.info("Este análisis permite identificar qué formato de tienda genera mayores ventas medias")
    st.divider()

    # 3. Productos más beneficiados por promociones
    st.subheader("Productos más beneficiados por promociones")
    promo_product = (df.groupby(["family", "promo_flag"])["sales"].mean().unstack())
    promo_product["incremento_%"] = ((promo_product[True] - promo_product[False]) / promo_product[False] * 100)

    top_products = (promo_product["incremento_%"].sort_values(ascending=False).head(10))

    st.bar_chart(top_products)

    st.info("Este análisis permite identificar si las promociones incrementan las ventas y qué productos responden mejor a ellas")

