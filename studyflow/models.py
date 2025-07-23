from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PerfilUsuario(models.Model):
    TEMAS_CHOICES = [
        ('claro', 'Tema Claro'),
        ('oscuro', 'Tema Oscuro'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre_completo = models.CharField(max_length=100, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    genero = models.CharField(
        max_length=20,
        choices=[
            ('M', 'Masculino'),
            ('F', 'Femenino'),
            ('O', 'Otro'),
        ],
        blank=True
    )
    biografia = models.TextField(max_length=500, blank=True)
    carrera = models.CharField(max_length=100, blank=True)
    universidad = models.CharField(max_length=100, blank=True)
    tema_preferido = models.CharField(max_length=10, choices=TEMAS_CHOICES, default='claro')
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def calcular_edad(self):
        from datetime import date
        if self.fecha_nacimiento:
            hoy = date.today()
            return hoy.year - self.fecha_nacimiento.year - (
                (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

class EstadoAnimo(models.Model):
    ESTADOS_CHOICES = [
        ('feliz', '😊 Feliz'),
        ('triste', '😢 Triste'),
        ('estresado', '😤 Estresado'),
        ('relajado', '😌 Relajado'),
        ('motivado', '💪 Motivado'),
        ('cansado', '😴 Cansado'),
        ('ansioso', '😰 Ansioso'),
        ('neutral', '😐 Neutral'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES)
    fecha = models.DateField(default=timezone.now)
    comentario = models.TextField(blank=True, max_length=200)
    
    class Meta:
        unique_together = ['usuario', 'fecha']
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_estado_display()} ({self.fecha})"

class NotaRapida(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    contenido = models.TextField(max_length=500)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    importante = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-fecha_actualizacion']
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"
    
class Evento(models.Model):
    COLORES_CHOICES = [
        ('#3788d8', 'Azul'),
        ('#28a745', 'Verde'),
        ('#dc3545', 'Rojo'),
        ('#ffc107', 'Amarillo'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    color = models.CharField(max_length=20, default='#3788d8')
    completado = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['fecha_inicio']
        
    def __str__(self):
        return self.titulo