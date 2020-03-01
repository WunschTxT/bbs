
from django.template import Library
from django.db.models import Count
from django.db.models.functions import TruncMonth

from app01 import models

register = Library()

@register.inclusion_tag("blog_left.html")
def index(username):
    blog_obj = models.Blog.objects.filter(name = username).first()
    # 分类对象
    classify_ls = models.Classify.objects.filter(blog=blog_obj).annotate(count=Count("article__pk")).values_list("pk","name", "count")
    # 标签对象
    # tag_ls = models.Tag.objects.filter(blog=blog_obj).annotate(count=Count("article__pk")).values_list("pk","name","count")
    tag_ls = models.Article.objects.filter(blog=blog_obj).values("tag").annotate(count=Count("tag")).order_by("tag__pk").values_list("tag__pk", "tag__name", "count")
    # 随笔档案
    archives_ls = models.Article.objects.filter(blog=blog_obj).annotate(month=TruncMonth("create_time")).values("month").annotate(count=Count("month")).values_list("month","count")

    return locals()

