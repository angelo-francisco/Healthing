from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from medicine.models import is_medico, MedicoData


def auth_login(request):
    if request.user.is_authenticated:
        return redirect(reverse("auth_doctor"))

    else:
        if request.method == "GET":
            return render(request, "user_auth/login.html")

        else:
            username = request.POST["username"]
            password = request.POST["senha"]

            user = auth.authenticate(request, username=username, password=password)
            if user:
                auth.login(request, user)
                return redirect(reverse("auth_doctor"))

            messages.add_message(
                request, constants.ERROR, "Username ou senha inválidos"
            )
            return redirect(reverse("auth_login"))


def auth_signup(request):
    if request.user.is_authenticated:
        return redirect(reverse("auth_doctor"))

    else:
        if request.method == "GET":
            return render(request, "user_auth/signup.html")

        else:
            first_name = request.POST["first_name"]
            last_name = request.POST["last_name"]
            username = request.POST["username"]
            email = request.POST["email"]
            password = request.POST["senha"]
            password_conf = request.POST["confirmar_senha"]

            user = User.objects.filter(username=username)

            if not user.exists():
                if password == password_conf:
                    User.objects.create_user(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password,
                    )

                    messages.add_message(
                        request, constants.SUCCESS, "Dados Cadastrados!"
                    )
                    return redirect(reverse("auth_login"))

                messages.add_message(
                    request, constants.WARNING, "As senhas não coincidem!"
                )
                return redirect(reverse("auth_signup"))

            messages.add_message(request, constants.ERROR, "Username em utilização!")
            return redirect(reverse("auth_signup"))


def auth_logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
        return redirect(reverse("auth_login"))

    else:
        return redirect(reverse("auth_doctor"))


@login_required(login_url="/auth/login")
def my_account(request):
    if request.method == "GET":
        medico = MedicoData.objects.filter(user=request.user).exists()
        return render(
            request,
            "user_auth/my_account.html",
            {"is_medico": is_medico(request.user), "medico": medico, "date": request.user.date_joined.strftime("%d/%m/%Y")},
        )
