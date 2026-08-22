from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from djoser.views import UserViewSet
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView
from .serializers import (
    CustomTokenObtainPairSerializer,
)


class RegisterView(UserViewSet):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": serializer.data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(TokenBlacklistView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
