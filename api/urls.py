from django.urls import path
from .views import *
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('users/', UsersAPIView.as_view()),                                       #all user
    path('user/', UserAPIView.as_view()),                                         #user by id
    path('login/', obtain_auth_token, name='login'),                              #login user
    path('register/', UserRegisterAPIView.as_view()),                             #register user
 
    path('comments/', CommentsAPIView.as_view()),                                  #all comments
    path('posts/', PostsAPIView.as_view()),                                       #all posts
 
    path('user/posts/', PostsUserAPIView.as_view()),                       #current user's posts

    # path('post/<int:id/comments', CommentsPostAPIView.as_view()),                  #all comments of a post
    # path('post/int:post_id/comments/<int:comment_id>/', CommentAPIView.as_view()) #comment of a post
    
]