import datetime
from django.utils import timezone
from .models import ReadDetail
from django.db.models import Sum

def get_seven_days_read_data(content_type):
	today = timezone.now().date()
	dates = []
	read_nums = []
	for i in range(7, 0 , -1):
		date = today - datetime.timedelta(days=i)
		dates.append(date.strftime('%m/%d'))
		read_details = ReadDetail.objects.filter(content_type=content_type, date=date)
		result = read_details.aggregate(read_num_sum=Sum('read_num'))
		read_nums.append(result['read_num_sum'] or 0)
	return dates, read_nums

def get_today_hot_read(content_type):
	today = timezone.now().date()
	read_details = ReadDetail.objects.filter(content_type=content_type, date=today).order_by('-read_num')
	return read_details[:5]

def get_yesterday_hot_read(content_type):
	today = timezone.now().date()
	yesterday = today - datetime.timedelta(days=1)
	read_details = ReadDetail.objects.filter(content_type=content_type, date=yesterday).order_by('-read_num') 
	return read_details[:5]


