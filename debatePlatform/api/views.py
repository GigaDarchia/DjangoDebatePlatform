from django.contrib.auth import authenticate, login
from drf_spectacular.utils import extend_schema
from rest_framework import generics, views, viewsets, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from user.models import User
from debate.models import Debate, Argument, Category, Vote
from .serializers import UserRegisterSerializer, UserLoginSerializer, CategorySerializer, DebateSerializer, \
    CreateDebateSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from .serializer_utils import SerializerFactory
from django.db import models
from .permissions import IsOwnerOrReadOnly

"""---------------------------------   Authentication Views   ---------------------------------------"""


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


"""---------------------------------   Debate Views   ---------------------------------------"""


@extend_schema(tags=["Categories"])
class CategoryListing(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


@extend_schema(tags=["Debates"])
class DebateViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD functionality for managing Debate instances.

    This class leverages Django REST Framework's ModelViewSet to offer full
    CRUD operations for the Debate model. It supports custom serializers
    for different actions, handles dynamic permissions based on actions,
    and annotates the queryset for additional data. This class is
    customized to ensure that debates are created with the correct author
    and appropriate permissions are enforced based on the action.
    """
    queryset = Debate.objects.select_related('category', 'author') \
        .prefetch_related('participants', 'debate_arguments') \
        .annotate(participant_count=models.Count('participants')) \
        .order_by('-participant_count', '-created_at')

    serializer_class = SerializerFactory(
        default=DebateSerializer,
        create=CreateDebateSerializer
    )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
        elif self.action == "list":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
