from django.urls import path
from .emotion_views import text_emotion, speech_emotion, facial_emotion, music_recommendation
from .user_views import register, login

urlpatterns = [
    # User endpoints
    path('users/register/', register, name='register'),
    path('users/login/', login, name='login'),
    
    # Emotion endpoints
    path('text_emotion/', text_emotion, name='text_emotion'),
    path('speech_emotion/', speech_emotion, name='speech_emotion'),
    path('facial_emotion/', facial_emotion, name='facial_emotion'),
    path('music_recommendation/', music_recommendation, name='music_recommendation'),
]
