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
        
        # Obtener usuarios que han tenido actividad reciente
        usuarios_activos = LogEntry.objects.filter(
            action_time__gte=limite_fecha
        ).values_list('user_id', flat=True).distinct()
        
        # Obtener todos los usuarios staff (que deberían usar el admin)
        usuarios_staff = User.objects.filter(
            is_staff=True,
            is_active=True
        ).exclude(is_superuser=True)  # Excluir superusuarios
        
        # Usuarios sin actividad
        usuarios_sin_actividad = usuarios_staff.exclude(
            id__in=usuarios_activos
        )
        
        self.stdout.write(f'Total usuarios staff activos: {usuarios_staff.count()}')
        self.stdout.write(f'Usuarios con actividad reciente: {len(usuarios_activos)}')
        self.stdout.write(f'Usuarios sin actividad: {usuarios_sin_actividad.count()}')
        
        # SIEMPRE ENVIAR REPORTE (modificado)
        if modo_prueba:
            self.mostrar_reporte_consola(usuarios_sin_actividad, usuarios_staff, horas)
        else:
            self.enviar_reporte(usuarios_sin_actividad, usuarios_staff, horas)
        
        if usuarios_sin_actividad.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'Se encontraron {usuarios_sin_actividad.count()} usuarios sin actividad'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Todos los usuarios han tenido actividad reciente')
            )

    def mostrar_reporte_consola(self, usuarios_inactivos, usuarios_staff, horas):
        """Muestra el reporte en la consola para pruebas"""
        self.stdout.write(self.style.WARNING('\n=== REPORTE DE ACTIVIDAD (MODO PRUEBA) ==='))
        self.stdout.write(f'Período: Últimas {horas} horas')
        self.stdout.write(f'Fecha de verificación: {timezone.now().strftime("%d/%m/%Y %H:%M")}')
        self.stdout.write(f'Total usuarios staff: {usuarios_staff.count()}')
        self.stdout.write(f'Usuarios sin actividad: {usuarios_inactivos.count()}')
        
        if usuarios_inactivos.exists():
            self.stdout.write('\nUsuarios sin actividad:')
            for usuario in usuarios_inactivos:
                ultima_actividad = LogEntry.objects.filter(
                    user=usuario
                ).order_by('-action_time').first()
                
                fecha_ultima = "Nunca" if not ultima_actividad else ultima_actividad.action_time.strftime('%d/%m/%Y %H:%M')
                
                self.stdout.write(
                    f"- {usuario.get_full_name() or usuario.username} "
                    f"(Usuario: {usuario.username}) - Última actividad: {fecha_ultima}"
                )
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Todos los usuarios han tenido actividad reciente'))

    def enviar_reporte(self, usuarios_inactivos, usuarios_staff, horas):
        """Envía el reporte por correo a los administradores - SIEMPRE"""
        
        if usuarios_inactivos.exists():
            # Hay usuarios inactivos - reporte de alerta
            usuarios_lista = []
            for usuario in usuarios_inactivos:
                ultima_actividad = LogEntry.objects.filter(
                    user=usuario
                ).order_by('-action_time').first()
                
                fecha_ultima = "Nunca" if not ultima_actividad else ultima_actividad.action_time.strftime('%d/%m/%Y %H:%M')
                
                usuarios_lista.append(
                    f"- {usuario.get_full_name() or usuario.username} "
                    f"(Usuario: {usuario.username}) - Última actividad: {fecha_ultima}"
                )
            
            mensaje = f"""
⚠️ REPORTE DE ACTIVIDAD - USUARIOS INACTIVOS DETECTADOS

Período verificado: Últimas {horas} horas

USUARIOS SIN ACTIVIDAD:
{chr(10).join(usuarios_lista)}

RESUMEN:
- Total de usuarios staff: {usuarios_staff.count()}
- Usuarios inactivos: {len(usuarios_lista)}
- Usuarios activos: {usuarios_staff.count() - len(usuarios_lista)}

NOTA: Este reporte incluye solo usuarios con permisos de staff que deberían tener actividad regular en el sistema.

---
Sistema de administración de FuetaTX - Reporte automático
            """
            
            asunto = f'⚠️ ALERTA: {usuarios_inactivos.count()} usuarios inactivos ({horas}h)'
            
        else:
            # No hay usuarios inactivos - reporte de confirmación
            mensaje = f"""
✅ REPORTE DE ACTIVIDAD - TODOS LOS USUARIOS ACTIVOS

Período verificado: Últimas {horas} horas

RESULTADO: Todos los usuarios staff han tenido actividad reciente en el sistema.

RESUMEN:
- Total de usuarios staff monitoreados: {usuarios_staff.count()}
- Usuarios con actividad reciente: {usuarios_staff.count()}
- Usuarios sin actividad: 0

NOTA: Este reporte se envía diariamente para confirmar que el sistema de monitoreo está funcionando correctamente.

---
Sistema de administración de FuetaTX - Reporte automático
            """
            
            asunto = f'✅ Reporte Diario: Todos los usuarios activos ({horas}h)'
        
        # Enviar correo a los administradores
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