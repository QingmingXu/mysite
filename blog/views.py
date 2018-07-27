from django.shortcuts import get_object_or_404, render
from .models import Blog, BlogType
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from reading_statistics.models import ReadNum, ReadDetail
from django.db.models import F
from django.utils import timezone
from comment.models import Comment
from comment.forms import CommentForm
from user.forms import LoginForm

# 一个公共的函数，该函数用于获取以下几个视图函数都需要的数据
def get_blog_common_data(request, blogs_all_list):
    # 从django.core.paginator导入分页器Paginator,并在此实例化。第一个参数是要分页的对象（一个结果集）,第二个参数是要分的页数。
    paginator = Paginator(blogs_all_list, 5)
    # 在前端页面中，点击上一页下一页或者具体的页面按钮都会触发一个链接。这个链接的最后一个部分是页面参数（?page=一个页码数字）。
    # 由于这个参数在url里，所以可以从request的get请求中得到它。使用request.GET.get('page', 1)，第一个参数是要获取的url参数，第二个参数是一个默认值（即默认的页码是第一页）。
    page_num = request.GET.get('page', 1)
    # 获取页面对象。（当前页面）
    page_of_blogs = paginator.get_page(page_num)
    # 当前页面的页码。
    current_page_num = page_of_blogs.number
    # 页码范围，list(range(max(current_page_num-2, 1), current_page_num))是当前页面的前两页，list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))是当前页以及后两页
    page_range = list(range(max(current_page_num-2, 1), current_page_num)) + list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))
    # 制作理想的页面范围
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 获取所有博客对象的创建日期对象，精确到月，倒序。
    blog_dates = Blog.objects.dates('create_time', 'month', order="DESC")
    # 创建一个字典。这个字典的key是精确到月的日期，value是博客数。（某月的博客数，用于日期归档）
    blog_dict_with_date = {} 
    # 遍历日期对象结果集中的日期对象。
    for blog_date in blog_dates:
        # 用遍历的日期来查找对应的所有的博客对象，并计数。
        blog_count = Blog.objects.filter(create_time__year=blog_date.year, create_time__month=blog_date.month).count()
        # 保存到字典中
        blog_dict_with_date[blog_date] = blog_count

    # 上下文，用于渲染模版页面
    context = {}
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_types'] = BlogType.objects.annotate(blog_count_with_type=Count('blog')) 
    context['blog_dates'] = blog_dict_with_date

    return context
 
 # 处理用户请求博客列表页面的视图函数  
def blog_list(request):
    # 获取所有的博客对象
    blogs_all_list =Blog.objects.all()

    # 使用公共函数获取通用的上下文
    context = get_blog_common_data(request, blogs_all_list)
    context['blogs'] = Blog.objects.all()

    # 转到结果页面
    return render(request, 'blog/blog_list.html', context)

# 处理用户请求具体博客的视图函数
def blog_detail(request, blog_pk):
    # 获取用户请求的具体的博客对象
    blog = get_object_or_404(Blog, pk=blog_pk)
    # 获取ContentType表示博客模型的实例
    ct = ContentType.objects.get_for_model(blog)
    # 获取cookie，这个cookie用来标记这篇博客有没有被该用户读过，如果没有被读过，就对阅读进行计数
    if not request.COOKIES.get('blog_%s_read' % (blog_pk,)):
        # 该博客对象所对应的阅读统计对象存在（已创建）
        if ReadNum.objects.filter(content_type=ct, object_id=blog_pk).count():
            # 获取该阅读统计对象
            readnum = ReadNum.objects.get(content_type=ct, object_id=blog_pk)
            # 使用F()函数进行计数，即阅读数加一
            readnum.read_num = F('read_num') + 1
            # 保存
            readnum.save()
        # 如果该博客对象所对应的阅读统计对象不存在（未创建）
        else:
            # 创建对应的阅读统计对象
            readnum = ReadNum(content_type=ct, object_id=blog_pk)
            # 计数，即阅读数加一
            readnum.read_num += 1
            # 保存
            readnum.save()

        # 获取当前时间，并转化为date类型
        date = timezone.now().date()
        # 如果该博客对象所对应的当日阅读统计对象存在（已创建）
        if ReadDetail.objects.filter(content_type=ct, object_id=blog_pk, date=date).count():
            # 获取该当日阅读统计对象
            readDetail = ReadDetail.objects.get(content_type=ct, object_id=blog_pk, date=date)
            # 使用F()函数进行计数，即当日阅读数加一
            readDetail.read_num = F('read_num') + 1
            # 保存
            readDetail.save()
        # 如果该博客对象对应的当日阅读统计对象不存在（未创建）
        else:
            # 创建该当日阅读统计对象
            readDetail = ReadDetail(content_type=ct, object_id=blog_pk, date=date)
            # 计数，即阅读数加一
            readDetail.read_num += 1
            # 保存
            readDetail.save()
    
    # 上下文，用于渲染模版页面
    context = {}
    # 上一篇博客
    context['previous_blog'] = Blog.objects.filter(create_time__gt=blog.create_time).last()
    # 下一篇博客
    context['next_blog'] = Blog.objects.filter(create_time__lt=blog.create_time).first()
    # 该博客
    context['blog'] = blog
    # 登录表单
    context['login_form'] = LoginForm()

    # 构造响应
    response = render(request, 'blog/blog_detail.html', context)
    # 设置cookie给客户端
    response.set_cookie('blog_%s_read' % (blog_pk,), 'true')
    # 返回响应
    return response

# 处理用户请求某个类型的博客列表页面的视图函数
def blog_with_type(request, blog_type_pk):
    # 获取用户请求的博客类型
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    # 根据用户所请求的博客类型来获取对应的所有博客
    blogs_all_list =Blog.objects.filter(blog_type=blog_type)

    # 使用公共函数获取通用的上下文
    context = get_blog_common_data(request, blogs_all_list)
    # 博客类型上下文
    context['blog_type'] = blog_type
    # 类型为用户请求的类型的博客上下文
    context['blogs'] = Blog.objects.filter(blog_type=blog_type)

    # 转到结果页面
    return render(request, 'blog/blog_type.html', context)

# 处理用户请求某个日期的博客列表页面的视图函数（精确到某年某月）
def blog_with_date(request, year, month):
    # 获取用户所请求的特定年月的所有博客对象
    blogs_all_list = Blog.objects.filter(create_time__year=year, create_time__month=month)

    # 使用公共函数获取通用的上下文
    context = get_blog_common_data(request, blogs_all_list)
    # 标题上下文，用于日期归档博客列表页面中的面板的标题
    context['blog_date_title'] = '%s年%s月' %(year, month)

    # 转到结果页面
    return render(request, 'blog/blog_date.html', context)





