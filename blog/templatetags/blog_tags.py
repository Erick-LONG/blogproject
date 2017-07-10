from ..models import Post,Category,Tag
from django import template
from django.db.models.aggregates import Count
register = template.Library()

@register.simple_tag
def get_recent_posts(num=5):
	return Post.objects.all()[:num]

@register.simple_tag
def archives(): # 按月归档
	return Post.objects.dates('created_time','month')

@register.simple_tag
def get_categories(): # 分类标签
	# annotate会返回数据库中全部 Category 的记录
	# Count 计算分类下的文章数，其接受的参数为需要计数的模型的名称
	return Category.objects.annotate(num_posts =Count('post')).filter(num_posts__gt = 0)

@register.simple_tag
def get_tags():
	return Tag.objects.annotate(num_posts =Count('post')).filter(num_posts__gt = 0)