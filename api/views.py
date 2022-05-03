from sqlite3 import SQLITE_DROP_INDEX
from statistics import multimode
from .models import CustomUser, Post, Comment
from .serializers import CommentSerialzier, PostSerializer, UserSerializer, RegisterSerializer
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

class UsersAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many = True)
        return Response(serializer.data)

#view for getting user with token specified in headers
class UserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        try:
            uid = request.query_params["uid"]
            if uid != None:
                user = CustomUser.objects.get(id=uid)
                serializer = UserSerializer(user)
            
        except:
            user = request.user
            serializer = UserSerializer(user)

        return Response(serializer.data)   

class PostsUserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        try:
            uid = request.query_params["uid"]
            if uid != None:
                posts = Post.objects.filter(user_id=uid)
                serializer = PostSerializer(posts, many=True)
        except:
            posts = Post.objects.filter(user_id=request.user.id)
            serializer = PostSerializer(posts, many=True)

        return Response(serializer.data)
        
class UserRegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data = request.data)
        response_data = {}
        if serializer.is_valid():
            account = serializer.save()
            account = CustomUser.objects.get(pk=account.id)
            account.user = 'user_' + str(account.pk)
            new_account = account.save()
            response_data['id'] = account.id
            # response_data['user'] = account.user
            # response_data['email'] = account.email
            token = Token.objects.get(user=account).key
            response_data['token'] = token

            return Response(response_data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class PostsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many = True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class CommentsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerialzier(comments, many = True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerialzier(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)