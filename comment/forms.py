from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from ckeditor.widgets import CKEditorWidget
from .models import Comment

# 使用django forms，创建一个表单类，表单类的所有属性都会被转化为相应的html代码显示在前端页面
class CommentForm(forms.Form):
	content_type = forms.CharField(widget=forms.HiddenInput)
	object_id = forms.IntegerField(widget=forms.HiddenInput)
	text = forms.CharField(label='', widget=CKEditorWidget(config_name='comment_ckeditor', attrs={'class':'form-control', 'placeholder':'登录后在此评论'}), error_messages={'required': '评论不能为空！'})
	# 用来区分是提交评论还是提交回复。表单类将在相应的视图函数里被实例化并被加入到上下文里用来渲染模版页面，可以在实例化时给定一些值。
	# 是0代表评论，是其他大于0的值（comment实例的主键值）代表回复。
	reply_comment_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'id': 'reply_comment_id'}))

	'''在view.py中的处理提交评论的视图函数中有：comment_form = CommentForm(request.POST, user=request.user)，这是将request中的post和
	   user作为参数实例化一个CommentForm表单实例，其中request.POST是用户填写的或者给定的content_type，object_id，text，reply_comment_id
	   而request.user是原本表单类中所没有的，这里用了python的语言特性，用关键字参数的形式动态的为实例添加了属性'''
	# 从关键字参数中取得user并设成属性
	def __init__(self, *args, **kwargs):
		if 'user' in kwargs:
			self.user = kwargs.pop('user')
		super(CommentForm, self).__init__(*args, **kwargs)

	# 将被is_vaild方法调用.对数据进行验证和处理
	def clean(self):
		# 上面的方法使得实例有了user属性，这个user是从前端页面传来的，原本是渲染前端的数据。验证用户是否已登录
		if self.user.is_authenticated:
			# 如果已登录则给表单实例的cleaned_data添加一个user元素
			self.cleaned_data['user'] = self.user
		else:
			# 未登录，报错
			raise forms.ValidationError('尚未登录，登录后方可评论！')
		# 从表单实例的cleaned_data中拿到content_type和object_id
		content_type = self.cleaned_data['content_type']
		object_id = self.cleaned_data['object_id']
		try:
			# 获取评论对象
			# 拿到类，比如Blog
			model_class = ContentType.objects.get(model=content_type).model_class()
			# 拿到类的某个实例
			model_obj = model_class.objects.get(pk=object_id)
			# 将这个实例放到cleaned_data
			self.cleaned_data['content_object'] = model_obj
		except ObjectDoesNotExist:
			# 评论对象不存在，报错
			raise forms.ValidationError('评论对象不存在！')
		# 返回cleaned_data
		return self.cleaned_data

	# 将被is_vaild方法调用.对数据进行验证和处理
	def clean_reply_comment_id(self):
		# 从表单类实例的cleaned_data中取得reply_comment_id
		reply_comment_id = self.cleaned_data['reply_comment_id']
		# 错误
		if reply_comment_id < 0:
			raise forms.ValidationError('回复出错！')
		# reply_comment_id表示被回复的评论或回复的id，为0表示这是进行评论
		elif reply_comment_id == 0:
			# 评论没有上级
			self.cleaned_data['parent'] = None
		# eply_comment_id为comment实例的主键值（大于零），表示这是进行回复，如果被回复对像存在
		elif Comment.objects.filter(pk=reply_comment_id).exists():
			#将被回复对像作为当前回复的上级
			self.cleaned_data['parent'] = Comment.objects.get(pk=reply_comment_id)
		else:
			# 错误
			raise forms.ValidationError('回复出错！')
		# 返回cleaned_data
		return self.cleaned_data

		