from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from medicine.models import *
from django.contrib import messages
from django.contrib.messages import constants
import datetime as dt
from patient.models import Consulta, Documento


@login_required(login_url="/auth/login/")
def auth_doctor(request):

    if is_medico(request.user):
        messages.add_message(request, constants.ERROR, "Você já está cadastrado!")
        return redirect(reverse("horarios"))

    else:
        if request.method == "GET":
            areas = MedicineArea.objects.all()

            context = {
                "areas": areas,
            }
            return render(request, "medicine/auth_doctor.html", context=context)

        else:
            crm = request.POST["crm"]
            nome_completo = request.POST["nome"]
            cep = request.POST["cep"]
            rua = request.POST["rua"]
            bairro = request.POST["bairro"]
            numero = request.POST["numero"]
            rg = request.FILES["rg"]
            foto_perfil = request.FILES["foto"]
            cedula_identidade_medica = request.FILES["cim"]
            descricao = request.POST["descricao"]
            valor_consulta = request.POST["valor_consulta"]
            area = request.POST["especialidade"]

            # TODO: validar campos

            medico = MedicoData.objects.create(
                crm=crm,
                nome_completo=nome_completo,
                cep=cep,
                rua=rua,
                bairro=bairro,
                numero=numero,
                rg=rg,
                foto_perfil=foto_perfil,
                cedula_identidade_medica=cedula_identidade_medica,
                descricao=descricao,
                valor_consulta=valor_consulta,
                user=request.user,
                area_id=area,
            )

            medico.save()

            messages.add_message(
                request,
                constants.SUCCESS,
                "Médico cadastrado!",
                {"is_medico": is_medico(request.user)},
            )
            return redirect(reverse("horarios"))


@login_required(login_url="/auth/login/")
def horarios(request):
    if request.method == "GET":
        medico = MedicoData.objects.filter(user=request.user)
        horarios = Horarios.objects.filter(user=request.user)
        if medico.exists():
            context = {
                "medico": medico.first(),
                "horarios": horarios,
                "is_medico": is_medico(request.user),
            }
            return render(request, "medicine/horarios.html", context=context)
        else:
            messages.add_message(
                request, constants.ERROR, "Você não está cadastrado como médico!"
            )
            return redirect(reverse("auth_doctor"))

    else:
        data = request.POST["data"]

        formatted_data = dt.datetime.strptime(data, "%Y-%m-%dT%H:%M")
        actual_data = dt.datetime.now()

        if formatted_data <= actual_data:
            messages.add_message(
                request,
                constants.ERROR,
                "Você não pode marcar consultas para agora ou para o passado!",
            )
            return redirect(reverse("horarios"))

        else:
            Horarios.objects.create(
                data=formatted_data,
                user=request.user,
            ).save()

            messages.add_message(request, constants.SUCCESS, "Horário adicionado!")
            return redirect(reverse("horarios"))


@login_required(login_url="/auth/login/")
def medico_consultas(request):
    if not is_medico(request.user):
        messages.add_message(
            request, constants.ERROR, "Somente médicos podem acessar está área!"
        )
        return redirect(reverse("patient_home"))

    hoje = dt.datetime.now().date()

    consultas_hoje = (
        Consulta.objects.filter(horario__user=request.user)
        .filter(horario__data__gte=hoje)
        .filter(horario__data__lt=hoje + dt.timedelta(days=1))
    )
    consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values("id"))
    return render(
        request,
        "medicine/medico_consultas.html",
        {
            "consultas_hoje": consultas_hoje,
            "consultas_restantes": consultas_restantes,
            "is_medico": is_medico(request.user),
        },
    )


@login_required(login_url="/auth/login/")
def ver_consultas(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, "Você não é médico!")
        return redirect(reverse("patient_home"))

    if request.method == "GET":
        consultas = Consulta.objects.get(id=id_consulta)
        documentos = Documento.objects.filter(consulta=consultas)

        context = {
            "consulta": consultas,
            "documentos": documentos,
            "is_medico": is_medico(request.user),
        }
        return render(request, "medicine/ver_consulta.html", context=context)

    elif request.method == "POST":
        consulta = Consulta.objects.get(id=id_consulta)
        link = request.POST.get("link")

        if consulta.status == "F" or consulta.status == "C":
            messages.add_message(
                request, constants.WARNING, "Consulta já foi finalizada/cancelada!"
            )
            return redirect(f"/medicine/ver_consultas/{id_consulta}")

        consulta.link = link
        consulta.status = "I"
        consulta.save()

        messages.add_message(request, constants.SUCCESS, "Consulta Inicializada!")
        return redirect(f"/medicine/ver_consultas/{id_consulta}")


@login_required(login_url="/auth/login/")
def terminar_consulta(request, id_consulta):
    consulta = Consulta.objects.get(id=id_consulta)

    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, "Você não é médico!")
        return redirect(f"/medicine/ver_consultas/{id_consulta}")

    if request.user != consulta.horario.user:
        messages.add_message(request, constants.WARNING, "Essa consulta não é sua!")
        return redirect(f"/medicine/ver_consultas/{id_consulta}")

    consulta.status = "F"
    consulta.save()

    return redirect(f"/medicine/ver_consultas/{id_consulta}")


@login_required(login_url="/auth/login/")
def add_documento(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(
            request, constants.WARNING, "Somente médicos podem acessar essa página."
        )
        return redirect(reverse("patient_home"))

    consulta = Consulta.objects.get(id=id_consulta)

    if consulta.horario.user != request.user:
        print(consulta.horario.user)
        print(request.user)
        messages.add_message(request, constants.ERROR, "Essa consulta não é sua!")
        return redirect(f"/medicine/ver_consultas/{id_consulta}")

    titulo = request.POST.get("titulo")
    documento = request.FILES.get("documento")

    if not documento:
        messages.add_message(request, constants.WARNING, "Adicione o documento.")
        return redirect(f"/medicine/ver_consultas/{id_consulta}")

    documento = Documento(consulta=consulta, titulo=titulo, documento=documento)

    documento.save()

    messages.add_message(request, constants.SUCCESS, "Documento enviado com sucesso!")
    return redirect(f"/medicine/ver_consultas/{id_consulta}")
