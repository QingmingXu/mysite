from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist 
from django.http import JsonResponse
from .models import LikeCount, LikeRecord

def like_change(request):
	user = request.user
	if not user.is_authenticated:
		data = {}
		data['status'] = 'ERROR'
		data['message'] = '登录后才能点赞～'
		return JsonResponse(data)

	content_type = request.GET.get('content_type')
	object_id = request.GET.get('object_id')

	try:
		content_type = ContentType.objects.get(model=content_type)
		model_class = content_type.model_class()
		content_object = model_class.objects.get(pk=object_id)
	except ObjectDoesNotExist:
		data = {}
		data['status'] = 'ERROR'
		data['message'] = '对象不存在'
		return JsonResponse(data)

	# 用户页面的点赞处于未激活状态
	if request.GET.get('can_like') == 'true':
		# 先检验用户是否已经有相应的点赞记录。点赞处于未激活状态，不代表数据库里没有该用户对该点赞对像的点赞记录
		like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id, user=user)
		# created为true,数据库里没有相应的点赞记录
		if created:
		# 进行点赞
			like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
			like_count.liked_num += 1
			like_count.save()
			like_record.save()
			data ={}
			data['status'] = 'SUCCESS'
			data['liked_num'] =like_count.liked_num
			return JsonResponse(data)
		# 用户对该点赞对象的点赞记录已存在
		else:
			data = {}
			data['status'] = 'ERROR'
			data['message'] = '不能重复点赞～'
			return JsonResponse(data)
	# 用户页面的点赞处于激活状态
	else:
		# 如果有相应的用户点赞记录
		if LikeRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists():
			# 取消点赞
			like_record = LikeRecord.objects.get(content_type=content_type, object_id=object_id, user=user)
			like_record.delete()
			like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
			if not created:
				like_count.liked_num -= 1
				like_count.save()
				data = {}
				data['status'] = 'SUCCESS'
				data['liked_num'] =like_count.liked_num
				return JsonResponse(data)
			# 相应的点赞统计记录不存在
			else:
				data = {}
				data['status'] = 'ERROR'
				data['message'] = '数据错误'
				return JsonResponse(data)
		# 没有相应的用户点赞记录
		else:
			data = {}
			data['status'] = 'ERROR'
			data['message'] = '你还没有点赞～'
			return JsonResponse(data)


	

