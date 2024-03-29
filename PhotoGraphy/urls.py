"""PhotoGraphy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]
from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    # It changes the route to feed app 
    path('', include('feed.urls')),
    # It returns the user's they were not friend
    path('users/', user_views.users_list, name='users_list'),
    # It returns the profile of any user
    path('users/<slug>/', user_views.profile_view, name='profile_view'),
    # It returns the edit page of current user
    path('edit-profile/', user_views.edit_profile, name='edit_profile'),
    # It returns the profile of current user
    path('my-profile/', user_views.my_profile, name='my_profile'),
    # It is used to search friends
    path('search_users/', user_views.search_users, name='search_users'),
    # Below all are used for authentication and authorization factors
    path('register/', user_views.register_user, name='register'),
    path('login/', user_views.login_user, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
              template_name='users/request_password_reset.html',
              html_email_template_name = 'users/password_reset_email.html',
              subject_template_name="users/password_reset_subject.txt"), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
         name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
