import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io
from datetime import date # Necesario para st.date_input, aunque a veces pandas lo maneja

# --- Inicio de la función mostrar_formulario corregida ---
def mostrar_formulario():
    # Este título se mostrará cuando selecciones "Formulario" desde el menú principal de la app
    st.title("⚙️Datos de la Finca")

    # ✅ Asegurar que session_state contiene las claves antes de acceder
    if "ultimo_registro_produccion" not in st.session_state:
        st.session_state["ultimo_registro_produccion"] = []
    if "ultimo_registro" not in st.session_state:
         st.session_state["ultimo_registro"] = []
    # Inicializar session_state para bajas si no existe
    if "ultimo_registro_baja" not in st.session_state:
        st.session_state["ultimo_registro_baja"] = pd.DataFrame(columns=["Tipo", "FechaNacimiento", "PesoKg", "Potrero", "Comentarios", "Procedencia"])
    # Inicializar tipo_baja en session_state si no existe
    if "tipo_baja" not in st.session_state:
        st.session_state["tipo_baja"] = "seleccione"


    DATA_FILE = "animales.csv"
    HISTORIAL_FILE = "bajas.csv"
    LECHE_FILE = "leche.csv" # Definir el nombre del archivo de leche
    ROTACIONES_FILE = "rotaciones_potrero.csv" # Definir el nombre del archivo de rotaciones


    # --- Funciones de carga/guardado (pueden quedarse fuera o dentro, mejor dentro si solo las usa esta sección) ---
    # Las he dejado dentro de mostrar_formulario para encapsular la lógica
    def cargar_datos():
        if os.path.exists(DATA_FILE):
            # Añadir error_bad_lines=False, warn_bad_lines=False si hay problemas con filas mal formadas
            try:
                 df = pd.read_csv(DATA_FILE)
                 # Asegurarse de que las columnas de fecha existan antes de intentar convertir
                 if "FechaNacimiento" in df.columns:
                     df["FechaNacimiento"] = pd.to_datetime(df["FechaNacimiento"], errors='coerce')
                 if "FechaAdquisicion" in df.columns:
                     df["FechaAdquisicion"] = pd.to_datetime(df["FechaAdquisicion"], errors='coerce')
                 return df
            except Exception as e:
                 st.error(f"Error al cargar {DATA_FILE}: {e}")
                 return pd.DataFrame(columns=[
                    "Tipo", "FechaNacimiento", "FechaAdquisicion", "PesoKg", "Potrero", "Hierro",
                    "Comentarios", "Procedencia"
                ]) # Devolver DataFrame vacío con columnas esperadas

        else:
            return pd.DataFrame(columns=[
                "Tipo", "FechaNacimiento", "FechaAdquisicion", "PesoKg", "Potrero", "Hierro",
                "Comentarios", "Procedencia"
            ])

    def guardar_datos(df):
        # Convertir columnas de fecha a string antes de guardar si son datetime
        df_copy = df.copy()
        if "FechaNacimiento" in df_copy.columns and pd.api.types.is_datetime64_any_dtype(df_copy["FechaNacimiento"]):
             df_copy["FechaNacimiento"] = df_copy["FechaNacimiento"].dt.strftime('%Y-%m-%d')
        if "FechaAdquisicion" in df_copy.columns and pd.api.types.is_datetime64_any_dtype(df_copy["FechaAdquisicion"]):
            df_copy["FechaAdquisicion"] = df_copy["FechaAdquisicion"].dt.strftime('%Y-%m-%d')
        df_copy.to_csv(DATA_FILE, index=False)


    def cargar_historial():
        if os.path.exists(HISTORIAL_FILE):
            try:
                df = pd.read_csv(HISTORIAL_FILE)
                if "Fecha de salida" in df.columns:
                     df["Fecha de salida"] = pd.to_datetime(df["Fecha de salida"], errors='coerce')
                return df
            except Exception as e:
                 st.error(f"Error al cargar {HISTORIAL_FILE}: {e}")
                 return pd.DataFrame(columns=["Tipo", "Fecha de salida", "Motivo", "Comentario de Baja", "Hierro", "Potrero", "PesoKg", "Procedencia", "FechaNacimiento", "FechaAdquisicion", "Comentarios"])

        else:
            # Asegurarse de que las columnas del historial coincidan con las columnas al dar de baja animales
             return pd.DataFrame(columns=["Tipo", "Fecha de salida", "Motivo", "Comentario de Baja", "Hierro", "Potrero", "PesoKg", "Procedencia", "FechaNacimiento", "FechaAdquisicion", "Comentarios"])


    def guardar_historial(df):
        df_copy = df.copy()
        if "Fecha de salida" in df_copy.columns and pd.api.types.is_datetime64_any_dtype(df_copy["Fecha de salida"]):
            df_copy["Fecha de salida"] = df_copy["Fecha de salida"].dt.strftime('%Y-%m-%d')
        # Convertir otras fechas si existen en el df de bajas (FechaNacimiento, FechaAdquisicion)
        if "FechaNacimiento" in df_copy.columns and pd.api.types.is_datetime64_any_dtype(df_copy["FechaNacimiento"]):
            df_copy["FechaNacimiento"] = df_copy["FechaNacimiento"].dt.strftime('%Y-%m-%d')
        if "FechaAdquisicion" in df_copy.columns and pd.api.types.is_datetime64_any_dtype(df_copy["FechaAdquisicion"]):
             df_copy["FechaAdquisicion"] = df_copy["FechaAdquisicion"].dt.strftime('%Y-%m-%d')

        df_copy.to_csv(HISTORIAL_FILE, index=False)


    def cargar_produccion():
        if os.path.exists(LECHE_FILE):
            try:
                 df = pd.read_csv(LECHE_FILE)
                 if "Fecha" in df.columns:
                     df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce')
                 # Asegurarse de que Litros y Precio son numéricos
                 if "Litros" in df.columns:
                     df["Litros"] = pd.to_numeric(df["Litros"], errors='coerce').fillna(0)
                 if "Precio" in df.columns:
                     df["Precio"] = pd.to_numeric(df["Precio"], errors='coerce').fillna(0)
                 return df
            except Exception as e:
                 st.error(f"Error al cargar {LECHE_FILE}: {e}")
                 return pd.DataFrame(columns=["Fecha", "Litros", "Precio"])
        else:
            return pd.DataFrame(columns=["Fecha", "Litros", "Precio"])

    def guardar_produccion(df):
        df_copy = df.copy()
        if "Fecha" in df_copy.columns and pd.api.types.is_datetime64_any_dtype(df_copy["Fecha"]):
             df_copy["Fecha"] = df_copy["Fecha"].dt.strftime('%Y-%m-%d')
        df_copy.to_csv(LECHE_FILE, index=False)


    def cargar_rotaciones():
        if os.path.exists(ROTACIONES_FILE):
            try:
                 df = pd.read_csv(ROTACIONES_FILE, parse_dates=["Fecha Rotacion"])
                 if "Fecha Rotacion" in df.columns:
                     df["Fecha Rotacion"] = pd.to_datetime(df["Fecha Rotacion"], errors='coerce')
                 return df
            except Exception as e:
                 st.error(f"Error al cargar {ROTACIONES_FILE}: {e}")
                 return pd.DataFrame(columns=["Fecha Rotacion", "Grupo", "Potrero_Anterior", "Potrero_Nuevo", "Comentario"])
        else:
            return pd.DataFrame(columns=["Fecha Rotacion", "Grupo", "Potrero_Anterior", "Potrero_Nuevo", "Comentario"])


    def guardar_rotaciones(df):
        df_copy = df.copy()
        if "Fecha Rotacion" in df_copy.columns and pd.api.types.is_datetime64_any_dtype(df_copy["Fecha Rotacion"]):
             df_copy["Fecha Rotacion"] = df_copy["Fecha Rotacion"].dt.strftime('%Y-%m-%d')
        df_copy.to_csv(ROTACIONES_FILE, index=False)


    # --- Menú interno para navegar entre secciones dentro del Formulario ---
    # Este menú se mostrará en la BARRA LATERAL IZQUIERDA cuando selecciones "Formulario"
    menu = st.sidebar.radio("Opciones de Registro",
        ["Registrar animal", "Registrar bajas", "Registro Producción Lechera", "Registro de rotaciones de potrero","Borrar base datos"],
        key="form_menu_radio" # Añadir una key para evitar problemas de duplicidad si hay otros radios
    )


    # --- Contenido de cada sección del formulario (AHORA DENTRO DE mostrar_formulario) ---

    if menu == "Registrar animal":
        st.subheader("📋 Ingresar nuevo grupo de animales")

        # Cargar datos existentes para validar cantidades si es necesario, o simplemente mostrar
        # No es necesario cargar datos aquí para el registro, se cargan al guardar.


        tipo = st.selectbox("Tipo de animal", [
            "Becerro", "Becerra", "Maute", "Mauta", # Corregidos a singular según tu ejemplo anterior
            "Novilla", "Toro", "Vaca", "Vaca Preñada", "Vaca de ordeño",
        ], key="reg_animal_tipo") # Añadir keys únicas

        cantidad = st.number_input("Cantidad de animales", min_value=1, max_value=1000, step=1, key="reg_animal_cantidad") # Aumentado max_value
        procedencia = st.selectbox("Procedencia", ["Nacido en finca", "Adquirido"], key="reg_animal_procedencia")

        fecha_nac = None
        fecha_adq = None

        if procedencia == "Nacido en finca":
            fecha_nac = st.date_input("Fecha de nacimiento", key="reg_animal_fecha_nac")
            fecha_adq_str = "-" # Usar string para guardar si no aplica
        else:
            fecha_nac_str = "-" # Usar string para guardar si no aplica
            fecha_adq = st.date_input("Fecha de adquisición", key="reg_animal_fecha_adq")

        peso = st.number_input("Peso promedio (Kg)", min_value=0.0, step=0.1, key="reg_animal_peso")

        animal_Hierro = st.selectbox(
            "Hierro (¿Está marcado con hierro?)",
            ["Seleccione...", "Sí", "No"],
            key="reg_animal_hierro"
        )

        potrero = st.selectbox("Potrero asignado", ["_", "Potrero 1", "Potrero 2", "Potrero 3", "Potrero 4", "Potrero 5", "Potrero 6"], key="reg_animal_potrero")
        comentario = st.text_area("Comentarios (opcional)", key="reg_animal_comentario")

        # VALIDACIÓN EDAD PARA BECERROS/BECERRAS
        mostrar_warning_edad = False
        if tipo in ["Becerro", "Becerra"] and procedencia == "Nacido en finca" and fecha_nac is not None: # Asegurarse que fecha_nac no sea None
             hoy = datetime.now().date()
             # Asegurarse de que fecha_nac sea un objeto date
             if isinstance(fecha_nac, date):
                 edad_dias = (hoy - fecha_nac).days
                 if edad_dias > 180:
                     mostrar_warning_edad = True
                     if tipo == "Becerro":
                         st.warning(f"⚠️ La edad ingresada es {edad_dias} días. Si es mayor a 180 días, por favor registre el animal como 'Maute'.")
                     else:  # Becerras
                         st.warning(f"⚠️ La edad ingresada es {edad_dias} días. Si es mayor a 180 días, por favor registre el animal como 'Mauta'.")
             else:
                  st.warning("⚠️ Error con el formato de la fecha de nacimiento.") # Mensaje de debug si fecha_nac no es date


        if animal_Hierro == "Seleccione...":
            st.warning("⚠️ Por favor selecciona una opción válida para el campo 'Hierro'.")
            boton_guardar_deshabilitado = True
        elif mostrar_warning_edad: # Deshabilitar botón si hay advertencia de edad que bloquea
             boton_guardar_deshabilitado = True
        else:
            boton_guardar_deshabilitado = False


        if st.button("Guardar grupo de animales", disabled=boton_guardar_deshabilitado):

            data = cargar_datos() # Cargar datos justo antes de guardar

            nuevos_registros = []
            for _ in range(int(cantidad)):
                registro = {
                    "Tipo": tipo,
                    # Convertir fechas a string solo al preparar el diccionario para guardar
                    "FechaNacimiento": fecha_nac.strftime("%Y-%m-%d") if fecha_nac is not None else "-",
                    "FechaAdquisicion": fecha_adq.strftime("%Y-%m-%d") if fecha_adq is not None else "-",
                    "PesoKg": peso if peso > 0 else None, # Guardar None si es 0 o negativo para representar dato faltante
                    "Potrero": potrero if potrero != "_" else "-",
                    "Hierro": animal_Hierro,
                    "Comentarios": comentario if comentario.strip() else "-",
                    "Procedencia": procedencia
                }
                nuevos_registros.append(registro)

            st.session_state["ultimo_registro"] = nuevos_registros # Almacenar la lista completa de diccionarios

            df_nuevos = pd.DataFrame(nuevos_registros)
            # No usar dropna(how="all") aquí, porque queremos guardar filas con algunos "-" o None

            data = pd.concat([data, df_nuevos], ignore_index=True)
            guardar_datos(data)

            st.success(f"✅ Se guardaron {int(cantidad)} animales del tipo '{tipo}' correctamente.")
            st.rerun() # Opcional: Recargar la página para limpiar inputs y actualizar tabla


        # Deshacer el último ingreso
        if st.session_state["ultimo_registro"]: # Comprobar si la lista no está vacía
             if st.button("↩️ Deshacer último ingreso"):
                 data = cargar_datos() # Cargar datos antes de modificar
                 # Eliminar las últimas N filas, donde N es la cantidad de registros del último ingreso
                 num_a_eliminar = len(st.session_state["ultimo_registro"])
                 if len(data) >= num_a_eliminar:
                     data = data.iloc[:-num_a_eliminar] # Usar iloc para eliminar por índice numérico
                     guardar_datos(data)
                     st.session_state["ultimo_registro"] = [] # Limpiar el registro de session_state
                     st.warning(f"⚠️ Últimos {num_a_eliminar} animal(es) eliminados correctamente.")
                     st.rerun() # Recargar para actualizar tabla
                 else:
                     st.error("❌ No hay suficientes registros para deshacer el último ingreso.") # Mensaje de seguridad

        st.subheader("📄 Registros actuales de animales")
        # Asegurarse de cargar los datos actualizados para mostrar
        df_mostrar = cargar_datos().copy()
        # Convertir columnas de fecha a string si son datetime para evitar problemas de formato al mostrar
        if "FechaNacimiento" in df_mostrar.columns and pd.api.types.is_datetime64_any_dtype(df_mostrar["FechaNacimiento"]):
             df_mostrar["FechaNacimiento"] = df_mostrar["FechaNacimiento"].dt.strftime('%Y-%m-%d')
        if "FechaAdquisicion" in df_mostrar.columns and pd.api.types.is_datetime64_any_dtype(df_mostrar["FechaAdquisicion"]):
             df_mostrar["FechaAdquisicion"] = df_mostrar["FechaAdquisicion"].dt.strftime('%Y-%m-%d')

        st.dataframe(df_mostrar, use_container_width=True)

        # Descargar Excel (Este bloque estaba bien, solo lo muevo dentro de la función)
        output = io.BytesIO()
        # Asegurarse de que df_mostrar tiene las fechas como strings o un formato compatible con ExcelWriter si no quieres string
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
             # Convertir fechas a string explícitamente para Excel si no se hizo antes
             df_excel = cargar_datos().copy() # Cargar de nuevo para asegurar formato correcto si es necesario
             if "FechaNacimiento" in df_excel.columns and pd.api.types.is_datetime64_any_dtype(df_excel["FechaNacimiento"]):
                  df_excel["FechaNacimiento"] = df_excel["FechaNacimiento"].dt.strftime('%Y-%m-%d')
             if "FechaAdquisicion" in df_excel.columns and pd.api.types.is_datetime64_any_dtype(df_excel["FechaAdquisicion"]):
                  df_excel["FechaAdquisicion"] = df_excel["FechaAdquisicion"].dt.strftime('%Y-%m-%d')

             df_excel.to_excel(writer, index=False, sheet_name='Animales')
        datos_excel = output.getvalue()

        st.download_button(
            label="📥 Descargar Excel (.xlsx)",
            data=datos_excel,
            file_name="registro_animales_el_tornado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


    # -------- REGISTRAR BAJAS --------
    # Este bloque estaba bien, solo lo muevo dentro de mostrar_formulario y reviso detalles
    elif menu == "Registrar bajas":

        st.subheader("🔪 Registrar bajas de animales")

# Cargar datos
        data = cargar_datos()  # Cargar el dataframe principal de animales
        historial_bajas = cargar_historial()  # Cargar el historial de bajas

        if data.empty:
            st.warning("⚠️ No hay registros de animales disponibles para dar de baja.")
        else:
            st.subheader("📄 Registros actuales de animales disponibles")
            st.dataframe(data, use_container_width=True)

            tipos_animales_disponibles = sorted(data["Tipo"].dropna().unique().tolist())
            tipos_animales_disponibles = ['seleccione'] + tipos_animales_disponibles

            if st.session_state["tipo_baja"] not in tipos_animales_disponibles:
                st.session_state["tipo_baja"] = 'seleccione'

            tipo_seleccionado = st.selectbox(
                "Selecciona el tipo de animal a dar de baja:",
                tipos_animales_disponibles,
                index=tipos_animales_disponibles.index(st.session_state["tipo_baja"]),
                key="baja_tipo_animal"
            )

            st.session_state["tipo_baja"] = tipo_seleccionado

            if tipo_seleccionado != 'seleccione':
                animales_disponibles_tipo = data[data["Tipo"] == tipo_seleccionado]

                cantidad_maxima = len(animales_disponibles_tipo)
                cantidad_a_dar_de_baja = st.number_input(
                    f"Cantidad de animales tipo '{tipo_seleccionado}' a dar de baja:",
                    min_value=1,
                    max_value=cantidad_maxima,
                    step=1,
                    key="baja_cantidad"
                )

                motivo = st.selectbox("Motivo de baja", ["Vendido", "Muerto", "Otros"], key="baja_motivo")
                fecha_baja = st.date_input("Fecha de salida", key="baja_fecha")
                comentario_baja = st.text_area("Comentario sobre la baja", key="baja_comentario")

                st.markdown(f"<div style='font-size:22px; font-weight:bold; color:#2980B9;'>Actualmente hay {cantidad_maxima} animales tipo {tipo_seleccionado} disponibles.</div>", unsafe_allow_html=True)

                st.subheader(f"Lista de animales tipo '{tipo_seleccionado}'")
                st.dataframe(animales_disponibles_tipo, use_container_width=True)

                opciones_indices = animales_disponibles_tipo.index.tolist()

                seleccion_indices = st.multiselect(
                    f"Selecciona exactamente {cantidad_a_dar_de_baja} animales por su índice:",
                    opciones_indices,
                    key="baja_seleccion_indices"
                )

                cantidad_seleccionada = len(seleccion_indices)
                st.write(f"Cantidad de animales seleccionados: **{cantidad_seleccionada}**")

                if st.button("Registrar baja"):
                    if cantidad_seleccionada == cantidad_a_dar_de_baja:
                        bajas_a_registrar = data.loc[seleccion_indices].copy()
                        bajas_a_registrar["Motivo"] = motivo
                        bajas_a_registrar["Fecha de salida"] = fecha_baja
                        bajas_a_registrar["Comentario de Baja"] = comentario_baja

                        historial_bajas = cargar_historial()
                        historial_bajas = pd.concat([historial_bajas, bajas_a_registrar], ignore_index=True)
                        guardar_historial(historial_bajas)

                        data = data.drop(index=seleccion_indices)
                        guardar_datos(data)

                        st.session_state["ultimo_registro_baja"] = bajas_a_registrar.copy()

                        st.success(f"✅ Se ha registrado la baja de {cantidad_seleccionada} animal(es) del tipo '{tipo_seleccionado}' con motivo '{motivo}'.")
                        st.rerun()
                    else:
                        st.warning(f"⚠️ Debes seleccionar exactamente {cantidad_a_dar_de_baja} animales. Actualmente seleccionaste {cantidad_seleccionada}.")

            else:
                st.info("⚠️ Por favor, selecciona un tipo de animal válido para dar de baja.")

        if "ultimo_registro_baja" in st.session_state and not st.session_state["ultimo_registro_baja"].empty:
            if st.button("↩️ Deshacer última baja"):
                registros_a_restaurar = st.session_state["ultimo_registro_baja"].copy()

                cols_baja_a_eliminar = ["Motivo", "Fecha de salida", "Comentario de Baja"]
                for col in cols_baja_a_eliminar:
                    if col in registros_a_restaurar.columns:
                        registros_a_restaurar = registros_a_restaurar.drop(columns=[col])

                data = cargar_datos()
                registros_a_restaurar = registros_a_restaurar.dropna(how="all", axis=1)

                if not registros_a_restaurar.empty:
                    data = pd.concat([data, registros_a_restaurar], ignore_index=True)
                    guardar_datos(data)

                historial_bajas = cargar_historial()
                num_a_restaurar = len(registros_a_restaurar)
                if len(historial_bajas) >= num_a_restaurar:
                    historial_bajas = historial_bajas.iloc[:-num_a_restaurar]
                    guardar_historial(historial_bajas)
                else:
                    st.error("Error al deshacer: No hay suficientes registros en el historial para eliminar.")

                st.session_state["ultimo_registro_baja"] = pd.DataFrame(columns=["Tipo", "Fecha de salida", "Motivo", "Comentario de Baja"])
                st.warning(f"⚠️ Última baja de {num_a_restaurar} animal(es) revertida correctamente.")
                st.rerun()

        st.subheader("📄 Historial completo de bajas")
        historial_bajas_mostrar = cargar_historial()
        if "Fecha de salida" in historial_bajas_mostrar.columns and pd.api.types.is_datetime64_any_dtype(historial_bajas_mostrar["Fecha de salida"]):
            historial_bajas_mostrar["Fecha de salida"] = historial_bajas_mostrar["Fecha de salida"].dt.strftime('%Y-%m-%d')

        st.dataframe(historial_bajas_mostrar, use_container_width=True)



    # -------- REGISTRO DE PRODUCCIÓN DE LECHE --------
    # Este bloque estaba bien, solo lo muevo dentro de mostrar_formulario
    elif menu == "Registro Producción Lechera":
        st.subheader("🥛 Registro de Producción de Leche")


        # Cargar datos de leche para obtener el último precio si existe
        df_leche_actual = cargar_produccion()
        ultimo_precio = 0.0 # Valor por defecto
        if not df_leche_actual.empty:
            # Asegurarse de que la columna Precio sea numérica antes de tomar el último valor
            df_leche_actual["Precio"] = pd.to_numeric(df_leche_actual["Precio"], errors='coerce')
            # Tomar el último precio no nulo si existe
            if df_leche_actual["Precio"].notna().any():
                 ultimo_precio = df_leche_actual["Precio"].dropna().iloc[-1]
            else:
                 ultimo_precio = 0.0 # Si todos los precios son NaN

        litros = st.number_input("Ingrese la cantidad de litros", min_value=0.0, step=0.1, format="%.2f", key="leche_litros") # Formato para mostrar decimales
        # Usar el último precio registrado como valor por defecto
        precio = st.number_input("Ingrese precio por litro", min_value=0.0, step=0.01, format="%.2f", value=ultimo_precio, key="leche_precio")
        fecha = st.date_input("Seleccione fecha", key="leche_fecha")


        if st.button("Guardar producción"):
            df_leche = cargar_produccion() # Cargar datos justo antes de guardar

            # No necesitas esta verificación si cargar_produccion ya devuelve un DataFrame vacío
            # if df_leche.empty:
            #     df_leche = pd.DataFrame(columns=["Fecha", "Litros", "Precio"])

            nuevo_registro = {
                "Fecha": str(fecha), # Guardar como string YYYY-MM-DD
                "Litros": litros,
                "Precio": precio
            }

            # Almacenar en session_state como una lista de diccionarios
            st.session_state["ultimo_registro_produccion"] = [nuevo_registro]

            df_leche = pd.concat([df_leche, pd.DataFrame([nuevo_registro])], ignore_index=True)
            guardar_produccion(df_leche)

            st.success("✅ Producción registrada exitosamente")
            st.rerun() # Recargar para actualizar la tabla y limpiar inputs


        # Mostrar tabla de producción registrada
        df_leche_mostrar = cargar_produccion() # Cargar datos actualizados para mostrar
        if not df_leche_mostrar.empty:
            st.markdown("### 📊 Producción registrada")
            # Asegurarse de que las columnas sean numéricas para el cálculo total si no se hizo en cargar_produccion
            df_leche_mostrar["Litros"] = pd.to_numeric(df_leche_mostrar["Litros"], errors='coerce').fillna(0)
            df_leche_mostrar["Precio"] = pd.to_numeric(df_leche_mostrar["Precio"], errors='coerce').fillna(0)

            # Calcular el total
            total_litros = df_leche_mostrar["Litros"].sum()
            # El total de precio no tiene sentido, pero el total de ingresos sí
            # total_precio = df_leche_mostrar["Precio"].sum() # Esto no es útil

            # Calcular Ingresos Totales si tienes columna Precio y Litros
            if "Precio" in df_leche_mostrar.columns:
                df_leche_mostrar["Ingreso"] = df_leche_mostrar["Litros"] * df_leche_mostrar["Precio"]
                total_ingresos = df_leche_mostrar["Ingreso"].sum()
                st.write(f"**Total de litros registrados:** {total_litros:,.2f} L")
                st.write(f"**Total de ingresos registrados:** ${total_ingresos:,.2f}")

                # Mostrar DataFrame con Ingreso
                st.dataframe(df_leche_mostrar[["Fecha", "Litros", "Precio", "Ingreso"]].sort_values("Fecha", ascending=False), use_container_width=True, hide_index=True)

            else:
                 st.write(f"**Total de litros registrados:** {total_litros:,.2f} L")
                 st.dataframe(df_leche_mostrar[["Fecha", "Litros", "Precio"]].sort_values("Fecha", ascending=False), use_container_width=True, hide_index=True)


        # Deshacer última producción
        if "ultimo_registro_produccion" in st.session_state and st.session_state["ultimo_registro_produccion"]:
            st.subheader("⏪ Opciones de recuperación")
            if st.button("↩️ Deshacer última producción"):
                df_leche = cargar_produccion() # Cargar el estado actual
                # Obtener la cantidad de registros a eliminar de session_state
                num_a_eliminar = len(st.session_state["ultimo_registro_produccion"])

                if len(df_leche) >= num_a_eliminar:
                     # Eliminar las últimas N filas
                     df_leche = df_leche.iloc[:-num_a_eliminar]
                     guardar_produccion(df_leche)
                     st.session_state["ultimo_registro_produccion"] = [] # Limpiar session_state
                     st.warning("⚠️ Último registro de producción eliminado correctamente.")
                     st.rerun() # Recargar para actualizar tabla
                else:
                    st.error("❌ No hay suficientes registros para deshacer la última producción.")


    # -------- REGISTRO DE ROTACIONES --------
    # Este bloque estaba bien, solo lo muevo dentro de mostrar_formulario y reviso detalles
    elif menu == "Registro de rotaciones de potrero":
        st.subheader("🔄 Registro de rotaciones de potreros")


        # Las funciones de carga/guardado de rotaciones ya están definidas dentro de mostrar_formulario

        df_animales = cargar_datos() # Cargar el dataframe principal de animales
        df_rotaciones = cargar_rotaciones() # Cargar el historial de rotaciones


        if df_animales.empty:
            st.warning("⚠️ No hay animales registrados para asignar rotación.")
        else:
            # Mostrar estado actual de animales en potreros (movido dentro del elif)
            st.markdown("### 📍 Estado actual de animales en potreros")
            estado_actual = df_animales.groupby(["Potrero", "Tipo"]).size().reset_index(name="Cantidad")
            # Manejar el caso donde no hay potreros asignados ("-")
            if not estado_actual.empty:
                # Asegurarse de que 'Potrero' es string o manejable por sorted
                estado_actual["Potrero"] = estado_actual["Potrero"].astype(str)
                potreros_en_animales = sorted(estado_actual["Potrero"].unique())

                for potrero in potreros_en_animales:
                    sub_df = estado_actual[estado_actual["Potrero"] == potrero]
                    descripcion = [f"{row['Cantidad']} {row['Tipo'].lower()}" for _, row in sub_df.iterrows()]
                    st.markdown(f"**{potrero}** — {', '.join(descripcion)}")
            else:
                 st.info("No hay animales asignados a potreros.")

            st.markdown("---")

            # Definir los grupos/tipos que se pueden rotar
            # Usar los tipos únicos presentes en el dataframe de animales para los selectboxes
            tipos_disponibles_animales = sorted(df_animales["Tipo"].dropna().unique().tolist())
            # Añadir un valor por defecto si la lista está vacía
            if not tipos_disponibles_animales:
                 tipos_disponibles_animales = ["No hay tipos disponibles"]


            # Obtener lista de potreros únicos del dataframe de animales (excluir "-")
            potreros_existentes = sorted(df_animales["Potrero"].dropna().unique().tolist())
            if "-" in potreros_existentes:
                 potreros_existentes.remove("-")

            # Añadir un valor por defecto si no hay potreros válidos
            if not potreros_existentes:
                 potreros_existentes = ["No hay potreros asignados"]

            fecha = st.date_input("Fecha de rotación", key="rotacion_fecha")
            tipo_seleccionado_rotacion = st.selectbox(
                "Selecciona tipo de animal para rotar",
                tipos_disponibles_animales,
                key="rotacion_tipo"
            )

            # Filtrar potreros donde EXISTEN animales del tipo seleccionado
            potreros_con_este_tipo = df_animales[df_animales["Tipo"] == tipo_seleccionado_rotacion]["Potrero"].dropna().unique().tolist()
            if "-" in potreros_con_este_tipo:
                 potreros_con_este_tipo.remove("-")

            # Añadir un valor por defecto si no hay potreros para este tipo
            if not potreros_con_este_tipo:
                 potreros_con_este_tipo = ["No hay potreros con este tipo"]

            # Asegurarse de que el potrero anterior seleccionado esté en la lista de potreros con este tipo
            potrero_anterior = st.selectbox(
                "Potrero actual de este grupo",
                potreros_con_este_tipo,
                key="rotacion_potrero_anterior"
            )

            # Opciones para el nuevo potrero (todos los potreros existentes menos el actual)
            opciones_nuevo_potrero = [p for p in potreros_existentes if p != potrero_anterior]
            # Añadir un valor por defecto si solo hay un potrero o ninguno válido
            if not opciones_nuevo_potrero:
                 opciones_nuevo_potrero = ["No hay potreros disponibles"]


            potrero_nuevo = st.selectbox(
                "Nuevo potrero",
                 opciones_nuevo_potrero,
                 key="rotacion_potrero_nuevo"
            )

            comentario_rotacion = st.text_area("Comentario adicional (opcional)", key="rotacion_comentario")


            # Filtrar animales disponibles para mover (del tipo y potrero anterior)
            disponibles_para_rotar = df_animales[(df_animales["Tipo"] == tipo_seleccionado_rotacion) & (df_animales["Potrero"] == potrero_anterior)]


            st.write(f"📦 Animales disponibles en **{potrero_anterior}** del grupo '{tipo_seleccionado_rotacion}': **{len(disponibles_para_rotar)}**")

            # Solo mostrar opciones de movimiento si hay animales disponibles y potrero nuevo válido
            if len(disponibles_para_rotar) > 0 and potrero_nuevo in potreros_existentes: # Verificar que potrero_nuevo es un potrero real
                 mover_todos = st.checkbox("Mover todos los animales de este grupo en este potrero", value=True, key="rotacion_mover_todos")
                 cantidad_a_mover = len(disponibles_para_rotar) # Valor por defecto si "mover todos" está marcado

                 if not mover_todos:
                     cantidad_a_mover = st.number_input(
                         "Cantidad a mover",
                         min_value=1,
                         max_value=len(disponibles_para_rotar),
                         step=1,
                         key="rotacion_cantidad_a_mover"
                     )

                 # Deshabilitar el botón si no hay animales para mover O si no hay potrero nuevo válido
                 if st.button("📥 Guardar rotación", disabled=(len(disponibles_para_rotar) == 0 or potrero_nuevo == "No hay potreros disponibles")):
                      if cantidad_a_mover > 0:
                           indices = disponibles_para_rotar.index[:cantidad_a_mover] # Seleccionar los primeros 'cantidad_a_mover' animales
                           df_animales.loc[indices, "Potrero"] = potrero_nuevo # Actualizar el potrero en el df principal
                           guardar_datos(df_animales) # Guardar el df principal actualizado

                           # Registrar en el historial de rotaciones
                           nuevo_registro_rotacion = {
                               "Fecha Rotacion": fecha,
                               "Grupo": tipo_seleccionado_rotacion,
                               "Potrero_Anterior": potrero_anterior,
                               "Potrero_Nuevo": potrero_nuevo,
                               "Comentario": comentario_rotacion if comentario_rotacion.strip() else "-"
                           }
                           df_rotaciones = cargar_rotaciones() # Recargar por si acaso
                           df_rotaciones = pd.concat([df_rotaciones, pd.DataFrame([nuevo_registro_rotacion])], ignore_index=True)
                           guardar_rotaciones(df_rotaciones) # Guardar el historial actualizado


                           st.success(f"✅ Se movieron {cantidad_a_mover} animal(es) del grupo '{tipo_seleccionado_rotacion}' de **{potrero_anterior}** a **{potrero_nuevo}**")
                           st.rerun() # Recargar para actualizar tablas y inputs
                      else:
                           st.warning("La cantidad a mover debe ser mayor que 0.")
            elif potrero_nuevo == "No hay potreros disponibles":
                 st.warning("⚠️ No hay potreros disponibles para mover los animales.")
            else:
                 st.info("No hay animales de este grupo en el potrero seleccionado para mover.")


            # Mostrar historial de rotaciones
            if not df_rotaciones.empty:
                st.markdown("### 📋 Historial de rotaciones")
                # Formatear la columna de fecha para mostrar
                if "Fecha Rotacion" in df_rotaciones.columns and pd.api.types.is_datetime64_any_dtype(df_rotaciones["Fecha Rotacion"]):
                     df_rotaciones["Fecha Rotacion"] = df_rotaciones["Fecha Rotacion"].dt.strftime('%Y-%m-%d')
                st.dataframe(df_rotaciones.sort_values("Fecha Rotacion", ascending=False), use_container_width=True)


                
    elif menu == "Borrar base datos":
            
        
        st.markdown("### 🧨 Borrar toda la base de datos (solo para reinicio)")
        st.warning("Esta acción eliminará *todos los datos actuales* de la finca. Úselo solo si está seguro.")

        clave = st.text_input("Ingrese la clave para borrar los datos", type="password")
        clave_correcta = "Ethan2024"

        if st.button("Borrar base de datos"):
            if clave == clave_correcta:
                try:
                    # Definir los encabezados de cada CSV según tus archivos
                    encabezados = {
                        "animales.csv": ["Tipo", "FechaNacimiento", "FechaAdquisicion", "Potrero", "Comentarios", "Hierro", "Procedencia"],
                        "leche.csv": ["Fecha", "Litros", "Precio"],
                        "bajas.csv": ["Tipo", "Fecha de salida", "Motivo", "Comentario de Baja", "Hierro", "Potrero", "PesoKg", "Procedencia", "FechaNacimiento", "FechaAdquisicion", "Comentarios"],
                        "rotaciones_potrero.csv": ["Fecha Rotacion", "Grupo", "Potrero_Anterior", "Potrero_Nuevo", "Comentario"]
                    }

                    for archivo, cols in encabezados.items():
                        df_vacio = pd.DataFrame(columns=cols)
                        df_vacio.to_csv(archivo, index=False)

                    st.success("✅ Todos los datos fueron borrados (archivos vacíos).")
                    st.rerun()  # Recarga la app para reflejar cambios

                except Exception as e:
                    st.error(f"Ocurrió un error al borrar los datos: {e}")
            else:
                st.error("❌ Clave incorrecta. No se realizó ninguna acción.")







