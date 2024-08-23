from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import FaceComparisonSerializer
from deepface import DeepFace
from PIL import Image
import os
from django.core.files.uploadedfile import InMemoryUploadedFile

# save temporary image
def save_image(image_data, filename):
    with open(filename, "wb+") as f:
        for chunk in image_data.chunks():
            f.write(chunk)

def save_training_image(image_data, filename):
    # Ensure the directory exists within the 'api' folder
    current_dir = os.path.dirname(__file__)
    api_dir = os.path.abspath(os.path.join(current_dir, ".."))
    full_path = os.path.join(api_dir, filename)

    directory = os.path.dirname(full_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    print("directory: ", directory)

    # Open the image from the uploaded file
    if isinstance(image_data, InMemoryUploadedFile):
        image = Image.open(image_data)
    else:
        raise ValueError("Expected an InMemoryUploadedFile object")

    # Convert image to RGB if saving as JPEG or PNG
    if full_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        if image.mode == 'RGBA':
            image = image.convert('RGB')

    # Save the image to the specified file
    image.save(full_path)


@api_view(["POST"])
def verif_faces(request):
    serializer = FaceComparisonSerializer(data=request.data)
    if serializer.is_valid():
        image1 = serializer.validated_data["image1"]
        image2 = serializer.validated_data["image2"]

        # save temporary image from image1 and image2
        save_image(image1, "image1.jpg")
        save_image(image2, "image2.jpg")

        # Compare image using DeepFace Library
        # Face Detectors using opencv
        # distance metric using cosine similarity
        print()
        try:
            result = DeepFace.verify(
                img1_path="image1.jpg",
                img2_path="image2.jpg",
                detector_backend="mtcnn",
            )
            is_verified = result["verified"]
            distance = result["distance"]
            threshold = result["threshold"]
        except Exception:
            is_verified = False
            distance = None
            threshold = None

        # remove temporary image
        os.remove("image1.jpg")
        os.remove("image2.jpg")

        return Response(
            {
                "verified": is_verified,
                "distance": distance,
                "threshold": threshold,
            },
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
