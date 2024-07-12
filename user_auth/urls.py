from django.urls import path
from user_auth.views import *

urlpatterns = [
    path("login/", auth_login, name="auth_login"),
    path("signup/", auth_signup, name="auth_signup"),
    path("logout/", auth_logout, name="auth_logout"),
    path("my_account/", my_account, name="my_account"),
]
