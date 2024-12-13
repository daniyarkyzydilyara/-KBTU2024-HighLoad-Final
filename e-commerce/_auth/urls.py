from django.urls import path

from .views import (
    GetUserInformationView,
    RegisterUserView,
    SpectacularTokenObtainPairView,
    SpectacularTokenRefreshView,
)

urlpatterns = [
    path("token/", SpectacularTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", SpectacularTokenRefreshView.as_view(), name="token_refresh"),
    path("user/", GetUserInformationView.as_view(), name="user_information"),
    path("register/", RegisterUserView.as_view(), name="register"),
]
