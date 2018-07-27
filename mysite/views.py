import datetime
from django.shortcuts import render,redirect
from django.urls import reverse
from reading_statistics.utils import get_seven_days_read_data, get_today_hot_read, get_yesterday_hot_read
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.core.cache import cache
from blog.models import Blog
from django.utils import timezone


def get_seven_days_hot_blogs():
	today = timezone.now().date()
	date = today - datetime.timedelta(days=7)
	blogs = Blog.objects.filter(read_details__date__lt=today, read_details__date__gte=date).values('id', 'title').annotate(read_num_sum=Sum('read_details__read_num')).order_by('-read_num_sum')
	return blogs[:5]

def home(request):
	content_type = ContentType.objects.get_for_model(Blog)
	dates, read_nums = get_seven_days_read_data(content_type)
	#today_hot_read = get_today_hot_read(content_type)
	#yesterday_hot_read = get_yesterday_hot_read(content_type)

	seven_days_hot_blogs = cache.get('seven_days_hot_blogs')
	if seven_days_hot_blogs is None:
		seven_days_hot_blogs = get_seven_days_hot_blogs()
		cache.set('seven_days_hot_blogs', seven_days_hot_blogs, 3600)
		print('clac seven_days_hot_blogs')
	else:
		print('use cache')

	today_hot_read = cache.get('today_hot_read')
	if today_hot_read is None:
		today_hot_read = get_today_hot_read(content_type)
		cache.set('today_hot_read', today_hot_read, 3600)
		print('clac today_hot_read')
	else:
		print('use cache')

	yesterday_hot_read = cache.get('yesterday_hot_read')
	if yesterday_hot_read is None:
		yesterday_hot_read = get_yesterday_hot_read(content_type)
		cache.set('yesterday_hot_read', yesterday_hot_read, 3600)
		print('clac yesterday_hot_read')
	else:
		print('use cache')

	context = {}
	context['dates'] = dates
	context['read_nums'] = read_nums
	context['today_hot_read'] = today_hot_read
	context['yesterday_hot_read'] = yesterday_hot_read
	context['seven_days_hot_blogs'] = seven_days_hot_blogs
	return render(request, 'home.html', context)
