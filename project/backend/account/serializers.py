# 📦 account/serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from .models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'name']

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'name']
        read_only_fields = ['email']


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Старый пароль неверный.')
        return value

    def validate_new_password(self, value):
        validate_password(value, self.context['request'].user)
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self, request):
        email = self.validated_data['email']
        user = CustomUser.objects.filter(email=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"{request.build_absolute_uri('/reset-password/')}?uid={uid}&token={token}"
            send_mail(
                'Сброс пароля',
                f'Ссылка для сброса пароля: {reset_link}',
                'noreply@yourdomain.com',
                [email],
                fail_silently=False,
            )


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def save(self, **kwargs):
        uid = self.validated_data['uid']
        token = self.validated_data['token']
        new_password = self.validated_data['new_password']

        user_id = force_str(urlsafe_base64_decode(uid))
        user = CustomUser.objects.get(pk=user_id)

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError('Неверный токен или пользователь.')

        user.set_password(new_password)
        user.save()
        return user
