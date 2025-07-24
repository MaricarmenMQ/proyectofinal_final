# studyflow/control.py
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Sum, Avg
from .models import Tarea, Gasto, Presupuesto, SesionEstudio, EstadoAnimo, NotaRapida

class ControlFinanciero:
    """Control inteligente de gastos en soles peruanos"""
    
    def __init__(self, usuario):
        self.usuario = usuario
    
    def analizar_gastos_detallado(self):
        """Análisis completo de gastos para el dashboard"""
        mes_actual = timezone.now().month
        año_actual = timezone.now().year
        
        gastos_mes = Gasto.objects.filter(
            usuario=self.usuario,
            fecha__month=mes_actual,
            fecha__year=año_actual
        )
        
        total_gastado = gastos_mes.aggregate(Sum('monto'))['monto__sum'] or 0
        presupuesto = Presupuesto.objects.filter(usuario=self.usuario).first()
        
        # Calcular días restantes del mes
        hoy = timezone.now().date()
        if hoy.month == 12:
            ultimo_dia = hoy.replace(year=hoy.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            ultimo_dia = hoy.replace(month=hoy.month + 1, day=1) - timedelta(days=1)
        
        dias_restantes = (ultimo_dia - hoy).days + 1
        
        analisis = {
            'total_gastado': float(total_gastado),
            'dias_restantes': dias_restantes,
            'promedio_diario_actual': float(total_gastado) / max(hoy.day, 1),
        }
        
        if presupuesto:
            dinero_restante = float(presupuesto.monto) - float(total_gastado)
            porcentaje_usado = (float(total_gastado) / float(presupuesto.monto)) * 100
            gasto_diario_recomendado = dinero_restante / max(dias_restantes, 1)
            
            analisis.update({
                'presupuesto_total': float(presupuesto.monto),
                'dinero_restante': dinero_restante,
                'porcentaje_usado': porcentaje_usado,
                'gasto_diario_recomendado': gasto_diario_recomendado,
                'alerta_principal': self._generar_alerta_principal(porcentaje_usado, dias_restantes),
                'consejo_inteligente': self._generar_consejo_gasto(
                    porcentaje_usado, 
                    gasto_diario_recomendado,
                    analisis['promedio_diario_actual']
                )
            })
        else:
            analisis.update({
                'alerta_principal': '⚙️ Configura tu presupuesto para obtener consejos personalizados',
                'consejo_inteligente': 'Sin presupuesto definido, es difícil controlar tus gastos. ¡Configúralo ahora!'
            })
        
        return analisis
    
    def obtener_gastos_por_categoria(self):
        """Gastos por categoría para el gráfico"""
        mes_actual = timezone.now().month
        gastos = Gasto.objects.filter(
            usuario=self.usuario,
            fecha__month=mes_actual
        ).values('categoria').annotate(total=Sum('monto'))
        
        categorias_nombres = {
            'materiales': 'Materiales',
            'libros': 'Libros',
            'tecnologia': 'Tecnología',
            'transporte': 'Transporte',
            'entretenimiento': 'Entretenimiento',
            'otros': 'Otros'
        }
        
        return {
            categorias_nombres.get(gasto['categoria'], gasto['categoria']): float(gasto['total']) 
            for gasto in gastos
        }
    
    def _generar_alerta_principal(self, porcentaje, dias_restantes):
        """Alerta principal según el estado del presupuesto"""
        if porcentaje >= 95:
            return "🚨 ¡ALERTA ROJA! Has superado el 95% de tu presupuesto"
        elif porcentaje >= 85:
            return f"⚠️ CUIDADO: {porcentaje:.1f}% gastado, solo quedan {dias_restantes} días"
        elif porcentaje >= 70:
            return f"📊 Vas por el {porcentaje:.1f}% del presupuesto, controla tus gastos"
        elif porcentaje >= 50:
            return f"👍 Llevas {porcentaje:.1f}% gastado, vas por buen camino"
        else:
            return f"✅ Excelente control: solo {porcentaje:.1f}% gastado"
    
    def _generar_consejo_gasto(self, porcentaje, gasto_recomendado, promedio_actual):
        """Consejo inteligente personalizado"""
        if porcentaje >= 90:
            return f"💡 Limítate a S/ {gasto_recomendado:.2f} por día para no pasarte del presupuesto"
        elif porcentaje >= 75:
            return f"🎯 Intenta gastar máximo S/ {gasto_recomendado:.2f} diarios los días restantes"
        elif promedio_actual > gasto_recomendado * 1.5:
            return f"📉 Tu promedio diario (S/ {promedio_actual:.2f}) es alto. Reduce a S/ {gasto_recomendado:.2f}"
        else:
            return f"🎉 ¡Vas genial! Puedes gastar hasta S/ {gasto_recomendado:.2f} por día"

class ControlTareas:
    """Control de tareas y recordatorios"""
    
    def __init__(self, usuario):
        self.usuario = usuario
    
    def obtener_tareas_criticas(self):
        """Tareas críticas para mostrar en dashboard"""
        ahora = timezone.now()
        
        # Tareas que vencen hoy
        tareas_hoy = Tarea.objects.filter(
            usuario=self.usuario,
            fecha_entrega__date=ahora.date(),
            completada=False
        ).order_by('fecha_entrega')
        
        # Tareas que vencen mañana
        mañana = ahora + timedelta(days=1)
        tareas_mañana = Tarea.objects.filter(
            usuario=self.usuario,
            fecha_entrega__date=mañana.date(),
            completada=False
        ).order_by('fecha_entrega')
        
        # Tareas vencidas
        tareas_vencidas = Tarea.objects.filter(
            usuario=self.usuario,
            fecha_entrega__lt=ahora,
            completada=False
        ).order_by('fecha_entrega')
        
        return {
            'tareas_hoy': tareas_hoy,
            'tareas_mañana': tareas_mañana,
            'tareas_vencidas': tareas_vencidas,
            'total_pendientes': tareas_hoy.count() + tareas_mañana.count() + tareas_vencidas.count()
        }
    
    def generar_alerta_tareas(self):
        """Genera alerta principal de tareas para el dashboard"""
        criticas = self.obtener_tareas_criticas()
        
        if criticas['tareas_vencidas']:
            return f"🚨 Tienes {criticas['tareas_vencidas'].count()} tareas vencidas"
        elif criticas['tareas_hoy']:
            return f"⏰ {criticas['tareas_hoy'].count()} tareas vencen HOY"
        elif criticas['tareas_mañana']:
            return f"📅 {criticas['tareas_mañana'].count()} tareas vencen mañana"
        else:
            return "✅ No tienes tareas urgentes por ahora"

class ControlEstudio:
    """Control de productividad en estudios"""
    
    def __init__(self, usuario):
        self.usuario = usuario
    
    def resumen_productividad_semanal(self):
        """Resumen de productividad para dashboard"""
        semana_pasada = timezone.now() - timedelta(days=7)
        sesiones = SesionEstudio.objects.filter(
            usuario=self.usuario,
            fecha_inicio__gte=semana_pasada
        )
        
        if not sesiones:
            return {
                'mensaje': "📚 Aún no tienes sesiones de estudio registradas esta semana",
                'sesiones_count': 0,
                'horas_totales': 0,
                'productividad_promedio': 0
            }
        
        total_horas = 0
        productividad_total = 0
        
        for sesion in sesiones:
            if sesion.duracion_total():
                total_horas += sesion.duracion_total().total_seconds() / 3600
            productividad_total += sesion.productividad()
        
        productividad_promedio = productividad_total / len(sesiones)
        
        return {
            'sesiones_count': len(sesiones),
            'horas_totales': round(total_horas, 1),
            'productividad_promedio': round(productividad_promedio, 1),
            'mensaje': self._mensaje_productividad(productividad_promedio, total_horas)
        }
    
    def _mensaje_productividad(self, productividad, horas):
        """Mensaje según productividad"""
        if productividad >= 4:
            return f"🌟 ¡Increíble! {horas}h de estudio con excelente productividad"
        elif productividad >= 3:
            return f"👍 Buen trabajo: {horas}h estudiadas con buena productividad"
        elif productividad >= 2:
            return f"📈 {horas}h estudiadas, pero puedes mejorar tu concentración"
        else:
            return f"💪 Necesitas más concentración en tus {horas}h de estudio"

class ControlAnimo:
    """Control del estado emocional"""
    
    def __init__(self, usuario):
        self.usuario = usuario
    
    def analisis_animo_semanal(self):
        """Análisis del ánimo para mostrar en dashboard"""
        ultimos_7_dias = EstadoAnimo.objects.filter(
            usuario=self.usuario,
            fecha__gte=timezone.now().date() - timedelta(days=7)
        ).order_by('-fecha')
        
        if not ultimos_7_dias:
            return {
                'mensaje': "📊 Registra tu estado de ánimo para obtener análisis personalizados",
                'dias_registrados': 0,
                'promedio': 0
            }
        
        niveles = [estado.nivel for estado in ultimos_7_dias]
        promedio = sum(niveles) / len(niveles)
        
        # Detectar tendencia
        if len(niveles) >= 3:
            recientes = niveles[:3]
            anteriores = niveles[3:6] if len(niveles) >= 6 else niveles[3:]
            
            if anteriores and sum(recientes) > sum(anteriores):
                tendencia = "mejorando"
            elif anteriores and sum(recientes) < sum(anteriores):
                tendencia = "decayendo"
            else:
                tendencia = "estable"
        else:
            tendencia = "estable"
        
        return {
            'dias_registrados': len(ultimos_7_dias),
            'promedio': round(promedio, 1),
            'tendencia': tendencia,
            'mensaje': self._mensaje_animo(promedio, tendencia, len(ultimos_7_dias))
        }
    
    def _mensaje_animo(self, promedio, tendencia, dias):
        """Mensaje según el estado de ánimo"""
        if promedio >= 4:
            return f"😊 ¡Genial! Te has sentido muy bien estos {dias} días"
        elif promedio >= 3:
            if tendencia == "mejorando":
                return f"🌅 Tu ánimo está mejorando, sigue así ({dias} días registrados)"
            elif tendencia == "decayendo":
                return f"🤗 Has tenido algunos altibajos últimamente"
            return f"👌 Tu ánimo ha estado bien estos {dias} días"
        else:
            if tendencia == "mejorando":
                return f"💪 Aunque has pasado momentos difíciles, estás mejorando"
            return f"💙 Has tenido días complicados, cuídate mucho"

# Función principal que obtiene todo el resumen para el dashboard
def obtener_resumen_dashboard(usuario):
    """Obtiene resumen completo para mostrar en el dashboard"""
    financiero = ControlFinanciero(usuario)
    tareas = ControlTareas(usuario)
    estudio = ControlEstudio(usuario)
    animo = ControlAnimo(usuario)
    
    # Contar estadísticas generales
    total_notas = NotaRapida.objects.filter(usuario=usuario).count()
    
    return {
        'gastos': financiero.analizar_gastos_detallado(),
        'gastos_por_categoria': financiero.obtener_gastos_por_categoria(),
        'tareas': tareas.obtener_tareas_criticas(),
        'alerta_tareas': tareas.generar_alerta_tareas(),
        'productividad': estudio.resumen_productividad_semanal(),
        'animo': animo.analisis_animo_semanal(),
        'estadisticas_generales': {
            'total_notas': total_notas,
            'fecha_actual': timezone.now().strftime('%d/%m/%Y')
        }
    }

# Función específica para la página de gastos
def obtener_datos_gastos_completo(usuario):
    """Datos completos para la página de gastos con consejos inteligentes"""
    financiero = ControlFinanciero(usuario)
    
    analisis = financiero.analizar_gastos_detallado()
    por_categoria = financiero.obtener_gastos_por_categoria()
    
    # Agregar datos específicos para la página de gastos
    mes_actual = timezone.now().month
    gastos_recientes = Gasto.objects.filter(
        usuario=usuario,
        fecha__month=mes_actual
    ).order_by('-fecha')[:10]
    
    return {
        'analisis_financiero': analisis,
        'gastos_por_categoria': por_categoria,
        'gastos_recientes': gastos_recientes,
        'recomendacion_categoria': _obtener_categoria_mas_gastada(por_categoria),
    }

def _obtener_categoria_mas_gastada(gastos_por_categoria):
    """Identifica la categoría donde más se gasta"""
    if not gastos_por_categoria:
        return "No hay datos suficientes para recomendaciones"
    
    categoria_max = max(gastos_por_categoria.items(), key=lambda x: x[1])
    return f"Tu mayor gasto es en {categoria_max[0]} (S/ {categoria_max[1]:.2f}). ¿Puedes reducirlo?"