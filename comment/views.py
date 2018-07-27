from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from .models import Comment
from .forms import CommentForm

def submit_comment(request):
	'''referer = request.META.get('HTTP_REFERER', reverse('home'))
	if not request.user.is_authenticated:
		#return render(request, 'error.html', {'message':'用户未登录！', 'redirect_to':referer})
		data = {}
		data['status'] = 'ERROR'
		data['message'] = '用户未登录!'
		return JsonResponse(data)
	text = request.POST.get('text', '').strip()
	if text == '':
		#return render(request, 'error.html', {'message':'评论内容为空！', 'redirect_to':referer})
		data = {}
		data['status'] = 'ERROR'
		data['message'] = '评论内容不能为空！'
		return JsonResponse(data)
	try:
		content_type = request.POST.get('content_type', '')
		object_id = int(request.POST.get('object_id', ''))
		model_class = ContentType.objects.get(model=content_type).model_class()
		model_obj = model_class.objects.get(pk=object_id)
	except Exception as e:
		#return render(request, 'error.html', {'message':'评论对象不存在！', 'redirect_to':referer})
		data = {}
		data['status'] = 'ERROR'
		data['message'] = '评论对象不存在！'
		return JsonResponse(data)
	comment = Comment()
	comment.user = request.user
	comment.text = text
	comment.content_object = model_obj
	comment.save()

	data = {}
	data['status'] = 'SUCCESS'
	data['username'] = comment.user.username
	data['comment_time'] = comment.comment_time.strftime('%Y-%m-%d %H:%M:%S')
	data['text'] = comment.text
	return JsonResponse(data)'''

	# 请求从哪跳过来，拿到它
	referer = request.META.get('HTTP_REFERER', reverse('home'))
	# 用评论表单的数据以及request.user中的数据作为参数来实例化表单类
	comment_form = CommentForm(request.POST, user=request.user)
	# 数据验证，将调用clean方法
	if comment_form.is_valid():
		# 通过，从表单类实例的cleaned_data中拿到所需数据来实例化相应的comment实例。即将用户提交的相应的评论或回复保存到数据库
		comment = Comment()
		comment.user = comment_form.cleaned_data['user']
		comment.text = comment_form.cleaned_data['text']
		comment.content_object = comment_form.cleaned_data['content_object']

		parent = comment_form.cleaned_data['parent']
		# 判断是回复
		if not parent is None:
			comment.root = parent.root if not parent.root is None else parent
			# 当前comment实例的上一级，可能是评论也可能是回复
			comment.parent = parent
			# comment.reply_to是comment实例的回复对象属性，parent.user是回复的对象
			comment.reply_to = parent.user
		comment.save()
		# 发送邮件通知
		comment.send_mail()

		# 创建一个字典，制作一些数据返回给前端ajax，ajax将利用这些数据来插入评论和回复
		data = {}
		data['status'] = 'SUCCESS'
		data['username'] = comment.user.get_nickname_or_username()
		data['comment_time'] = comment.comment_time.timestamp()
		data['text'] = comment.text
		data['content_type'] = ContentType.objects.get_for_model(Comment).model
		if not parent is None:
			data['reply_to'] = comment.reply_to.get_nickname_or_username()
		else:
			data['reply_to'] = ''
		data['pk'] = comment.pk
		data['root_pk'] = comment.root.pk  if not comment.root is None else ''
		#return redirect(referer)
	else:
		data = {}
		data['status'] = 'ERROR'
		data['message'] = list(comment_form.errors.value())[0][0]
	return JsonResponse(data)




