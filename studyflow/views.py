from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import date
from .models import PerfilUsuario, EstadoAnimo, NotaRapida
from datetime import datetime
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
    
    # Obtener las últimas notas
    notas_recientes = NotaRapida.objects.filter(usuario=request.user)[:5]
    
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
    """Crear nueva nota rápida"""
    if request.method == 'POST':
        titulo = request.POST['titulo']
        contenido = request.POST['contenido']
        importante = request.POST.get('importante') == 'on'
        
        NotaRapida.objects.create(
            usuario=request.user,
            titulo=titulo,
            contenido=contenido,
            importante=importante
        )
        
        messages.success(request, 'Nota creada exitosamente')
        return redirect('dashboard')
    
    return render(request, 'studyflow/crear_nota.html')