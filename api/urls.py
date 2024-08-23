from django.urls import path
from .views import verif_faces
from .detector import train_faces, test_training_faces

urlpatterns = [path("verif/", verif_faces, name="verif_faces"),
               path("train/", train_faces, name="train_faces"),
               path("test/", test_training_faces, name="test_training_faces")]
