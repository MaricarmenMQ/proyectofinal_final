from django.urls import path
from . import views

urlpatterns = [
    # Páginas principales
    path('', views.inicio, name='inicio'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Autenticación
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    
    # Funcionalidades
    path('estado/', views.registrar_estado, name='registrar_estado'),
    path('nota/', views.crear_nota, name='crear_nota'),
    path('calendario/', views.calendario, name='calendario'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('evento/crear/', views.crear_evento, name='crear_evento'),
    path('cursos/', views.lista_cursos, name='lista_cursos'),
    path('tareas/', views.lista_tareas, name='lista_tareas'),
    path('tarea/<int:tarea_id>/completar/', views.completar_tarea, name='completar_tarea'),
    path('gastos/', views.lista_gastos, name='lista_gastos'),
    path('gastos/crear/', views.crear_gasto, name='crear_gasto'),
]