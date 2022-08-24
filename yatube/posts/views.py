from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from posts.forms import CommentForm, PostForm

from .models import Follow, Group, Post, User

NUMBERS_OF_LIMIT = 10


def paginator(request, post_list):
    paginator = Paginator(post_list, NUMBERS_OF_LIMIT)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


@cache_page(20, key_prefix="index_page")
def index(request):
    template = "posts/index.html"
    post_list = Post.objects.all()
    page_obj = paginator(request, post_list)
    context = {
        "page_obj": page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = "posts/group_list.html"
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator(request, post_list)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = "posts/profile.html"
    author = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False
    post_list = author.posts.all()
    count = post_list.count()
    page_obj = paginator(request, post_list)
    context = {
        "author": author,
        "page_obj": page_obj,
        "count": count,
        "following": following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = "posts/post_detail.html"
    post = get_object_or_404(Post, id=post_id)
    count = post.author.posts.count()
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        "post": post,
        "count": count,
        "comments": comments,
        "form": form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = "posts/create_post.html"
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(reverse("posts:profile", args=[post.author]))
    return render(request, template, {"form": form})


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, id=post_id)
    template = "posts/create_post.html"
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect(reverse("posts:post_detail", args=[post.id]))
    if request.user != post.author:
        return redirect(reverse("posts:post_detail", args=[post.id]))
    return render(
        request, template, {"form": form, "post": post, "is_edit": is_edit}
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    template = "posts/follow.html"
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(request, post_list)
    context = {
        "page_obj": page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (
        request.user != author
        and not Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    ):
        Follow.objects.create(user=request.user, author=author)
    return redirect(reverse("posts:profile", args=[username]))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user, author=author).exists():
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect(reverse("posts:profile", args=[username]))
