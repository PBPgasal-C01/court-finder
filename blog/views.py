from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django import forms
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import BlogPost, Favorite


def post_list(request):
	q = request.GET.get('q', '').strip()
	show_favs = request.GET.get('favs') in ('1', 'true', 'True')
	posts = BlogPost.objects.all()

	# hanya cari di title
	if q:
		posts = posts.filter(title__icontains=q)

	# Favorite state for current user
	fav_post_ids = set()
	if request.user.is_authenticated:
		fav_post_ids = set(
			Favorite.objects.filter(user=request.user).values_list('post_id', flat=True)
		)

	if show_favs:
		# filter to favorites only
		posts = posts.filter(pk__in=fav_post_ids or [-1])

	is_admin_flag = is_admin(request.user)

	# jika AJAX (partial)
	if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('partial'):
		return render(request, 'partials/cards.html', {
			'posts': posts,
			'is_admin': is_admin_flag,
			'fav_post_ids': fav_post_ids,
			'show_favs': show_favs,
		})

	return render(request, 'list.html', {
		'posts': posts,
		'q': q,
		'is_admin': is_admin_flag,
		'show_favs': show_favs,
		'fav_post_ids': fav_post_ids,
	})


def _serialize_post(post: BlogPost):
	"""Helper to convert BlogPost instance to dict for JSON."""
	return {
		'id': post.pk,
		'title': post.title,
		'author': post.author,
		'content': post.content,
		'thumbnail_url': post.thumbnail_url,
		'created_at': post.created_at.isoformat() if getattr(post, 'created_at', None) else None,
		'reading_time': getattr(post, 'reading_time', None),
	}


def api_post_list(request):
	"""Return all blog posts as JSON list for Flutter app."""
	q = request.GET.get('q', '').strip()
	posts = BlogPost.objects.all()
	if q:
		posts = posts.filter(title__icontains=q)
	data = [_serialize_post(p) for p in posts.order_by('-created_at')]
	return JsonResponse(data, safe=False)


def post_detail(request, pk: int):
	post = get_object_or_404(BlogPost, pk=pk)

	if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
		return JsonResponse(_serialize_post(post))

	is_admin_flag = is_admin(request.user)
	# Base: exclude current post
	others_qs = BlogPost.objects.exclude(pk=pk)
	# exclude favourited post (if user authenticated)
	if request.user.is_authenticated:
		fav_ids = Favorite.objects.filter(user=request.user).values_list('post_id', flat=True)
		others_qs = others_qs.exclude(pk__in=fav_ids)
	others = others_qs[:5]
	is_favorited = False
	if request.user.is_authenticated:
		is_favorited = Favorite.objects.filter(user=request.user, post=post).exists()
	return render(request, 'detail.html', {
		'post': post,
		'is_admin': is_admin_flag,
		'others': others,
		'is_favorited': is_favorited,
	})


def api_post_detail(request, pk: int):
	"""Return single blog post as JSON for Flutter app."""
	post = get_object_or_404(BlogPost, pk=pk)
	return JsonResponse(_serialize_post(post))


@login_required
def toggle_favorite(request, pk: int):
	if request.method != 'POST':
		return JsonResponse({'ok': False, 'error': 'Invalid method'}, status=405)
	post = get_object_or_404(BlogPost, pk=pk)
	fav, created = Favorite.objects.get_or_create(user=request.user, post=post)
	if not created:
		fav.delete()
		return JsonResponse({'ok': True, 'favorited': False})
	else:
		return JsonResponse({'ok': True, 'favorited': True})


@csrf_exempt
def api_toggle_favorite(request, pk: int):
	"""JSON-only favorite toggle for Flutter app.
	Returns 401 JSON instead of HTML redirect when unauthenticated.
	"""
	if not request.user.is_authenticated:
		return JsonResponse({'ok': False, 'error': 'unauthenticated'}, status=401)
	if request.method != 'POST':
		return JsonResponse({'ok': False, 'error': 'Invalid method'}, status=405)
	post = get_object_or_404(BlogPost, pk=pk)
	fav, created = Favorite.objects.get_or_create(user=request.user, post=post)
	if not created:
		fav.delete()
		return JsonResponse({'ok': True, 'favorited': False})
	else:
		return JsonResponse({'ok': True, 'favorited': True})


@csrf_exempt
def api_get_favorites(request):
	"""Return list of user's favorite post IDs for Flutter app.
	Returns 401 JSON instead of redirect when unauthenticated.
	"""
	if not request.user.is_authenticated:
		return JsonResponse({'ok': False, 'error': 'unauthenticated', 'favorite_ids': []}, status=401)
	fav_ids = list(Favorite.objects.filter(user=request.user).values_list('post_id', flat=True))
	return JsonResponse({'ok': True, 'favorite_ids': fav_ids})

@csrf_exempt
def api_get_favorites_posts(request):
	"""Return full serialized favorite posts for the current user."""
	if not request.user.is_authenticated:
		return JsonResponse({'ok': False, 'error': 'unauthenticated', 'posts': []}, status=401)
	fav_post_qs = BlogPost.objects.filter(
		pk__in=Favorite.objects.filter(user=request.user).values_list('post_id', flat=True)
	).order_by('-created_at')
	data = [_serialize_post(p) for p in fav_post_qs]
	return JsonResponse({'ok': True, 'posts': data})


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
			# messages.success(request, 'Post created.')
			if request.headers.get('x-requested-with') == 'XMLHttpRequest':
				return JsonResponse({'ok': True, 'redirect': post.get_absolute_url()})
			return redirect(post.get_absolute_url())
		else:
			# surface errors so user sees whats wrong
			messages.error(request, f"Please fix the errors below: {form.errors.as_text()}")
			if request.headers.get('x-requested-with') == 'XMLHttpRequest':
				return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
	else:
		form = BlogPostForm(initial={"author": "Admin"})
	return render(request, 'form.html', {'form': form, 'action': 'Create', 'action_url': request.path})


@csrf_exempt
def api_post_create(request):
	"""API endpoint for creating blog post from Flutter.
	Returns JSON response. Requires admin authentication.
	"""
	if not request.user.is_authenticated:
		return JsonResponse({'ok': False, 'error': 'unauthenticated'}, status=401)
	
	if not is_admin(request.user):
		return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)
	
	if request.method != 'POST':
		return JsonResponse({'ok': False, 'error': 'Invalid method'}, status=405)
	
	import json
	try:
		data = json.loads(request.body)
	except json.JSONDecodeError:
		return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)
	
	# Validate required fields
	title = data.get('title', '').strip()
	content = data.get('content', '').strip()
	author = data.get('author', '').strip()
	thumbnail_url = data.get('thumbnail_url', '').strip()
	
	if not title:
		return JsonResponse({'ok': False, 'error': 'Title is required'}, status=400)
	if not content:
		return JsonResponse({'ok': False, 'error': 'Content is required'}, status=400)
	
	# Create post
	post = BlogPost.objects.create(
		title=title,
		content=content,
		author=author or getattr(request.user, 'username', '') or getattr(request.user, 'email', '') or 'Admin',
		thumbnail_url=thumbnail_url or '',
	)
	
	return JsonResponse({
		'ok': True,
		'message': 'Post created successfully',
		'post': _serialize_post(post)
	}, status=201)


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
			# messages.success(request, 'Post updated.')
			if request.headers.get('x-requested-with') == 'XMLHttpRequest':
				return JsonResponse({'ok': True, 'redirect': post.get_absolute_url()})
			return redirect(post.get_absolute_url())
		else:
			messages.error(request, f"Please fix the errors below: {form.errors.as_text()}")
			if request.headers.get('x-requested-with') == 'XMLHttpRequest':
				return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
	else:
		form = BlogPostForm(instance=post)
	return render(request, 'form.html', {'form': form, 'action': 'Update', 'action_url': request.path})


@login_required
@user_passes_test(is_admin)
def post_delete(request, pk: int):
	post = get_object_or_404(BlogPost, pk=pk)
	if request.method == 'POST':
		post.delete()
		# messages.success(request, 'Post deleted.')
		if request.headers.get('x-requested-with') == 'XMLHttpRequest':
			return JsonResponse({'ok': True, 'redirect': reverse('blog:list')})
		return redirect('blog:list')
	return render(request, 'confirm_delete.html', {'post': post, 'action_url': request.path})


@csrf_exempt
def api_post_delete(request, pk: int):
	"""API endpoint for deleting blog post from Flutter.
	Returns JSON response. Requires admin authentication.
	Accepts both DELETE and POST methods for compatibility.
	"""
	if not request.user.is_authenticated:
		return JsonResponse({'ok': False, 'error': 'unauthenticated'}, status=401)
	
	if not is_admin(request.user):
		return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)
	
	if request.method not in ['DELETE', 'POST']:
		return JsonResponse({'ok': False, 'error': 'Invalid method'}, status=405)
	
	post = get_object_or_404(BlogPost, pk=pk)
	post.delete()
	return JsonResponse({'ok': True, 'message': 'Post deleted successfully'}, status=200)
