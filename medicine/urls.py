from django.urls import path
from medicine.views import *

urlpatterns = [
    path("sign_doctor/", auth_doctor, name="auth_doctor"),
    path("horarios/", horarios, name="horarios"),
    path("consultas/", medico_consultas, name="medico_consultas"),
    path("ver_consultas/<int:id_consulta>/", ver_consultas, name="medico_consultas2"),
    path(
        "terminar_consulta/<int:id_consulta>/",
        terminar_consulta,
        name="terminar_consulta",
    ),
    path("add_documento/<int:id_consulta>/", add_documento, name="add_consulta"),
]
