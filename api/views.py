from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from .models import ModelProfile, ContactMessage, ClientProfile
from .serializers import (
    ModelProfileSerializer, 
    ContactMessageSerializer,
    SignupSerializer,
    UserSerializer
)

# ==============================================
# VIEW 1: MODEL PROFILE API
# Job: List all models + their photos for React
# GET /api/models/ → returns all ModelProfile objects
# ==============================================
class ModelProfileViewSet(viewsets.ModelViewSet):
    queryset = ModelProfile.objects.all().prefetch_related('photos')
    serializer_class = ModelProfileSerializer

# ==============================================
# VIEW 2: CONTACT FORM SUBMIT - EXISTING
# Job: Save contact message + send email to admin
# POST /api/contact/ → creates ContactMessage
# ==============================================
@api_view(['POST'])
def contact_create(request):
    serializer = ContactMessageSerializer(data=request.data)
    
    if serializer.is_valid():
        # 1. Save to database first
        contact = serializer.save()
        
        # 2. Send email notification to you
        subject = f"New {contact.inquiry_type} inquiry from {contact.name}"
        message = f"""
New contact form submission!

Name: {contact.name}
Email: {contact.email}
Phone: {contact.phone or 'Not provided'}
Inquiry Type: {contact.inquiry_type}
Submitted: {contact.created_at}

Message:
{contact.message}

---
View in admin: http://127.0.0.1:8000/admin/api/contactmessage/
        """
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False
            )
        except Exception as e:
            print(f"Email error: {e}")
        
        return Response(
            {'message': 'Message sent successfully'}, 
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==============================================
# VIEW 3: SIGNUP API - NEW
# Job: Create new user account
# POST /api/signup/ → {username, email, password, password2, first_name, last_name, phone}
# Returns: user info + JWT tokens
# ==============================================
class SignupAPI(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Account created successfully'
        }, status=status.HTTP_201_CREATED)

# ==============================================
# VIEW 4: LOGIN API - NEW
# Job: Authenticate user + return JWT tokens
# POST /api/login/ → {username, password}
# Returns: user info + JWT tokens
# ==============================================
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Login successful'
        })
    else:
        return Response(
            {'error': 'Invalid username or password'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

# ==============================================
# VIEW 5: USER DASHBOARD API - NEW
# Job: Show logged-in user's info + their messages
# GET /api/dashboard/ → requires JWT token in header
# ==============================================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_api(request):
    user = request.user
    
    user_messages = ContactMessage.objects.filter(user=user).order_by('-created_at')
    messages_serializer = ContactMessageSerializer(user_messages, many=True)
    
    return Response({
        'user': UserSerializer(user).data,
        'messages': messages_serializer.data,
        'message': f'Welcome back, {user.first_name or user.username}!'
    })

# ==============================================
# VIEW 6: UPDATE PROFILE API - NEW
# Job: Update logged-in user's profile + avatar
# PUT /api/update-profile/ → requires JWT token + FormData
# ==============================================
class UpdateProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        client_profile = user.client_profile

        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        client_profile.phone = request.data.get('phone', client_profile.phone)

        if 'avatar' in request.FILES:
            client_profile.avatar = request.FILES['avatar']

        user.save()
        client_profile.save()

        return Response({
            'user': UserSerializer(user).data,
            'message': 'Profile updated successfully'
        }, status=status.HTTP_200_OK)

# ==============================================
# VIEW 7: DELETE ACCOUNT API - NEW
# Job: Delete logged-in user account + all data
# DELETE /api/delete-account/ → requires JWT token
# ==============================================
class DeleteAccountAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        # Deletes User + ClientProfile + all ContactMessages due to CASCADE
        user.delete()
        return Response(
            {'message': 'Account deleted successfully'}, 
            status=status.HTTP_204_NO_CONTENT
        )