from django.contrib.auth.models import User
from drf_spectacular.views import extend_schema
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

__all__ = (
    "SpectacularTokenObtainPairView",
    "SpectacularTokenRefreshView",
    "GetUserInformationView",
    "RegisterUserView",
)


class SpectacularTokenObtainPairView(TokenObtainPairView):
    @extend_schema(summary="Obtain JWT token", tags=["auth"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SpectacularTokenRefreshView(TokenRefreshView):
    @extend_schema(summary="Refresh JWT token", tags=["auth"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class GetUserInformationView(APIView):
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = (
                "id",
                "username",
                "email",
                "first_name",
                "last_name",
                "is_active",
                "is_staff",
                "is_superuser",
            )
            ref_name = "UserSerializer"

    permission_classes = (IsAuthenticated,)

    @extend_schema(summary="Get user information", tags=["auth"], responses=UserSerializer)
    def get(self, request):
        serializer = self.UserSerializer(request.user)
        return Response(serializer.data, status=200)


class RegisterUserView(APIView):
    class RegisterUserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = (
                "id",
                "username",
                "email",
                "password",
                "first_name",
                "last_name",
            )
            ref_name = "RegisterUserSerializer"

    @extend_schema(summary="Register user", tags=["auth"], request=RegisterUserSerializer)
    def post(self, request):
        serializer = self.RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(**serializer.validated_data)
        user.set_password(serializer.validated_data["password"])
        user.save()
        return Response(status=201)
