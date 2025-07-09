import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from account.models import CustomUser
from documents.models import Document


@pytest.fixture
def user():
    return CustomUser.objects.create_user(
        email='user@example.com',
        password='Testpass123'
    )


@pytest.fixture
def other_user():
    return CustomUser.objects.create_user(
        email='other@example.com',
        password='Otherpass123'
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def document(user):
    return Document.objects.create(
        title="Test Document",
        description="A test document",
        category="General",
        created_by=user
    )


# --- CREATE ---
@pytest.mark.django_db
def test_create_document_success(auth_client, user):
    """Авторизованный пользователь может создать документ"""
    payload = {
        'title': 'Company Report',
        'description': 'Annual financial report',
        'category': 'Reports'
    }
    response = auth_client.post(reverse('documents:document-list'), payload)

    assert response.status_code == status.HTTP_201_CREATED
    document = Document.objects.get(id=response.data['id'])
    assert document.slug == 'company-report'
    assert response.data['slug'] == document.slug
    assert document.created_by == user


@pytest.mark.django_db
def test_create_document_unauthenticated():
    """Неавторизованный пользователь не может создать документ"""
    client = APIClient()
    payload = {'title': 'Unauthorized Doc', 'description': '...', 'category': 'General'}
    response = client.post(reverse('documents:document-list'), payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# --- READ ---
@pytest.mark.django_db
def test_get_document_list_authenticated(auth_client, document):
    """Авторизованный пользователь может получить список документов"""
    response = auth_client.get(reverse('documents:document-list'))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 1


@pytest.mark.django_db
def test_get_document_detail_authenticated(auth_client, document):
    """Авторизованный пользователь может получить один документ по UUID"""
    url = reverse('documents:document-detail', args=[document.slug])
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == document.title


@pytest.mark.django_db
def test_get_document_list_unauthenticated(document):
    """Неавторизованный пользователь не может получить список"""
    client = APIClient()
    response = client.get(reverse('documents:document-list'))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# --- UPDATE ---
@pytest.mark.django_db
def test_update_document_success(auth_client, document):
    """Автор документа может обновить его"""
    url = reverse('documents:document-detail', args=[document.slug])
    payload = {'title': 'Updated Title'}
    response = auth_client.patch(url, payload)

    assert response.status_code == status.HTTP_200_OK
    document.refresh_from_db()
    assert document.title == 'Updated Title'
    assert document.slug == 'updated-title'


@pytest.mark.django_db
def test_update_document_other_user_forbidden(other_user, document):
    """Другой пользователь не может обновить чужой документ"""
    client = APIClient()
    client.force_authenticate(user=other_user)
    url = reverse('documents:document-detail', args=[document.slug])
    payload = {'title': 'Hacked Title'}
    response = client.patch(url, payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN


# --- DELETE ---
@pytest.mark.django_db
def test_delete_document_success(auth_client, document):
    """Автор документа может удалить его"""
    url = reverse('documents:document-detail', args=[document.slug])
    response = auth_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Document.objects.filter(id=document.id).exists()
    
    


@pytest.mark.django_db
def test_delete_document_other_user_forbidden(other_user, document):
    """Другой пользователь не может удалить чужой документ"""
    client = APIClient()
    client.force_authenticate(user=other_user)
    url = reverse('documents:document-detail', args=[document.slug])
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


# --- EDGE CASES ---
@pytest.mark.django_db
def test_slug_uniqueness(auth_client, user):
    """Slug уникален: второй документ с тем же заголовком получает уникальный slug"""
    Document.objects.create(
        title="Duplicate Title", description="...", category="General", created_by=user
    )
    payload = {'title': 'Duplicate Title', 'description': 'Another one', 'category': 'General'}
    response = auth_client.post(reverse('documents:document-list'), payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['slug'].startswith('duplicate-title')


@pytest.mark.django_db
def test_get_nonexistent_document(auth_client):
    """Получение несуществующего документа должно вернуть 404"""
    import uuid
    url = reverse('documents:document-detail', args=[uuid.uuid4()])
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
