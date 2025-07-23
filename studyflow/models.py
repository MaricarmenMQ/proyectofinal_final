from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg 
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

    NIVEL_CHOICES = [
        (5, 'Muy Bien'),
        (4, 'Bien'),
        (3, 'Regular'),
        (2, 'Mal'),
        (1, 'Muy Mal'),
    ]
    
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES)
    nivel = models.IntegerField(choices=NIVEL_CHOICES, default=3) 
    fecha = models.DateField(default=timezone.now)
    comentario = models.TextField(blank=True, max_length=200)
    
    class Meta:
        unique_together = ['usuario', 'fecha']
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_estado_display()} ({self.fecha})"
    @classmethod
    def get_promedio_semanal(cls, usuario):
        una_semana_atras = timezone.now() - timedelta(days=7)
        estados = cls.objects.filter(
            usuario=usuario,
            fecha__gte=una_semana_atras
        )
        return estados.aggregate(Avg('nivel'))['nivel__avg']

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
    
class Curso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    profesor = models.CharField(max_length=100, blank=True)
    horario = models.CharField(max_length=200, blank=True, help_text="Ejemplo: Lunes y Miércoles 10:00-12:00")
    color = models.CharField(max_length=20, default='#3788d8')
    
    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"

class Tarea(models.Model):
    PRIORIDAD_CHOICES = [
        ('alta', '🔴 Alta'),
        ('media', '🟡 Media'),
        ('baja', '🟢 Baja'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_entrega = models.DateTimeField()
    prioridad = models.CharField(max_length=5, choices=PRIORIDAD_CHOICES, default='media')
    completada = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['fecha_entrega']
    
    def __str__(self):
        return f"{self.titulo} - {self.curso.nombre}"
        
class Gasto(models.Model):
    CATEGORIA_CHOICES = [
        ('materiales', 'Materiales de Estudio'),
        ('libros', 'Libros'),
        ('tecnologia', 'Tecnología'),
        ('transporte', 'Transporte'),
        ('Entretenimiento', 'Entretenimiento'),
        ('otros', 'Otros'),
    ]

    PERIODO_CHOICES = [
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
    ]

    titulo = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    fecha = models.DateField()
    descripcion = models.TextField(blank=True, null=True)
    periodo = models.CharField(max_length=10, choices=PERIODO_CHOICES)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.titulo} - ${self.monto}"
    
# ...existing code...

class Presupuesto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    periodo = models.CharField(max_length=10, choices=Gasto.PERIODO_CHOICES)
    fecha_inicio = models.DateField(auto_now_add=True)
    alerta_porcentaje = models.IntegerField(default=80)  # Alerta cuando se alcance el 80% del presupuesto

    def calcular_gastos_actuales(self):
        from django.db.models import Sum
        from django.utils import timezone
        
        fecha_actual = timezone.now().date()
        if self.periodo == 'mensual':
            gastos = Gasto.objects.filter(
                usuario=self.usuario,
                fecha__year=fecha_actual.year,
                fecha__month=fecha_actual.month
            )
        else:  # semanal
            from datetime import timedelta
            inicio_semana = fecha_actual - timedelta(days=fecha_actual.weekday())
            gastos = Gasto.objects.filter(
                usuario=self.usuario,
                fecha__gte=inicio_semana,
                fecha__lte=fecha_actual
            )
        
        total = gastos.aggregate(Sum('monto'))['monto__sum'] or 0
        return total

    def calcular_porcentaje_usado(self):
        total_gastado = self.calcular_gastos_actuales()
        return (total_gastado / self.monto) * 100

    def __str__(self):
        return f"Presupuesto de {self.usuario.username} - ${self.monto} ({self.get_periodo_display()})"