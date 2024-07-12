from django.urls import path
from patient.views import *

urlpatterns = [
    path("", patient_home, name="patient_home"),
    path(
        "escolher_horario/<int:id_medico>/", escolher_horario, name="escolher_horario"
    ),
    path(
        "agendar_consulta/<int:id_consulta>", agendar_consulta, name="agendar_consulta"
    ),
    path("consultas/", patient_consultas, name="patient_consultas"),
    path("ver_consultas/<int:id_consulta>", ver_consultas, name="ver_consulta"),
]
