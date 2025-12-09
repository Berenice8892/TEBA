from django.contrib import admin
from .models import Plantel, Noticia, MensajeContacto
from .models import Alumno, Calificacion

admin.site.register(Alumno)
admin.site.register(Calificacion)
admin.site.register(Plantel)
admin.site.register(Noticia)
admin.site.register(MensajeContacto)
