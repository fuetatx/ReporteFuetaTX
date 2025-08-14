from datetime import datetime
import uuid
from django.db import models
from .panels import Panels

class Power_Station(models.Model):
    TIPO_CHOICES = [
        ('300w', '300W'),
        ('600w', '600W'),
        ('1200w', '1200W'),
        ('2400w', '2400W'),
        ('3000w', '3000W'),
    ]

    DISTRIBUIDORA_CHOICES = [
    ('donki', 'Donki'),
    ('fueta', 'Fueta'),
    ('mkl', 'MKL'),
]
    
    sn = models.CharField("ID", max_length=255, primary_key=True)
    fecha_armado = models.DateField("Fecha de Compra", default=datetime.now)
    tipo = models.CharField("Tipo", max_length=10, choices=TIPO_CHOICES)
    w = models.IntegerField("Potencia/Capacidad(Watts)", editable=False)
    paneles = models.IntegerField("Paneles", editable=False)
    expansiones = models.IntegerField("Expansiones", editable=False)
    bases = models.IntegerField("Bases de Paneles", editable=False)
    modelo = models.CharField("Modelo", max_length=255, default="Longi", help_text="Modelo por defecto de las Power_Stations")
    marca = models.CharField("Marca", default="Perro Rojo", help_text="Marca por defecto de las Power_Stations", max_length=255)
    dist = models.CharField("Ditribuidora/Tienda", max_length = 255, choices=DISTRIBUIDORA_CHOICES)
    dist_client = models.CharField("Cliente de Distribuidora", max_length=255, default="")
    vendido = models.BooleanField("Vendido", default=False, help_text="Cuando se realice una relacion de venta de power station se vera reflejado aqui")
    fecha_v = models.DateField("Fecha de Venta", default=None, null=True, blank=True, help_text="Al marcarse como vendida una power station la fecha se actualiza")
    video = models.FileField("Video", upload_to="ventas/videos/", blank=True, null=True, help_text="Video de la power station")
    foto = models.ImageField("Foto", upload_to="ventas/fotos/", blank=True, null=True, help_text="Foto de la power station")



    def __str__(self):
        return f"ID: {self.sn} Tipo: {self.tipo}"

    def save(self, *args, **kwargs):
        tipo_mapping = {
            '300w': {'w': 300, 'paneles': 1, 'expansiones': 4, 'bases': 2},
            '600w': {'w': 600, 'paneles': 1, 'expansiones': 4, 'bases': 2},
            '1200w': {'w': 1200, 'paneles': 2, 'expansiones': 8, 'bases': 4},
            '2400w': {'w': 2400, 'paneles': 3, 'expansiones': 12, 'bases': 6},
            '3000w': {'w': 3000, 'paneles': 3, 'expansiones': 12, 'bases': 6},
        }
        if self.tipo in tipo_mapping:
            data = tipo_mapping[self.tipo]
            self.w = data['w']
            self.paneles = data['paneles']
            self.expansiones = data['expansiones']
            self.bases = data['bases']
        super().save(*args, **kwargs)

class PowerStationPanel(models.Model):
    power_station = models.ForeignKey(Power_Station, on_delete=models.CASCADE)
    panel = models.OneToOneField(Panels, on_delete=models.CASCADE, unique=True)  # Referencia directa