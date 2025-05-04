from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.models import UserProfile
import os
import logging
import traceback
import tempfile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import time
from datetime import datetime
import sys
from dal import UserDAO, MoodHistoryDAO, ListeningHistoryDAO
import json

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the AI/ML modules
try:
    from ai_ml.src.models.text_emotion import infer_text_emotion
    from ai_ml.src.models.speech_emotion import infer_speech_emotion
    from ai_ml.src.models.facial_emotion import infer_facial_emotion
    from ai_ml.src.recommendation.music_recommendation import get_music_recommendation
    logging.debug(f"Successfully imported AI/ML modules from {project_root}")
except ImportError as e:
    logging.error(f"Failed to import AI/ML modules: {str(e)}")
    logging.error(f"Python path: {sys.path}")
    raise

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize DAOs
user_dao = UserDAO()
mood_history_dao = MoodHistoryDAO()
listening_history_dao = ListeningHistoryDAO()

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'text': openapi.Schema(type=openapi.TYPE_STRING, description='Text to analyze for emotion'),
        },
        required=['text'],
    ),
    responses={
        200: openapi.Response('Emotion detected successfully'),
        400: openapi.Response('Invalid input'),
        500: openapi.Response('Internal server error'),
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def text_emotion(request):
    """
    Process text and detect emotion.
    """
    try:
        logger.debug("Received text emotion detection request")
        
        # Get text from request
        text = request.data.get('text')
        if not text:
            logger.error("No text provided in request")
            return Response({'error': 'No text provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        logger.debug(f"Processing text: {text}")
        
        # Detect emotion from text
        detected_emotion = infer_text_emotion(text)
        logger.debug(f"Detected emotion: {detected_emotion}")
        
        try:
            # Get user profile and save emotion to history
            user_profile = UserProfile.objects.get(username=request.user.username)
            user_profile.add_mood({
                'emotion': detected_emotion,
                'timestamp': datetime.utcnow()
            })
            logger.debug(f"Saved emotion to user history: {detected_emotion}")
            
            # Get music recommendations based on the detected emotion
            recommendations = get_music_recommendation(detected_emotion)
            logger.debug(f"Got {len(recommendations)} music recommendations")
            
            # Save recommendations to user history
            for track in recommendations:
                user_profile.add_recommendation(
                    track_id=track['external_url'].split('/')[-1],
                    track_name=track['name'],
                    artist=track['artist'],
                    emotion=detected_emotion
                )
            logger.debug("Saved recommendations to user history")
            
        except Exception as e:
            logger.error(f"Error saving to user history: {str(e)}")
            # Continue even if saving fails - we still want to return the emotion and recommendations
            recommendations = get_music_recommendation(detected_emotion)
        
        return Response({
            'emotion': detected_emotion,
            'message': 'Emotion detected and saved to history',
            'recommendations': recommendations
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error processing text emotion: {str(e)}", exc_info=True)
        return Response({
            'error': 'Failed to process text emotion',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'audio_file': openapi.Schema(type=openapi.TYPE_FILE, description='Audio file to analyze for emotion'),
        },
        required=['audio_file'],
    ),
    responses={
        200: openapi.Response('Emotion detected successfully'),
        400: openapi.Response('Invalid input'),
        500: openapi.Response('Internal server error'),
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def speech_emotion(request):
    """
    Analyze speech audio to detect emotion and get music recommendations.
    """
    try:
        logger.debug("Received speech emotion detection request")
        
        # Check if audio file is provided
        if not request.FILES:
            logger.error("No files found in request")
            return Response({'error': 'No audio file provided in request'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get the audio file from either 'audio_file' or 'file' key
        audio_key = next(iter(request.FILES), None)
        if not audio_key:
            logger.error("No file key found in request.FILES")
            return Response({'error': 'No audio file key found in request'}, status=status.HTTP_400_BAD_REQUEST)
            
        audio_file = request.FILES[audio_key]
        logger.debug(f"Using file with key: {audio_key}")
        logger.debug(f"Received audio file: {audio_file.name}, size: {audio_file.size} bytes, content type: {audio_file.content_type}")
        
        if audio_file.size == 0:
            logger.error("Empty audio file received")
            return Response({'error': 'Empty audio file'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create temporary directory if it doesn't exist
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        logger.debug(f"Using temporary directory: {temp_dir}")
        
        # Save the uploaded file temporarily with a unique name based on timestamp
        timestamp = int(time.time() * 1000)
        temp_path = os.path.join(temp_dir, f'temp_speech_{timestamp}_{audio_file.name}')
        logger.debug(f"Saving temporary file to: {temp_path}")
        
        try:
            with open(temp_path, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)
            
            # Verify the file was saved correctly
            if not os.path.exists(temp_path):
                logger.error(f"Failed to save temporary file at {temp_path}")
                return Response({'error': 'Failed to save audio file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            file_size = os.path.getsize(temp_path)
            logger.debug(f"Temporary file saved successfully, size: {file_size} bytes")
            
            if file_size == 0:
                logger.error("Saved file is empty")
                return Response({'error': 'Saved audio file is empty'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get emotion from speech
            logger.debug("Starting speech emotion detection")
            emotion = infer_speech_emotion(temp_path)
            logger.debug(f"Detected emotion: {emotion}")
            
            # Get user profile
            user_profile = UserProfile.objects.get(username=request.user.username)
            
            # Add emotion to user's mood history
            user_profile.add_mood({
                'emotion': emotion,
                'timestamp': datetime.utcnow()
            })
            logger.debug(f"Saved emotion to user history: {emotion}")
            
            # Get music recommendations
            recommendations = get_music_recommendation(emotion)
            logger.debug(f"Got {len(recommendations)} music recommendations")
            
            # Store recommendations
            for track in recommendations:
                user_profile.add_recommendation(
                    track_id=track['external_url'].split('/')[-1],
                    track_name=track['name'],
                    artist=track['artist'],
                    emotion=emotion
                )
            logger.debug("Saved recommendations to user history")
            
            return Response({
                "emotion": emotion,
                "message": "Emotion detected and saved to history",
                "recommendations": recommendations
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing audio file: {str(e)}", exc_info=True)
            return Response({
                "error": "Failed to process audio file",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    logger.debug("Cleaned up temporary audio file")
            except Exception as e:
                logger.error(f"Error cleaning up temporary file: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error in speech emotion endpoint: {str(e)}", exc_info=True)
        return Response({
            "error": "Internal server error",
            "detail": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'image': openapi.Schema(type=openapi.TYPE_FILE, description='Image file to analyze for facial emotion'),
        },
        required=['image'],
    ),
    responses={
        200: openapi.Response('Emotion detected successfully'),
        400: openapi.Response('Invalid input'),
        500: openapi.Response('Internal server error'),
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def facial_emotion(request):
    """
    Process facial image and detect emotion.
    """
    try:
        logger.debug("Received facial emotion detection request")
        logger.debug(f"Request FILES keys: {list(request.FILES.keys())}")
        logger.debug(f"Request content type: {request.content_type}")
        
        # Check if image file is provided
        if not request.FILES:
            logger.error("No files found in request")
            return Response({'error': 'No image file provided in request'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get the image file from either 'image' or 'file' key
        image_key = next(iter(request.FILES), None)
        if not image_key:
            logger.error("No file key found in request.FILES")
            return Response({'error': 'No image file key found in request'}, status=status.HTTP_400_BAD_REQUEST)
            
        image_file = request.FILES[image_key]
        logger.debug(f"Using file with key: {image_key}")
        logger.debug(f"Received image file: {image_file.name}, size: {image_file.size} bytes, content type: {image_file.content_type}")
        
        if image_file.size == 0:
            logger.error("Empty image file received")
            return Response({'error': 'Empty image file'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create temporary directory if it doesn't exist
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        logger.debug(f"Using temporary directory: {temp_dir}")
        
        # Save the uploaded file temporarily with a unique name based on timestamp
        timestamp = int(time.time() * 1000)
        temp_path = os.path.join(temp_dir, f'temp_facial_{timestamp}_{image_file.name}')
        logger.debug(f"Saving temporary file to: {temp_path}")
        
        try:
            with open(temp_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)
            
            # Verify the file was saved correctly
            if not os.path.exists(temp_path):
                logger.error(f"Failed to save temporary file at {temp_path}")
                return Response({'error': 'Failed to save image file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            file_size = os.path.getsize(temp_path)
            logger.debug(f"Temporary file saved successfully, size: {file_size} bytes")
            
            if file_size == 0:
                logger.error("Saved file is empty")
                return Response({'error': 'Saved image file is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
            # Detect emotion from the image
            logger.debug("Calling facial emotion detection model")
            detected_emotion = infer_facial_emotion(temp_path)
            logger.debug(f"Model returned emotion: {detected_emotion}")
            
            if not detected_emotion:
                logger.warning("No emotion detected, defaulting to neutral")
                detected_emotion = "neutral"
                
            logger.debug(f"Final detected emotion: {detected_emotion}")
            
            # Get music recommendations based on the detected emotion
            logger.debug(f"Getting music recommendations for emotion: {detected_emotion}")
            try:
                recommendations = get_music_recommendation(detected_emotion)
                logger.debug(f"Got {len(recommendations)} music recommendations")
            except Exception as e:
                logger.error(f"Error getting music recommendations: {str(e)}")
                logger.error(traceback.format_exc())
                recommendations = []

            # Save emotion and recommendations to user history
            try:
                user_profile = UserProfile.objects.get(username=request.user.username)
                user_profile.add_mood({
                    'emotion': detected_emotion,
                    'timestamp': datetime.utcnow()
                })
                logger.debug(f"Saved emotion to user history: {detected_emotion}")
                
                # Save recommendations to user history
                for track in recommendations:
                    user_profile.add_recommendation(
                        track_id=track['external_url'].split('/')[-1],
                        track_name=track['name'],
                        artist=track['artist'],
                        emotion=detected_emotion
                    )
                logger.debug("Saved recommendations to user history")
            except Exception as e:
                logger.error(f"Error saving to user history: {str(e)}")
                # Continue even if saving fails - we still want to return the emotion and recommendations
            
            return Response({
                'emotion': detected_emotion,
                'message': 'Emotion detected and saved to history',
                'recommendations': recommendations
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({'error': f'Failed to process image: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    logger.debug(f"Temporary file removed: {temp_path}")
            except Exception as e:
                logger.error(f"Error removing temporary file: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error in facial emotion endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return Response({
            'error': 'Failed to process facial emotion',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'emotion': openapi.Schema(type=openapi.TYPE_STRING, description='Detected emotion'),
            'market': openapi.Schema(type=openapi.TYPE_STRING, description='Market code for Spotify recommendations'),
        },
        required=['emotion'],
    ),
    responses={
        200: openapi.Response('Music recommendations generated successfully'),
        400: openapi.Response('Invalid input'),
        500: openapi.Response('Internal server error'),
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def music_recommendation(request):
    """
    Generate music recommendations based on detected emotion and save to user history.
    """
    logger.debug("Received music recommendation request")
    
    emotion = request.data.get('emotion')
    market = request.data.get('market')
    
    logger.debug(f"Requested emotion: {emotion}, market: {market}")
    
    if not emotion:
        logger.error("No emotion provided in request")
        return Response({"error": "Emotion is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get music recommendations
        logger.debug(f"Getting music recommendations for emotion: {emotion}, market: {market}")
        recommendations = get_music_recommendation(emotion, market)
        logger.debug(f"Got {len(recommendations)} music recommendations")
        
        # Save emotion and recommendations to user history
        try:
            user_profile = UserProfile.objects.get(username=request.user.username)
            # Add mood to history
            user_profile.add_mood({
                'emotion': emotion,
                'timestamp': datetime.utcnow()
            })
            logger.debug(f"Saved emotion to user history: {emotion}")
            
            # Save recommendations to user history
            for track in recommendations:
                user_profile.add_recommendation(
                    track_id=track['external_url'].split('/')[-1],
                    track_name=track['name'],
                    artist=track['artist'],
                    emotion=emotion
                )
            logger.debug("Saved recommendations to user history")
        except Exception as e:
            logger.error(f"Error saving to user history: {str(e)}")
            # Continue even if saving fails - we still want to return the recommendations
        
        return Response({
            "emotion": emotion,
            "recommendations": recommendations,
            "message": "Recommendations generated and saved to history"
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting music recommendations: {str(e)}")
        logger.error(traceback.format_exc())
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def analyze_emotion(request):
    try:
        # Get user from request
        username = request.data.get('username')
        user = user_dao.get_by_username(username)
        
        if not user:
            return Response({'error': 'User not found'}, status=404)
            
        # Get emotion from request
        emotion = request.data.get('emotion')
        
        # Record mood history
        mood_data = {
            'user_id': user[0],  # First column is id
            'mood': emotion,
            'song_id': request.data.get('song_id')
        }
        mood_history_dao.insert(mood_data)
        
        # Record listening history
        listening_data = {
            'user_id': user[0],
            'song_id': request.data.get('song_id'),
            'song_title': request.data.get('song_title'),
            'artist': request.data.get('artist'),
            'mood': emotion,
            'duration': request.data.get('duration')
        }
        listening_history_dao.insert(listening_data)
        
        return Response({
            'status': 'success',
            'message': f'Emotion {emotion} recorded for user {username}'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_user_mood_history(request, username):
    try:
        user = user_dao.get_by_username(username)
        if not user:
            return Response({'error': 'User not found'}, status=404)
            
        mood_history = mood_history_dao.get_user_mood_history(user[0])
        return Response({'mood_history': mood_history})
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_user_listening_history(request, username):
    try:
        user = user_dao.get_by_username(username)
        if not user:
            return Response({'error': 'User not found'}, status=404)
            
        listening_history = listening_history_dao.get_user_listening_history(user[0])
        return Response({'listening_history': listening_history})
        
    except Exception as e:
        return Response({'error': str(e)}, status=500) 