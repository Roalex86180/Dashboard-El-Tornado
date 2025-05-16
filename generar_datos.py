import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

# Eliminar archivos existentes para evitar conflictos
for archivo in ['animales.csv', 'bajas.csv', 'leche.csv', 'rotaciones_potrero.csv']:
    if os.path.exists(archivo):
        os.remove(archivo)

# Parámetros
n_animales = 110
n_vacas_de_ordeño = 30
proveedores = ['Juan Perez', 'Carlos Ruiz', 'Maria Gomez']
tipos_extra = ['Toro', 'Mauta', 'Maute', 'Novilla', 'Vacas Preñadas', 'Vacas']

# Tipos y cantidades
vacas_de_ordeño = ['Vaca de ordeño'] * n_vacas_de_ordeño
becerros = ['Becerro'] * (n_vacas_de_ordeño // 2)
becerras = ['Becerra'] * (n_vacas_de_ordeño - len(becerros))  # Para asegurar que Becerros + Becerras = Vacas
tipos_principales = vacas_de_ordeño + becerros + becerras
tipos_restantes = random.choices(tipos_extra, k=n_animales - len(tipos_principales))
tipos = tipos_principales + tipos_restantes

# Fechas de nacimiento
hoy = datetime.today()
fechas_nacimiento = []
for tipo in tipos:
    if tipo in ['Becerro', 'Becerra']:
        fecha_nac = hoy - timedelta(days=random.randint(1, 180))
    else:
        fecha_nac = hoy - timedelta(days=random.randint(365, 1825))
    fechas_nacimiento.append(fecha_nac.strftime('%Y-%m-%d'))

# Procedencia, comentarios y fechas de adquisición
procedencias = []
comentarios = []
fechas_adquisicion = []
hierros = []
for tipo in tipos:
    if tipo == 'Vaca':
        if random.random() < 0.5:
            proveedor = random.choice(proveedores)
            procedencias.append('Adquirido')
            comentarios.append(f'Comprado a {proveedor}')
            fechas_adquisicion.append(pd.to_datetime(np.random.choice(pd.date_range('2020-01-01', '2023-12-31'))).strftime('%Y-%m-%d'))
        else:
            procedencias.append('Nacido en finca')
            comentarios.append('Cría propia')
            fechas_adquisicion.append('')
    else:
        procedencias.append('Nacido en finca')
        comentarios.append('Cría propia')
        fechas_adquisicion.append('')

    if tipo in ['Becerro', 'Becerra']:
        hierros.append(random.choice(['Sí', 'No']))
    else:
        hierros.append('Sí')


animales = pd.DataFrame({
    'Tipo': tipos,
    'FechaNacimiento': fechas_nacimiento,
    'FechaAdquisicion': fechas_adquisicion,
    'PesoKg': np.random.randint(200, 700, size=len(tipos)),
    'Potrero': [f'Potrero {random.randint(1, 6)}' for _ in range(len(tipos))],
    'Hierro': hierros,
    'Comentarios': comentarios,
    'Procedencia': procedencias,
    
})

animales.to_csv("animales.csv", index=False)

# Generar bajas
# Generar bajas (10 animales aleatorios)
bajas = animales.sample(10).copy()
bajas['Fecha'] = pd.to_datetime(np.random.choice(pd.date_range('2024-01-01', '2025-12-31'), 10)).strftime('%Y-%m-%d')
bajas['Comentario'] = ['Baja automática con nota'] * 10

# Ajustar motivos según lo esperado por app.py
motivos_posibles = ['vendido', 'muerto', 'otros']
bajas['Motivo'] = np.random.choice(motivos_posibles, 10)

# Comentarios de baja según motivo
comentarios_baja = []
for motivo in bajas['Motivo']:
    if motivo == 'vendido':
        comentario = random.choice(["Vendida a Doris", "Vendida a Martha", "Vendida a Mato Arrecho"])
    elif motivo == 'muerto':
        comentario = random.choice(["Enfermedad", "Accidente", "Edad avanzada"])
    elif motivo == 'otros':
        comentario = random.choice(["Intercambiado con finca El Milagro", "Intercambio con finca Las Rosas"])
    
    else:
        comentario = "Sin comentario"
    comentarios_baja.append(comentario)

bajas['Fecha de salida'] = bajas['Fecha']
bajas['Comentario de Baja'] = comentarios_baja

bajas = bajas[["Tipo", "Fecha de salida", "Motivo", "Comentario de Baja", "Hierro", "Potrero", "PesoKg", "Procedencia", "FechaNacimiento", "FechaAdquisicion", "Comentarios"]]
bajas.to_csv("bajas.csv", index=False)

# Generar leche (producción diaria total)
fecha = pd.date_range(start="2024-01-01", end="2025-12-31", freq="D").strftime('%Y-%m-%d')
produccion = []
for f in fecha:
    mes = int(f.split('-')[1])
    if mes <= 5:
        litros = random.uniform(58, 62)
        precio = 0.39
    elif 6 <= mes <= 10:
        litros = random.uniform(78, 82)
        precio = 0.42
    else:
        litros = random.uniform(68, 72)
        precio = 0.41
    produccion.append([f, round(litros, 2), precio])

leche = pd.DataFrame(produccion, columns=["Fecha", "Litros", "Precio"])
leche.to_csv("leche.csv", index=False)

# Generar rotaciones de potrero
grupos = ['Vaca', 'Becerro', 'Becerra', 'Mauta', 'Maute', 'Toro', 'Novilla']
rotaciones = []
for i in range(20):
    fecha = pd.to_datetime(np.random.choice(pd.date_range('2024-01-01', '2025-12-31'))).strftime('%Y-%m-%d')
    grupo = random.choice(grupos)
    potrero_anterior = f"Potrero {random.randint(1, 6)}"
    potrero_nuevo = f"Potrero {random.randint(1, 6)}"
    while potrero_nuevo == potrero_anterior:
        potrero_nuevo = f"Potrero {random.randint(1, 6)}"
    comentario = f"Rotación {i+1}"
    rotaciones.append([fecha, grupo, potrero_anterior, potrero_nuevo, comentario])

rotaciones_df = pd.DataFrame(rotaciones, columns=["Fecha Rotacion", "Grupo", "Potrero_Anterior", "Potrero_Nuevo", "Comentario"])
rotaciones_df.to_csv("rotaciones_potrero.csv", index=False)

print("Datos simulados generados correctamente.")
