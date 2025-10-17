from django.db import models

# Create your models here.
from django.db import models

class Source(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name or "Unknown Source"

class ExternalArticle(models.Model):
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=400)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(unique=True)
    image = models.ImageField(upload_to='external_images/', blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
