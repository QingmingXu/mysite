from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import Comment
from ..forms import CommentForm

# django自定义标签，在相应的应用里创建templatetags包，把方法注册后，这些方法将成为标签

register = template.Library()

@register.simple_tag()
def get_comment_count(obj):
	content_type = ContentType.objects.get_for_model(obj)
	return Comment.objects.filter(content_type=content_type, object_id=obj.pk, parent=None).count()

@register.simple_tag()
def get_comment_form(obj):
	content_type = ContentType.objects.get_for_model(obj)
	form = CommentForm(initial={'content_type':content_type.model, 'object_id':obj.pk, 'reply_comment_id': 0})
	return form

@register.simple_tag()
def get_comments(obj):
	content_type = ContentType.objects.get_for_model(obj)
	return Comment.objects.filter(content_type=content_type, object_id=obj.id, parent=None).order_by('-comment_time')
