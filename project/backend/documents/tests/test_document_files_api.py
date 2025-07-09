import io
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from account.models import CustomUser
from documents.models import Document, DocumentFile
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
def test_upload_document_file():
    """Авторизованный пользователь может загрузить файл к документу"""
    user = CustomUser.objects.create_user(email='user@example.com', password='Testpass123')
    document = Document.objects.create(
        title='Test Document',
        description='Test Description',
        category='General',
        created_by=user
    )

    client = APIClient()
    client.force_authenticate(user=user)

    file_content = b'Test file content'
    uploaded_file = SimpleUploadedFile("testfile.xlsx", file_content, content_type="text/plain")

    payload = {'document': str(document.id), 'file': uploaded_file}
    url = reverse('documents:documentfile-list')
    response = client.post(url, payload, format='multipart')

    assert response.status_code == status.HTTP_201_CREATED
    assert DocumentFile.objects.filter(document=document).exists()


@pytest.mark.django_db
def test_upload_excel_file_success():
    """Авторизованный пользователь может загрузить Excel файл"""
    user = CustomUser.objects.create_user(email='user@example.com', password='Testpass123')
    document = Document.objects.create(
        title='Excel Doc',
        description='Testing Excel upload',
        category='General',
        created_by=user
    )
    client = APIClient()
    client.force_authenticate(user=user)

    excel_content = b"Fake Excel content"
    uploaded_file = SimpleUploadedFile("testfile.xlsx", excel_content, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    payload = {'document': str(document.id), 'file': uploaded_file}
    url = reverse('documents:documentfile-list')
    response = client.post(url, payload, format='multipart')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['file'].endswith('testfile.xlsx')
