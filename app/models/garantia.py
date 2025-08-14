from django.db import models
from .cliente import Cliente
from.empresa import Empresa
from .triciclo import Triciclo
from .power_station import Power_Station
ESPEC = [
    ("abraham pino valdes", "Abraham Pino Valdes"),
    ("juan", "Juan"),
    ("jose", "Jose"),
    ("ailet", "Ailet"),
    ("tamara", "Tamara"),
    ("dago", "Dago"),
    ("roberto", "Roberto"),
]

FACT = [
    ("cliente", "Cliente"),
    ("vendedor", "Vendedor"),
]
class Garantia(models.Model):
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL)
    empresa = models.ForeignKey(Empresa, null=True, blank=True, on_delete=models.SET_NULL)
    triciclo = models.ForeignKey(Triciclo, null=True, blank=True, on_delete=models.SET_NULL)
    power_station = models.ForeignKey(Power_Station, null=True, blank=True, on_delete=models.SET_NULL)
    motivo=models.TextField("Motivo", max_length=255)
    evaluacion=models.TextField("Evaluacion resumen", max_length=255)
    trabajos_hechos=models.TextField("Trabajos realizados", max_length=255)
    piezas_usadas=models.TextField("Lista de piezas usadas", null=True, blank=True, max_length=255)

    tubo_escape = models.BooleanField("Tubo de escape", default=False)
    tarjeta = models.BooleanField("Tarjeta", default=False)
    motor_1000w = models.BooleanField("Motor de 1 000w", default=False)
    motor_1200w = models.BooleanField("Motor 1200w", default=False)
    motor_1500w = models.BooleanField("Motor 1 500w", default=False)
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
    claxon = models.BooleanField("Claxon", default=False)
    otros = models.TextField("Otros", blank=True, help_text="Especifica otra pieza no listada")

    recomendaciones=models.TextField("Algunas recomendaciones", max_length=255)
    nombre_especialista=models.CharField("Especialista encargado", choices=ESPEC, max_length=255)
    conformidad_cliente=models.BooleanField("Conformidad del cliente")

    video = models.FileField("Video", upload_to="ventas/videos/", blank=True, null=True)
    foto = models.ImageField("Foto", upload_to="ventas/fotos/", blank=True, null=True)

    def __str__(self):
        if self.cliente:
            if self.triciclo:
                return f"Reporte de Reclamacion: {self.cliente}  -> {self.triciclo}"
            else:
                return f"Reporte de Reclamacion: {self.cliente}  -> {self.power_station}"
        else:
            if self.triciclo:
                return f"Reporte de Reclamacion: {self.empresa}  -> {self.triciclo}"
            else:
                return f"Reporte de Reclamacion: {self.empresa}  -> {self.power_station}"

    class Meta:
        verbose_name = "Reporte de Reclamacion"
        verbose_name_plural = "Reporte de Reclamaciones"

