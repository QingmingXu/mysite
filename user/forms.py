from django import forms
from django.contrib import auth
from django.contrib.auth.models import User

# 登录表单类
class LoginForm(forms.Form):
	username_or_email = forms.CharField(label='用户名或邮箱', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'请输入用户名'}))
	password = forms.CharField(label='密码', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入密码'}))

	# 验证登录的用户是否存在（用户名或密码是否正确）
	def clean(self):
		username_or_email = self.cleaned_data['username_or_email']
		password = self.cleaned_data['password']
		user = auth.authenticate(username=username_or_email, password=password)
		if user is None:
			if User.objects.filter(email=username_or_email).exists():
				username = User.objects.get(email=username_or_email).username
				user = auth.authenticate(username=username, password=password)
				if user:
					self.cleaned_data['user'] = user
					return self.cleaned_data
			raise forms.ValidationError('用户名(邮箱)或密码不正确！')
		else:
			self.cleaned_data['user'] = user
		return self.cleaned_data

# 注册表单类
class RegisterForm(forms.Form):
	username = forms.CharField(label='用户名', min_length=3, max_length=30, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'请输入用户名，3到30个字符'}))
	email = forms.EmailField(label='邮箱', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'请输入注册邮箱'}))
	password = forms.CharField(label='密码', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入密码,不少于六个字符'}))
	password_again = forms.CharField(label='确认密码', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请再次输入密码'}))
	verification_code = forms.CharField(label='验证码', required=False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'点击获取验证码，注意查看邮箱'}))

	def __init__(self, *args, **kwargs):
		if 'request' in kwargs:
			self.request = kwargs.pop('request')
		super(RegisterForm, self).__init__(*args, **kwargs)

	def clean(self):
		# 获取后台生成的发送给用户的邮箱的验证码，该验证码保存在session中
		code = self.request.session.get('register_code', '')
		# 获取用户输入的验证码
		verification_code = self.cleaned_data.get('verification_code', '')
		# 如果发送的验证码没有过期，并且用户输入的验证码与发送的验证码不一致，报错
		if not (code != '' and code==verification_code):
			raise forms.ValidationError('验证码不正确')
		# （用户输入的内容）通过验证，返回cleaned_data
		return self.cleaned_data

	# 验证注册的用户名是否已经存在
	def clean_username(self):
		username = self.cleaned_data['username']
		if User.objects.filter(username=username).exists():
			raise forms.ValidationError('用户名已存在！')
		return username

	# 验证注册的邮箱是否已经存在
	def clean_email(self):
		email = self.cleaned_data['email']
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError('邮箱已存在！')
		return email

	# 验证第二次输入的密码是否与第一次输入的相同，并返回第二次输入的密码
	def clean_password_again(self):
		password = self.cleaned_data['password']
		password_again = self.cleaned_data['password_again']
		if password != password_again:
			raise forms.ValidationError('两次输入的密码不一致！')
		return password_again

	# 验证用户输入的验证码
	def clean_verification_code(self):
		verification_code = self.cleaned_data.get('verification_code', '').strip()
		if verification_code == '':
			raise forms.ValidationError('验证码不能为空')
		return verification_code


# 用户昵称更改表单类
class ChangeNicknameForm(forms.Form):
	nickname_new = forms.CharField(label='新的昵称', max_length=20, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'请输入新的昵称'}))

	def __init__(self, *args, **kwargs):
		if 'user' in kwargs:
			self.user = kwargs.pop('user')
		super(ChangeNicknameForm, self).__init__(*args, **kwargs)

	# 将被is_vaild方法调用.对数据进行验证和处理
	def clean(self):
		# 上面的方法使得实例有了user属性，这个user是从前端页面传来的，原本是渲染前端的数据。验证用户是否已登录
		if self.user.is_authenticated:
			# 如果已登录则给表单实例的cleaned_data添加一个user元素
			self.cleaned_data['user'] = self.user
		else:
			# 未登录，报错
			raise forms.ValidationError('尚未登录！')
		# 返回cleaned_data
		return self.cleaned_data

	# 验证用户输入的用户名是否为空
	def clean_nickname_new(self):
		nickname_new = self.cleaned_data.get('nickname_new', '').strip()
		if nickname_new == '':
			raise forms.ValidationError('新的昵称不能为空！')
		return nickname_new

class BindEmailForm(forms.Form):
	email = forms.EmailField(label='邮箱', widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'输入要绑定的邮箱'}))
	verification_code = forms.CharField(label='验证码', required=False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'点击获取验证码，注意查看邮箱'}))

	def __init__(self, *args, **kwargs):
		if 'request' in kwargs:
			self.request = kwargs.pop('request')
		super(BindEmailForm, self).__init__(*args, **kwargs)

	# 将被is_vaild方法调用.对数据进行验证和处理
	def clean(self):
		# 验证用户是否已登录
		if self.request.user.is_authenticated:
			# 如果已登录则给表单实例的cleaned_data添加一个user元素
			self.cleaned_data['user'] = self.request.user
		else:
			# 未登录，报错
			raise forms.ValidationError('尚未登录！')
		# 如果用户已绑定邮箱，报错
		if self.request.user.email != '':
			raise forms.ValidationError('你已经绑定了邮箱')
		# 获取后台生成的发送给用户的邮箱的验证码，该验证码保存在session中
		code = self.request.session.get('bind_email_code', '')
		# 获取用户输入的验证码
		verification_code = self.cleaned_data.get('verification_code', '')
		# 如果发送的验证码没有过期，并且用户输入的验证码与发送的验证码不一致，报错
		if not (code != '' and code==verification_code):
			raise forms.ValidationError('验证码不正确')
		# （用户输入的内容）通过验证，返回cleaned_data
		return self.cleaned_data

	def clean_email(self):
		email = self.cleaned_data['email']
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError('该邮箱已被绑定')
		return email

	def clean_verification_code(self):
		verification_code = self.cleaned_data.get('verification_code', '').strip()
		if verification_code == '':
			raise forms.ValidationError('验证码不能为空')
		return verification_code

class ChangePasswordForm(forms.Form):
	old_password = forms.CharField(label='旧密码', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入旧密码'}))
	new_password = forms.CharField(label='新密码', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入新密码'}))
	new_password_again = forms.CharField(label='确认密码', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'再次输入新密码'}))

	def __init__(self, *args, **kwargs):
		if 'user' in kwargs:
			self.user = kwargs.pop('user')
		super(ChangePasswordForm, self).__init__(*args, **kwargs)

	# 验证用户两次输入的新密码是否一致
	def clean(self):
		new_password = self.cleaned_data.get('new_password', '')
		new_password_again = self.cleaned_data.get('new_password_again', '')
		if not (new_password != new_password_again or new_password != ''):
			raise forms.ValidationError('两次输入的密码不一致！')
		return self.cleaned_data

	# 验证用户输入的旧密码是否正确
	def clean_old_password(self):
		old_password = self.cleaned_data.get('old_password', '')
		if not self.user.check_password(old_password):
			raise forms.ValidationError('旧密码错误')
		return old_password

class ForgotPasswordForm(forms.Form):
	username = forms.CharField(label='用户名', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'请输入用户名'}))
	email = forms.EmailField(label='注册邮箱', widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'请输入用户绑定的邮箱'}))
	new_password = forms.CharField(label='新密码', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入新密码'}))
	new_password_again = forms.CharField(label='确认密码', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'再次输入新密码'}))
	verification_code = forms.CharField(label='验证码', required=False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'点击获取验证码，注意查看邮箱'}))

	def __init__(self, *args, **kwargs):
		if 'request' in kwargs:
			self.request = kwargs.pop('request')
		super(ForgotPasswordForm, self).__init__(*args, **kwargs)

	def clean(self):
		new_password = self.cleaned_data.get('new_password', '')
		new_password_again = self.cleaned_data.get('new_password_again', '')
		if not (new_password != new_password_again or new_password != ''):
			raise forms.ValidationError('两次输入的密码不一致！')
		return self.cleaned_data

	def clean_username(self):
		username = self.cleaned_data['username'].strip()
		if not User.objects.filter(username=username).exists():
			raise forms.ValidationError('用户名不存在！')
		return username

	def clean_email(self):
		email = self.cleaned_data['email'].strip()
		if not User.objects.filter(email=email).exists():
			raise forms.ValidationError('邮箱不存在！')
		return email

	def clean_verification_code(self):
		verification_code = self.cleaned_data.get('verification_code', '').strip()
		if verification_code == '':
			raise forms.ValidationError('验证码不能为空')
		code = self.request.session.get('forgot_password_code', '')
		# 获取用户输入的验证码
		# 如果发送的验证码没有过期，并且用户输入的验证码与发送的验证码不一致，报错
		if not (code != '' and code==verification_code):
			raise forms.ValidationError('验证码不正确')
		return verification_code

		






		
