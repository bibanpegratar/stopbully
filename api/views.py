from .models import CustomUser, Post, Comment
from .serializers import *
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.authtoken.views import obtain_auth_token, ObtainAuthToken
from rest_framework import parsers, renderers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import ManualSchema
from rest_framework.schemas import coreapi as coreapi_schema
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
import threading
from rest_framework.decorators import api_view
from django.shortcuts import render, redirect

class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

def send_activation_email(user, request):
    current_site = get_current_site(request)
    email_subject = 'Activate your account'
    generated_token = generate_token.make_token(user)

    email_body = render_to_string('verification/activate.html', {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generated_token
    })

    email = EmailMessage(subject=email_subject, body=email_body,
                         from_email=settings.DEFAULT_FROM_EMAIL,
                         to=[user.email]
                         )

    print(generated_token)
    if not settings.TESTING:
        EmailThread(email).start()

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request):
        user = CustomUser.objects.get(pk=request.user.id)
        user.delete()
        return Response(status = status.HTTP_200_OK)

    @action(detail=False)
    def current_user(self, request):
        user = CustomUser.objects.get(pk=request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        data = request.data
        data['user_id'] = request.user.id

        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            print(request.user)
            print(serializer.validated_data)
            post = serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors)   

    def update(self, request, partial=True, pk=None, uid=None):
        try:
            posts = Post.objects.get(pk=pk)
        except:
            return Response({'error':'not found'}, status = status.HTTP_404_NOT_FOUND)
        data = request.data
        print(request.user.id)
        print(posts.user_id.id)
        
        if posts.user_id.id == request.user.id:
            posts.caption = data['caption']
            posts.content = data['content']
            posts.likes = data['likes']
            posts.save()
            serializer = self.get_serializer(posts)

            return Response(serializer.data)
        else:
            return Response("unauthorized", status = status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, pk=None, uid=None):
        try:
            post = Post.objects.get(pk=pk)
        except:
            return Response({'error':'not found'}, status = status.HTTP_404_NOT_FOUND)

        if post.user_id.id == request.user.id:
            post.delete()
            return Response(status = status.HTTP_200_OK)
        else:
            return Response("unauthorized", status = status.HTTP_401_UNAUTHORIZED)

    @action(detail=False)
    def retrieve_by_user(self, request, uid=None):
        posts = Post.objects.filter(user_id=uid)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerialzier
    permission_classes = [IsAuthenticated]

    def update(self, request, partial=True, pk=None, pid=None):
        try:
            comment = Comment.objects.get(pk=pk)
        except:
            return Response({'error':'not found'}, status = status.HTTP_404_NOT_FOUND)
            
        data = request.data
        print(request.user.id)
        print(comment.post_id.user_id.id)
        
        if comment.post_id.user_id.id == request.user.id:
            comment.content = data['content']
            comment.likes = data['likes']
            comment.save()
            serializer = self.get_serializer(comment)

            return Response(serializer.data)
        else:
            return Response("unauthorized", status = status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, pk=None, pid=None):
        try:
            comment = Comment.objects.get(pk=pk)
        except:
            return Response({'error':'not found'}, status = status.HTTP_404_NOT_FOUND)

        if comment:
            if comment.post_id.user_id.id == request.user.id:
                comment.delete()
                return Response(status = status.HTTP_200_OK)
            else:
                return Response("unauthorized", status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response('not found')
    
    @action(detail=False)
    def retrieve_by_post(self, request, pid=None):
        comments = Comment.objects.filter(post_id=pid)
        serializer = self.get_serializer(comments, many = True)
        return Response(serializer.data)

class UserRegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data = request.data)
        
        response_data = {}
        if serializer.is_valid():
            account = serializer.save()

            if not settings.TESTING:
                send_activation_email(account, request)

            account = CustomUser.objects.get(pk=account.id)
            account.user = 'user_' + str(account.pk)
            new_account = account.save()
            response_data['id'] = account.id
            # response_data['user'] = account.user
            # response_data['email'] = account.email
            token = Token.objects.get(user=account).key
            # response_data['token'] = token

            return Response(response_data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class UserUpdatePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = CustomUser.objects.get(pk=request.user.id)
        data = request.data
        if user.id == request.user.id:
            if data['password'] == data['password2']:
                user.set_password(data['password'])
                user.save()
                serializer = UserSerializer(user)
                return Response(serializer.data)
            else:
                return Response({"password":"Password fields didn't match"}, status = status.HTTP_400_BAD_REQUEST)
        else:
            return Response("unauthorized", status = status.HTTP_401_UNAUTHORIZED)

class UserUpdateEmailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = CustomUser.objects.get(pk=request.user.id)
        data = request.data
        if user.id == request.user.id:
            user.email = data['email']
            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            return Response("unauthorized", status = status.HTTP_401_UNAUTHORIZED)
            

class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    if coreapi_schema.is_enabled():
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="username",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Username",
                        description="Valid username for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        token, created = Token.objects.get_or_create(user=user)
        if not settings.TESTING:
            print(user.is_email_verified)

            if not user.is_email_verified:
                print('not verified')
                return Response('verify user first')

        return Response({'token': token.key})

obtain_auth_token = ObtainAuthToken.as_view()


@api_view(['GET'])
def activate_user(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)

    except Exception as e:
        user = None

    if user and generate_token.check_token(user, token):
        user.is_email_verified = True
        user.save()

        return render(request, 'verification/activated.html')
    return render(request, 'verification/already_activated.html')



