"""BBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')

Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.static import serve
from app01 import views
from BBS import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^error$', views.error),
    url(r'^register$', views.register, name="register"),
    url(r'^login$', views.login, name="login"),
    url(r'^set_pwd', views.set_pwd, name="set_pwd"),
    url(r'^getCheck$', views.getCheck, name="getCheck"),
    url(r'^home$', views.home, name="home"),
    url(r'^logout$', views.logout, name="logout"),
    url(r'^is_up$', views.is_up, name="is_up"),
    url(r'^comment$', views.comment, name="comment"),
    url(r'^black_home$', views.black_home, name="black_home"),
    url(r'^add_article$', views.add_article, name="add_article"),
    url(r'^upload$', views.upload, name="upload"),
    url(r'^edit_avatar$', views.edit_avatar, name="edit_avatar"),
    url(r'^pay/success$', views.pay_success, name="pay_success"),
    url(r'^pay_success$', views.pay_success, name="pay_success"),

    # 上传文件夹
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    url(r'^media/(?P<path>.*)', serve, {"document_root": settings.MEDIA_ROOT}),
    # 个人博客
    url(r'^(?P<username>\w+)$', views.blog, name="blog"),
    url(r'^(?P<username>\w+)/(?P<type>classify|tag|month|p)/(?P<pk>.*)$', views.blog, name="blog"),
    url(r'^$', views.home, name="home"),
]
