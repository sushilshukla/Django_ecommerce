from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, LogoutView, ProfileView, ChangePasswordView,AddressListCreateView,AddressRetrieveUpdateDestroyView,SetDefaultAddressView,ForgotPasswordView,ResetPasswordView


urlpatterns = [
   path("register/", RegisterView.as_view(), name = "register"),
   path("login/", LoginView.as_view(), name="login"),
   path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
   path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
   path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
   path("logout/", LogoutView.as_view(), name="logout"),
   path("me/", ProfileView.as_view(), name="profile"),
   path("change-password/", ChangePasswordView.as_view(),name="changePassword"),
   path("me/addresses/", AddressListCreateView.as_view(),name="address_list_create"),
   path("me/addresses/<int:pk>/", AddressRetrieveUpdateDestroyView.as_view(),name="address_retrieve_update_destroy"),
   path("me/addresses/<int:pk>/set-default/",SetDefaultAddressView.as_view(),name="address_set_default")
]