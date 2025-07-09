from rest_framework import serializers
from .models import Document, DocumentFile
from django.utils.text import slugify


class DocumentSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.email')

    class Meta:
        model = Document
        fields = ['id', 'title', 'slug', 'description', 'category', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_by', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        if 'title' in validated_data and validated_data['title'] != instance.title:
            # Сброс slug если title изменился
            base_slug = slugify(validated_data['title'])
            slug = base_slug
            counter = 1
            while Document.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            instance.slug = slug
        return super().update(instance, validated_data)
    
    
    
class DocumentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFile
        fields = ['id', 'document', 'file', 'uploaded_at', 'uploaded_by']
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by']

    def validate_file(self, value):
        """
        Проверка загружаемого файла:
        - допустимые расширения (включая Excel)
        - максимальный размер (10MB)
        """
        allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.xls', '.xlsx']
        max_file_size = 10 * 1024 * 1024  # 10 MB

        # Проверка расширения
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Файл с расширением '{ext}' не поддерживается. "
                f"Разрешённые форматы: {', '.join(allowed_extensions)}."
            )

        # Проверка размера
        if value.size > max_file_size:
            raise serializers.ValidationError(
                f"Размер файла превышает 10MB (текущий: {value.size / (1024 * 1024):.2f} MB)."
            )

        return value