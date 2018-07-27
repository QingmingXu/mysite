from django.urls import path
from . import views

app_name = 'user'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('login_for_modal/', views.login_for_modal, name='login_for_modal'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('user_center/', views.user_center, name='user_center'),
    path('change_nickname/', views.change_nickname, name='change_nickname'),
    path('bind_email/', views.bind_email, name='bind_email'),
    path('send_verification_code/', views.send_verification_code, name='send_verification_code'),
    path('change_password/', views.change_password, name='change_password'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
]