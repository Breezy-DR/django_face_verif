from rest_framework import serializers


class FaceComparisonSerializer(serializers.Serializer):
    image1 = serializers.ImageField()
    image2 = serializers.ImageField()

class FaceTrainingSerializer(serializers.Serializer):
    username = serializers.CharField(max_length = 200)
    image_data_1 = serializers.ImageField()

class FaceTestingSerializer(serializers.Serializer):
    screenshot = serializers.ImageField()