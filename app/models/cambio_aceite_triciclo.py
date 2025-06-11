# Nueva tabla para cambios de aceite de triciclos
from django.db import models
from .cliente import Cliente
from .empresa import Empresa
from .triciclo import Triciclo
from .registro import Registro
from datetime import date

class CambioAceiteTriciclo(models.Model):
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL, help_text="Cliente que realizó el cambio")
    empresa = models.ForeignKey(Empresa, null=True, blank=True, on_delete=models.SET_NULL, help_text="Empresa que realizó el cambio")
    triciclo = models.ForeignKey(Triciclo, on_delete=models.CASCADE, help_text="Triciclo asociado al cambio de aceite")
    fecha = models.DateField("Fecha del cambio de aceite", default=date.today)
    km300 = models.BooleanField("300 km", default=False, help_text="¿Se realizó el cambio a los 300 km?")
    km600 = models.BooleanField("600 km", default=False, help_text="¿Se realizó el cambio a los 600 km?")
    km1000 = models.BooleanField("1000 km", default=False, help_text="¿Se realizó el cambio a los 1000 km?")
    kilometros = models.PositiveIntegerField("Kilómetros reales", help_text="Kilometraje al momento del cambio")
    foto = models.ImageField("Foto del kilometraje/cambio", upload_to="cambios_aceite/fotos/", blank=True, null=True)
    comentario = models.TextField("Comentario", blank=True)
    aprobado = models.BooleanField("Aprobado", default=False)
    no_paso_garantia = models.BooleanField("No pasó la garantía", default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Si no pasó la garantía, poner tiempoR en 0 en la relación de venta
        if self.no_paso_garantia and self.triciclo:
            try:
                registro = Registro.objects.get(triciclo=self.triciclo)
                if registro.tiempoR != 0:
                    registro.tiempoR = 0
                    registro.save()
            except Registro.DoesNotExist:
                pass

    def __str__(self):
        comprador = self.cliente if self.cliente else self.empresa
        return f"Cambio de aceite: {comprador} - {self.triciclo} - {self.fecha}"

    class Meta:
        verbose_name = "Cambio de aceite (triciclo)"
        verbose_name_plural = "Cambios de aceite (triciclos)"
