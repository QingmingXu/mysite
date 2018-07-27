from django.contrib import admin
from .models import Blog, BlogType

# 博客类型模型的后台管理类，创建该类使得博客类型可以在后台管理，后台管理类应该继承admin.ModelAdmin
class BlogTypeAdmin(admin.ModelAdmin):
	# 显示id和type_name
    list_display = ('id', 'type_name')

# 博客模型的后台管理类，创建该类使得博客可以在后台管理，后台管理类应该继承admin.ModelAdmin
class BlogAdmin(admin.ModelAdmin):
	# 显示id，title，blog_type，。。。
    list_display = ('id', 'title', 'blog_type', 'author', 'get_read_num', 'create_time', 'last_updated_time')

# 注册
admin.site.register(Blog, BlogAdmin)
admin.site.register(BlogType, BlogTypeAdmin)