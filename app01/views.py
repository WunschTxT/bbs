from django.shortcuts import render, HttpResponse, redirect, reverse
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db import transaction

from django.http import JsonResponse
from app01 import models

from django.contrib import auth
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO, StringIO

from bs4 import BeautifulSoup

from BBS import settings

import random
import json
import os


# Create your views here.

def error(request):
    return render(request, "error.html")


def register(request):
    reg = models.Register()
    if request.method == "POST":
        black = {}
        reg = models.Register(request.POST)
        if reg.is_valid():
            username = reg.cleaned_data.get("username")
            user_obj = models.User.objects.filter(username=username)
            if user_obj:
                black["code"] = 1001
                black["msg"] = "用户名已存在"
                black["error"] = {}
                return JsonResponse(black)
            password = reg.cleaned_data.get("password")
            avatar = request.FILES.get("avatar")
            Blog = models.Blog.objects.create(name=username, title=username, css='/', js='/')

            if avatar:
                user_obj = models.User.objects.create_user(username=username, password=password, blog_id=Blog.id,
                                                           avatar=avatar)
            else:
                user_obj = models.User.objects.create_user(username=username, password=password, blog_id=Blog.id)
            black["code"] = 1000
            black["url"] = '/login'

        else:
            black["code"] = 2000
            black["error"] = reg.errors
        return JsonResponse(black)
    return render(request, 'register.html', locals())


def login(request):
    if request.method == "POST":
        black = {}
        next = request.GET.get("next")
        username = request.POST.get("username")
        password = request.POST.get("password")
        CheckCode = request.POST.get("check").lower()
        code = request.session.get("code").lower()

        if CheckCode != code:
            black["code"] = 1003
            black["msg"] = "验证码错误"
            return JsonResponse(black)

        user_obj = auth.authenticate(username=username, password=password)
        if not user_obj:
            black["code"] = 1002
            black["msg"] = "用户名或密码错误"
            return JsonResponse(black)
        auth.login(request, user_obj)
        black["code"] = 1000
        if next:
            black["url"] = next
        else:
            black["url"] = '/home'
        return JsonResponse(black)

    return render(request, "login.html", locals())


def getRandom():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def getCheck(request):
    img_obj = Image.new("RGB", (150, 40), getRandom())
    draw_obj = ImageDraw.Draw(img_obj)
    font_obj = ImageFont.truetype('static/fonts/111.ttf', 30)
    code = ""

    for i in range(5):
        check_upper = chr(random.randint(65, 90))
        check_lower = chr(random.randint(97, 122))
        check_int = str(random.randint(0, 9))

        temp = random.choice([check_upper, check_lower, check_int])
        draw_obj.text((i * 27 + 15, 2), temp, getRandom(), font_obj)
        code += temp

    request.session["code"] = code
    print(code)

    io_obj = BytesIO()
    img_obj.save(io_obj, "png")
    return HttpResponse(io_obj.getvalue())


# 修改密码
@login_required
def set_pwd(request):
    if request.method == "POST":
        old_pwd = request.POST.get("old_pwd")
        if not request.user.check_password(old_pwd):
            return JsonResponse({
                "code": 1001,
                "msg": "原密码错误"
            })
        new_pwd = request.POST.get("new_pwd")
        request.user.set_password(new_pwd)
        request.user.save()
        return JsonResponse({
            "code": 1000,
            "msg": "密码修改成功！请重新登录！"
        })

    return render(request, "set_pwd.html", locals())


@login_required(redirect_field_name="/login")
def logout(request):
    auth.logout(request)
    return redirect("/home")


def home(request):
    article_ls = models.Article.objects.all()

    return render(request, "home.html", locals())


# 个人博客视图函数
def blog(request, username, **kwargs):
    # 博客对象
    blog_obj = models.Blog.objects.filter(name=username).first()
    if not blog_obj:
        return redirect("/error")
    # 文章对象
    article_ls = models.Article.objects.filter(blog=blog_obj)
    # 分类对象
    # classify_ls = models.Classify.objects.filter(blog=blog_obj).annotate(count=Count("article__pk")).values_list("pk","name", "count")
    # # 标签对象
    # # tag_ls = models.Tag.objects.filter(blog=blog_obj).annotate(count=Count("article__pk")).values_list("pk","name","count")
    # tag_ls = models.Article.objects.filter(blog=blog_obj).values("tag").annotate(count=Count("tag")).order_by("tag__pk").values_list("tag__pk", "tag__name", "count")
    # # 随笔档案
    # archives_ls = models.Article.objects.filter(blog=blog_obj).annotate(month=TruncMonth("create_time")).values("month").annotate(count=Count("month")).values_list("month","count")
    if kwargs:
        if kwargs.get("type") == "classify":
            id = kwargs.get("pk")
            article_ls = models.Article.objects.filter(classify__pk=id)
        elif kwargs.get("type") == "tag":
            id = kwargs.get("pk")
            # article_list = article_ls.filter(tag__id=id)
            article_ls = article_ls.filter(blog=blog_obj).filter(tag__pk=id)
            if not article_ls:
                return redirect("/error")
        elif kwargs.get("type") == "month":
            year, month = kwargs.get("pk").split("-")
            article_ls = article_ls.filter(create_time__year=year, create_time__month=month)
            if not article_ls:
                return redirect("/error")

        elif kwargs.get("type") == "p":
            id = kwargs.get("pk")
            article_obj = article_ls.filter(pk=id).first()
            comment_ls = models.Comment.objects.filter(article=article_obj)
            if not article_obj:
                return redirect("/error")
            return render(request, "aritcle_detail.html", locals())
        else:
            return redirect("/error")

    return render(request, 'blog.html', locals())


def is_up(request):
    if request.is_ajax():
        black = {"code": 1000, "msg": ""}
        if not request.user.is_authenticated:
            black["code"] = 1001  # 用户未登录
            black["msg"] = "请先<a href='/login'>登录</a>"
            return JsonResponse(black)
        article_id = request.POST.get("article_id")
        is_up = json.loads(request.POST.get("is_up"))
        # 判断用户是否是自己的文章
        articl_obj = models.Article.objects.filter(pk=article_id).first()
        if articl_obj.blog.user == request.user:
            black["code"] = 1002  # 正在评论自己文章
            if is_up:
                black["msg"] = "不能给自己点赞</a>"
            else:
                black["msg"] = "不能给自己点踩</a>"
            return JsonResponse(black)
        up_down_obj = models.Up_Down.objects.filter(user=request.user, article=articl_obj).first()
        if up_down_obj:
            black["code"] = 1003  # 已经点过赞
            if up_down_obj.is_up:
                black["msg"] = "你已经点过赞</a>"
            else:
                black["msg"] = "你已经点过踩</a>"
            return JsonResponse(black)
        up_down_obj = models.Up_Down.objects.create(user=request.user, article=articl_obj, is_up=is_up)
        if is_up:
            black["msg"] = "点赞成功</a>"
            models.Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
        else:
            black["msg"] = "点踩成功</a>"
            models.Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)
        return JsonResponse(black)
    return redirect("/error")


def comment(request):
    black = {"code": 1000, "msg": "评论发布成功"}
    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    parent_id = request.POST.get("comment_id")

    with transaction.atomic():
        print('++++++++++++')
        comment_obj = models.Comment.objects.create(user=request.user, article_id=article_id, content=content,
                                                    parent_id=parent_id)
        print('**********')
        models.Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)
        print('-------------')
    return JsonResponse(black)


# 后台页面
@login_required
def black_home(request):
    article_list = models.Article.objects.filter(blog=request.user.blog)

    return render(request, "Backstage/home.html", locals())


# 添加随笔
@login_required
def add_article(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        classify_id = request.POST.get("classify")
        tag_list = request.POST.getlist("tag")
        # if not classify_id:
        #     classify = models.Classify.objects.create(name='默认', blog_id=request.user.blog)
        # if not tag_list:
        #     tag = models.Tag.objects.create(name='默认', blog_id=request.user.blog)
        soup = BeautifulSoup(content, "html.parser")
        tags = soup.find_all()
        for i in tags:
            if i.name is "script":
                i.decompose()

        abstract = soup.text[:150]
        print('++++++++++++')
        article_obj = models.Article.objects.create(title=title, abstract=abstract, content=content,
                                                    blog=request.user.blog, classify_id=classify_id)
        print('------------------')
        article_tag_ls = [models.Article_Tag(article=article_obj, tag_id=i) for i in tag_list]
        print('*****************')
        models.Article_Tag.objects.bulk_create(article_tag_ls)
        return redirect("/black_home")

    classify_list = models.Classify.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)

    return render(request, "Backstage/add_article.html", locals())


# 上传文件
@login_required
def upload(request):
    if request.method == "POST":
        img_obj = request.FILES.get("imgFile")
        img_path = os.path.join(settings.BASE_DIR, "media", "upload_file", img_obj.name)
        with open(img_path, 'wb') as f:
            for line in img_obj:
                f.write(line)

        return JsonResponse({

            "error": 0,
            "url": "/media/upload_file/" + img_obj.name

        })

    return HttpResponse("ok")


# 修改头像
@login_required
def edit_avatar(request):
    if request.method == "POST":
        avatar_obj = request.FILES.get("avatar")
        user_obj = request.user
        user_obj.avatar = avatar_obj
        user_obj.save()

        return HttpResponse("头像修改成功！")

    return render(request, "Backstage/edit_avatar.html", locals())


# 支付成功
@csrf_exempt
def pay_success(request):
    if request.method == "POST":
        print(request.POST)

        return HttpResponse("success")

    return HttpResponse("error")
