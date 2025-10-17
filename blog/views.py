from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django import forms

from .models import BlogPost


def post_list(request):
	posts = BlogPost.objects.all()
	return render(request, 'blog/list.html', {'posts': posts})


def post_detail(request, pk: int):
	post = get_object_or_404(BlogPost, pk=pk)
	return render(request, 'blog/detail.html', {'post': post})


class BlogPostForm(forms.ModelForm):
	class Meta:
		model = BlogPost
		fields = ['author', 'title', 'content']


def is_admin(user):
	return getattr(user, 'is_admin', lambda: False)() if user.is_authenticated else False


@login_required
@user_passes_test(is_admin)
def post_create(request):
	if request.method == 'POST':
		form = BlogPostForm(request.POST)
		if form.is_valid():
			post = form.save()
			messages.success(request, 'Post created.')
			return redirect(post.get_absolute_url())
	else:
		form = BlogPostForm(initial={"author": "Admin"})
	return render(request, 'blog/form.html', {'form': form, 'action': 'Create'})


@login_required
@user_passes_test(is_admin)
def post_update(request, pk: int):
	post = get_object_or_404(BlogPost, pk=pk)
	if request.method == 'POST':
		form = BlogPostForm(request.POST, instance=post)
		if form.is_valid():
			form.save()
			messages.success(request, 'Post updated.')
			return redirect(post.get_absolute_url())
	else:
		form = BlogPostForm(instance=post)
	return render(request, 'blog/form.html', {'form': form, 'action': 'Update'})


@login_required
@user_passes_test(is_admin)
def post_delete(request, pk: int):
	post = get_object_or_404(BlogPost, pk=pk)
	if request.method == 'POST':
		post.delete()
		messages.success(request, 'Post deleted.')
		return redirect('blog:list')
	return render(request, 'blog/confirm_delete.html', {'post': post})
