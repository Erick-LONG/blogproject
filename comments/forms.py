from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment # 表明数据库
		fields = ['name','email','url','text'] # 表明要显示的表单字段