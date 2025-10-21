from django.db import models

class ENSource(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class ENArticle(models.Model):
    source = models.ForeignKey(ENSource, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(unique=True)
    published_at = models.DateTimeField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)  # لینک مستقیم عکس

    def __str__(self):
        return self.title
