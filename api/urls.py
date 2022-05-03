from django.urls import path
from .views import UsersAPIView, CommentAPIView, PostAPIView, UserRegisterAPIView, UserIDAPIView, UserTokenAPIView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('users/', UsersAPIView.as_view()),
    path('users/id/', UserIDAPIView.as_view()),
    path('users/token/', UserTokenAPIView.as_view()),
    path('login/', obtain_auth_token, name='login'),
    path('register/', UserRegisterAPIView.as_view()),
    path('comments/', CommentAPIView.as_view()),
    path('posts/', PostAPIView.as_view())
]