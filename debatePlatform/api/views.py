from django.contrib.auth import authenticate, login
from drf_spectacular.utils import extend_schema
from rest_framework import generics, views, viewsets, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from user.models import User
from .serializers import UserRegisterSerializer, UserLoginSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

"""-------------------   Authentication Views   -------------------"""


@extend_schema(tags=['Authentication'])
class UserRegisterView(generics.CreateAPIView):
    """

    Handles user registration by creating a new user instance.

    """
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Authentication'])
class UserLoginView(TokenObtainPairView):
    """
    Handles the user login and token generation process.

    Provides an endpoint for users to log in and obtain authentication tokens. This view
    extends the functionality of `TokenObtainPairView`. Upon successful login, it adds the
    user's ID to the response data, allowing the client to link the token to a specific user.

    """
    serializer_class = TokenObtainPairView.serializer_class

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = super().post(request, *args, **kwargs)
        response.data['user_id'] = serializer.user.id
        return response


@extend_schema(tags=["Authentication"])
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [IsAuthenticated]


@extend_schema(tags=["Authentication"])
class CustomTokenBlacklistView(TokenBlacklistView):
    permission_classes = [IsAuthenticated]
