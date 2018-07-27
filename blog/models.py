from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from ckeditor_uploader.fields import RichTextUploadingField
from reading_statistics.models import ReadNumExpandMethod,ReadDetail

# 博客类型模型，继承models.Model
class BlogType(models.Model):
    # 博客类型名称。字符串类型，最大长度为15
    type_name = models.CharField(max_length=15)

    # __str__ 方法自定义类，用print()函数打印该类的实例时，输出该方法返回的内容，这里是类型名称
    def __str__(self):
        return self.type_name

'''
博客模型，继承models.Model(django里的每个数据模型都要继承)，ReadNumExpandMethod是在reading_statistics这个app中定义的扩展类
class ReadNumExpandMethod():
    def get_read_num(self):
        try:
            ct = ContentType.objects.get_for_model(self)
            blog_read_num = ReadNum.objects.get(content_type=ct, object_id=self.pk)
            return blog_read_num.read_num
        except exceptions.ObjectDoesNotExist:
            return 0
继承该类后Blog模型就有了get_read_num方法，该方法返回某个博客对象的阅读数
'''
class Blog(models.Model, ReadNumExpandMethod):
    # 博客标题。字符串类型，最大长度60
    title = models.CharField(max_length=60)
    # 博客正文。使用类ckeditor提供的富文本域：RichTextUploadingField，这与RichTextField不同的是，它提供了上传图片的功能。从ckeditor_uploader.fields导入
    content = RichTextUploadingField()
    # 创建时间
    create_time = models.DateTimeField(auto_now_add=True)
    # 上次更新的时间
    last_updated_time = models.DateTimeField(auto_now=True)
    # 作者。外键关联django自带的用户模型，on_delete=models.CASCADE 表示使用级联删除
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 博客分类。外键关联博客类型模型，on_delete=models.CASCADE 表示使用级联删除
    blog_type = models.ForeignKey(BlogType, on_delete=models.CASCADE)
    # GenericRelation(ReadDetail)关联ReadDetail模型。效果是：对于一个博客对象，它的read_details属性将获取到这个博客对象所对应的所有ReadDetail实例，即所有的每日阅读计数对象
    read_details = GenericRelation(ReadDetail)

    # 获取博客URL
    def get_url(self):
        return reverse('blog:blog_detail', kwargs={'blog_pk':self.pk})

    # 获取博客作者邮箱
    def get_email(self):
        return self.author.email
    
     # __str__ 方法自定义类，用print()函数打印该类的实例时，输出该方法返回的内容，这里是类型名称
    def __str__(self):
        return '<Blog: %s>' % (self.title,)

    # 结果集按默认时间顺序的倒序排列。即新的在前，旧的在后
    class Meta:
        ordering = ['-create_time']


