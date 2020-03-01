from django.db import models

from django import forms
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    phone = models.CharField(max_length=11, null=True , blank=True)
    addr = models.CharField(max_length=32, null=True, blank=True)
    avatar = models.FileField(upload_to="avatar", default="avatar/default.png")
    blog = models.OneToOneField(to="Blog", null=True)

    class Meta():
        verbose_name_plural = "用户表"


class Blog(models.Model):
    name = models.CharField(max_length=32)
    title = models.CharField(max_length=32)
    css = models.TextField()
    js = models.TextField()

    def __str__(self):
        return self.name

    class Meta():
        verbose_name_plural = "个人站点表"


class Tag(models.Model):
    name = models.CharField(max_length=32)
    blog = models.ForeignKey(to="Blog")

    def __str__(self):
        return self.name

    class Meta():
        verbose_name_plural = "标签表"


class Classify(models.Model):
    name = models.CharField(max_length=32)
    blog = models.ForeignKey(to="Blog")

    def __str__(self):
        return self.name + str(self.blog)

    class Meta():
        verbose_name_plural = "分类表"


class Article(models.Model):
    title = models.CharField(max_length=32)
    abstract = models.CharField(max_length=255)
    content = models.TextField()
    create_time = models.DateField(auto_now_add=True)

    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)

    blog = models.ForeignKey(to="Blog")
    tag = models.ManyToManyField(to="Tag", through="Article_Tag", through_fields=("article", "tag"))
    classify = models.ForeignKey(to="Classify")

    def __str__(self):
        return self.title

    class Meta():
        verbose_name_plural = "文章表"


class Article_Tag(models.Model):
    article = models.ForeignKey(to="Article")
    tag = models.ForeignKey(to="Tag")

    class Meta():
        verbose_name_plural = "文章-标签表"


class Up_Down(models.Model):
    user = models.ForeignKey(to="User")
    article = models.ForeignKey(to="Article")
    is_up = models.BooleanField()

    class Meta():
        verbose_name_plural = "点赞点踩表"


class Comment(models.Model):
    user = models.ForeignKey(to="User")
    article = models.ForeignKey(to="Article")
    content = models.CharField(max_length=255)
    parent = models.ForeignKey(to="self", null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta():
        verbose_name_plural = "评论表"


class Register(forms.Form):
    username = forms.CharField(
        min_length=4,
        max_length=8,
        label="用户名：",
        error_messages={
            "min_length": "用户名不能小于4个字符",
            "max_length": "用户名不能大于8个字符",
            "required": "用户名不能为空",
        },
        widget=forms.widgets.TextInput(attrs={
            "class": "form-control"
        })
    )

    password = forms.CharField(
        min_length=6,
        max_length=18,
        label="密码",
        error_messages={
            "min_length": "密码不能小于6个字符",
            "max_length": "密码不能大于18个字符",
            "required": "密码不能为空",
        },
        widget=forms.widgets.PasswordInput(attrs={
            "class": "form-control"
        })
    )

    re_password = forms.CharField(
        min_length=6,
        max_length=18,
        label="重复密码",
        error_messages={
            "min_length": "密码不能小于6个字符",
            "max_length": "密码不能大于18个字符",
            "required": "密码不能为空",
        },
        widget=forms.widgets.PasswordInput(attrs={
            "class": "form-control"
        })
    )

    def clean(self):
        username = self.data.get("username")
        password = self.data.get("password")
        repassword = self.data.get("re_password")

        if password in username:
            self.add_error("password", "用户名中不能包含密码")
        if password != repassword:
            self.add_error("re_password", "密码不一致")
        return self.data
