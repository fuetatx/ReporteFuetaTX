from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import registro, registro_ps

def enviar_correo(instance, producto, comprador, destinatarios):
    comprador_data = "\n".join([
        f"{key}: {value}" 
        for key, value in comprador.__dict__.items() 
        if not key.startswith('_')
    ])
    producto_data = "\n".join([
        f"{key}: {value}" 
        for key, value in producto.__dict__.items() 
        if not key.startswith('_')
    ])
    
    # Obtener problemas reportados del nuevo sistema de checkboxes
    problemas_reportados = instance.get_problemas_reportados()
    motivo_reporte = "\n".join([f"- {problema}" for problema in problemas_reportados]) if problemas_reportados else "Sin problemas especificados"
    
    subject = f"Reporte de Cliente: {comprador.nombre}"
    message = (
        f"Datos del Comprador:\n{comprador_data}\n\n"
        f"Datos del Producto:\n{producto_data}\n\n"
        f"Problemas Reportados:\n{motivo_reporte}"
    )
    
    # Asegúrate de que 'from_email' esté configurado en settings o pásalo aquí
    send_mail(
        subject,
        message,
        None,  # O define aquí un remitente válido
        destinatarios,
        fail_silently=False,
    )

@receiver(post_save, sender=registro.Registro)
def enviar_notificacion_registro(sender, instance, **kwargs):
    # Verificar si hay problemas reportados y receptor configurado
    problemas_reportados = instance.get_problemas_reportados()
    if problemas_reportados and instance.receptor:
        destinatarios = instance.receptor.split(',')

        # Seleccionar comprador: debe ser cliente o empresa (según la validación en el formulario)
        comprador = instance.cliente if instance.cliente else instance.empresa

        # Seleccionar el producto de forma exclusiva (se asume que en este modelo se usa 'triciclo' o 'panel')
        if instance.triciclo:
            producto = instance.triciclo
        elif hasattr(instance, 'panel') and instance.panel:
            producto = instance.panel
        else:
            # Si no hay producto definido, abortamos
            return
        
        enviar_correo(instance, producto, comprador, destinatarios)

@receiver(post_save, sender=registro_ps.Registro_ps)
def enviar_notificacion_registro_ps(sender, instance, **kwargs):
    # Verificar si hay problemas reportados y receptor configurado
    # Para Registro_ps, verificamos si tiene el campo 'llamada' o el nuevo sistema
    if hasattr(instance, 'get_problemas_reportados'):
        problemas_reportados = instance.get_problemas_reportados()
        condition = problemas_reportados and instance.receptor
    else:
        # Mantener compatibilidad con el campo anterior si existe
        condition = getattr(instance, 'llamada', None) and instance.receptor
        
    if condition:
        destinatarios = instance.receptor.split(',')

        comprador = instance.cliente if instance.cliente else instance.empresa
        
        # En Registro_ps se trabaja con power_station
        if instance.power_station:
            producto = instance.power_station
        else:
            return
        
        enviar_correo(instance, producto, comprador, destinatarios)
