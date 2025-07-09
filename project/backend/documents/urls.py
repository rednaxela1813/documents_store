from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, DocumentFileViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'files', DocumentFileViewSet, basename='documentfile')

app_name = 'documents'

urlpatterns = [
    path('', include(router.urls)),
]
