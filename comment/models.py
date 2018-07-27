import threading
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.mail import send_mail
from django.contrib.auth.models import User 

class SendMail(threading.Thread):
	def __init__(self, subject, text, email, fail_silently=False):
		self.subject = subject
		self.text = text
		self.email = email
		self.fail_silently = fail_silently
		threading.Thread.__init__(self)

	def run(self):
		send_mail(self.subject, '', settings.EMAIL_HOST_USER, [self.email], fail_silently=self.fail_silently, html_message=self.text)

# 评论与回复功能的模型设计，共用一个模型类，因为回复也可以看成一种评论。具体如何区分？外键区分！
class Comment(models.Model):
	# 使用ContentType，这个模型将相当通用，因为ContentType记录了整个项目中所有应用的模型，content_type确定类，object_id确定这个类的某个实例
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')

	# 评论或回复的内容
	text = models.TextField()
	# 评论或回复的时间
	comment_time = models.DateTimeField(auto_now_add=True)

	# 外键，指明Comment实例属于是哪个user的，即评论或回复是哪个用户的。
	user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
	# 外键，指明该Comment实例属于谁。说明一下，对于评论，该外键为空，对于一级回复，root外键是该回复所属的评论，对于次级或更低级的回复，root外键也是该回复所属的评论。这通过推理就可以得到。
	# 对于评论，comment.root就是该评论下的所有回复
	root = models.ForeignKey('self', related_name="root_comment", null=True, on_delete=models.CASCADE)
	# 外键，指明某个comment的上级
	parent = models.ForeignKey('self', related_name="parent_comment", null=True, on_delete=models.CASCADE)
	# 外键，指明回复谁
	reply_to = models.ForeignKey(User, related_name="replies", null=True, on_delete=models.CASCADE)

	def send_mail(self):
		if self.parent is None:
			# 评论博客
			subject = '有人评论了你的博客'
			email = self.content_object.get_email()
		else:
			# 回复评论(回复)
			subject = '有人回复了你'
			email = self.reply_to.email
		if email != '':
			text = '%s<a href="%s">%s</a>' %(self.text, self.content_object.get_url(), '点击查看')
			sendmail = SendMail(subject, text, email)
			sendmail.start()

	# 自定义类
	def __str__(self):
		return self.text

	#class Meta:
		#ordering = ['-comment_time']

