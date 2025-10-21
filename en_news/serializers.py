from rest_framework import serializers
from .models import ENArticle, ENSource

class ENSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ENSource
        fields = "__all__"


class ENArticleSerializer(serializers.ModelSerializer):
    source = ENSourceSerializer()

    class Meta:
        model = ENArticle
        fields = "__all__"
