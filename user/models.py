from django.db import models
from django.contrib.auth.models import User

'''django自带的的User模型很强大，但在此项目中并不能满足我的需求，而且项目开发到了中后期，所以这里使用拓展类来扩展'''

# 创建拓展类
class Profile(models.Model):
	# 拓展类与User建立一对一关系，一个拓展类实例对象与一个用户实例对象唯一关联
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	# 以下是拓展的属性
	nickname = models.CharField(max_length=20, default='', verbose_name='昵称') # 昵称

	# 自定义类，用print打印一个实例化的类的时候，显示__str__函数返回的内容
	def __str__(self):
		return '<Profile: %s for %s>' %(self.nickname, self.user.username)

# 定义实例方法，再动态的赋予User模型
def get_nickname(self):
	if Profile.objects.filter(user=self).exists():
		profile = Profile.objects.get(user=self)
		return profile.nickname
	else:
		return ''

def get_nickname_or_username(self):
	if Profile.objects.filter(user=self).exists():
		profile = Profile.objects.get(user=self)
		return profile.nickname
	else:
		return self.username

def has_nickname(self):
	return Profile.objects.filter(user=self).exists()

User.get_nickname = get_nickname
User.get_nickname_or_username = get_nickname_or_username
User.has_nickname = has_nickname



