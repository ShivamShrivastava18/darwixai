from django.contrib import admin
from .models import BlogPost, AudioTranscription

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'updated_at']
    list_filter = ['created_at', 'author']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AudioTranscription)
class AudioTranscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'audio_file', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'transcription']
