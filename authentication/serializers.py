"""
Serializers for authentication API
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
import re

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - matches frontend expectations"""
    
    # Convert UUID to string for frontend
    id = serializers.UUIDField(format='hex_verbose', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role']
        read_only_fields = ['id']
    
    def to_representation(self, instance):
        """Ensure id is returned as string"""
        representation = super().to_representation(instance)
        representation['id'] = str(instance.id)
        return representation


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    Matches frontend data: name, email, password, confirm_password, role
    """
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="A user with this email already exists.")]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    name = serializers.CharField(required=True, max_length=255)
    role = serializers.ChoiceField(choices=['student', 'teacher'], default='student')
    
    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'confirm_password', 'role']
    
    def validate_name(self, value):
        """Validate name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value.strip()
    
    def validate_email(self, value):
        """Validate email"""
        return value.lower().strip()
    
    def validate_password(self, value):
        """Validate password with custom rules matching frontend"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        # Check for uppercase, lowercase, and number
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number.")
        
        return value
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs
    
    def create(self, validated_data):
        """Create user"""
        # Remove confirm_password as it's not needed
        validated_data.pop('confirm_password')
        
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            role=validated_data.get('role', 'student')
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    Matches frontend data: email, password
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_email(self, value):
        """Normalize email"""
        return value.lower().strip()