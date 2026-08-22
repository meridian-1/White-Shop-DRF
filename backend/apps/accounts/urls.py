from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegisterView, LoginView, LogoutView
from djoser.views import UserViewSet


user_list = UserViewSet.as_view({"get": "list"})
user_me = UserViewSet.as_view({"get": "me", "put": "me", "delete": "me"})
user_set_password = UserViewSet.as_view({"post": "set_password"})

urlpatterns = [
    path("register/", RegisterView.as_view({"post": "create"}), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("users/me/", user_me, name="user-me"),
    path("user/set_password", user_set_password, name="user-set-password"),
    path("users/", user_list, name="user-list"),
]
