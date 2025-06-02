from rest_framework import serializers
from .models import BlogPost, AudioTranscription

class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at']

class TitleSuggestionSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=10000)

class AudioTranscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioTranscription
        fields = ['id', 'audio_file', 'transcription', 'created_at']
        read_only_fields = ['transcription']
