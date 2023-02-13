from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
# from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .forms import NewCommentForm, NewPostForm
from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Comments, Like
from django.contrib.auth.decorators import login_required
import json
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import random
class PostListView(ListView):
    model = Post
    template_name = 'feed/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 10
    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        items = list(Post.objects.all())
        # change 4 to how many random items you want
        random_items = random.sample(items, 6)
        context['carousel_item'] = random_items
        if self.request.user.is_authenticated:
            liked = [i for i in Post.objects.all() if Like.objects.filter(
                user=self.request.user, post=i)]
            context['liked_post'] = liked
        return context


class UserPostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'feed/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(UserPostListView, self).get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        liked = [i for i in Post.objects.filter(
            user_name=user) if Like.objects.filter(user=self.request.user, post=i)]
        context['liked_post'] = liked
        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(user_name=user).order_by('-date_posted')


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    is_liked = Like.objects.filter(user=user, post=post)
    if request.method == 'POST':
        form = NewCommentForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.post = post
            data.username = user
            data.save()
            return redirect('post-detail', pk=pk)
    else:
        form = NewCommentForm()
    return render(request, 'feed/post_detail.html', {'post': post, 'is_liked': is_liked, 'form': form})


@login_required
def create_post(request):
    user = request.user
    if request.method == "POST":
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            # data = form.save(commit=False)
            # data.user_name = user
            # data.save()
            admin_name = User.objects.filter(is_superuser=True).values_list('username')[0][0]
            user_name = request.user.username
            domain_url = "http://127.0.0.1:8000"
            description = form.cleaned_data['description']
            tags = form.cleaned_data['tags']
            if tags=='':
                tags = None
            if description == '':
                description = None
            print(description, tags)
            context = {
                'admin_name': admin_name.title(),
                'user_name' : user_name.title(),
                "link_to_user" : f'{domain_url}/users/{user_name}',
                "link_to_admin_page" : f'{domain_url}/admin/',
                "link_to_post" : f'{domain_url}/admin/feed/post/add/',
                "domain_url" : domain_url,
                "tags" : tags,
                "description" : description,
            }
            print(context)

            from_mail = settings.EMAIL_HOST_USER
            to_mail = User.objects.filter(is_superuser=True).values_list('email')[0]
            subject = f"Post requested from {user_name}"

            html_template = 'feed/create_post_mail.html'
            html_message = render_to_string(html_template, context)
            attach = request.FILES['pic']
                        
            if from_mail and to_mail:
                try:
                    mail = EmailMessage(subject=subject, body=html_message, from_email=from_mail, to=to_mail)
                    mail.attach(attach.name, attach.read(), attach.content_type)
                    mail.content_subtype = 'html'
                    mail.send()
                except ArithmeticError as aex:
                    print(aex.args)
            
            messages.success(request, f'Posted Successfully')
            return redirect('home')
    else:
        form = NewPostForm()
    return render(request, 'feed/create_post.html', {'form': form})

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['description', 'pic', 'tags']
    template_name = 'feed/create_post.html'

    def form_valid(self, form):
        form.instance.user_name = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user_name:
            return True
        return False


@login_required
def post_delete(request, pk):
    post = Post.objects.get(pk=pk)
    if request.user == post.user_name:
        Post.objects.get(pk=pk).delete()
    return redirect('home')


@login_required
def search_posts(request):
    query = request.GET.get('p')
    object_list = Post.objects.filter(tags__icontains=query)
    liked = [i for i in object_list if Like.objects.filter(
        user=request.user, post=i)]
    context = {
        'posts': object_list,
        'liked_post': liked
    }
    return render(request, "feed/search_posts.html", context)


@login_required
def like(request):
    post_id = request.GET.get("likeId", "")
    user = request.user
    post = Post.objects.get(pk=post_id)
    liked = False
    like = Like.objects.filter(user=user, post=post)
    if like:
        like.delete()
    else:
        liked = True
        Like.objects.create(user=user, post=post)
    resp = {
        'liked': liked
    }
    response = json.dumps(resp)
    return HttpResponse(response, content_type="application/json")
