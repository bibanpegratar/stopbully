from xmlrpc.client import ServerProxy
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import numpy as np
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from api.models import CustomUser
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from face_detection.serializers import ImageDataSerializer, ImageSerializer
from .models import Image
from rest_framework.permissions import IsAuthenticated
from django.core.files.base import ContentFile
from rest_framework.decorators import action, renderer_classes

# import urllib # python 2
import urllib.request # python 3
import json
import cv2
import os
import cloudinary

from .custom_renderers import *

# define the path to the face detector
FACE_DETECTOR_PATH = "{base_path}/cascades/haarcascade_frontalface_default.xml".format(
	base_path=os.path.abspath(os.path.dirname(__file__)))

BLACK_SQUARE = True
BLUR_IMAGE = False

class ProcessImage(viewsets.ModelViewSet):
	serializer_class = ImageSerializer
	queryset = Image.objects.all()
	permission_classes = [IsAuthenticated]

	def list(self, request):
		images = self.get_queryset()
		serializer = ImageDataSerializer(images, many=True)
		print(serializer.data)
		return Response(serializer.data)

	def retrieve(self, request, pk=None, uid=None):
		image = Image.objects.get(pk = pk)
		serializer = ImageDataSerializer(image)
		return JsonResponse(serializer.data)

	def create(self, request):
		data = {"success": False}

		if request.FILES.get("image", None) is not None:
			image = grab_image(stream=request.FILES["image"])

		# otherwise, assume that a URL was passed in
		else:
			url = request.POST.get("url", None)

			if url is None:
				data["error"] = "No URL provided."
				return JsonResponse(data)

			image = grab_image(url=url)

		# convert the image to grayscale, load the face cascade detector,
		# and detect faces in the image
		raw_image = image
		image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		detector = cv2.CascadeClassifier(FACE_DETECTOR_PATH)
		rects = detector.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5,
			minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)

		# construct a list of bounding boxes from the detection
		
		rects = [(int(x), int(y), int(x + w), int(y + h)) for (x, y, w, h) in rects]
		print(rects)

		for rect in rects:
			print(rect)
			#create black rectangle
			if BLACK_SQUARE:
				cv2.rectangle(raw_image, (rect[0], rect[1]), (rect[2], rect[3]), (0,0,0), -1)

			#blur image portion
			if BLUR_IMAGE:
				x, y = rect[0], rect[1]
				w, h = rect[2] ,rect[3]
				ROI = image[y:h, x:w]
				blur = cv2.GaussianBlur(raw_image,(51,51), 0) 
				image[y:h, x:w] = blur

		# upload image
		ret, buf = cv2.imencode('.jpg', raw_image) # cropped_image: cv2 / np array
		content = ContentFile(buf.tobytes())
		# user_id = Token.objects.get(key=request.auth.key).user_id
		# user = CustomUser.objects.get(id=request.user.id)

		img_model = Image(user_id=request.user)
		if len(rects) > 0:
			img_model.has_face = True
		else:
			img_model.has_face = False

		img_model.image.save('output.jpg', content)
		img_model.save()

		serializer = ImageDataSerializer(img_model)

		return JsonResponse(serializer.data)
		
def grab_image(path=None, stream=None, url=None):
	# if the path is not None, then load the image from disk
	if path is not None:
		image = cv2.imread(path)

	# otherwise, the image does not reside on disk
	else:	
		# if the URL is not None, then download the image
		if url is not None:
			resp = urllib.request.urlopen(url)
			data = resp.read()

		# if the stream is not None, then the image has been uploaded
		elif stream is not None:
			data = stream.read()
			
		# convert the image to a NumPy array and then read it into
		# OpenCV format
		image = np.asarray(bytearray(data), dtype="uint8")
		image = cv2.imdecode(image, cv2.IMREAD_COLOR)

	# return the image
	return image