from rest_framework import serializers
from .models import CustomUser

from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import password_validation


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True}}
        
    def validate_password(self, value):
        """Проверка пароля с использованием стандартных валидаторов Django"""
        try:
            password_validation.validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        """Создать нового пользователя с хэшированным паролем"""
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name']
        )
        return user
    
    

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения и обновления данных пользователя"""

    class Meta:
        model = CustomUser
        fields = ['email', 'name']
        read_only_fields = ['email']  # email не редактируем
        
        
        




class SetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        """Проверяем старый пароль"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Старый пароль неверный.")
        return value

    def validate_new_password(self, value):
        """Проверяем новый пароль с использованием стандартных валидаторов"""
        password_validation.validate_password(value, self.context['request'].user)
        return value

    def save(self, **kwargs):
        """Сохраняем новый пароль"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
