from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import BlogPost


def index(request):
    posts = BlogPost.objects.all()
    return render(request, 'blog/index.html', dict(
        posts=posts,
    ))
