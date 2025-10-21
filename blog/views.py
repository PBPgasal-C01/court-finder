from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django import forms
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse

from .models import BlogPost


def post_list(request):
	q = request.GET.get('q', '').strip()
	posts = BlogPost.objects.all()

	# hanya cari di title
	if q:
		posts = posts.filter(title__icontains=q)

	is_admin_flag = is_admin(request.user)

	# jika AJAX (partial)
	if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('partial'):
		return render(request, 'partials/cards.html', {
			'posts': posts,
			'is_admin': is_admin_flag
		})

	return render(request, 'list.html', {
		'posts': posts,
		'q': q,
		'is_admin': is_admin_flag
	})


def post_detail(request, pk: int):
	post = get_object_or_404(BlogPost, pk=pk)
	is_admin_flag = is_admin(request.user)
	others = BlogPost.objects.exclude(pk=pk)[:5]
	return render(request, 'detail.html', {'post': post, 'is_admin': is_admin_flag, 'others': others})


class BlogPostForm(forms.ModelForm):
	class Meta:
		model = BlogPost
		fields = ['author', 'title', 'content', 'thumbnail_url']
		widgets = {
			'author': forms.TextInput(attrs={'placeholder': 'Insert author name...', 'class': 'mt-2 w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#79A6B9]'}),
			'title': forms.TextInput(attrs={'placeholder': 'Insert your blog title...', 'class': 'mt-2 w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#79A6B9]'}),
			'content': forms.Textarea(attrs={'rows': 10, 'placeholder': 'Type your blog content here...', 'class': 'mt-2 w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#79A6B9]'}),
			'thumbnail_url': forms.URLInput(attrs={'placeholder': 'Insert thumbnail link here...', 'class': 'mt-2 w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#79A6B9]'}),
		}


def is_admin(user):
    return getattr(user, 'is_admin', lambda: False)() if user.is_authenticated else False


@login_required
@user_passes_test(is_admin)
def post_create(request):
	if request.method == 'POST':
		form = BlogPostForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			if not post.author:
				# fallback to current admin identity
				post.author = getattr(request.user, 'username', '') or getattr(request.user, 'email', '') or 'Admin'
			post.save()
			messages.success(request, 'Post created.')
			if request.headers.get('x-requested-with') == 'XMLHttpRequest':
				return JsonResponse({'ok': True, 'redirect': post.get_absolute_url()})
			return redirect(post.get_absolute_url())
		else:
			# surface errors so user sees what's wrong
			messages.error(request, f"Please fix the errors below: {form.errors.as_text()}")
			if request.headers.get('x-requested-with') == 'XMLHttpRequest':
				return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
	else:
		form = BlogPostForm(initial={"author": "Admin"})
	return render(request, 'form.html', {'form': form, 'action': 'Create'})


@login_required
@user_passes_test(is_admin)
def post_update(request, pk: int):
	post = get_object_or_404(BlogPost, pk=pk)
	if request.method == 'POST':
		form = BlogPostForm(request.POST, instance=post)
		if form.is_valid():
			post = form.save(commit=False)
			if not post.author:
				post.author = getattr(request.user, 'username', '') or getattr(request.user, 'email', '') or 'Admin'
			post.save()
			messages.success(request, 'Post updated.')
			if request.headers.get('x-requested-with') == 'XMLHttpRequest':
				return JsonResponse({'ok': True, 'redirect': post.get_absolute_url()})
			return redirect(post.get_absolute_url())
		else:
			messages.error(request, f"Please fix the errors below: {form.errors.as_text()}")
			if request.headers.get('x-requested-with') == 'XMLHttpRequest':
				return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
	else:
		form = BlogPostForm(instance=post)
	return render(request, 'form.html', {'form': form, 'action': 'Update'})


@login_required
@user_passes_test(is_admin)
def post_delete(request, pk: int):
	post = get_object_or_404(BlogPost, pk=pk)
	if request.method == 'POST':
		post.delete()
		messages.success(request, 'Post deleted.')
		if request.headers.get('x-requested-with') == 'XMLHttpRequest':
			return JsonResponse({'ok': True, 'redirect': reverse('blog:list')})
		return redirect('blog:list')
	return render(request, 'confirm_delete.html', {'post': post})
