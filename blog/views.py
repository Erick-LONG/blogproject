from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from .models import Post,Category
import markdown
from comments.forms import CommentForm
from django.views.generic import ListView,DetailView

class IndexView(ListView):
	model = Post
	template_name = 'blog/index.html'
	context_object_name = 'post_list'

# 分类页面
class CategoryView(IndexView):
	# 重写get_queryset方法，根据分类返回的ID，筛选文章
	# 命名组参数保存在kwargs中，非命名组参数保存在args中
	def get_queryset(self):
		cate = get_object_or_404(Category,pk = self.kwargs.get('pk'))
		return super(CategoryView,self).get_queryset().filter(category=cate)

#按月归档函数
class ArchivesView(IndexView):
	def get_queryset(self):
		year = self.kwargs.year
		month = self.kwargs.month
		return super(ArchivesView,self).get_queryset().filter(
			created_time__year=year,
			created_time__month=month,)


class PostDetailView(DetailView):
	model = Post
	template_name = 'blog/detail.html'
	context_object_name = 'post'

	# 重写get方法，目的为了文章浏览量+1
	def get(self, request, *args, **kwargs):
		response = super(PostDetailView,self).get(request, *args, **kwargs)
		self.object.increase_views()
		return response

	def get_object(self, queryset=None):
		# 重写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
		post = super(PostDetailView,self).get_object(queryset=None)
		# 将文章转换成markdown格式
		post.body = markdown.markdown (post.body, extensions=[
			'markdown.extensions.extra',
			'markdown.extensions.codehilite',
			'markdown.extensions.toc', ])
		return post

	def get_context_data(self, **kwargs):
		# 重写目的是把评论表单、post 下的评论列表传递给模板
		context = super(PostDetailView,self).get_context_data(**kwargs)
		form = CommentForm ()
		comment_list = self.object.comment_set.all ()
		context.update({
			'form': form,
			'comment_list': comment_list,
		})
		return context


