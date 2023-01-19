from api import views
from django.urls import path

urlpatterns = [
    path('terms/', views.TermAndConditionAPI.as_view()),
    path('privacy-policy/', views.PrivacyPolicyAPI.as_view()),
    path('admin-contact/', views.AdminContactAPI.as_view()),
    path('payment-terms/', views.PaymentTermAPI.as_view()),
    path('user-notifications/', views.UserNotificationList.as_view()),
    path('user-notifications/<str:pk>/', views.UserNotificationDetail.as_view()),
    path('device-token/', views.DeviceTokenView.as_view()),
    path('check-email/', views.CheckEmail.as_view()),
    path('login/', views.LoginAPI.as_view()),
    path('refresh-token/', views.RefreshTokenView.as_view()),
    path('profile/', views.ProfileAPI.as_view()),
    path('forget-password/', views.ForgetPasswordAPI.as_view()),
    path('register/', views.RegistrationView.as_view()),
    path('otp/', views.OTPView.as_view()),
    path('email-verify/', views.EmailVerify.as_view()),
    path('unread-notification-count/', views.UserNotificationCountAPI.as_view()),
    path('frequently-asked-question/', views.FrequentlyAskedQuestionList.as_view()),
    path('frequently-asked-question/<str:pk>/', views.FrequentlyAskedQuestionDetail.as_view()),
    path('users/', views.UserList.as_view(), name='users'),
]
