from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User 

# LikeCount模型用于记录被点赞对象（博客，评论，回复）的点赞总数
class LikeCount(models.Model):
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')
	# 点赞总数
	liked_num = models.IntegerField(default=0)

# 用户对某个点赞对象的点赞记录
class LikeRecord(models.Model):
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')
	# 外键关联用户
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	# 点赞日期时间
	liked_time = models.DateTimeField(auto_now_add=True)


