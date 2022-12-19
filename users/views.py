from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile
from feed.models import Post
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import HttpResponseRedirect
from .models import Profile
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
import random

User = get_user_model()


@login_required
def users_list(request):
    users = Profile.objects.exclude(user=request.user)
    context = {
        'users': users
    }
    return render(request, "users/users_list.html", context)

@login_required
def profile_view(request, slug):
    p = Profile.objects.filter(slug=slug).first()
    u = p.user
    user_posts = Post.objects.filter(user_name=u)
    context = {
        'u': u,
        'post_count': user_posts.count
    }
    return render(request, "users/profile.html", context)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request, f'Your account has been created! You can now login!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('my_profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'users/edit_profile.html', context)


@login_required
def my_profile(request):
    p = request.user.profile
    you = p.user
    user_posts = Post.objects.filter(user_name=you)

    context = {
        'u': you,
        'post_count': user_posts.count
    }

    return render(request, "users/profile.html", context)


@login_required
def search_users(request):
    query = request.GET.get('q')
    object_list = User.objects.filter(username__icontains=query)
    context = {
        'users': object_list
    }
    return render(request, "users/search_users.html", context)
