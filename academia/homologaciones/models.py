from datetime import date
from django.db import models

# Create your models here.
TIPO_IES_CHOICES = [
    ("U", "Universidad"),
    ("I", "Instituto Tecnológico")
]

MODALIDAD_CHOICES = [
    ("P", "Presencial"),
    ("H", "Híbrida"),
    ("L", "En Línea")
]

class Ies(models.Model):
    codigo = models.CharField(max_length=8)
    nombre = models.CharField(max_length=64)
    tipo = models.CharField(max_length=2, choices=TIPO_IES_CHOICES)

    class Meta:
        verbose_name = 'IES'
        verbose_name_plural = 'IES'

    def __str__(self) -> str:
        return self.codigo

class Carrera(models.Model):
    ies = models.ForeignKey(Ies, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    aprobacion = models.CharField(max_length=32, blank=True)
    modalidad = models.CharField(max_length=2, choices=MODALIDAD_CHOICES)
    nota_aprobacion = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nota_maxima = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f"{self.nombre} ({self.ies})"

class Asignatura(models.Model):
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    nivel = models.IntegerField(default=1)
    codigo = models.CharField(max_length=32, blank=True)
    nombre = models.CharField(max_length=255)
    horas = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.nombre}"

class Contenido(models.Model):
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    unidad =  models.IntegerField(default=1)
    tema = models.CharField(max_length=255)
    contenido = models.TextField()

    def __str__(self) -> str:
        return self.tema

class Homologacion(models.Model):
    origen = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='carrera_origen')
    destino = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='carrera_destino')
    fecha = models.DateField(default=date.today)
    cedula = models.CharField(max_length=10, unique=True)
    nombres = models.CharField(max_length=64)
    apellidos = models.CharField(max_length=64)

    class Meta:
        verbose_name = 'Homologación'
        verbose_name_plural = 'Homologaciones'

    def __str__(self) -> str:
        return f"{self.nombres} {self.apellidos}"


class Analisis(models.Model):
    homologacion = models.ForeignKey(Homologacion, on_delete=models.CASCADE)
    destino = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='asignatura_destino')
    origen = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='asignatura_origen')
    nota_aprobacion = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    periodo = models.CharField(max_length=128)
    porcentaje_horas = models.IntegerField(default=80)
    porcentaje_contenidos = models.IntegerField(default=80)
    nota_final = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cumple = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Analisis'
        verbose_name_plural = 'Analisis'

    def __str__(self) -> str:
        return f"{self.destino} - {self.nota_final}"