import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt
import matplotlib.pyplot as plt
import os
import plotly.express as px
from datetime import date
import base64


st.set_page_config(layout="wide")

from streamlit_option_menu import option_menu
from formulario import mostrar_formulario




    # Función para cargar imagen como base64
def get_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

    

def load_data():
    animales_df = pd.read_csv("animales.csv", parse_dates=["FechaNacimiento", "FechaAdquisicion"])
    animales_df["FechaNacimiento"] = pd.to_datetime(animales_df["FechaNacimiento"], errors='coerce')
    animales_df["FechaAdquisicion"] = pd.to_datetime(animales_df["FechaAdquisicion"], errors='coerce')

    leche_df = pd.read_csv("leche.csv", parse_dates=["Fecha"])
    leche_df["Fecha"] = pd.to_datetime(leche_df["Fecha"], errors='coerce')

    bajas_df = pd.read_csv("bajas.csv", parse_dates=["Fecha de salida"])
    bajas_df["Fecha de salida"] = pd.to_datetime(bajas_df["Fecha de salida"], errors='coerce')

    rotaciones_df = pd.read_csv("rotaciones_potrero.csv", parse_dates=["Fecha Rotacion"])
    rotaciones_df["Fecha Rotacion"] = pd.to_datetime(rotaciones_df["Fecha Rotacion"], errors='coerce')

    return animales_df, leche_df, bajas_df, rotaciones_df

with st.sidebar:
    opcion = option_menu(
        "Menú Principal",
        ["Dashboard", "Formulario"],
        icons=["bar-chart", "clipboard-check"],
        menu_icon="cast",
        default_index=0,
    )
if opcion == "Dashboard":
       # Carga las dos imágenes
    img_izquierda = get_image_base64("encabezado1.jpeg")  # Cambia por tu archivo
    img_derecha = get_image_base64("encabezado2.jpeg")    # Cambia por tu archivo


    # Mostrar encabezado con estilo
    st.markdown(f"""
    <style>
    .header-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #99ccff;
        padding: 20px 30px;
        border-radius: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        margin-bottom: 25px;
    }}
    .header-image {{
        height: 120px;
        border-radius: 12px;
    }}
    .header-title {{
        font-size: 32px;
        font-weight: bold;
        color: #002244;
        text-align: center;
        flex-grow: 1;
    }}
    </style>

    <div class="header-container">
        <img src="data:image/jpeg;base64,{img_izquierda}" class="header-image">
        <div class="header-title">Dashboard de KPIs - Finca El Tornado</div>
        <img src="data:image/jpeg;base64,{img_derecha}" class="header-image">
    </div>
    """, unsafe_allow_html=True)


    # Ejecutar la función para obtener los DataFrames
    animales_df, leche_df, bajas_df, rotaciones_df = load_data()


    if "animales_df" not in st.session_state:
        st.session_state["animales_df"], _, _, _ = load_data()

    animales_df = st.session_state["animales_df"]

    #st.title("Dashboard de KPIs - Finca El Tornado")

    tab1, tab2, tab3 = st.tabs(["📋 Información de Animales", "🥛 Análisis Producción Lechera", "Cosulta Historica Precio Leche"])

    # ---------------------------
    # KPIs generales
    # ---------------------------
    with tab1:
        
        st.header("Resumen General")

        # TOTAL ANIMALES
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #4FC3F7, #0288D1);
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            color: white;
            font-size: 22px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        '>
            <h2 style='margin-bottom:10px;'>🐮 Total Animales</h2>
            <div style='font-size: 44px; font-weight: bold;'>{len(animales_df)}</div>
        </div>
        """, unsafe_allow_html=True)

        # Tipos de animales
        st.markdown("---")
        st.subheader("Tipos de Animales")
        tipos = animales_df["Tipo"].value_counts()
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]

        for idx, (tipo, count) in enumerate(tipos.items()):
            col = cols[idx % 3]
            with col:
                st.markdown(f"""
                <div style='
                    background-color: #f1f8ff;
                    border-left: 6px solid #2196F3;
                    padding: 15px;
                    margin: 8px 0;
                    border-radius: 8px;
                    box-shadow: 1px 1px 5px rgba(0,0,0,0.05);
                '>
                    <h4 style='margin: 0 0 5px;'>{tipo}</h4>
                    <p style='font-size: 24px; margin: 0; color: #0D47A1; font-weight: bold;'>{count}</p>
                </div>
                """, unsafe_allow_html=True)

        



        # Gráfico por tipo
        st.markdown("---")
        st.subheader("Cantidad de Animales por Tipo")

        # Contar animales por tipo
        tipos = animales_df["Tipo"].value_counts().reset_index()
        tipos.columns = ['Tipo', 'Cantidad']

        # Colores personalizados (ajusta si tienes más tipos)
        colores = ['#FF6347', '#32CD32', '#FFD700', '#8A2BE2', '#FF4500', '#00BFFF']

        # Barra base
        barras = alt.Chart(tipos).mark_bar().encode(
            x=alt.X('Tipo:N', title='Tipo de Animal'),
            y=alt.Y('Cantidad:Q', title='Cantidad'),
            color=alt.Color('Tipo:N', scale=alt.Scale(domain=tipos['Tipo'], range=colores))
        )

        # Etiquetas de cantidad encima de las barras
        etiquetas = alt.Chart(tipos).mark_text(
            align='center',
            baseline='bottom',
            dy=-5,
            color='black'
        ).encode(
            x='Tipo:N',
            y='Cantidad:Q',
            text='Cantidad:Q'
        )

        # Mostrar gráfico combinado
        st.altair_chart(barras + etiquetas, use_container_width=True)
        
        st.markdown("---")

        # Crear columna de grupo
        animales_df["Grupo"] = animales_df["Tipo"].apply(
            lambda x: "Vaca/Becerro/Becerra" if x in ["Vaca", "Becerro", "Becerra"] else x
        )

        # Contar animales por potrero y grupo
        conteo = animales_df.groupby(["Potrero", "Grupo"]).size().reset_index(name="Cantidad")

        # Calcular totales por potrero para etiquetas
        totales = conteo.groupby("Potrero")["Cantidad"].sum().reset_index()
        totales.columns = ["Potrero", "Total"]

        # Gráfico de barras apiladas
        barras = alt.Chart(conteo).mark_bar().encode(
            x=alt.X("Potrero:N", title="Potrero"),
            y=alt.Y("Cantidad:Q", title="Cantidad de Animales"),
            color=alt.Color("Grupo:N", title="Grupo de Animal")
        )

        # Etiquetas de totales encima de cada barra
        etiquetas = alt.Chart(totales).mark_text(
            dy=-5,
            color="black",
            fontWeight="bold"
        ).encode(
            x="Potrero:N",
            y="Total:Q",
            text="Total:Q"
        )

        # Mostrar gráfico combinado
        st.markdown("---")
        st.subheader("Cantidad de Animales por Potrero")
        st.altair_chart(barras + etiquetas, use_container_width=True)


        st.markdown("---")
            #alerta de marcaje
        # Asegurarse de que la columna FechaNacimiento es datetime
        animales_df["FechaNacimiento"] = pd.to_datetime(animales_df["FechaNacimiento"], errors='coerce')
        hoy = pd.Timestamp(datetime.now())

        # ----------------------------
        # 1. Actualizar tipo por edad
        # ----------------------------
        animales_df["EdadDias"] = (hoy - animales_df["FechaNacimiento"]).dt.days

        # Convertir becerros/becerras mayores de 240 días a mautes/mautas
        animales_df.loc[
            (animales_df["Tipo"] == "Becerros") & (animales_df["EdadDias"] >= 240),
            "Tipo"
        ] = "Mautes"

        animales_df.loc[
            (animales_df["Tipo"] == "Becerras") & (animales_df["EdadDias"] >= 240),
            "Tipo"
        ] = "Mautas"

        # ----------------------------
        # 2. Filtrar animales sin marcar nacidos en la finca
        # ----------------------------
        sin_marcar = animales_df[
            (animales_df["Hierro"] == "No") & 
            (animales_df["Procedencia"] == "Nacido en finca") &
            (animales_df["FechaNacimiento"].notna())
        ].copy()

        # Recalcular edad por seguridad
        sin_marcar["EdadDias"] = (hoy - sin_marcar["FechaNacimiento"]).dt.days

        st.subheader("Animales Sin Marcar")
        st.write(f"Cantidad: {len(sin_marcar)}")

        # ----------------------------
        # 3. Próximos a marcar (150-180 días)
        # ----------------------------
        proximos = sin_marcar[sin_marcar["EdadDias"].between(150, 180)]
        st.subheader("Alerta: Próximos a Marcar (150-180 días)")
        st.write(f"Cantidad: {len(proximos)}")
        st.dataframe(proximos[["Tipo", "FechaNacimiento", "Potrero", "EdadDias"]])

        # ----------------------------
        # 4. Pasados de 180 días sin marcar
        # ----------------------------
        pasados_180 = sin_marcar[sin_marcar["EdadDias"] > 180]
        st.subheader("Alerta: Animales Pasados de 180 Días Sin Marcar")
        st.write(f"Cantidad: {len(pasados_180)}")
        st.dataframe(pasados_180[["Tipo", "FechaNacimiento", "Potrero", "EdadDias"]])

        # 6. Marcar animales manualmente desde cualquier alerta
        # ----------------------------
        st.markdown("---")
        st.subheader("✅ Marcar animales (cambiar 'Hierro' a 'Sí')")

        # Combinar ambos grupos de alerta
        animales_a_marcar = pd.concat([proximos, pasados_180]).drop_duplicates()
        
        if not animales_a_marcar.empty:
            st.write(f"Total animales en alerta para marcar: {len(animales_a_marcar)}")

            # Mostrar tabla
            st.dataframe(animales_a_marcar[["Tipo", "FechaNacimiento", "Potrero", "EdadDias"]])

            # Permitir selección por índice
            indices_a_marcar = animales_a_marcar.index.tolist()
            seleccion = st.multiselect("Selecciona los índices de animales a marcar:", indices_a_marcar)

            if st.button("Marcar seleccionados"):
                animales_df.loc[seleccion, "Hierro"] = "Sí"
                animales_df.to_csv("animales.csv", index=False)
                st.success(f"{len(seleccion)} animal(es) marcados correctamente.")

                # Actualizar session_state si aplica
                if "animales_df" in st.session_state:
                    st.session_state["animales_df"] = animales_df
        else:
            st.info("No hay animales en alerta para marcar.")


        st.markdown("---")
        st.markdown("### 📉 Bajas de Animales")

        # Asegurar formato de fecha correcto
        bajas_df["Fecha de salida"] = pd.to_datetime(bajas_df["Fecha de salida"], errors="coerce")
        bajas_df["Año"] = bajas_df["Fecha de salida"].dt.year
        bajas_df["Mes"] = bajas_df["Fecha de salida"].dt.month

        # Filtro de año
        años_disponibles = sorted(bajas_df["Año"].dropna().unique(), reverse=True)
        año_seleccionado = st.selectbox("Selecciona un año para analizar las bajas:", options=["Todos"] + list(map(str, map(int, años_disponibles))))

        # Aplicar filtro si se selecciona un año específico
        if año_seleccionado != "Todos":
            año_seleccionado = int(año_seleccionado)
            bajas_filtradas = bajas_df[bajas_df["Año"] == año_seleccionado]
        else:
            bajas_filtradas = bajas_df.copy()

        # Mensaje informativo
        st.markdown(f"### 📆 En el año {año_seleccionado if año_seleccionado != 'Todos' else 'los últimos años'} se han registrado **{len(bajas_filtradas)} bajas**.")

        # Gráfico: Bajas por año
        bajas_por_año = bajas_df.groupby("Año").size().reset_index(name="Bajas")
        fig = px.bar(
            bajas_por_año,
            x="Año",
            y="Bajas",
            title="📉 Bajas de animales por año",
            text="Bajas"
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

        # Normalizar texto de motivos
        bajas_filtradas = bajas_filtradas.copy()
        bajas_filtradas["Motivo"] = bajas_filtradas["Motivo"].str.lower()
        bajas_filtradas["Motivo"] = bajas_filtradas["Motivo"].str.lower().str.strip()
        # Separar por motivo
        ventas = bajas_filtradas[bajas_filtradas["Motivo"] == "vendido"]
        muertes = bajas_filtradas[bajas_filtradas["Motivo"] == "muerto"]
        otros = bajas_filtradas[bajas_filtradas["Motivo"] == "otros"]

        # KPI por motivo
        col1, col2, col3 = st.columns(3)

        # Función para mostrar descripción de ventas
        def descripcion_venta(fila):
            hierro = fila["Hierro"]
            # Buscar procedencia y fecha de adquisición en animales_df
            animal_info = animales_df[animales_df["Hierro"] == hierro]
            if animal_info.empty:
                return "Origen desconocido"

            tipo = animal_info.iloc[0]["Tipo"]
            procedencia = animal_info.iloc[0]["Procedencia"]
            fecha_adq = animal_info.iloc[0]["FechaAdquisicion"]
            comentario = fila.get("Comentario de Baja", "")

            origen = f"{tipo} {procedencia.lower()} el {pd.to_datetime(fecha_adq).date()}" if pd.notnull(fecha_adq) else f"{tipo} {procedencia.lower()}"
            return f"{origen} – {comentario}" if comentario else origen

        with col1:
            st.markdown("### 💰 Ventas")
            st.markdown(f"**{len(ventas)} animales vendidos**")
            if not ventas.empty:
                descripciones = ventas.apply(descripcion_venta, axis=1)
                resumen = descripciones.value_counts()
                for desc, count in resumen.items():
                    st.markdown(f"- {desc} – {count} veces")

        with col2:
            st.markdown("### ☠️ Muertes")
            st.markdown(f"**{len(muertes)} animales muertos**")
            if not muertes.empty:
                descripciones = muertes.apply(
                    lambda x: f"{x['Tipo']} muerto – {x['Comentario de Baja']}" if pd.notnull(x['Comentario de Baja']) else f"{x['Tipo']} muerto",
                    axis=1
                )
                resumen = descripciones.value_counts()
                for desc, count in resumen.items():
                    st.markdown(f"- {desc} – {count} veces")

        with col3:
            st.markdown("### ❗ Otros Motivos")
            st.markdown(f"**{len(otros)} animales**")
            if not otros.empty:
                descripciones = otros.apply(
                    lambda x: f"{x['Tipo']} – {x['Comentario de Baja']}" if pd.notnull(x['Comentario de Baja']) else f"{x['Tipo']}",
                    axis=1
                )
                resumen = descripciones.value_counts()
                for desc, count in resumen.items():
                    st.markdown(f"- {desc} – {count} veces")


        # Mostrar historial completo
        if st.button("🔍 Ver historial completo de bajas"):
            st.dataframe(bajas_df)




    with tab2:
        st.header("🥛 Análisis de Producción Lechera")

        def kpi_produccion_leche(leche_df):
            # Asegurar que Fecha es datetime
            leche_df["Fecha"] = pd.to_datetime(leche_df["Fecha"], errors="coerce")

            # Agregar columnas de año y mes
            leche_df["Mes"] = leche_df["Fecha"].dt.month
            leche_df["Año"] = leche_df["Fecha"].dt.year

            # Producción mensual
            produccion_mensual = leche_df.groupby(["Año", "Mes"])["Litros"].sum().reset_index()

        
            # Gráfico mensual
            fig = px.bar(
                produccion_mensual,
                x="Mes",
                y="Litros",
                color="Año",
                barmode="group",
                text="Litros",
                title="Producción de Leche por Mes",
                labels={"Litros": "Litros", "Mes": "Mes"}
            )

            # Personalizar etiquetas
            fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
            fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

            st.plotly_chart(fig, use_container_width=True)


            st.markdown("---")
        def kpi_mensual_anual(leche_df):
            # Asegurar formato de fecha correcto
            leche_df["Fecha"] = pd.to_datetime(leche_df["Fecha"], errors="coerce")

            # Extraer mes y año
            leche_df["Mes"] = leche_df["Fecha"].dt.month
            leche_df["Año"] = leche_df["Fecha"].dt.year

            # Agrupaciones
            litros_mensuales = leche_df.groupby(["Año", "Mes"])["Litros"].sum().reset_index()
            litros_anuales = leche_df.groupby("Año")["Litros"].sum().reset_index()

            # Cálculos
            promedio_mensual_total = litros_mensuales["Litros"].mean()
            promedio_anual_total = litros_anuales["Litros"].mean()

            # Mostrar en cajas con diseño
            st.markdown("---")
            st.markdown("### 📊 Producción Promedio")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    f"""
                    <div style='background-color:#DFF0D8; padding:20px; border-radius:10px; text-align:center'>
                        <h4 style='color:#3C763D;'>Promedio mensual total</h4>
                        <p style='font-size:24px; font-weight:bold'>{promedio_mensual_total:,.0f} litros</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"""
                    <div style='background-color:#D9EDF7; padding:20px; border-radius:10px; text-align:center'>
                        <h4 style='color:#31708F;'>Promedio anual producido</h4>
                        <p style='font-size:24px; font-weight:bold'>{promedio_anual_total:,.0f} litros</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        kpi_produccion_leche(leche_df)
        kpi_mensual_anual(leche_df)


        st.markdown("---")
        def kpi_ingresos(leche_df):
            # Asegurar que Fecha es datetime
            leche_df["Fecha"] = pd.to_datetime(leche_df["Fecha"], errors="coerce")

            # Extraer mes y año
            leche_df["Mes"] = leche_df["Fecha"].dt.month
            leche_df["Año"] = leche_df["Fecha"].dt.year

            # Calcular ingresos diarios
            leche_df["Ingreso"] = leche_df["Litros"] * leche_df["Precio"]

            # Ingresos mensuales y anuales
            ingresos_mensuales = leche_df.groupby(["Año", "Mes"])["Ingreso"].sum().reset_index()
            ingresos_anuales = leche_df.groupby("Año")["Ingreso"].sum().reset_index()

            # Promedios
            promedio_mensual_ingreso = ingresos_mensuales["Ingreso"].mean()
            promedio_anual_ingreso = ingresos_anuales["Ingreso"].mean()

            # Mostrar en cajas con estilo
            st.markdown("### 💰 Ingresos por Producción Lechera")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    f"""
                    <div style='background-color:#FCF8E3; padding:20px; border-radius:10px; text-align:center'>
                        <h4 style='color:#8A6D3B;'>Promedio mensual de ingresos</h4>
                        <p style='font-size:24px; font-weight:bold'>${promedio_mensual_ingreso:,.2f}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"""
                    <div style='background-color:#F2DEDE; padding:20px; border-radius:10px; text-align:center'>
                        <h4 style='color:#A94442;'>Promedio anual de ingresos</h4>
                        <p style='font-size:24px; font-weight:bold'>${promedio_anual_ingreso:,.2f}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Gráfico de ingresos mensuales
            fig = px.bar(
                ingresos_mensuales,
                x="Mes",
                y="Ingreso",
                color="Año",
                barmode="group",
                text="Ingreso",
                title="Ingresos por Mes",
                labels={"Ingreso": "Ingresos ($)", "Mes": "Mes"}
            )
            fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
            fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

            st.plotly_chart(fig, use_container_width=True)

        kpi_ingresos(leche_df)


        st.markdown("---")
        st.header("🔄 Resumen de Rotaciones de Potreros")

        # Cargar rotaciones
        try:
            rotaciones_df = pd.read_csv("rotaciones_potrero.csv", parse_dates=["Fecha Rotacion"])
        except FileNotFoundError:
            rotaciones_df = pd.DataFrame(columns=["Fecha Rotacion", "Grupo", "Potrero_Anterior", "Potrero_Nuevo", "Comentario"])

        if rotaciones_df.empty:
            st.info("No se han registrado rotaciones de potrero aún.")
        else:
            # KPI: total de rotaciones
            total_rotaciones = len(rotaciones_df)
            st.metric("📦 Total de rotaciones registradas", total_rotaciones)

            # KPI: rotaciones por grupo
            rotaciones_por_grupo = rotaciones_df["Grupo"].value_counts().reset_index()
            rotaciones_por_grupo.columns = ["Grupo de Animal", "Número de Rotaciones"]
            st.dataframe(rotaciones_por_grupo)

            # Mostrar últimas 5 rotaciones
            st.subheader("📋 Últimas 5 rotaciones")
            ultimas = rotaciones_df.sort_values("Fecha Rotacion", ascending=False).head(5)
            ultimas["Fecha Rotacion"] = pd.to_datetime(ultimas["Fecha Rotacion"], errors="coerce")
            ultimas["Fecha Rotacion"] = ultimas["Fecha Rotacion"].dt.strftime("%Y-%m-%d")
            ultimas = ultimas[["Fecha Rotacion", "Grupo", "Potrero_Anterior", "Potrero_Nuevo", "Comentario"]]
            st.table(ultimas)


        st.markdown("---")
        st.header("📍 Distribución Actual de Animales en Potreros")

        try:
            animales_df = pd.read_csv("animales.csv")
        except FileNotFoundError:
            animales_df = pd.DataFrame(columns=["Tipo", "Potrero"])

        if animales_df.empty:
            st.info("No hay animales registrados actualmente.")
        else:
            distribucion = animales_df.groupby(["Potrero", "Tipo"]).size().reset_index(name="Cantidad")
            total_animales = distribucion["Cantidad"].sum()

            # Mostrar texto resumido por potrero
            potreros_unicos = distribucion["Potrero"].unique()
            for potrero in sorted(potreros_unicos):
                sub_df = distribucion[distribucion["Potrero"] == potrero]
                descripciones = [f"{row['Cantidad']} {row['Tipo'].lower()}" for _, row in sub_df.iterrows()]
                st.markdown(f"**{potrero}** — {', '.join(descripciones)}")






    with tab3:


        st.markdown("### 🔍 Consulta de Precio de Leche en un Día Específico")

        # Cargar datos y asegurar que la fecha esté bien formateada
        leche_df["Fecha"] = pd.to_datetime(leche_df["Fecha"], errors="coerce")

        # Selector de fecha
        fecha_consulta = st.date_input("Selecciona la fecha que deseas consultar")

        # Buscar ese día en el dataframe
        resultado = leche_df[leche_df["Fecha"] == pd.to_datetime(fecha_consulta)]

        if not resultado.empty:
            precio = resultado["Precio"].values[0]
            litros = resultado["Litros"].values[0]
            ingreso = litros * precio

            st.success(f"📅 El {fecha_consulta.strftime('%d/%m/%Y')} el precio fue de **${precio:.2f}** por litro.")
            st.info(f"Se produjeron **{litros:.2f} litros**, generando **${ingreso:.2f}** en ingresos ese día.")
        else:
            st.warning("⚠️ No se encontró información para esa fecha.")

        # Opción para mostrar el DataFrame completo
        if st.checkbox("Mostrar todos los registros de leche"):
            st.dataframe(leche_df.sort_values("Fecha", ascending=False))

    #-----------------------------------------------------------------------------------------#

        st.markdown("---")
        st.markdown("### 📄 ¿Necesita ver el listado completo de animales?")
        st.info("Use los filtros y presione el botón para mostrar los registros que desea visualizar.")

        # Filtros dinámicos basados en los datos actuales
        potreros_unicos = animales_df["Potrero"].dropna().unique().tolist()
        tipos_unicos = animales_df["Tipo"].dropna().unique().tolist()
        comentarios_unicos = animales_df["Comentarios"].dropna().unique().tolist()

        # Filtros seleccionables
        filtro_potrero = st.multiselect("📍 Filtrar por Potrero", sorted(potreros_unicos))
        filtro_tipo = st.multiselect("🐄 Filtrar por Tipo de animal", sorted(tipos_unicos))
        filtro_comentarios = st.multiselect("🗒️ Filtrar por Comentarios", sorted(comentarios_unicos))

        # Botón para mostrar resultados filtrados
        if st.button("🔍 Mostrar animales filtrados"):
            df_filtrado = animales_df.copy()

            # Aplicar filtros si están seleccionados
            if filtro_potrero:
                df_filtrado = df_filtrado[df_filtrado["Potrero"].isin(filtro_potrero)]
            if filtro_tipo:
                df_filtrado = df_filtrado[df_filtrado["Tipo"].isin(filtro_tipo)]
            if filtro_comentarios:
                df_filtrado = df_filtrado[df_filtrado["Comentarios"].isin(filtro_comentarios)]

            if df_filtrado.empty:
                st.warning("⚠️ No se encontraron animales con los filtros seleccionados.")
            else:
                st.success(f"✅ Se encontraron {len(df_filtrado)} registros:")
                st.dataframe(df_filtrado.reset_index(drop=True))

    
elif opcion == "Formulario":
    mostrar_formulario()


    # ---- HIDE STREAMLIT STYLE ----
    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)
