from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Prueba el envío de correos'

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write('Probando configuración de email...')
            self.stdout.write(f'EMAIL_HOST: {settings.EMAIL_HOST}')
            self.stdout.write(f'EMAIL_PORT: {settings.EMAIL_PORT}')
            self.stdout.write(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
            self.stdout.write(f'DEFAULT_FROM_EMAIL: {getattr(settings, "DEFAULT_FROM_EMAIL", "No configurado")}')
            
            send_mail(
                subject='Prueba de configuración de email',
                message='Este es un correo de prueba desde Django',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['darioroque20033@gmail.com'],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Correo enviado exitosamente')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error enviando correo: {e}')
            )