from tkinter import Image
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q,Avg
from django.contrib import messages

from tebaev import settings
from .models import HorarioEstandar, Plantel, Noticia, MensajeContacto, Oferta, Alumno, Calificacion
from .models import Docente
from .forms import AvatarForm
from django.http import FileResponse, HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from django.contrib.staticfiles import finders
import io
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Alumno
from django.shortcuts import get_object_or_404

# PDF individual
def descargar_pdf_alumno(request, no_control):
    alumno = get_object_or_404(Alumno, no_control=no_control)
    calificaciones = alumno.calificaciones.all()

    html_string = render_to_string('pdf/reporte_alumno.html', {
        'alumno': alumno,
        'calificaciones': calificaciones
    })

    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{alumno.no_control}_calificaciones.pdf"'
    return response

def descargar_pdf_alumnos(request):
    # Obtenemos todos los alumnos y sus calificaciones
    alumnos = Alumno.objects.prefetch_related('calificaciones').all()

    # Renderizamos un template HTML a string
    html_string = render_to_string('alumnos_dashboard_pdf.html', {
        'alumnos': alumnos
    })

    # Generamos el PDF
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    # Retornamos como descarga
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="alumnos_calificaciones.pdf"'
    return response


def descargar_calificaciones_pdf(request, no_control):
    alumno = Alumno.objects.get(no_control=no_control)
    calificaciones = Calificacion.objects.filter(alumno=alumno)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # --- LOGO ---
    logo_path = os.path.join(settings.MEDIA_ROOT, 'LOGOO.jpg')  # tu logo en MEDIA
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=120, height=120)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    elements.append(Spacer(1, 20))

    # --- TÍTULO ---
    title = Paragraph(f"<b>Boleta de Calificaciones</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    subtitle = Paragraph(f"Alumno: {alumno.nombre} | No. Control: {alumno.no_control}", styles['Normal'])
    elements.append(subtitle)
    elements.append(Spacer(1, 20))

    # --- TABLA ---
    data = [['Materia', 'Calificación', 'Periodo']]
    for c in calificaciones:
        data.append([c.materia, c.calificacion, c.periodo])

    table = Table(data, colWidths=[200, 100, 100], hAlign='CENTER')
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])

    # Colores según calificación
    for i, c in enumerate(calificaciones, start=1):
        if c.calificacion >= 9:
            style.add('TEXTCOLOR', (1,i), (1,i), colors.green)
        elif c.calificacion >= 7:
            style.add('TEXTCOLOR', (1,i), (1,i), colors.orange)
        else:
            style.add('TEXTCOLOR', (1,i), (1,i), colors.red)

    table.setStyle(style)
    elements.append(table)
    elements.append(Spacer(1, 50))

    # --- ESPACIO PARA FIRMAS ---
    signatures = Table([
        ['_________________________', '_________________________'],
        ['Firma del Tutor', 'Firma del Alumno']
    ], colWidths=[250, 250], hAlign='CENTER')
    signatures.setStyle(TableStyle([
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,1), (-1,-1), 10)
    ]))
    elements.append(signatures)

    # --- GENERAR PDF ---
    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'boleta_{alumno.no_control}.pdf')

def actualizar_avatar(request, no_control):
    alumno = get_object_or_404(Alumno, no_control=no_control)
    if request.method == 'POST' and request.FILES.get('avatar'):
        alumno.avatar = request.FILES['avatar']
        alumno.save()
        messages.success(request, "Avatar actualizado correctamente")
    return redirect('dashboard_alumno', no_control=alumno.no_control)

def login_docente(request):
    if request.method == "POST":
        usuario = request.POST.get('usuario')
        contraseña = request.POST.get('password')

        try:
            docente = Docente.objects.get(usuario=usuario, contraseña=contraseña)
            # Guardar en sesión
            request.session['docente_id'] = docente.id
            messages.success(request, f"Bienvenido {docente.nombre}")
            return redirect('dashboard_docente')
        except Docente.DoesNotExist:
            messages.error(request, "Usuario o contraseña incorrecta")
    
    return render(request, 'login_docente.html')


# Dashboard docente
def dashboard_docente(request):
    alumnos = Alumno.objects.all()
    total_alumnos = alumnos.count()
    total_calificaciones = Calificacion.objects.count()

    # Promedio general
    promedio_general = Calificacion.objects.aggregate(promedio=Avg('calificacion'))['promedio']

    # Alumnos con calificación promedio < 8
    alertas_bajas = []
    for alumno in alumnos:
        promedio_alumno = alumno.calificaciones.aggregate(promedio=Avg('calificacion'))['promedio']
        if promedio_alumno and promedio_alumno < 8:
            alertas_bajas.append({
                'alumno': alumno,
                'promedio': round(promedio_alumno, 2)
            })

    # Datos para gráfica: promedio por materia
    materias = Calificacion.objects.values_list('materia', flat=True).distinct()
    promedios_materia = []
    for materia in materias:
        promedio = Calificacion.objects.filter(materia=materia).aggregate(promedio=Avg('calificacion'))['promedio']
        promedios_materia.append(round(promedio or 0, 2))

    # ✅ Agregar la lista de todos los alumnos para el dropdown de PDF individual
    return render(request, 'dashboard_docente.html', {
        'total_alumnos': total_alumnos,
        'total_calificaciones': total_calificaciones,
        'promedio_general': round(promedio_general or 0, 2),
        'alertas_bajas': alertas_bajas,
        'materias': list(materias),
        'promedios_materia': promedios_materia,
        'todos_los_alumnos': alumnos  # <-- Nuevo
    })
# Lista de alumnos con búsqueda
def lista_alumnos_docente(request):
    query = request.GET.get('q')
    if query:
        alumnos = Alumno.objects.filter(
            Q(no_control__icontains=query) | Q(nombre__icontains=query)
        )
    else:
        alumnos = Alumno.objects.all()
    return render(request, 'lista_alumnos_docente.html', {'alumnos': alumnos})

# Detalle y calificaciones
def detalle_alumno_docente(request, no_control):
    alumno = Alumno.objects.get(no_control=no_control)
    calificaciones = alumno.calificaciones.all()

    return render(request, "detalle_alumno_docente.html", {
        "alumno": alumno,
        "calificaciones": calificaciones
    })


# Agregar calificación
def agregar_calificacion(request, alumno_id):
    if request.method == "POST":
        alumno = get_object_or_404(Alumno, id=alumno_id)
        materia = request.POST['materia']
        calificacion = float(request.POST['calificacion'])
        periodo = request.POST['periodo']
        Calificacion.objects.create(
            alumno=alumno,
            materia=materia,
            calificacion=calificacion,
            periodo=periodo
        )
        messages.success(request, f"Calificación de {materia} agregada.")
        return redirect('detalle_alumno_docente', alumno_id=alumno.id)
    
def editar_calificacion(request, calificacion_id):
    calificacion = get_object_or_404(Calificacion, id=calificacion_id)

    if request.method == "POST":
        calificacion.materia = request.POST.get("materia")
        calificacion.calificacion = request.POST.get("calificacion")
        calificacion.periodo = request.POST.get("periodo")
        calificacion.save()

        messages.success(request, "Calificación actualizada correctamente.")
        return redirect('detalle_alumno_docente', no_control=calificacion.alumno.no_control)

    return render(request, 'docente/editar_calificacion.html', {
        "calificacion": calificacion
    })
def eliminar_calificacion(request, calificacion_id):
    calificacion = get_object_or_404(Calificacion, id=calificacion_id)
    no_control = calificacion.alumno.no_control

    calificacion.delete()

    messages.success(request, "Calificación eliminada correctamente.")
    return redirect('detalle_alumno_docente', no_control=no_control)


# Editar datos del alumno
def editar_alumno_docente(request, no_control):
    alumno = get_object_or_404(Alumno, no_control=no_control)
    if request.method == 'POST':
        for field in ['nombre', 'correo', 'tutor', 'periodo_actual', 'plan_estudios']:
            setattr(alumno, field, request.POST.get(field, getattr(alumno, field)))
        alumno.save()
        messages.success(request, 'Datos del alumno actualizados')
        return redirect('detalle_alumno_docente', no_control=no_control)
    return render(request, 'editar_alumno_docente.html', {'alumno': alumno})



# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Alumno

def editar_alumno(request, no_control):
    alumno = get_object_or_404(Alumno, no_control=no_control)

    if request.method == "POST":
        alumno.nombre = request.POST.get('nombre')
        alumno.correo = request.POST.get('correo')
        alumno.tutor = request.POST.get('tutor')
        # Agregar más campos editables si quieres
        alumno.save()
        messages.success(request, "Datos actualizados correctamente")
        return redirect('dashboard_alumno', no_control=alumno.no_control)

    return render(request, 'editar_alumno.html', {'alumno': alumno})

def cambiar_contraseña(request, no_control):
    alumno = get_object_or_404(Alumno, no_control=no_control)
    if request.method == "POST":
        actual = request.POST.get('contraseña_actual')
        nueva = request.POST.get('contraseña_nueva')
        confirmar = request.POST.get('confirmar_contraseña')

        if actual != alumno.contraseña:
            messages.error(request, "La contraseña actual es incorrecta")
        elif nueva != confirmar:
            messages.error(request, "La nueva contraseña y la confirmación no coinciden")
        else:
            alumno.contraseña = nueva
            alumno.save()
            messages.success(request, "Contraseña actualizada correctamente")
            return redirect('dashboard_alumno', no_control=alumno.no_control)

    return render(request, 'cambiar_contraseña.html', {'alumno': alumno})


# -------------------------------
# DASHBOARD ALUMNO
# -------------------------------
def dashboard_alumno(request, no_control):
    alumno = get_object_or_404(Alumno, no_control=no_control)
    calificaciones = alumno.calificaciones.all()
    
    # Traemos horario estándar para todos los alumnos
    horario = HorarioEstandar.objects.all().order_by('dia', 'hora_inicio')

    return render(request, 'dashboard_alumno.html', {
        'alumno': alumno,
        'calificaciones': calificaciones,
        'horario': horario
    })


# -------------------------------
def login_alumno(request):
    error = None
    if request.method == "POST":
        no_control = request.POST['no_control']
        contraseña = request.POST['contraseña']

        try:
            alumno = Alumno.objects.get(no_control=no_control, contraseña=contraseña)
            # Guardar en sesión
            request.session['no_control'] = alumno.no_control
            return redirect('dashboard_alumno', no_control=alumno.no_control)  # <-- corregido
        except Alumno.DoesNotExist:
            error = "Número de control o contraseña incorrecta"
    
    # Si no es POST o credenciales incorrectas, mostrar login con error
    return render(request, "login_alumno.html", {"error": error})



# -------------------------------
# DASHBOARD ALUMNO CON SESIÓN
# -------------------------------
def dashboard_alumno_sesion(request):
    no_control = request.session.get('no_control')
    if not no_control:
        return redirect('login_alumno')
    alumno = get_object_or_404(Alumno, no_control=no_control)
    calificaciones = alumno.calificaciones.all()
    return render(request, 'dashboard_alumno.html', {
        'alumno': alumno,
        'calificaciones': calificaciones
    })


# -------------------------------
# LISTADO DE ALUMNOS
# -------------------------------
def lista_alumnos(request):
    alumnos = Alumno.objects.all().order_by('nombre')
    datos = []
    for a in alumnos:
        calificaciones = a.calificaciones.all()
        datos.append({
            "alumno": a,
            "calificaciones": calificaciones
        })
    return render(request, "alumnos.html", {"datos": datos})

def alumnos(request):
    query = request.GET.get('q')
    if query:
        lista = Alumno.objects.filter(
            Q(no_control__icontains=query) | Q(nombre__icontains=query)
        )
    else:
        lista = Alumno.objects.all()
    return render(request, 'alumnos.html', {"alumnos": lista})

# -------------------------------
# DETALLE DE ALUMNO
# -------------------------------
def detalle_alumno(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    calificaciones = alumno.calificaciones.all()
    return render(request, 'detalle_alumno.html', {
        "alumno": alumno,
        "calificaciones": calificaciones
    })

# -------------------------------
# FORMULARIO AGREGAR ALUMNO
# -------------------------------
def agregar_alumno(request):
    if request.method == "POST":
        alumno = Alumno.objects.create(
            no_control = request.POST['no_control'],
            nombre = request.POST['nombre'],
            modalidad = request.POST.get('modalidad', ''),
            plan_estudios = request.POST['plan_estudios'],
            modulo_especialidad = request.POST['modulo_especialidad'],
            creditos_acumulados = request.POST.get('creditos_acumulados', 0),
            situacion_vigencia = request.POST['situacion_vigencia'],
            periodo_ingreso = request.POST['periodo_ingreso'],
            periodos_convalidados = request.POST.get('periodos_convalidados', 0),
            periodo_actual = request.POST['periodo_actual'],
            clave_curp = request.POST['clave_curp'],
            fecha_nacimiento = request.POST['fecha_nacimiento'],
            calle = request.POST['calle'],
            numero = request.POST['numero'],
            colonia = request.POST['colonia'],
            ciudad = request.POST['ciudad'],
            cp = request.POST['cp'],
            telefono_domicilio = request.POST['telefono_domicilio'],
            telefono_celular = request.POST['telefono_celular'],
            correo = request.POST['correo'],
            escuela_procedencia = request.POST['escuela_procedencia'],
            tutor = request.POST.get('tutor', ''),
            contraseña = request.POST['contraseña']
        )
        return redirect('detalle_alumno', alumno_id=alumno.id)
    return render(request, 'agregar_alumno.html')

# -------------------------------
# PÁGINAS PRINCIPALES
# -------------------------------
def inicio(request):
    noticias = Noticia.objects.all().order_by('-fecha')[:5]
    return render(request, 'inicio.html', {"noticias": noticias})

def planteles(request):
    lista = Plantel.objects.all()
    return render(request, 'planteles.html', {"planteles": lista})

def noticias(request):
    lista = Noticia.objects.all().order_by('-fecha')
    return render(request, 'noticias.html', {"noticias": lista})

def contacto(request):
    if request.method == "POST":
        MensajeContacto.objects.create(
            nombre=request.POST['nombre'],
            email=request.POST['email'],
            mensaje=request.POST['mensaje']
        )
        return render(request, "contacto.html", {"exito": True})
    return render(request, 'contacto.html')

def home(request):
    noticias = Noticia.objects.all().order_by('-fecha')[:5]
    return render(request, 'inicio.html', {'noticias': noticias})

def oferta(request):
    datos = Oferta.objects.all()
    return render(request, 'oferta.html', {'datos': datos})