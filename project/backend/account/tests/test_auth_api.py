import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from account.models import CustomUser

REGISTER_URL = reverse('account:register')
TOKEN_URL = reverse('account:token_obtain_pair')  # JWT эндпоинт
ME_URL = reverse('account:me')  # будущий эндпоинт для получения текущего пользователя


@pytest.mark.django_db
def test_create_user_invalid_password():
    """Тест: регистрация с коротким паролем должна провалиться"""
    payload = {
        'email': 'invalidpass@example.com',
        'password': '123',  # слишком короткий
        'name': 'Invalid User'
    }
    client = APIClient()
    response = client.post(REGISTER_URL, payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert CustomUser.objects.filter(email=payload['email']).count() == 0


@pytest.mark.django_db
def test_create_user_existing_email():
    """Тест: регистрация с уже существующим email должна провалиться"""
    CustomUser.objects.create_user(
        email='test@example.com',
        password='Testpass123',
        name='Test User'
    )
    payload = {
        'email': 'test@example.com',
        'password': 'Newpass123',
        'name': 'Duplicate User'
    }
    client = APIClient()
    response = client.post(REGISTER_URL, payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert CustomUser.objects.filter(email='test@example.com').count() == 1


@pytest.mark.django_db
def test_obtain_token_success():
    """Тест: получение JWT токена с правильными данными"""
    user = CustomUser.objects.create_user(
        email='tokenuser@example.com',
        password='StrongPass123',
        name='Token User'
    )
    payload = {
        'email': 'tokenuser@example.com',
        'password': 'StrongPass123'
    }
    client = APIClient()
    response = client.post(TOKEN_URL, payload)

    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data


@pytest.mark.django_db
def test_obtain_token_invalid_credentials():
    """Тест: получение токена с неправильными данными должно провалиться"""
    CustomUser.objects.create_user(
        email='wrongpass@example.com',
        password='RightPass123',
        name='Wrong Pass User'
    )
    payload = {
        'email': 'wrongpass@example.com',
        'password': 'WrongPass123'  # неправильный пароль
    }
    client = APIClient()
    response = client.post(TOKEN_URL, payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'access' not in response.data
    assert 'refresh' not in response.data


@pytest.mark.django_db
def test_get_user_profile_authenticated():
    """Тест: получение профиля пользователя с токеном"""
    user = CustomUser.objects.create_user(
        email='profileuser@example.com',
        password='ProfilePass123',
        name='Profile User'
    )
    client = APIClient()
    token_response = client.post(TOKEN_URL, {
        'email': user.email,
        'password': 'ProfilePass123'
    })
    token = token_response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = client.get(ME_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == user.email
    assert response.data['name'] == user.name


@pytest.mark.django_db
def test_get_user_profile_unauthenticated():
    """Тест: неавторизованный пользователь не может получить профиль"""
    client = APIClient()
    response = client.get(ME_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    

@pytest.mark.django_db
def test_create_user_successful():
    """Тест успешной регистрации пользователя"""
    payload = {
        'email': 'testuser@example.com',
        'password': 'SuperSecret123!',
        'name': 'Test User'
    }
    client = APIClient()
    response = client.post(REGISTER_URL, payload)

    assert response.status_code == status.HTTP_201_CREATED
    user = CustomUser.objects.get(email=payload['email'])
    assert user.check_password(payload['password'])  # Пароль хэширован
    assert response.data['email'] == payload['email']
    assert 'password' not in response.data  # Пароль не возвращаем
    
    
@pytest.mark.django_db
def test_update_user_profile_authenticated():
    """Тест: авторизованный пользователь может обновить свои данные"""
    user = CustomUser.objects.create_user(
        email='updateuser@example.com',
        password='UpdatePass123',
        name='Old Name'
    )
    client = APIClient()
    token_response = client.post(TOKEN_URL, {
        'email': user.email,
        'password': 'UpdatePass123'
    })
    token = token_response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    payload = {'name': 'New Name'}
    response = client.patch(ME_URL, payload)

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.name == payload['name']
    assert response.data['name'] == payload['name']


SET_PASSWORD_URL = reverse('account:set_password')


@pytest.mark.django_db
def test_change_password_successful():
    """Тест: успешная смена пароля авторизованным пользователем"""
    user = CustomUser.objects.create_user(
        email='changepass@example.com',
        password='OldPassword123',
        name='Change Pass'
    )
    client = APIClient()
    # Авторизация
    response = client.post(reverse('account:token_obtain_pair'), {
        'email': user.email,
        'password': 'OldPassword123'
    })
    token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    payload = {
        'old_password': 'OldPassword123',
        'new_password': 'NewPassword456'
    }
    response = client.post(SET_PASSWORD_URL, payload)

    user.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert user.check_password(payload['new_password'])
    
    
    
@pytest.mark.django_db
def test_change_password_invalid_old_password():
    """Тест: смена пароля с неправильным старым паролем должна провалиться"""
    user = CustomUser.objects.create_user(
        email='wrongoldpass@example.com',
        password='OldPassword123',
        name='Wrong Old Pass'
    )
    client = APIClient()
    token_response = client.post(reverse('account:token_obtain_pair'), {
        'email': user.email,
        'password': 'OldPassword123'
    })
    token = token_response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    payload = {
        'old_password': 'WrongOldPass',
        'new_password': 'NewPassword456'
    }
    response = client.post(SET_PASSWORD_URL, payload)

    user.refresh_from_db()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not user.check_password(payload['new_password'])



LOGOUT_URL = reverse('account:logout')

@pytest.mark.django_db
def test_logout_success():
    """Тест: успешный logout (blacklist refresh токена)"""
    # Создаем пользователя и логинимся
    user = CustomUser.objects.create_user(
        email='logout@example.com',
        password='LogoutPass123',
        name='Logout User'
    )
    client = APIClient()
    token_response = client.post(reverse('account:token_obtain_pair'), {
        'email': user.email,
        'password': 'LogoutPass123'
    })
    refresh_token = token_response.data['refresh']

    # Делаем logout (blacklist refresh токена)
    response = client.post(LOGOUT_URL, {'refresh': refresh_token})

    assert response.status_code == status.HTTP_205_RESET_CONTENT
    
    
    
    
@pytest.mark.django_db
def test_logout_invalid_refresh_token():
    """Тест: logout с невалидным refresh токеном должен вернуть 400"""
    client = APIClient()
    invalid_refresh_token = "this.is.not.a.valid.token"
    response = client.post(LOGOUT_URL, {'refresh': invalid_refresh_token})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data
    assert response.data['detail'] == 'Token is blacklisted or invalid'
    
    
    
    
@pytest.mark.django_db
def test_logout_without_refresh_token():
    """Тест: logout без refresh токена должен вернуть 400"""
    client = APIClient()
    response = client.post(LOGOUT_URL, {})  # пустое тело запроса

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data
    assert response.data['detail'] == 'Refresh token is required'



