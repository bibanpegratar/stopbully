from django.urls import path
from .views import UserAPIView, CommentAPIView, PostAPIView, UserRegisterAPIView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('users/', UserAPIView.as_view()),
    path('login/', obtain_auth_token, name='login'),
    path('register/', UserRegisterAPIView.as_view()),
    path('comments/', CommentAPIView.as_view()),
    path('posts/', PostAPIView.as_view())
]