# news/models.py
from django.db import models

class Source(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(unique=True)
    image_url = models.ImageField(upload_to='news_images/', blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title
