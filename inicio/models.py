from django.db import models



class HorarioEstandar(models.Model):
    MATERIAS = [
        ('Matemáticas', 'Matemáticas'),
        ('Español', 'Español'),
        ('Historia', 'Historia'),
        ('Ciencias', 'Ciencias'),
        ('Inglés', 'Inglés'),
    ]

    DIAS = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
    ]
    materia = models.CharField(max_length=50, choices=MATERIAS)
    dia = models.CharField(max_length=10, choices=DIAS)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    salon = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.materia} - {self.dia} {self.hora_inicio}-{self.hora_fin}"

# Planteles
class Plantel(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=300)
    telefono = models.CharField(max_length=50)
    municipio = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# Noticias
class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha = models.DateField(auto_now_add=True)
    imagen = models.ImageField(upload_to='noticias/', null=True, blank=True)

    def __str__(self):
        return self.titulo

# Mensajes de contacto
class MensajeContacto(models.Model):
    nombre = models.CharField(max_length=200)
    email = models.EmailField()
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensaje de {self.nombre}"

# Oferta educativa
class Oferta(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

# Alumnos
class Alumno(models.Model):
    no_control = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    modalidad = models.CharField(max_length=50, blank=True, null=True)
    plan_estudios = models.CharField(max_length=100, default="TEBAEV-2024")
    modulo_especialidad = models.CharField(max_length=50, blank=True, null=True)
    creditos_acumulados = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)
    situacion_vigencia = models.CharField(max_length=50, blank=True, null=True)
    periodo_ingreso = models.CharField(max_length=20, blank=True, null=True)
    periodos_convalidados = models.IntegerField(default=0)
    periodo_actual = models.CharField(max_length=20, blank=True, null=True)
    clave_curp = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    calle = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    colonia = models.CharField(max_length=50, blank=True, null=True)
    ciudad = models.CharField(max_length=50, blank=True, null=True)
    cp = models.CharField(max_length=10, blank=True, null=True)
    telefono_domicilio = models.CharField(max_length=20, blank=True, null=True)
    telefono_celular = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField()
    escuela_procedencia = models.CharField(max_length=200, blank=True, null=True)
    tutor = models.CharField(max_length=200, blank=True, null=True)
    contraseña = models.CharField(max_length=50, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)


    def __str__(self):
        return f"{self.no_control} - {self.nombre}"

# Calificaciones
class Calificacion(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name="calificaciones")
    materia = models.CharField(max_length=100)
    calificacion = models.DecimalField(max_digits=5, decimal_places=2)
    periodo = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.alumno.no_control} - {self.materia}: {self.calificacion}"

class Docente(models.Model):
    usuario = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    correo = models.EmailField()
    contraseña = models.CharField(max_length=50)  # Podría ser hashed luego
    # campos opcionales
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre
