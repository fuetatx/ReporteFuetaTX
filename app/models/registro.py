from datetime import date
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

    fecha_entregado = models.DateField("Fecha entregado")
    tiempoR = models.IntegerField("Tiempo Restante", editable=False)
    numero_reporte = models.IntegerField(editable=False, unique=True)
    
    # Campos para reportes por correo - checkboxes
    fallo = models.BooleanField("Fallo", default=False)
    motor_1000w = models.BooleanField("Motor de 1000w", default=False)
    motor_1200w = models.BooleanField("Motor 1200w", default=False)
    motor_1500w = models.BooleanField("Motor 1500w", default=False)
    cargador_bateria = models.BooleanField("Cargador de batería", default=False)
    baterias = models.BooleanField("Baterías", default=False)
    caja_reguladora = models.BooleanField("Caja reguladora", default=False)
    diferencial = models.BooleanField("Diferencial", default=False)
    extensor_rango = models.BooleanField("Extensor de rango", default=False)
    problema_electrico = models.BooleanField("Problema eléctrico", default=False)
    caja_luces = models.BooleanField("Caja luces", default=False)
    farol_delantero = models.BooleanField("Farol delantero", default=False)
    farol_trasero = models.BooleanField("Farol trasero", default=False)
    rodamientos_direccion = models.BooleanField("Rodamientos dirección", default=False)
    rodamientos_delanteros = models.BooleanField("Rodamientos delanteros", default=False)
    rodamientos_traseros = models.BooleanField("Rodamientos traseros", default=False)
    bandas_freno = models.BooleanField("Bandas de freno", default=False)
    tubo_escape = models.BooleanField("Tubo de escape", default=False)
    tarjeta_extensor = models.BooleanField("Tarjeta del extensor", default=False)
    panel_instrumentos = models.BooleanField("Panel de instrumentos", default=False)
    pulmon_stops = models.BooleanField("Pulmón de stops", default=False)
    claxon = models.BooleanField("Claxon", default=False)
    conmutadores = models.BooleanField("Conmutadores", default=False)
    calso_extensor = models.BooleanField("Calso del extensor", default=False)
    llave_combustible = models.BooleanField("Llave de combustible", default=False)
    otros = models.TextField("Otros (especificar)", blank=True, help_text="Especifica cualquier problema no listado arriba")
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
        """Retorna una lista de los problemas seleccionados para el reporte."""
        problemas = []
        campos_problema = [
            ('fallo', 'Fallo'),
            ('motor_1000w', 'Motor de 1000w'),
            ('motor_1200w', 'Motor 1200w'),
            ('motor_1500w', 'Motor 1500w'),
            ('cargador_bateria', 'Cargador de batería'),
            ('baterias', 'Baterías'),
            ('caja_reguladora', 'Caja reguladora'),
            ('diferencial', 'Diferencial'),
            ('extensor_rango', 'Extensor de rango'),
            ('problema_electrico', 'Problema eléctrico'),
            ('caja_luces', 'Caja luces'),
            ('farol_delantero', 'Farol delantero'),
            ('farol_trasero', 'Farol trasero'),
            ('rodamientos_direccion', 'Rodamientos dirección'),
            ('rodamientos_delanteros', 'Rodamientos delanteros'),
            ('rodamientos_traseros', 'Rodamientos traseros'),
            ('bandas_freno', 'Bandas de freno'),
            ('tubo_escape', 'Tubo de escape'),
            ('tarjeta_extensor', 'Tarjeta del extensor'),
            ('panel_instrumentos', 'Panel de instrumentos'),
            ('pulmon_stops', 'Pulmón de stops'),
            ('claxon', 'Claxon'),
            ('conmutadores', 'Conmutadores'),
            ('calso_extensor', 'Calso del extensor'),
            ('llave_combustible', 'Llave de combustible'),
        ]
        
        for campo, etiqueta in campos_problema:
            if getattr(self, campo, False):
                problemas.append(etiqueta)
                
        if self.otros:
            problemas.append(f"Otros: {self.otros}")
            
        return problemas

    def save(self, *args, **kwargs):

        if not self.pk:
            dias_transcurridos = (date.today() - self.fecha_entregado).days
            self.tiempoR = max(0, 365 - dias_transcurridos) 
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
        
