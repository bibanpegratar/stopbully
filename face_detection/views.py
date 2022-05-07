from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import numpy as np
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from api.models import CustomUser

from face_detection.serializers import ImageSerializer
from .models import Image
from rest_framework.permissions import IsAuthenticated
from django.core.files.base import ContentFile
from rest_framework.views import APIView

# import urllib # python 2
import urllib.request # python 3
import json
import cv2
import os

# define the path to the face detector
FACE_DETECTOR_PATH = "{base_path}/cascades/haarcascade_frontalface_default.xml".format(
	base_path=os.path.abspath(os.path.dirname(__file__)))

class DetectImage(APIView):
	serializer_class = ImageSerializer
	permission_classes = [IsAuthenticated]

	def post(self, request):
		data = {"success": False}

		if request.FILES.get("image", None) is not None:
			image = _grab_image(stream=request.FILES["image"])

		# otherwise, assume that a URL was passed in
		else:
			url = request.POST.get("url", None)

			if url is None:
				data["error"] = "No URL provided."
				return JsonResponse(data)

			image = _grab_image(url=url)

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

		cv2.rectangle(raw_image, (rects[0][0], rects[0][1]), (rects[0][2], rects[0][3]), (255,0,0), -1)

		# upload image
		ret, buf = cv2.imencode('.jpg', raw_image) # cropped_image: cv2 / np array
		content = ContentFile(buf.tobytes())
		# user_id = Token.objects.get(key=request.auth.key).user_id
		# user = CustomUser.objects.get(id=request.user.id)
		img_model = Image(user_id=request.user)
		img_model.image.save('output.jpg', content)
		
		print(img_model.image)

		# update the data dictionary with the faces detected
		data.update({"num_faces": len(rects), "faces": rects, "success": True})

		# return a JSON response
		return JsonResponse(data)

def _grab_image(path=None, stream=None, url=None):
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