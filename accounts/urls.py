from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    

    path('forgot-password/',auth_views.PasswordResetView.as_view(
            template_name      = 'accounts/password_reset/request.html',
            email_template_name = 'accounts/password_reset/email.txt',
            success_url        = '/forgot-password/sent/',
        ),
        name='password_reset'
    ),
    path('forgot-password/sent/',auth_views.PasswordResetDoneView.as_view(
            template_name = 'accounts/password_reset/sent.html',
        ),
        name='password_reset_done'
    ),

    path('forgot-password/reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(
            template_name = 'accounts/password_reset/confirm.html',
            success_url   = '/forgot-password/complete/',
        ),
        name='password_reset_confirm'
    ),

    path('forgot-password/complete/',auth_views.PasswordResetCompleteView.as_view(
            template_name = 'accounts/password_reset/complete.html',
        ),
        name='password_reset_complete'
    ),
]