from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import date
from .models import PerfilUsuario, EstadoAnimo, NotaRapida, Evento, Curso, Tarea, Gasto
from datetime import datetime
from datetime import timedelta
from django.http import HttpResponse
from django.db.models import Sum
import csv
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

        # Validaciones básicas
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe')
            return render(request, 'studyflow/registro.html')

        # Crear usuario
        usuario = User.objects.create_user(username=username, email=email, password=password)

        # Convertir fecha de nacimiento
        fecha_nacimiento = None
        if fecha_nacimiento_str:
            try:
                fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Fecha de nacimiento inválida')
                return render(request, 'studyflow/registro.html')

        # Crear perfil con todos los datos
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
    # Obtener el estado de ánimo de hoy
    hoy = date.today()
    estado_hoy = EstadoAnimo.objects.filter(usuario=request.user, fecha=hoy).first()
    notas_recientes = NotaRapida.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:5]
    
    # Obtener próximos 3 eventos
    eventos_proximos = Evento.objects.filter(
        usuario=request.user,
        fecha_inicio__gte=timezone.now()
    ).order_by('fecha_inicio')[:3]
    
    # Obtener estado de ánimo semanal
    estados_semana = EstadoAnimo.objects.filter(
        usuario=request.user,
        fecha__gte=timezone.now() - timedelta(days=7)
    ).order_by('-fecha')
    
    
    # Obtener estados de ánimo de la semana
    estados_semana = EstadoAnimo.objects.filter(usuario=request.user)[:7]
    
    context = {
        'estado_hoy': estado_hoy,
        'notas_recientes': notas_recientes,
        'estados_semana': estados_semana,
    }
    
    return render(request, 'studyflow/dashboard.html', context)

@login_required
def registrar_estado(request):
    """Registrar estado de ánimo del día"""
    if request.method == 'POST':
        estado = request.POST['estado']
        comentario = request.POST.get('comentario', '')
        
        # Crear o actualizar el estado del día
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
            # Si es una vista previa
            preview = {
                'titulo': request.POST.get('titulo', ''),
                'contenido': request.POST.get('contenido', ''),
                'importante': request.POST.get('importante') == 'on'
            }
        else:
            # Si es el envío final
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
    promedio = EstadoAnimo.get_promedio_semanal(request.user)
    
    estadisticas = {
        'notas_count': NotaRapida.objects.filter(usuario=request.user).count(),
        'estados_count': EstadoAnimo.objects.filter(usuario=request.user).count(),
        'eventos_count': Evento.objects.filter(usuario=request.user).count(),
        'promedio_animo': promedio,
        'promedio_porcentaje': (promedio / 5) * 100 if promedio else 0
    }
    
    if request.method == 'POST':
        # Actualizar perfil
        perfil = request.user.perfilusuario
        perfil.biografia = request.POST.get('biografia', '')
        perfil.carrera = request.POST.get('carrera', '')
        perfil.universidad = request.POST.get('universidad', '')
        perfil.save()
        messages.success(request, 'Perfil actualizado exitosamente')
    
    return render(request, 'studyflow/perfil.html', {
        'estadisticas': estadisticas,
        'perfil': request.user.perfilusuario
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
    
@login_required
def lista_cursos(request):
    cursos = Curso.objects.filter(usuario=request.user)
    
    if request.method == 'POST':
        nombre = request.POST['nombre']
        profesor = request.POST.get('profesor', '')
        horario = request.POST.get('horario', '')
        color = request.POST.get('color', '#3788d8')
        
        Curso.objects.create(
            usuario=request.user,
            nombre=nombre,
            profesor=profesor,
            horario=horario,
            color=color
        )
        messages.success(request, 'Curso agregado exitosamente')
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
def completar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, usuario=request.user)
    tarea.completada = True
    tarea.save()
    messages.success(request, 'Tarea marcada como completada')
    return redirect('lista_tareas')

@login_required
def lista_gastos(request):
    gastos = Gasto.objects.filter(usuario=request.user)
    
    # Calcular total del mes actual
    mes_actual = timezone.now().month
    total_mes = gastos.filter(fecha__month=mes_actual).aggregate(
        total=Sum('monto'))['total'] or 0
    
    context = {
        'gastos': gastos,
        'total_mes': total_mes,
    }
    
    return render(request, 'studyflow/gastos.html', context)

@login_required
def crear_gasto(request):
    if request.method == 'POST':
        gasto = Gasto.objects.create(
            usuario=request.user,
            titulo=request.POST['titulo'],
            monto=request.POST['monto'],
            categoria=request.POST['categoria'],
            fecha=request.POST.get('fecha', timezone.now().date()),
            descripcion=request.POST.get('descripcion', ''),
            periodo=request.POST.get('periodo', 'mensual')
        )
        messages.success(request, 'Gasto registrado exitosamente')
        return redirect('lista_gastos')
    return redirect('lista_gastos')