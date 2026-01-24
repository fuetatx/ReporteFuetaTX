from django.core.management.base import BaseCommand
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Verifica la actividad de usuarios en las últimas 24 horas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Número de horas hacia atrás para verificar actividad (default: 24)'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Modo de prueba - no envía correos'
        )

    def handle(self, *args, **kwargs):
        horas = kwargs['hours']
        modo_prueba = kwargs['test']
        
        self.stdout.write(f'Verificando actividad de usuarios en las últimas {horas} horas...')
        
        # Fecha límite 
        limite_fecha = timezone.now() - timedelta(hours=horas)
        
        # Obtener TODOS los usuarios excepto superusuarios
        todos_usuarios = User.objects.filter(
            is_superuser=False
        )
        
        usuarios_con_actividad = []
        usuarios_sin_actividad = []
        
        for usuario in todos_usuarios:
            ultima_actividad = LogEntry.objects.filter(
                user=usuario
            ).order_by('-action_time').first()
            
            nombre_completo = usuario.get_full_name() or "Sin nombre"
            
            if ultima_actividad:
                fecha_ultima = ultima_actividad.action_time
                
                info_usuario = {
                    'username': usuario.username,
                    'nombre': nombre_completo,
                    'ultima_actividad': fecha_ultima,
                    'fecha_formateada': fecha_ultima.strftime('%d/%m/%Y %H:%M')
                }
                
                # Verificar si la actividad fue antes o después de las últimas X horas
                if fecha_ultima >= limite_fecha:
                    usuarios_con_actividad.append(info_usuario)
                else:
                    usuarios_sin_actividad.append(info_usuario)
            else:
                # Usuario sin ninguna actividad registrada
                info_usuario = {
                    'username': usuario.username,
                    'nombre': nombre_completo,
                    'ultima_actividad': None,
                    'fecha_formateada': 'Nunca'
                }
                usuarios_sin_actividad.append(info_usuario)
        
        self.stdout.write(f'Total usuarios (sin superusuarios): {todos_usuarios.count()}')
        self.stdout.write(f'Usuarios con actividad reciente: {len(usuarios_con_actividad)}')
        self.stdout.write(f'Usuarios sin actividad reciente: {len(usuarios_sin_actividad)}')
        
        if modo_prueba:
            self.mostrar_reporte_consola(usuarios_con_actividad, usuarios_sin_actividad, horas)
        else:
            self.enviar_reporte(usuarios_con_actividad, usuarios_sin_actividad, horas)
        
        self.stdout.write(self.style.SUCCESS('Reporte generado exitosamente'))

    def mostrar_reporte_consola(self, usuarios_activos, usuarios_inactivos, horas):
        """Muestra el reporte en la consola para pruebas"""
        self.stdout.write(self.style.WARNING('\n=== REPORTE DE ACTIVIDAD (MODO PRUEBA) ==='))
        self.stdout.write(f'Período: Últimas {horas} horas')
        self.stdout.write(f'Fecha de verificación: {timezone.now().strftime("%d/%m/%Y %H:%M")}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ USUARIOS CON ACTIVIDAD RECIENTE ({len(usuarios_activos)}):'))
        if usuarios_activos:
            for usuario in usuarios_activos:
                self.stdout.write(
                    f"- Usuario: {usuario['username']} | "
                    f"Nombre: {usuario['nombre']} | "
                    f"Última actividad: {usuario['fecha_formateada']}"
                )
        else:
            self.stdout.write('  (Ninguno)')
        
        self.stdout.write(self.style.WARNING(f'\n⚠️ USUARIOS SIN ACTIVIDAD RECIENTE ({len(usuarios_inactivos)}):'))
        if usuarios_inactivos:
            for usuario in usuarios_inactivos:
                self.stdout.write(
                    f"- Usuario: {usuario['username']} | "
                    f"Nombre: {usuario['nombre']} | "
                    f"Última actividad: {usuario['fecha_formateada']}"
                )
        else:
            self.stdout.write('  (Ninguno)')

    def enviar_reporte(self, usuarios_activos, usuarios_inactivos, horas):
        """Envía el reporte por correo a los administradores"""
        
        # Construir lista de usuarios activos
        lista_activos = []
        for usuario in usuarios_activos:
            lista_activos.append(
                f"- Usuario: {usuario['username']} | "
                f"Nombre: {usuario['nombre']} | "
                f"Última actividad: {usuario['fecha_formateada']}"
            )
        
        # Construir lista de usuarios inactivos
        lista_inactivos = []
        for usuario in usuarios_inactivos:
            lista_inactivos.append(
                f"- Usuario: {usuario['username']} | "
                f"Nombre: {usuario['nombre']} | "
                f"Última actividad: {usuario['fecha_formateada']}"
            )
        
        mensaje = f"""
REPORTE DE ACTIVIDAD DE USUARIOS

Período verificado: Últimas {horas} horas
Fecha de verificación: {timezone.now().strftime('%d/%m/%Y %H:%M')}

{'='*60}

✅ USUARIOS CON ACTIVIDAD RECIENTE ({len(usuarios_activos)}):
{chr(10).join(lista_activos) if lista_activos else '  (Ninguno)'}

{'='*60}

⚠️ USUARIOS SIN ACTIVIDAD RECIENTE ({len(usuarios_inactivos)}):
{chr(10).join(lista_inactivos) if lista_inactivos else '  (Ninguno)'}

{'='*60}

RESUMEN:
- Total de usuarios monitoreados: {len(usuarios_activos) + len(usuarios_inactivos)}
- Usuarios con actividad reciente: {len(usuarios_activos)}
- Usuarios sin actividad reciente: {len(usuarios_inactivos)}

NOTA: Este reporte excluye únicamente a los superusuarios.

---
Sistema de administración de FuetaTX - Reporte automático
        """
        
        # Determinar asunto según situación
        if usuarios_inactivos:
            asunto = f'⚠️ Reporte de Actividad: {len(usuarios_inactivos)} usuarios inactivos en {horas}h'
        else:
            asunto = f'✅ Reporte de Actividad: Todos los usuarios activos en {horas}h'
        
        # Enviar correo
        destinatarios = ['darioroque20033@gmail.com']
        
        try:
            send_mail(
                subject=asunto,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=destinatarios,
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS('Reporte enviado exitosamente a: ' + ', '.join(destinatarios))
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error enviando reporte: {e}')
            )