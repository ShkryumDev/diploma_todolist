from django.urls import path

from todolist.goals import views

urlpatterns = [
    path('verify', views.VerificationCodeView.as_view(), name='verify'),
]
