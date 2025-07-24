from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import date
from .models import PerfilUsuario, EstadoAnimo, NotaRapida, Evento, Curso, Tarea, Gasto, Presupuesto, SesionEstudio
from .control import obtener_resumen_dashboard
from datetime import datetime
from datetime import timedelta
from django.http import HttpResponse
from django.db.models import Sum
from decimal import Decimal
import csv
from django.conf import settings
import os 

def inicio(request):
    """Página de inicio/landing page"""
    return render(request, 'studyflow/inicio.html')

def registro_usuario(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        nombre_completo = request.POST.get('nombre_completo', '')
        fecha_nacimiento_str = request.POST.get('fecha_nacimiento', '')
        genero = request.POST.get('genero', '')
        pais = request.POST.get('pais', '')
        foto_perfil = request.FILES.get('foto_perfil', None)

        if len(password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres')
            return render(request, 'studyflow/registro.html')
        
        if len(password) > 8:
            messages.error(request, 'La contraseña no puede tener más de 8 caracteres')
            return render(request, 'studyflow/registro.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe')
            return render(request, 'studyflow/registro.html')

        usuario = User.objects.create_user(username=username, email=email, password=password)

        fecha_nacimiento = None
        if fecha_nacimiento_str:
            try:
                fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Fecha de nacimiento inválida')
                return render(request, 'studyflow/registro.html')

        PerfilUsuario.objects.create(
            usuario=usuario,
            nombre_completo=nombre_completo,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero,
            pais=pais,
            foto_perfil=foto_perfil
        )

        messages.success(request, 'Usuario registrado exitosamente')
        return redirect('login')

    return render(request, 'studyflow/registro.html')

def login_usuario(request):
    """Login de usuarios"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect('dashboard')
        else:
            messages.error(request, 'Credenciales incorrectas')
    
    return render(request, 'studyflow/login.html')

def logout_usuario(request):
    """Logout de usuarios"""
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente')
    return redirect('inicio')

@login_required
def dashboard(request):
    """Dashboard principal del usuario"""
    hoy = date.today()
    estado_hoy = EstadoAnimo.objects.filter(usuario=request.user, fecha=hoy).first()
    notas_recientes = NotaRapida.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:5]
    
    eventos_proximos = Evento.objects.filter(
        usuario=request.user,
        fecha_inicio__gte=timezone.now()
    ).order_by('fecha_inicio')[:3]
    
    estados_semana = EstadoAnimo.objects.filter(
        usuario=request.user,
        fecha__gte=timezone.now() - timedelta(days=7)
    ).order_by('-fecha')
    
    
    estados_semana = EstadoAnimo.objects.filter(usuario=request.user)[:7]
    
    context = {
        'estado_hoy': estado_hoy,
        'notas_recientes': notas_recientes,
        'estados_semana': estados_semana,
    }

    resumen_inteligente = obtener_resumen_dashboard(request.user)
    
    context = {
        'estado_hoy': estado_hoy,
        'notas_recientes': notas_recientes,
        'estados_semana': estados_semana,
        'control': resumen_inteligente,
    }
    
    return render(request, 'studyflow/dashboard.html', context)

@login_required
def registrar_estado(request):
    """Registrar estado de ánimo del día"""
    if request.method == 'POST':
        estado = request.POST['estado']
        comentario = request.POST.get('comentario', '')
        
        estado_obj, created = EstadoAnimo.objects.get_or_create(
            usuario=request.user,
            fecha=date.today(),
            defaults={
                'estado': estado,
                'comentario': comentario
            }
        )
        
        if not created:
            estado_obj.estado = estado
            estado_obj.comentario = comentario
            estado_obj.save()
        
        messages.success(request, 'Estado de ánimo registrado')
        return redirect('dashboard')
    
    return render(request, 'studyflow/registrar_estado.html', {
        'estados': EstadoAnimo.ESTADOS_CHOICES
    })

@login_required
def crear_nota(request):
    preview = None
    
    if request.method == 'POST':
        if 'preview' in request.POST:
            preview = {
                'titulo': request.POST.get('titulo', ''),
                'contenido': request.POST.get('contenido', ''),
                'importante': request.POST.get('importante') == 'on'
            }
        else:
            NotaRapida.objects.create(
                usuario=request.user,
                titulo=request.POST['titulo'],
                contenido=request.POST['contenido'],
                importante=request.POST.get('importante') == 'on'
            )
            messages.success(request, 'Nota creada exitosamente')
            return redirect('dashboard')
    
    return render(request, 'studyflow/crear_nota.html', {'preview': preview})
@login_required
def exportar_notas(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mis_notas.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Título', 'Contenido', 'Fecha'])
    
    notas = NotaRapida.objects.filter(usuario=request.user)
    for nota in notas:
        writer.writerow([nota.titulo, nota.contenido, nota.fecha_creacion])
        
    return response
@login_required
def perfil_usuario(request):
    perfil, created = PerfilUsuario.objects.get_or_create(
        usuario=request.user,
        defaults={
            'nombre_completo': '',
            'biografia': '',
            'carrera': '',
            'universidad': ''
        }
    )
    
    if created:
        messages.info(request, 'Se ha creado tu perfil automáticamente')
    
    promedio = EstadoAnimo.get_promedio_semanal(request.user)
    
    estadisticas = {
        'notas_count': NotaRapida.objects.filter(usuario=request.user).count(),
        'estados_count': EstadoAnimo.objects.filter(usuario=request.user).count(),
        'eventos_count': Evento.objects.filter(usuario=request.user).count(),
        'promedio_animo': promedio,
        'promedio_porcentaje': (promedio / 5) * 100 if promedio else 0
    }
    
    if request.method == 'POST':
        perfil.biografia = request.POST.get('biografia', '')
        perfil.carrera = request.POST.get('carrera', '')
        perfil.universidad = request.POST.get('universidad', '')
        perfil.nombre_completo = request.POST.get('nombre_completo', '')
        perfil.genero = request.POST.get('genero', '')
        perfil.fecha_nacimiento = request.POST.get('fecha_nacimiento', None)
        perfil.pais = request.POST.get('pais', '')
        perfil.save()
        messages.success(request, 'Perfil actualizado exitosamente')
        return redirect('perfil')
    
    return render(request, 'studyflow/perfil.html', {
        'estadisticas': estadisticas,
        'perfil': perfil 
    })

@login_required
def calendario(request):
    eventos = Evento.objects.filter(usuario=request.user)
    eventos_json = []
    
    for evento in eventos:
        eventos_json.append({
            'title': evento.titulo,
            'start': evento.fecha_inicio.isoformat(),
            'end': evento.fecha_fin.isoformat(),
            'color': evento.color,
            'className': 'evento-completado' if evento.completado else ''
        })
    
    return render(request, 'studyflow/calendario.html', {
        'eventos': eventos_json
    })

@login_required
def crear_evento(request):
    if request.method == 'POST':
        evento = Evento.objects.create(
            usuario=request.user,
            titulo=request.POST['titulo'],
            descripcion=request.POST['descripcion'],
            fecha_inicio=request.POST['fecha_inicio'],
            fecha_fin=request.POST['fecha_fin'],
            color=request.POST['color']
        )
        messages.success(request, 'Evento creado exitosamente')
        return redirect('calendario')
    return redirect('calendario')
    
from .models import Curso, Evento
from django.utils.dateparse import parse_datetime
from datetime import datetime, timedelta

@login_required
def lista_cursos(request):
    cursos = Curso.objects.filter(usuario=request.user)
    
    if request.method == 'POST':
        nombre = request.POST['nombre']
        profesor = request.POST.get('profesor', '')
        horario = request.POST.get('horario', '')  
        color = request.POST.get('color', '#3788d8')
        
        curso = Curso.objects.create(
            usuario=request.user,
            nombre=nombre,
            profesor=profesor,
            horario=horario,
            color=color
        )

        fecha_inicio = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(hours=2) 

        Evento.objects.create(
            usuario=request.user,
            titulo=f"{nombre} (Clase)",
            descripcion=f"Clase de {nombre} con {profesor}",
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            color=color
        )

        messages.success(request, 'Curso y evento creado exitosamente')
        return redirect('lista_cursos')
    
    return render(request, 'studyflow/cursos.html', {'cursos': cursos})

    

@login_required
def lista_tareas(request):
    cursos = Curso.objects.filter(usuario=request.user)
    tareas = Tarea.objects.filter(usuario=request.user, completada=False)
    context = {
        'cursos': cursos,
        'tareas': tareas
    }
    
    return render(request, 'studyflow/tareas.html', context)



@login_required
def crear_tarea(request):
    if request.method == 'POST':
        curso_id = request.POST.get('curso')
        titulo = request.POST.get('titulo', '')
        descripcion = request.POST.get('descripcion', '')
        fecha_entrega = request.POST.get('fecha_entrega')
        prioridad = request.POST.get('prioridad', 'media')
        
        curso = get_object_or_404(Curso, id=curso_id, usuario=request.user)
        
        tarea = Tarea.objects.create(
            usuario=request.user,
            curso=curso,
            titulo=titulo,
            descripcion=descripcion,
            fecha_entrega=fecha_entrega,
            prioridad=prioridad
        )
        
        messages.success(request, 'Tarea creada exitosamente')
        return redirect('lista_tareas')
    
    return redirect('lista_tareas')

@login_required
def completar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, usuario=request.user)
    tarea.completada = True
    tarea.save()
    messages.success(request, 'Tarea marcada como completada')
    return redirect('lista_tareas')

@login_required
def lista_gastos(request):
    gastos = Gasto.objects.filter(usuario=request.user)
    presupuesto = Presupuesto.objects.filter(usuario=request.user).first()
    
    mes_actual = timezone.now().month
    total_mes = gastos.filter(fecha__month=mes_actual).aggregate(
        total=Sum('monto'))['total'] or 0

    restante = 0
    porcentaje_usado = 0
    if presupuesto and presupuesto.monto > 0:
        restante = presupuesto.monto - total_mes
        porcentaje_usado = (total_mes / presupuesto.monto) * 100

    CATEGORIAS_CHOICES = [
        ('utiles', 'Útiles Escolares'),
        ('libros', 'Libros'),
        ('tecnologia', 'Tecnología'),
        ('transporte', 'Transporte'),
        ('comida', 'Comida'),
        ('otros', 'Otros')
    ]

    context = {
        'gastos': gastos,
        'total_mes': total_mes,
        'presupuesto': presupuesto,
        'porcentaje_usado': porcentaje_usado,
        'restante': restante,
        'categorias': CATEGORIAS_CHOICES,
    }

    return render(request, 'studyflow/gastos.html', context)



@login_required
def establecer_presupuesto(request):
    if request.method == 'POST':
        monto = request.POST.get('monto')
        periodo = request.POST.get('periodo', 'mensual')
        
        presupuesto, created = Presupuesto.objects.get_or_create(
            usuario=request.user,
            defaults={'monto': monto, 'periodo': periodo}
        )
        
        if not created:
            presupuesto.monto = monto
            presupuesto.periodo = periodo
            presupuesto.save()
            
        messages.success(request, 'Presupuesto actualizado exitosamente')
        return redirect('lista_gastos')
    return redirect('lista_gastos')

@login_required
def eliminar_gasto(request, gasto_id):
    gasto = get_object_or_404(Gasto, id=gasto_id, usuario=request.user)
    if request.method == 'POST':
        gasto.delete()
        messages.success(request, 'Gasto eliminado correctamente.')
    return redirect('lista_gastos')

@login_required
def crear_gasto(request):
    if request.method == 'POST':
        try:
            nuevo_gasto = Gasto(
                usuario=request.user,
                titulo=request.POST['titulo'],
                monto=Decimal(request.POST['monto']),
                categoria=request.POST['categoria'],
                fecha=request.POST['fecha'],
                descripcion=request.POST.get('descripcion', '')
            )
            nuevo_gasto.save()
            messages.success(request, 'Gasto registrado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al registrar el gasto: {str(e)}')
    
    return redirect('lista_gastos')


@login_required
def lista_sesiones(request):
    sesiones = SesionEstudio.objects.filter(usuario=request.user)
    
    total_horas = timedelta()
    total_sesiones = sesiones.count()
    promedio_productividad = 0
    
    for sesion in sesiones:
        if sesion.duracion_total():
            total_horas += sesion.duracion_total()
        promedio_productividad += sesion.productividad()

        sesion.productividad_porcentaje = sesion.productividad() * 20
    
    if total_sesiones > 0:
        promedio_productividad /= total_sesiones
    
    context = {
        'sesiones': sesiones,
        'total_horas': total_horas,
        'total_sesiones': total_sesiones,
        'promedio_productividad': promedio_productividad,
        'cursos': Curso.objects.filter(usuario=request.user)
    }
    
    return render(request, 'studyflow/sesiones_estudio.html', context)

@login_required
def iniciar_sesion_estudio(request):
    if request.method == 'POST':
        curso_id = request.POST.get('curso')
        ambiente = request.POST.get('ambiente')
        nivel_energia = request.POST.get('nivel_energia')
        
        sesion = SesionEstudio.objects.create(
            usuario=request.user,
            curso_id=curso_id,
            ambiente=ambiente,
            nivel_energia=nivel_energia,
            nivel_concentracion=nivel_energia  
        )
        
        messages.success(request, '¡Sesión de estudio iniciada!')
        return redirect('detalle_sesion', sesion_id=sesion.id)
    
    return redirect('lista_sesiones')

@login_required
def finalizar_sesion(request, sesion_id):
    sesion = get_object_or_404(SesionEstudio, id=sesion_id, usuario=request.user)
    
    if request.method == 'POST':
        sesion.fecha_fin = timezone.now()
        sesion.nivel_concentracion = request.POST.get('nivel_concentracion')
        sesion.objetivos_cumplidos = request.POST.get('objetivos_cumplidos', '')
        sesion.notas = request.POST.get('notas', '')
        sesion.interrupciones = request.POST.get('interrupciones', 0)
        sesion.descansos_tomados = request.POST.get('descansos_tomados', 0)
        sesion.save()
        
        messages.success(request, '¡Sesión de estudio finalizada!')
        return redirect('lista_sesiones')
    
    return redirect('detalle_sesion', sesion_id=sesion.id)

@login_required
def tablas(request):
    
    usuarios = User.objects.select_related('perfilusuario').all()
    estados = EstadoAnimo.objects.select_related('usuario').all().order_by('-fecha')[:50]  
    notas = NotaRapida.objects.select_related('usuario').all().order_by('-fecha_creacion')[:50]  
    cursos = Curso.objects.select_related('usuario').all()
    gastos = Gasto.objects.select_related('usuario').all().order_by('-fecha')[:50]  
    
    total_gastos_monto = gastos.aggregate(total=Sum('monto'))['total'] or 0
    
    db_path = settings.DATABASES['default']['NAME']
    
    context = {
        'usuarios': usuarios,
        'estados': estados,
        'notas': notas,
        'cursos': cursos,
        'gastos': gastos,
        
        # Totales para el resumen
        'total_usuarios': usuarios.count(),
        'total_estados': EstadoAnimo.objects.count(),
        'total_notas': NotaRapida.objects.count(),
        'total_cursos': cursos.count(),
        'total_gastos': Gasto.objects.count(),
        'total_gastos_monto': total_gastos_monto,
        
        # Info adicional
        'db_path': os.path.basename(str(db_path)),
        'fecha_actual': timezone.now(),
    }
    
    return render(request, 'studyflow/tablas.html', context)