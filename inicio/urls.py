from django.urls import path
from inicio import views

urlpatterns = [
    # Inicio / Home
    path('', views.home, name='home'),
    path('inicio/', views.inicio, name='inicio'),
    

    # Planteles y noticias
    path('planteles/', views.planteles, name='planteles'),
    path('noticias/', views.noticias, name='noticias'),

    # Contacto y oferta
    path('contacto/', views.contacto, name='contacto'),
    path('oferta/', views.oferta, name='oferta'),

    # Login Alumno
    path('login/alumno/', views.login_alumno, name='login_alumno'),
    path('alumno/<str:no_control>/', views.dashboard_alumno, name='dashboard_alumno'),
    path('alumno/<str:no_control>/editar/', views.editar_alumno, name='editar_alumno'),
    path('alumno/<str:no_control>/cambiar_contraseña/', views.cambiar_contraseña, name='cambiar_contraseña'),
    path('alumno/dashboard/', views.dashboard_alumno_sesion, name='dashboard_alumno_sesion'),

    # Login Docente
    path('login/docente/', views.login_docente, name='login_docente'),
    path('docente/dashboard/', views.dashboard_docente, name='dashboard_docente'),
    path('alumnos/', views.lista_alumnos, name='lista_alumnos'),  
    

    # Alumnos (Docente)
    path('docente/alumnos/', views.lista_alumnos_docente, name='lista_alumnos_docente'),
    path('docente/alumno/<str:no_control>/', views.detalle_alumno_docente, name='detalle_alumno_docente'),
    path('docente/alumno/<str:no_control>/editar/', views.editar_alumno_docente, name='editar_alumno_docente'),
    path('docente/alumno/<str:no_control>/agregar_calificacion/', views.agregar_calificacion, name='agregar_calificacion'),

    # Agregar alumno
    path('alumnos/agregar/', views.agregar_alumno, name='agregar_alumno'),
    path('alumno/<str:no_control>/avatar/', views.actualizar_avatar, name='actualizar_avatar'),

    path('docente/pdf-alumnos/', views.descargar_pdf_alumnos, name='pdf_alumnos'),
    path('alumno/<str:no_control>/pdf/', views.descargar_calificaciones_pdf, name='descargar_calificaciones_pdf'),
    # PDF individual
    path('docente/pdf-alumno/<str:no_control>/', views.descargar_pdf_alumno, name='pdf_alumno'),
    path('editar_calificacion/<int:id>/', views.editar_calificacion, name='editar_calificacion'),
    path('eliminar_calificacion/<int:id>/', views.eliminar_calificacion, name='eliminar_calificacion'),
    path('docente/pdf-alumno/<str:no_control>/', views.descargar_pdf_alumno, name='descargar_pdf_alumno'),
]
