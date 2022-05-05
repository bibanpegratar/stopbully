from django.urls import path
from .views import *
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import renderers

post_list = PostViewSet.as_view({
    'get' : 'list',
    'post' : 'create'
})

post_detail = PostViewSet.as_view({
    'get' : 'retrieve',
    'put' : 'update',
    'delete' : 'destroy'
})

retrieve_by_user = PostViewSet.as_view({
    'get' : 'retrieve_by_user'
})

user_list = UserViewSet.as_view({
    'get' : 'list'
})

user_detail = UserViewSet.as_view({
    'get' : 'retrieve'
})

current_user = UserViewSet.as_view({
    'get' : 'current_user',
    'delete' : 'destroy'
})

comment_list = CommentViewSet.as_view({
    'get' : 'list',
    'post' : 'create'
})
comment_detail = CommentViewSet.as_view({
    'get' : 'retrieve',
    'put' : 'update',
    'delete' : 'destroy'
})

retrieve_by_post = CommentViewSet.as_view({
    'get' : 'retrieve_by_post'
})

urlpatterns = [
    path('user/', current_user),
    path('user/change_password', UserUpdatePasswordAPIView.as_view()),
    path('user/change_email', UserUpdateEmailAPIView.as_view()),
    path('users/', user_list),

    path('users/<int:pk>', user_detail),
    path('login/', obtain_auth_token, name='login'),
    path('register/', UserRegisterAPIView.as_view()),

    path('comments/', comment_list),
    path('comments/<int:pid>/', retrieve_by_post),
    path('comments/<int:pid>/<int:pk>/', comment_detail),
    
    path('posts/', post_list),
    path('posts/<int:uid>/', retrieve_by_user),
    path('posts/<int:uid>/<int:pk>/', post_detail)
]

