from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "text", "author", "image", "created")
        model = Post
