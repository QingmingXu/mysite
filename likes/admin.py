from django.contrib import admin
from .models import LikeCount,LikeRecord

class LikeCountAdmin(admin.ModelAdmin):
	list_display = ('id', 'content_object', 'liked_num')

class  LikeRecordAdmin(admin.ModelAdmin):
	list_display = ('id', 'content_object', 'user', 'liked_time')

admin.site.register(LikeCount, LikeCountAdmin)
admin.site.register(LikeRecord, LikeRecordAdmin)