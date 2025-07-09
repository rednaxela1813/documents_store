from rest_framework import viewsets, permissions
from .models import Document, DocumentFile
from .serializers import DocumentSerializer, DocumentFileSerializer
from .permissions import IsOwnerOrReadOnly


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'slug'  # Используем slug вместо id для URL

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        
        
        
class DocumentFileViewSet(viewsets.ModelViewSet):
    queryset = DocumentFile.objects.all()
    serializer_class = DocumentFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
