from django.contrib import admin
from .models import ReadNum, ReadDetail

class ReadNumAdmin(admin.ModelAdmin):
    list_display = ('read_num', 'content_object')

class ReadDetailAdmin(admin.ModelAdmin):
    list_display = ('date', 'read_num', 'content_object')

admin.site.register(ReadNum, ReadNumAdmin)
admin.site.register(ReadDetail, ReadDetailAdmin)
