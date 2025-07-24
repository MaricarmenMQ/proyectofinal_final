from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    PerfilUsuario, EstadoAnimo, NotaRapida, Evento, 
    Curso, Tarea, Gasto, Presupuesto, SesionEstudio
)

# ===== FORMULARIOS DE AUTENTICACIÓN =====

class RegistroForm(UserCreationForm):
    """Formulario de registro extendido"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'tu@email.com'
        })
    )
    
    nombre_completo = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Tu nombre completo'
        })
    )
    
    fecha_nacimiento = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control form-control-lg',
            'type': 'date'
        })
    )
    
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    genero = forms.ChoiceField(
        choices=GENERO_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg'
        })
    )
    
    PAIS_CHOICES = [
        ('', 'Seleccione su país'),
        ('Perú', 'Perú'),
        ('México', 'México'),
        ('Argentina', 'Argentina'),
        ('Colombia', 'Colombia'),
        ('Chile', 'Chile'),
    ]
    
    pais = forms.ChoiceField(
        choices=PAIS_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg'
        })
    )
    
    foto_perfil = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control form-control-lg',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Mínimo 6 caracteres'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirma tu contraseña'
        })

class LoginForm(forms.Form):
    """Formulario de login"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Tu nombre de usuario'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Tu contraseña'
        })
    )

# ===== FORMULARIOS DE PERFIL =====

class PerfilForm(forms.ModelForm):
    """Formulario para editar perfil"""
    class Meta:
        model = PerfilUsuario
        fields = ['nombre_completo', 'biografia', 'carrera', 'universidad']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre completo'
            }),
            'biografia': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Cuéntanos un poco sobre ti...'
            }),
            'carrera': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu carrera'
            }),
            'universidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu universidad'
            }),
        }

# ===== FORMULARIOS DE ESTADO DE ÁNIMO =====

class EstadoAnimoForm(forms.ModelForm):
    """Formulario para registrar estado de ánimo"""
    class Meta:
        model = EstadoAnimo
        fields = ['estado', 'comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'maxlength': 200,
                'placeholder': 'Cuéntanos qué te hizo sentir así, qué pasó hoy, etc.'
            })
        }

# ===== FORMULARIOS DE NOTAS =====

class NotaRapidaForm(forms.ModelForm):
    """Formulario para crear notas rápidas"""
    class Meta:
        model = NotaRapida
        fields = ['titulo', 'contenido', 'importante']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '¿De qué va esta nota?',
                'maxlength': 100
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'maxlength': 500,
                'placeholder': 'Escribe aquí todo lo que necesites recordar'
            }),
            'importante': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

# ===== FORMULARIOS DE CURSOS =====

class CursoForm(forms.ModelForm):
    """Formulario para crear/editar cursos"""
    class Meta:
        model = Curso
        fields = ['nombre', 'profesor', 'horario', 'color']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del curso'
            }),
            'profesor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del profesor'
            }),
            'horario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Lunes y Miércoles 10:00-12:00'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            })
        }

# ===== FORMULARIOS DE TAREAS =====

class TareaForm(forms.ModelForm):
    """Formulario para crear/editar tareas"""
    class Meta:
        model = Tarea
        fields = ['titulo', 'curso', 'descripcion', 'fecha_entrega', 'prioridad']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la tarea'
            }),
            'curso': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la tarea'
            }),
            'fecha_entrega': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curso'].queryset = Curso.objects.filter(usuario=user)

# ===== FORMULARIOS DE EVENTOS =====

class EventoForm(forms.ModelForm):
    """Formulario para crear/editar eventos"""
    class Meta:
        model = Evento
        fields = ['titulo', 'descripcion', 'fecha_inicio', 'fecha_fin', 'color']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del evento'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del evento'
            }),
            'fecha_inicio': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'fecha_fin': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'color': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('#3788d8', 'Azul'),
                ('#28a745', 'Verde'),
                ('#dc3545', 'Rojo'),
                ('#ffc107', 'Amarillo'),
            ])
        }

# ===== FORMULARIOS DE GASTOS =====

class GastoForm(forms.ModelForm):
    """Formulario para registrar gastos"""
    class Meta:
        model = Gasto
        fields = ['titulo', 'monto', 'categoria', 'fecha', 'descripcion']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del gasto'
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del gasto'
            })
        }

class PresupuestoForm(forms.ModelForm):
    """Formulario para establecer presupuesto"""
    class Meta:
        model = Presupuesto
        fields = ['monto', 'periodo']
        widgets = {
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'periodo': forms.Select(attrs={
                'class': 'form-control'
            })
        }

# ===== FORMULARIOS DE SESIONES DE ESTUDIO =====

class IniciarSesionEstudioForm(forms.ModelForm):
    """Formulario para iniciar sesión de estudio"""
    class Meta:
        model = SesionEstudio
        fields = ['curso', 'ambiente', 'nivel_energia']
        widgets = {
            'curso': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ambiente': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nivel_energia': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curso'].queryset = Curso.objects.filter(usuario=user)

class FinalizarSesionEstudioForm(forms.Form):
    """Formulario para finalizar sesión de estudio"""
    nivel_concentracion = forms.ChoiceField(
        choices=SesionEstudio.NIVEL_CONCENTRACION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    objetivos_cumplidos = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': '¿Qué lograste en esta sesión?'
        })
    )
    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Notas adicionales sobre la sesión'
        })
    )
    interrupciones = forms.IntegerField(
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de interrupciones'
        })
    )
    descansos_tomados = forms.IntegerField(
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de descansos'
        })
    )