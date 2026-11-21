from django.urls import path
from .views import Logout_view, Login_view, Register_view

urlpatterns = [
    path('register/', Register_view, name='register'),
    path('login/', Login_view, name="login"),
    path('logout/', Logout_view, name='logout')
]