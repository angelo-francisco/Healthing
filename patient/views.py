from django.shortcuts import render, redirect
from django.urls import reverse
from medicine.models import *
from django.contrib.auth.decorators import login_required
from patient.models import Consulta, Documento
from django.contrib import messages
from django.contrib.messages import constants


@login_required()
def patient_home(request):
    medicos = MedicoData.objects.all()
    areas = MedicineArea.objects.all()

    if request.method == "GET":
        return render(
            request,
            "patient/patient_home.html",
            {"medicos": medicos, "areas": areas, "is_medico": is_medico(request.user)},
        )

    else:
        medico_filtrar = request.POST.get("medico")
        all_areas = request.POST.getlist("especialidades")
        if medico_filtrar:
            medicos = medicos.filter(nome_completo__icontains=medico_filtrar)

        if all_areas:
            medicos = medicos.filter(area_id__in=all_areas)
        # TODO: implementar lógica dos lembretes
        return render(
            request,
            "patient/patient_home.html",
            {"medicos": medicos, "areas": areas, "is_medico": is_medico(request.user)},
        )


@login_required()
def escolher_horario(request, id_medico):
    if request.method == "GET":
        medico = MedicoData.objects.get(id=id_medico)
        datas = (
            Horarios.objects.filter(user=medico.user)
            .filter(data__gte=dt.datetime.now())
            .filter(agendada=False)
        )

        print(datas)
        return render(
            request,
            "patient/escolher_horario.html",
            context={
                "medico": medico,
                "datas": datas,
                "is_medico": is_medico(request.user),
            },
        )

    else:
        return redirect(reverse("escolher_horario"))


@login_required()
def agendar_consulta(request, id_consulta):
    horario = Horarios.objects.get(id=id_consulta)

    consulta = Consulta.objects.create(
        patient=request.user,
        horario=horario,
    )
    consulta.save()

    horario.agendada = True
    horario.save()

    messages.add_message(request, constants.SUCCESS, "Consulta marcada!")
    return redirect(reverse("patient_consultas"))


@login_required()
def patient_consultas(request):
    if request.method == "GET":
        consultas = Consulta.objects.filter(patient=request.user).filter(
            horario__data__gte=dt.datetime.now()
        )
        return render(
            request,
            "patient/patient_consultas.html",
            {"consultas": consultas, "is_medico": is_medico(request.user)},
        )

    else:
        # TODO: lógica do filtro de pesquisa
        return redirect(reverse("patient_consultas"))


@login_required()
def ver_consultas(request, id_consulta):
    if request.method == "GET":
        consultas = Consulta.objects.get(id=id_consulta)
        dados_medico = MedicoData.objects.get(user=consultas.horario.user)
        documentos = Documento.objects.filter(consulta=consultas)
        return render(
            request,
            "patient/ver_consultas.html",
            {
                "consultas": consultas,
                "medico": dados_medico,
                "documentos": documentos,
                "is_medico": is_medico(request.user),
            },
        )
