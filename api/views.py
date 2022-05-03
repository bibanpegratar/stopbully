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
    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many = True)
        return Response(serializer.data)

class UserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = CustomUser.objects.all()
        
class UserRegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data = request.data)
        response_data = {}
        if serializer.is_valid():
            account = serializer.save()
            account_id = account.id
            account = CustomUser.objects.get(pk=account_id)
            account.user = 'user_' + str(account.pk)
            account = account.save()
            response_data['id'] = account_id
            response_data['user'] = account.user
            response_data['email'] = account.email
            token = Token.objects.get(user=account).key
            response_data['token'] = token

            return Response(response_data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class PostAPIView(APIView):
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

class CommentAPIView(APIView):
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