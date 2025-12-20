"""
API Views for authentication
Returns responses matching frontend expectations
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register a new user
    
    Expected input: {name, email, password, confirm_password, role}
    Returns: {success, message, user, token} OR {success: false, message, errors}
    """
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            user_data = UserSerializer(user).data
            
            return Response({
                'success': True,
                'message': 'Registration successful',
                'user': user_data,
                'token': tokens['access'],
                'refresh': tokens['refresh']
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Registration failed',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validation errors
    error_messages = {}
    for field, errors in serializer.errors.items():
        error_messages[field] = errors[0] if isinstance(errors, list) else errors
    
    # Create a user-friendly message
    first_error = next(iter(serializer.errors.values()))
    main_message = first_error[0] if isinstance(first_error, list) else str(first_error)
    
    return Response({
        'success': False,
        'message': main_message,
        'errors': error_messages
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login user
    
    Expected input: {email, password}
    Returns: {success, message, user, token} OR {success: false, message}
    """
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'message': 'Please provide valid email and password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    # Authenticate user
    user = authenticate(request, username=email, password=password)
    
    if user is not None:
        if user.is_active:
            tokens = get_tokens_for_user(user)
            user_data = UserSerializer(user).data
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'user': user_data,
                'token': tokens['access'],
                'refresh': tokens['refresh']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Account is disabled'
            }, status=status.HTTP_403_FORBIDDEN)
    else:
        return Response({
            'success': False,
            'message': 'Invalid email or password'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def verify_token_view(request):
    """
    Verify if the token is valid and return user data
    
    Requires: Authorization header with Bearer token
    Returns: {success, user}
    """
    user = request.user
    user_data = UserSerializer(user).data
    
    return Response({
        'success': True,
        'user': user_data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def logout_view(request):
    """
    Logout user (optional - mainly for token blacklisting if needed)
    
    Returns: {success, message}
    """
    try:
        # If you want to implement token blacklisting, do it here
        # For now, just return success (token expiry handles logout)
        return Response({
            'success': True,
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)