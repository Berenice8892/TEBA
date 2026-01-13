# cargar_alumnos.py
import os
import django

# Configura Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TEBA.settings")
django.setup()

from inicio.models import Alumno

# Lista de alumnos: (no_control, nombre, contraseña)
alumnos = [
    ("25Q02200", "ARMANDO AGUILAR LEYVA", "AGUILAR"),
    ("25Q02201", "PALOMA AGUILAR MARTINEZ", "AGUILAR"),
    ("25Q02202", "LUNA CITLALI AGUIRRE FERNANDEZ", "AGUIRRE"),
    ("25Q02203", "ALONDRA CAMACHO MENDOZA", "CAMACHO"),
    ("25Q02204", "BAYRON EDIEL CANO PEÑA", "CANO"),
    ("25Q02205", "XIMENA CASTILLO CRUZ", "CASTILLO"),
    ("25Q02206", "EVELYN DANAY GARCIA FLORES", "GARCIA"),
    ("25Q02207", "BRIAN ALDAIR GUEVARA AVENDAÑO", "GUEVARA"),
    ("25Q02208", "MARTHA IVANA HERNANDEZ AGUIRRE", "HERNANDEZ"),
    ("25Q02209", "FELIX HERNANDEZ PEÑA", "HERNANDEZ"),
    ("25Q02210", "MARIA ANDREA LOPEZ MERIÑO", "LOPEZ"),
    ("25Q02211", "MANUEL ANTONIO MENDOZA CRUZ", "MENDOZA"),
    ("25Q02212", "ARLETH YOSUANI MEZA ANGON", "MEZA"),
    ("25Q02213", "LUIS MANUEL MOLINA FLORES", "MOLINA"),
    ("25Q02214", "NAYELI MORA JIMENEZ", "MORA"),
    ("25Q02215", "CARLOS ADALBERTO MORALES CPRDERO", "MORALES"),
    ("25Q02216", "DAVID DE JESUS MORGADO LUNA", "MORGADO"),
]

# Crear alumnos si no existen
for no_control, nombre, password in alumnos:
    Alumno.objects.get_or_create(
        no_control=no_control,
        defaults={"nombre": nombre, "contraseña": password}
    )

print("✔ Alumnos cargados correctamente")
