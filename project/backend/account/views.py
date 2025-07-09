from rest_framework import generics
from .serializers import UserRegistrationSerializer, UserSerializer, SetPasswordSerializer
from .models import CustomUser
from rest_framework import permissions
from django.contrib.auth.password_validation import validate_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers





class RegisterUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    



class UserMeView(generics.RetrieveUpdateAPIView):
    """
    Позволяет получить или обновить данные авторизованного пользователя
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Возвращает текущего авторизованного пользователя"""
        return self.request.user



class SetPasswordView(APIView):
    """
    Позволяет авторизованному пользователю сменить пароль
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            return Response(
                {'old_password': 'Неверный старый пароль.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(new_password, user=user)
        except serializers.ValidationError as e:
            return Response({'new_password': e.detail}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'detail': 'Пароль успешно изменён.'}, status=status.HTTP_200_OK)