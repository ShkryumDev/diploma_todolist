from django.urls import path

from bot import views

urlpatterns = [
    path('verify', views.VerificationCodeView.as_view(), name='verify'),
]
