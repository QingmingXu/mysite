from django.urls import path
from . import views

app_name = 'likes'
urlpatterns = [
	path('like_change', views.like_change, name='like_change'),

]