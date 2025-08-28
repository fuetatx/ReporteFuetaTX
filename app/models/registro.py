from datetime import date, timedelta
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save
from .triciclo import Triciclo
from .power_station import Power_Station
from .cliente import Cliente
from .empresa import Empresa


class Registro(models.Model):
    RECEPTOR_CHOICES = [
            ('pino.isaac27@gmail.com', 'Isaac'),
            ('tallerjireh47@gmail.com', 'Abraham'),
        ]
    
    GARANTY_TYPE = [
        (365, '1 año'),
        (180, '6 meses')
    ]

    fecha_entregado = models.DateField("Fecha entregado")
    tipo_garantia = models.IntegerField("Tipo de garantia", choices=GARANTY_TYPE, default=0)
    fecha_v_garantia = models.DateField("Fecha de vencimiento de garantia", default=None, null=True, blank=True, editable=False)
    tiempoR = models.IntegerField("Tiempo Restante", help_text="Deprecado en nuevos registros", editable=False)
    numero_reporte = models.IntegerField(editable=False, unique=True)    
    otros = models.TextField("Motivo", blank=True, help_text="Especifica problema")
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL, help_text = "Cliente a ser Reportado")
    empresa = models.ForeignKey(Empresa, null=True, blank=True, on_delete=models.SET_NULL, help_text = "Empresa a ser Reportada")
    triciclo = models.ForeignKey(Triciclo, null=True, blank=True, on_delete=models.SET_NULL)
    receptor = models.CharField(
        "Receptor(es) del correo",
        max_length=255,
        blank=True,
        help_text="Selecciona uno o varios receptores, o Todos"
    )
    video = models.FileField("Video de la venta", upload_to="ventas/videos/", blank=True, null=True, help_text="Video de la venta de triciclo")
    foto = models.ImageField("Foto de la venta", upload_to="ventas/fotos/", blank=True, null=True, help_text="Foto de la venta de triciclo")

    def __str__(self):
        if self.cliente:
            return f"Venta: {self.numero_reporte} - {self.cliente}  -> {self.triciclo}"
        else:
            return f"Venta: {self.numero_reporte} - {self.empresa}  -> {self.triciclo}"

    def get_problemas_reportados(self):
        problemas = []        
        if self.otros:
            problemas.append(f"{self.otros}")
            
        return problemas

    def save(self, *args, **kwargs):

        if not self.pk:
            dias_transcurridos = (date.today() - self.fecha_entregado).days
            self.tiempoR = max(0, 365 - dias_transcurridos)
            
            self.fecha_v_garantia = self.fecha_entregado + timedelta(days=self.tipo_garantia)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Relacion de venta"
        verbose_name_plural = "Relacion de ventas"

@receiver(pre_save, sender=Registro)
def set_numero_reporte(sender, instance, **kwargs):
    if not instance.numero_reporte:
        last_reporte = Registro.objects.order_by('-numero_reporte').first()
        instance.numero_reporte = (last_reporte.numero_reporte + 1) if last_reporte else 1
    if instance.triciclo:
        instance.triciclo.vendido = True
        instance.triciclo.fecha_v = date.today()
        instance.triciclo.save()
        
