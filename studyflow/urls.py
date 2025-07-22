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
]