from django.core.management.base import BaseCommand
from inicio.models import Alumno

class Command(BaseCommand):
    help = "Carga alumnos iniciales"

    def handle(self, *args, **kwargs):
        alumnos = [
            ("25Q02200", "ARMANDO AGUILAR LEYVA", "AGUILAR"),
            ("25Q02201", "PALOMA AGUILAR MARTINEZ", "AGUILAR"),
            # agrega todos
        ]

        for no_control, nombre, password in alumnos:
            Alumno.objects.get_or_create(
                no_control=no_control,
                defaults={"nombre": nombre, "contraseña": password}  # tu campo real
            )

        self.stdout.write(self.style.SUCCESS("✔ Alumnos cargados correctamente"))
