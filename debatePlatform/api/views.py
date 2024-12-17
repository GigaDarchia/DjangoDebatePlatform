from drf_spectacular.utils import extend_schema
from rest_framework import generics, views, viewsets, mixins
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from user.models import User
from debate.models import Debate, Argument, Category, Vote
from .serializers import UserRegisterSerializer, CategorySerializer, DebateSerializer, \
    CreateDebateSerializer, ArgumentSerializer, CreateArgumentSerializer, VoteSerializer, UserSerializer, \
    UpdateDebateSerializer, UserStatSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from .serializer_utils import SerializerFactory
from django.db import models
from .permissions import IsOwnerOrModeratorOrReadOnly
from django.db import transaction
from rest_framework.throttling import ScopedRateThrottle

"""---------------------------------   Authentication Views   ---------------------------------------"""


@extend_schema(tags=['Authentication'])
class UserRegisterView(generics.CreateAPIView):
    """

    Handles user registration by creating a new user instance.

    """
    throttle_classes = [ScopedRateThrottle]
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    throttle_scope = 'auth'

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
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = super().post(request, *args, **kwargs)
        response.data['user_id'] = serializer.user.id
        return response


@extend_schema(tags=["Authentication"])
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'token_refresh'


@extend_schema(tags=["Authentication"])
class CustomTokenBlacklistView(TokenBlacklistView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'token_blacklist'


"""---------------------------------   Debate Views   ---------------------------------------"""


@extend_schema(tags=["Categories"])
class CategoryListing(generics.ListAPIView):
    """
    Handles listing of all categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    throttle_scope = 'general'
    throttle_classes = [ScopedRateThrottle]


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
        update=UpdateDebateSerializer,
        partial_update=UpdateDebateSerializer,
        create=CreateDebateSerializer
    )
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'general'

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            permission_classes = [IsOwnerOrModeratorOrReadOnly, IsAuthenticated]
        elif self.action == "create":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


@extend_schema(tags=["Arguments"])
class ArgumentViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    This class provides a viewset for handling argument-related operations.

    ArgumentViewSet allows users to perform CRUD operations on Argument objects.
    It utilizes serializers for input/output, and permission classes to enforce
    access control. The queryset is optimized through related field selection
    and prefetching, ensuring efficient database queries.
    """

    queryset = Argument.objects.select_related('debate', 'author') \
        .prefetch_related('votes') \
        .order_by('-vote_count', '-created_at')
    serializer_class = SerializerFactory(
        default=ArgumentSerializer,
        create=CreateArgumentSerializer
    )
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'general'

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            permission_classes = [IsOwnerOrModeratorOrReadOnly, IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@extend_schema(tags=["Votes"])
class VoteView(generics.CreateAPIView):
    """
    Handles voting functionality for an argument.

    VoteView allows authenticated users to vote on an argument.
    When a vote is cast for the first time, it adds the vote.
    If a user revotes (casts a vote on an argument they have already voted for),
    their previous vote is removed. The voting also updates the vote count for
    the argument and adjusts the experience points (xp) of the argument author.
    """
    serializer_class = SerializerFactory(
        default=VoteSerializer
    )
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'vote'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        argument = serializer.validated_data['argument']

        vote = Vote.objects.filter(argument=argument, user=user).first()
        with transaction.atomic():
            if vote:
                vote.delete()
                message = "Your vote was removed!"
                Argument.objects.filter(id=argument.id).update(vote_count=models.F('vote_count') - 1)
                User.objects.filter(id=argument.author.id).update(xp=models.F('xp') - 2)
            else:
                Vote.objects.create(argument=argument, user=user)
                message = "Your vote was added!"
                Argument.objects.filter(id=argument.id).update(vote_count=models.F('vote_count') + 1)
                User.objects.filter(id=argument.author.id).update(xp=models.F('xp') + 2)

        return Response({"message": message}, status=status.HTTP_200_OK)


@extend_schema(tags=["User"])
class UserRetrieveView(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Handles the retrieval of user details.
    """
    queryset = User.objects.all()
    serializer_class = UserStatSerializer
    permission_classes = [IsOwnerOrModeratorOrReadOnly]
    throttle_scope = 'general'
    throttle_classes = [ScopedRateThrottle]
