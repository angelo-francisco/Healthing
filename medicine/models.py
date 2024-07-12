from django.db import models
from django.contrib.auth.models import User
import datetime as dt


class MedicineArea(models.Model):
    area = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.area


class MedicoData(models.Model):
    crm = models.CharField(max_length=30)
    nome_completo = models.CharField(max_length=100)
    cep = models.CharField(max_length=20)
    rua = models.CharField(max_length=30)
    bairro = models.CharField(max_length=30)
    numero = models.IntegerField()
    rg = models.ImageField(upload_to="RGs")
    foto_perfil = models.ImageField(upload_to="FotoPerfil")
    cedula_identidade_medica = models.ImageField(upload_to="CedulasIdentidadeMedica")
    descricao = models.TextField()
    valor_consulta = models.FloatField(default=100)

    # ForgeinKey
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    area = models.ForeignKey(MedicineArea, on_delete=models.DO_NOTHING)

    def next_data(self):
        return (
            Horarios.objects.filter(user=self.user)
            .filter(data__gt=dt.datetime.now())
            .filter(agendada=False)
            .order_by("data")
            .first()
        )

    def __str__(self) -> str:
        return self.nome_completo


class Horarios(models.Model):
    data = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    agendada = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.data}"


# Auxiliary Functions
def is_medico(user):
    doctor = MedicoData.objects.filter(user=user)
    return doctor.exists()
