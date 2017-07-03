from django.conf.urls import url

from . import views

app_name = 'blog' #视图函数命名空间,防止冲突
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^post/(?P<pk>[0-9]+)/$', views.detail, name='detail'),
]