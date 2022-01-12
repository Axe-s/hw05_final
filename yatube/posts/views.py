from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def _page_obj(request, query_set):
    paginator = Paginator(query_set, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    posts = Post.objects.select_related('author', 'group').all()
    context = {
        'page_obj': _page_obj(request, posts),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_posts = group.posts.all()
    context = {
        'group': group,
        'page_obj': _page_obj(request, group_posts),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    total = author.posts.count()
    following = Follow.objects.filter(
        user__username=request.user, author=author
    )
    context = {
        'author': author,
        'total': total,
        'page_obj': _page_obj(request, posts),
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    total = post.author.posts.count()
    context = {
        'post': post,
        'total': total,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user)
        return render(
            request, 'posts/create_post.html', {'form': form, 'is_edit': False}
        )
    form = PostForm()
    return render(
        request, 'posts/create_post.html', {'form': form, 'is_edit': False}
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = PostForm(
            request.POST, instance=post, files=request.FILES or None
        )
        if form.is_valid():
            post = form.save(commit=False or None)
            post.save()
            return redirect('posts:post_detail', post_id)
        return render(
            request, 'posts/create_post.html', {'form': form, 'is_edit': True}
        )
    form = PostForm(instance=post)
    return render(
        request, 'posts/create_post.html', {'form': form, 'is_edit': True}
    )


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
    posts = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': _page_obj(request, posts),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author).exists()
    if author != request.user and follow is False:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author)
    if follow.exists():
        follow.delete()
    return redirect('posts:profile', username=username)
