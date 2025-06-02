from django.urls import path
from . import views

urlpatterns = [
    # Audio transcription endpoints
    path('transcribe/', views.transcribe_audio, name='transcribe_audio'),
    path('transcriptions/', views.transcription_history, name='transcription_history'),
    
    # Blog title suggestion endpoints
    path('suggest-titles/', views.suggest_titles, name='suggest_titles'),
    
    # Blog post management
    path('blog-posts/', views.blog_posts, name='blog_posts'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
]
