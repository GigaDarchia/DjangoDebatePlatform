from rest_framework import generics, views, viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from user.models import User
from .serializers import UserRegisterSerializer

class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "User registered successfully."},
            status=status.HTTP_201_CREATED
        )