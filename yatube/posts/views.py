from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Post, Group, Follow, User
from .forms import PostForm, CommentForm
from .utils import my_paginator


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    page_obj = my_paginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date')
    page_obj = my_paginator(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.all().filter(author__exact=author)
    page_obj = my_paginator(request, post_list)
    following = (request.user.is_authenticated and request.user != author and
                 Follow.objects.filter(author=author, user=request.user))
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'author': author,
        'form': form,
        'comments': comments,
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    context = {
        'form': form,
    }
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', request.user.username)
    return render(request, 'posts/create_post.html', context)


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    profile = User.objects.get(username=request.user.username)
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user,
                                          author=profile).exists()
    else:
        following = False
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = my_paginator(request, post_list)
    context = {'page_obj': page_obj, }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(author=author, user=user)
    return redirect('posts:profile', username=author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if Follow.objects.filter(author=author, user=user, ).exists() and\
            author != user:
        get_object_or_404(Follow, author=author, user=user).delete()
    return redirect('posts:profile', username=author)
