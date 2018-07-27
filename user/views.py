import datetime
import string
import random
import time
from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.models import User
from .forms import LoginForm, RegisterForm, ChangeNicknameForm, BindEmailForm, ChangePasswordForm, ForgotPasswordForm
from django.http import JsonResponse
from django.core.mail import send_mail
from .models import Profile

def login_for_modal(request):
    login_form = LoginForm(request.POST)
    data = {}
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data['status'] ='SUCCESS'
    else:
        data['status'] ='ERROR'
    return JsonResponse(data)

def login(request):
	if request.method == 'POST':
		login_form = LoginForm(request.POST)
		if login_form.is_valid():
			user = login_form.cleaned_data['user']
			auth.login(request, user)
			return redirect(request.GET.get('from', reverse('home')))
	else:
		login_form = LoginForm()

	context = {}
	context['login_form'] = login_form
	return render(request, 'user/login.html', context)

def logout(request):
	referer = request.META.get('HTTP_REFERER', reverse('home'))
	auth.logout(request)
	return redirect(referer)

def register(request):
	if request.method == 'POST':
		register_form = RegisterForm(request.POST, request=request)
		if register_form.is_valid():
			username = register_form.cleaned_data['username']
			email = register_form.cleaned_data['email']
			password =register_form.cleaned_data['password']
			user = User.objects.create_user(username,email,password)
			user.save()
			# 清除session
			del request.session['register_code']

			user = auth.authenticate(username=username, password=password)
			auth.login(request, user)
			return redirect(request.GET.get('from', reverse('home')))
	else:
		register_form = RegisterForm()

	context = {}
	context['register_form'] = register_form
	return render(request, 'user/register.html', context)

def user_center(request):
	context = {}
	return render(request, 'user/user_center.html', context)

def change_nickname(request):
	redirect_to = request.GET.get('from', reverse('home'))
	if request.method == 'POST':
		form = ChangeNicknameForm(request.POST, user=request.user)
		if form.is_valid():
			nickname_new = form.cleaned_data['nickname_new']
			profile, created = Profile.objects.get_or_create(user=request.user)
			profile.nickname = nickname_new
			profile.save()
			return redirect(redirect_to)
	else:
		form = ChangeNicknameForm()
	context = {}
	context['form'] = form
	context['page_title'] = '修改昵称'
	context['form_title'] = '修改昵称'
	context['submit_text'] = '修改'
	context['return_back_url'] = redirect_to
	return render(request, 'user/forms.html', context)

def bind_email(request):
	redirect_to = request.GET.get('from', reverse('home'))
	if request.method == 'POST':
		form = BindEmailForm(request.POST, request=request)
		if form.is_valid():
			email = form.cleaned_data['email']
			request.user.email = email
			request.user.save()
			# 清除session
			del request.session['bind_email_code']
			return redirect(redirect_to)
	else:
		form = BindEmailForm()
	context = {}
	context['form'] = form
	context['page_title'] = '绑定邮箱'
	context['form_title'] = '绑定邮箱'
	context['submit_text'] = '绑定'
	context['return_back_url'] = redirect_to
	return render(request, 'user/bind_email.html', context)

def send_verification_code(request):
	# 获取前端ajax传递的email，获取不到则取空字符
	email = request.GET.get('email', '')
	send_for = request.GET.get('send_for', '')
	data = {}
	# email不为空字符
	if email != '':
		# 生成验证码
		code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
		# 获取现在的时间，并用int函数取整
		now = int(time.time())
		# 从session中获取上次发送验证码的时间，如果session过期或者用户没有请求验证码则取零
		send_code_time = request.session.get('bind_email_time', 0)
		# 如果这次请求验证码的时间与上次请求验证码的时间之间的间隔小于30秒,则返回错误
		if now - send_code_time < 30:
			data['status'] = 'ERROR'
		# 将验证码和发送验证码的时间保存到session
		else:
			request.session[send_for] = code
			request.session['bind_email_time'] = now #将现在的时间作为发送验证码的时间
			# 发送邮件,fail_silently=False不忽略邮件发送时抛出的异常
			send_mail('绑定邮箱', '验证码：%s' %(code,), '2827980689@qq.com', [email], fail_silently=False)

			data['status'] = 'SUCCESS'
	else:
		data['status'] = 'ERROR'
	return JsonResponse(data)

def change_password(request):
	redirect_to = reverse('home')
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST, user=request.user)
		if form.is_valid():
			user = request.user
			new_password = form.cleaned_data['new_password']
			user.set_password(new_password)
			user.save()
			auth.logout(request)
			return redirect(redirect_to)
	else:
		form = ChangePasswordForm()
	context = {}
	context['form'] = form
	context['page_title'] = '修改密码'
	context['form_title'] = '修改密码'
	context['submit_text'] = '确认修改'
	context['return_back_url'] = redirect_to
	return render(request, 'user/forms.html', context)

def forgot_password(request):
	redirect_to = request.GET.get('from', reverse('home'))
	if request.method == 'POST':
		form = ForgotPasswordForm(request.POST, request=request)
		if form.is_valid():
			new_password = form.cleaned_data['new_password']
			email = form.cleaned_data['email']
			user = User.objects.get(email=email)
			user.set_password(new_password)
			user.save()
			del request.session['forgot_password_code']
			return redirect(redirect_to)
	else:
		form = ForgotPasswordForm()
	context = {}
	context['form'] = form
	context['page_title'] = '忘记密码'
	context['form_title'] = '忘记密码'
	context['submit_text'] = '重置密码'
	context['return_back_url'] = redirect_to
	return render(request, 'user/forgot_password.html', context)





