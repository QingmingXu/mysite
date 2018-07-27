from django.contrib import admin
from django.contrib.auth.models import User # 导入原本的用户模型
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # 导入原本的用户模型后台类，并且给予别名，方便重写该后台类
from .models import Profile # 导入用户模型的拓展

# 让拓展的内容（拓展类）能在后台的用户编辑页面中进行操作
# 以下代码会告诉django，Profile对象要在User后台页面编辑。
class ProfileInline(admin.StackedInline):
	model = Profile
	can_delete = False

class UserAdmin(BaseUserAdmin):
	inlines = (ProfileInline,)
	list_display = ('username', 'nickname', 'email', 'is_staff', 'is_active', 'is_superuser')

	def nickname(self, obj):
		return obj.profile.nickname

	nickname.short_description = '昵称'

# 创建拓展类的后台类
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'nickname')

admin.site.register(Profile, ProfileAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

