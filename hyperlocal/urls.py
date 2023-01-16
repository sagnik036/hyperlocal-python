from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from api.views import VerifyEmail, ResetPassword
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('verify-email/<str:token>', VerifyEmail.as_view()),
    path('reset-password/<str:token>', ResetPassword.as_view()),
    
    path(
        'admin/password_reset/',
        auth_views.PasswordResetView.as_view(),
        name='admin_password_reset',
    ),
    path(
        'admin/password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete',
    ),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
