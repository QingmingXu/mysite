from django.urls import path
from . import views

# 给特定的url绑定相应的视图函数，并给予别名

# 命名空间
app_name = 'blog'
urlpatterns = [
	path('', views.blog_list, name='blog_list'),
    path('<int:blog_pk>', views.blog_detail, name='blog_detail'),
    path('type/<int:blog_type_pk>', views.blog_with_type, name='blog_with_type'),
    path('date/<int:year>/<int:month>', views.blog_with_date, name='blog_with_date'),

]