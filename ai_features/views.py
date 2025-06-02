from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FileUploadParser, JSONParser
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import tempfile
import os
import shutil

from .models import BlogPost, AudioTranscription
from .serializers import (
    BlogPostSerializer, 
    TitleSuggestionSerializer, 
    AudioTranscriptionSerializer
)
from .services.transcription_service import AudioTranscriptionService
from .services.title_suggestion_service import TitleSuggestionService

# Lazy initialization functions
def get_transcription_service():
    if not hasattr(get_transcription_service, '_service'):
        get_transcription_service._service = AudioTranscriptionService()
    return get_transcription_service._service

def get_title_service():
    if not hasattr(get_title_service, '_service'):
        get_title_service._service = TitleSuggestionService()
    return get_title_service._service

def home_view(request):
    """
    Home page view with integrated web interface
    """
    return render(request, 'ai_features/home.html')

@api_view(['POST'])
@parser_classes([MultiPartParser, FileUploadParser])
def transcribe_audio(request):
    """
    Endpoint for audio transcription with speaker diarization
    Improved file handling to avoid Windows path issues
    
    Expected input: Audio file (mp3, wav, m4a, etc.)
    Returns: JSON with transcription, speaker information, and metadata
    """
    try:
        if 'audio_file' not in request.FILES:
            return Response({
                'success': False,
                'error': 'No audio file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        audio_file = request.FILES['audio_file']
        
        # Validate file type (more lenient since Whisper handles many formats)
        allowed_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.wma']
        file_extension = os.path.splitext(audio_file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            return Response({
                'success': False,
                'error': f'Unsupported file type. Allowed: {", ".join(allowed_extensions)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check file size (limit to 25MB for web upload)
        max_size = 25 * 1024 * 1024  # 25MB
        if audio_file.size > max_size:
            return Response({
                'success': False,
                'error': f'File too large. Maximum size is 25MB. Your file is {audio_file.size / (1024*1024):.1f}MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a safe temporary directory in the project folder
        temp_dir = os.path.join(os.getcwd(), 'temp_uploads')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save uploaded file to safe location with simple filename
        import uuid
        safe_filename = f"upload_{uuid.uuid4().hex[:8]}{file_extension}"
        temp_file_path = os.path.join(temp_dir, safe_filename)
        
        try:
            # Write file to safe location
            with open(temp_file_path, 'wb') as temp_file:
                for chunk in audio_file.chunks():
                    temp_file.write(chunk)
            
            print(f"📁 Saved uploaded file to: {temp_file_path}")
            print(f"📊 File size: {os.path.getsize(temp_file_path)} bytes")
            
            # Verify file was saved correctly
            if not os.path.exists(temp_file_path):
                return Response({
                    'success': False,
                    'error': 'Failed to save uploaded file'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Process transcription using lazy-loaded service
            transcription_service = get_transcription_service()
            result = transcription_service.transcribe_with_diarization(temp_file_path)
            
            # Save to database if successful
            if result['success']:
                try:
                    # Reset file pointer for saving
                    audio_file.seek(0)
                    file_path = default_storage.save(
                        f'audio/{audio_file.name}',
                        ContentFile(audio_file.read())
                    )
                    
                    transcription_record = AudioTranscription.objects.create(
                        audio_file=file_path,
                        transcription=result
                    )
                    
                    # Add database ID to response
                    result['transcription_id'] = transcription_record.id
                except Exception as e:
                    print(f"Warning: Could not save to database: {e}")
                    # Continue without saving to database
            
            return Response(result, status=status.HTTP_200_OK)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    print(f"🧹 Cleaned up uploaded file: {temp_file_path}")
                except Exception as e:
                    print(f"Warning: Could not clean up file: {e}")
    
    except Exception as e:
        print(f"❌ Upload processing failed: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': f'Processing failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@parser_classes([JSONParser])
def suggest_titles(request):
    """
    Endpoint for AI-powered blog post title suggestions
    
    Expected input: {"content": "blog post content here"}
    Returns: JSON with 3 title suggestions
    """
    try:
        serializer = TitleSuggestionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': 'Invalid input data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        content = serializer.validated_data['content']
        
        # Generate title suggestions using lazy-loaded service
        title_service = get_title_service()
        result = title_service.generate_title_suggestions(content)
        
        return Response(result, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Title generation failed: {str(e)}',
            'suggestions': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
def blog_posts(request):
    """
    Endpoint for managing blog posts
    """
    if request.method == 'GET':
        posts = BlogPost.objects.all().order_by('-created_at')
        serializer = BlogPostSerializer(posts, many=True)
        return Response({
            'success': True,
            'posts': serializer.data
        })
    
    elif request.method == 'POST':
        serializer = BlogPostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save()
            return Response({
                'success': True,
                'post': BlogPostSerializer(post).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'error': 'Invalid data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def transcription_history(request):
    """
    Get transcription history
    """
    transcriptions = AudioTranscription.objects.all().order_by('-created_at')
    serializer = AudioTranscriptionSerializer(transcriptions, many=True)
    return Response({
        'success': True,
        'transcriptions': serializer.data
    })

@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint
    """
    try:
        transcription_service = get_transcription_service()
        title_service = get_title_service()
        
        return Response({
            'status': 'healthy',
            'ffmpeg_required': False,  # No longer needed!
            'services': {
                'transcription': transcription_service.whisper_model is not None,
                'diarization': transcription_service.diarization_pipeline is not None,
                'title_generation': title_service.summarizer is not None or title_service.groq_client is not None
            },
            'notes': {
                'transcription': 'Whisper with librosa audio processing',
                'diarization': 'Requires HuggingFace token for speaker identification',
                'title_generation': 'Uses Groq API with local BART fallback'
            }
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'error': str(e),
            'services': {
                'transcription': False,
                'diarization': False,
                'title_generation': False
            }
        })
