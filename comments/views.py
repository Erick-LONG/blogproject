from django.shortcuts import render,get_object_or_404,redirect
from blog.models import Post

from .models import Comment
from .forms import CommentForm

# Create your views here.

def post_comment(request,post_pk):
	post = get_object_or_404 (Post, pk=post_pk)
	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			#commit=False 的作用是仅仅利用表单的数据生成 Comment 模型类的实例，但还不保存评论数据到数据库。
			comment = form.save(commit=False)
			# 将评论和博文关联起来
			comment.post = post
			# 最终将评论数据保存在数据库
			comment.save()
			# 重定向到文章详情页，当redirect接受一个模型的实例时，会调用这个模型实例的get_absolute_url方法，然后返回对应的url
			return redirect (post)
		else:
			# post.comment_set.all()反向查找当前微博博文的评论
			comment_list= post.comment_set.all()
			context = {'post':post,'form':form,'comment_list':comment_list}
			return render(request,'blog/detail.html',context=context)

	return redirect(post)