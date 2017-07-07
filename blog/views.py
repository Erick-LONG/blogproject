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
	# 指定 paginate_by 属性后开启分页功能，其值代表每一页包含多少篇文章
	paginate_by = 5

	def get_context_data(self, **kwargs):
		"""
		在视图函数中将模板变量传递给模板是通过给 render 函数的 context 参数传递一个字典实现的，
		例如 render(request, 'blog/index.html', context={'post_list': post_list})，
		这里传递了一个 {'post_list': post_list} 字典给模板。
		在类视图中，这个需要传递的模板变量字典是通过 get_context_data 获得的，
		所以我们复写该方法，以便我们能够自己再插入一些我们自定义的模板变量进去。
		"""
		# 首先获得父类生成的传递给模板的字典。
		context = super().get_context_data(**kwargs)

		# 父类生成的字典中已有 paginator、page_obj、is_paginated 这三个模板变量
		# 由于 context 是一个字典，所以调用 get 方法从中取出某个键对应的值。
		paginator = context.get('paginator')
		page = context.get('page_obj')
		is_paginated = context.get('is_paginated')

		pagination_data = self.pagination_data (paginator, page, is_paginated)

		context.update(pagination_data)

		return context

	def pagination_data(self,paginator, page, is_paginated):
		if not is_paginated:
			return {}

		# 当前页左边连续的页码号，初始值为空
		left = []

		# 当前页右边连续的页码号，初始值为空
		right = []

		# 标示第 1 页页码后是否需要显示省略号
		left_has_more = False

		# 标示最后一页页码前是否需要显示省略号
		right_has_more = False

		# 标示是否需要显示第 1 页的页码号。
		# 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
		# 其它情况下第一页的页码是始终需要显示的。
		# 初始值为 False
		first = False

		# 标示是否需要显示最后一页的页码号
		last = False

		# 获得用户当前请求的页码号
		page_number = page.number

		# 获得分页后的总页数
		total_pages = paginator.num_pages

		# 获得整个分页页码列表，比如分了四页，那么就是 [1, 2, 3, 4]
		page_range = paginator.page_range

		if page_number == 1:

			# 如果用户请求的是第一页的数据，那么当前页左边的不需要数据，因此 left=[]（已默认为空）。
			# 此时只要获取当前页右边的连续页码号
			right = page_range[page_number:page_number+2]

			# 如果最右边的页码号比最后一页的页码号减去 1 还要小，
			# 说明最右边的页码号和最后一页的页码号之间还有其它页码,因此需要显示省略号，通过 right_has_more 来指示
			if right[-1] < total_pages -1 :
				right_has_more = True

			if right[-1] < total_pages:
				last = True

		elif page_number == total_pages:
			left = page_range[(page_number - 3) if (page_number -3) > 0 else 0 : page_number -1]

			# 如果最左边的页码号比第 2 页页码号还大，
			# 说明最左边的页码号和第 1 页的页码号之间还有其它页码，因此需要显示省略号，通过 left_has_more 来指示。
			if left[0] > 2:
				left_has_more = True

			# 如果最左边的页码号比第 1 页的页码号大，说明当前页左边的连续页码号中不包含第一页的页码，
			# 所以需要显示第一页的页码号，通过 first 来指示
			if left[0] > 1:
				first = True

		else:
			# 用户请求的既不是最后一页，也不是第 1 页，则需要获取当前页左右两边的连续页码号，
			# 这里只获取了当前页码前后连续两个页码
			left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0 : page_number - 1]
			right = page_range[page_number:page_number + 2]

			# 是否需要显示最后一页和最后一页前的省略号
			# 如果最右边的页码号比最后一页的页码号减去 1 还要小，
			# 说明最右边的页码号和最后一页的页码号之间还有其它页码,因此需要显示省略号，通过 right_has_more 来指示
			if right[-1] < total_pages -1:
				right_has_more = True

			# 如果最左边的页码号比第 1 页的页码号大，说明当前页左边的连续页码号中不包含第一页的页码，
			# 所以需要显示第一页的页码号，通过 first 来指示
			if left[0] > 1 :
				first = True

		data = {
			'left':left,
			'right':right,
			'right_has_more':right_has_more,
			'left_has_more':left_has_more,
			'first':first,
			'last':last,
		}
		return data


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


