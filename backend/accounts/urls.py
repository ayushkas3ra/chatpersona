from django.urls import path
from .views import Logout_view, Login_view, Register_view, csrf_view, current_user_view

urlpatterns = [
    path('register/', Register_view, name='register'),
    path('login/', Login_view, name="login"),
    path('logout/', Logout_view, name='logout'),
    path('csrf/', csrf_view, name="csrf"),
    path('me/', current_user_view, name='current_user')
]

