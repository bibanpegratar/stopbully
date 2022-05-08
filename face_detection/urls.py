from multiprocessing.dummy import Process
from django.urls import path
from .views import *

images = ProcessImage.as_view({
    'get' : 'list',
    'post' : 'create'
})


# images_of_user = ProcessImage.as_view({
#     'get' : 'get_images_ids'
# })



urlpatterns = [
    path('images/', images),
    # path('images/<uid>', images_of_user),
    path('images/<uid>/<pk>', GetImageAPIView.as_view())
]