import requests
import os
import json

def test_speech_emotion():
    # API endpoint
    url = 'http://127.0.0.1:8000/api/speech_emotion/'
    
    # Path to your test audio file
    audio_file_path = os.path.join('audio_test', 'love_song.mp4')
    
    # Check if file exists
    if not os.path.exists(audio_file_path):
        print(f"Error: File {audio_file_path} does not exist")
        return
    
    # Get the file size
    file_size = os.path.getsize(audio_file_path)
    print(f"Testing with file: {audio_file_path}")
    print(f"File size: {file_size} bytes")
    
    # Prepare the file for upload
    files = {
        'audio_file': ('love_song.mp4', open(audio_file_path, 'rb'), 'video/mp4')
    }
    
    try:
        # Make the request
        print("\nSending request to server...")
        response = requests.post(url, files=files)
        
        # Print response
        print(f"\nStatus Code: {response.status_code}")
        print("\nResponse:")
        print(json.dumps(response.json(), indent=2))
        
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        # Close the file
        files['audio_file'][1].close()

if __name__ == "__main__":
    test_speech_emotion() 