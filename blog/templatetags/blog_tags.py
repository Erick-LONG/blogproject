from ..models import Post,Category
from django import template

register = template.Library()

@register.simple_tag
def get_recent_posts(num=5):
	return Post.objects.all().order_by('-created_time')[:num]

@register.simple_tag
def archives(): # 按月归档
	return Post.objects.dates('created_time','month',order='DESC')

@register.simple_tag
def get_categories(): # 分类标签
	return Category.objects.all()