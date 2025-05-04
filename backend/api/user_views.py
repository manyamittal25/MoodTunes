from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from dal import UserDAO
import hashlib

user_dao = UserDAO()

@api_view(['POST'])
def register(request):
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        # Check if user already exists
        if user_dao.get_by_username(username):
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user_dao.get_by_email(email):
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Create user
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash
        }
        user_id = user_dao.insert(user_data)

        return Response({
            'message': 'User registered successfully',
            'user_id': user_id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def login(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')

        # Get user
        user = user_dao.get_by_username(username)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Verify password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != user[3]:  # password_hash is the 4th column
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)

        # Update last login
        user_dao.update_last_login(user[0])

        return Response({
            'message': 'Login successful',
            'user_id': user[0],
            'username': user[1],
            'email': user[2]
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 