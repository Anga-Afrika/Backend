from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from .models import CustomUser

User = get_user_model()

class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'email', 'password')  # Add any additional fields here

class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = ('id', 'email', 'name') 