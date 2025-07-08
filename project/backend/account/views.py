from rest_framework import generics
from .serializers import UserRegistrationSerializer
from .models import CustomUser



class RegisterUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer

