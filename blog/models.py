from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User # Django 内置的应用，专门用于处理网站用户的注册、登录等流程，User 是 Django 为我们已经写好的用户模型。
import markdown
from django.utils.html import strip_tags

class Category(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Post(models.Model):

    title = models.CharField(max_length=70)
    body = models.TextField()
    created_time = models.DateTimeField()
    modified_time = models.DateTimeField()
    excerpt = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag, blank=True)
    author = models.ForeignKey(User)
    views = models.PositiveIntegerField(default=0) # 只允许正整数或0，不能为负数

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse ('blog:detail', kwargs={'pk': self.pk})

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views']) # 只更新views字段

    # 重写模型save方法，自动保存文章正文前45个字到摘要
    def save(self,*args,**kwargs):
        if not self.excerpt:
            md = markdown.Markdown(
                extensions=[
                    'markdown.extensions.extra',
                    'markdown.extensions.codehilite',
                ]
            )
            self.excerpt = strip_tags(md.convert(self.body)[:55])

        # 调用父类save方法，讲数据保存到数据库中
        super(Post,self).save(*args,**kwargs)

    class Meta:
        ordering = ['-created_time']