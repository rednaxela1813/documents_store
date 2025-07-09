import uuid
from django.db import models
from django.utils.text import slugify


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    created_by = models.ForeignKey(
        'account.CustomUser',
        on_delete=models.CASCADE,
        related_name='documents'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Document.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    
    
def document_file_path(instance, filename):
    """Генерирует путь для загружаемых файлов."""
    if instance.document_id:
        # если документ уже привязан
        return f"documents/{instance.document_id}/{filename}"
    # fallback пока нет document_id
    return f"documents/temp/{filename}"



class DocumentFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey('documents.Document', related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to=document_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Document File"
        verbose_name_plural = "Document Files"

    def __str__(self):
        return f"{self.file.name}"
