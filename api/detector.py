import argparse
import pickle
from collections import Counter
from pathlib import Path

import face_recognition
from PIL import Image, ImageDraw
from rest_framework.decorators import api_view
from .serializers import FaceTrainingSerializer, FaceTestingSerializer
from .views import save_training_image
from random import randint
from rest_framework.response import Response
from rest_framework import status

DEFAULT_ENCODINGS_PATH = Path("api/output/encodings.pkl")
BOUNDING_BOX_COLOR = "blue"
TEXT_COLOR = "white"

# Create directories if they don't already exist
Path("api/training").mkdir(parents=True, exist_ok=True)
Path("api/output").mkdir(parents=True, exist_ok=True)
Path("api/validation").mkdir(parents=True, exist_ok=True)
Path("api/test").mkdir(parents=True, exist_ok=True) 

def encode_known_faces(
    model: str = "cnn", encodings_location: Path = DEFAULT_ENCODINGS_PATH
) -> None:
    """
    Loads images in the training directory and builds a dictionary of their
    names and encodings.
    """
    names = []
    encodings = []

    for filepath in Path("api/training").glob("*/*"):
        name = filepath.parent.name
        image = face_recognition.load_image_file(filepath)

        face_locations = face_recognition.face_locations(image, model=model)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        for encoding in face_encodings:
            names.append(name)
            encodings.append(encoding)

    name_encodings = {"names": names, "encodings": encodings}
    #print(name_encodings)
    with encodings_location.open(mode="wb") as f:
        pickle.dump(name_encodings, f)
        print("Encoding names succeeded")


def recognize_faces(
    image_location: str,
    model: str = "cnn",
    encodings_location: Path = DEFAULT_ENCODINGS_PATH,
):
    """
    Given an unknown image, get the locations and encodings of any faces and
    compares them against the known encodings to find potential matches.
    """
    with encodings_location.open(mode="rb") as f:
        loaded_encodings = pickle.load(f)

    input_image = face_recognition.load_image_file(image_location)

    input_face_locations = face_recognition.face_locations(
        input_image, model=model
    )
    input_face_encodings = face_recognition.face_encodings(
        input_image, input_face_locations
    )

    print("Input face locations:", input_face_locations)

    pillow_image = Image.fromarray(input_image)
    draw = ImageDraw.Draw(pillow_image)

    # TODO: make name to dynamic :)
    name = "admin"

    for bounding_box, unknown_encoding in zip(
        input_face_locations, input_face_encodings
    ):
        name = _recognize_face(unknown_encoding, loaded_encodings)
        if not name:
            name = "Unknown"

    del draw
    pillow_image.show()
    return name


def _recognize_face(unknown_encoding, loaded_encodings):
    """
    Given an unknown encoding and all known encodings, find the known
    encoding with the most matches.
    """
    boolean_matches = face_recognition.compare_faces(
        loaded_encodings["encodings"], unknown_encoding
    )
    votes = Counter(
        name
        for match, name in zip(boolean_matches, loaded_encodings["names"])
        if match
    )
    print("Votes:", votes)
    if votes:
        return votes.most_common(1)[0][0]


def validate(model: str = "cnn"):
    """
    Runs recognize_faces on a set of images with known faces to validate
    known encodings.
    """
    for filepath in Path("api/validation").rglob("*"):
        if filepath.is_file():
            recognize_faces(
                image_location=str(filepath.absolute()), model=model
            )

@api_view(["POST"])
def train_faces(request):
    faces_data = request.data
    serializer = FaceTrainingSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer._validated_data["username"]
        image_data_1 = serializer.validated_data["image_data_1"]

        print("username", username)

        number = randint(1, 100000)

        save_training_image(image_data_1, "api/training/{name}/image{image_number}.jpg".format(name=username, image_number=number))

        encode_known_faces()

        return Response(
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def test_training_faces(request):
    serializer = FaceTestingSerializer(data=request.data)
    if serializer.is_valid():
        screenshot = serializer._validated_data["screenshot"]

        save_training_image(screenshot, "api/test/screenshot.jpg")  

        face = recognize_faces("api/test/screenshot.jpg") 

        return Response(
            {
                "face_result": face,
            },
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

