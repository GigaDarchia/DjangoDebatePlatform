from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from debate.models import Category, Debate, Argument, Vote
from user.models import User

"""-------------------   Authentication Serializers   -------------------"""


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer class for handling user registration.

    This serializer is used for creating a new User instance. It includes validation
    for ensuring password consistency, email uniqueness, and username uniqueness.

    :ivar username: Field for the username of the user, limited to 100 characters.
    :type username: serializers.CharField
    :ivar email: Field for the email address of the user.
    :type email: serializers.EmailField
    :ivar password: Field for the user's password.
    :type password: serializers.CharField
    :ivar confirm_password: Field to confirm the password during registration
        (write-only).
    :type confirm_password: serializers.CharField
    """

    username = serializers.CharField(
        max_length=100,
        error_messages={
            'required': _('Username field is required.')
        }
    )
    email = serializers.EmailField(
        error_messages={
            'required': _('Email field is required.')
        }
    )
    password = serializers.CharField(
        error_messages={
            'required': _('Password field is required.')
        }
    )
    confirm_password = serializers.CharField(
        write_only=True,
        error_messages={
            'required': _('Confirm Password field is required.')
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password')
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True}
        }

    def validate(self, data):
        confirm_password = data.pop('confirm_password', None)
        if data['password'] != confirm_password:
            raise serializers.ValidationError(
                {
                    "password": _("Passwords do not match.")
                }
            )

        validate_password(data['password'])

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {
                    "email": _("Email already exists.")
                }
            )

        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                {
                    "username": _("Username already exists.")
                }
            )
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login information.

    This serializer is responsible for validating and handling user login
    credentials, specifically the username and password provided by the user
    during authentication.

    :ivar username: The unique identifier for the user.
    :type username: serializers.CharField
    :ivar password: The password corresponding to the username.
    :type password: serializers.CharField
    """

    username = serializers.CharField(required=True, max_length=100)
    password = serializers.CharField(required=True, write_only=True)


"""-------------------   User Serializers   -------------------"""


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'xp', 'level', 'wins')


class UserStatSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model including specific fields.
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'xp', 'level', 'wins')


"""-------------------   Debate Serializers   -------------------"""


class CategorySerializer(serializers.ModelSerializer):
    """
    Handles serialization and deserialization of Category model instances.
    """

    class Meta:
        model = Category
        fields = '__all__'


class ArgumentSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Argument model.
    """

    class Meta:
        model = Argument
        fields = "__all__"


class DebateArgumentSerializer(serializers.ModelSerializer):
    """
    Handles the serialization of Argument model instances only for the DebateSerializer class.
    """

    class Meta:
        model = Argument
        fields = ['id', 'text', 'vote_count', 'side', 'created_at', 'winner', 'author']


class CreateArgumentSerializer(serializers.ModelSerializer):
    """
    Serializer class for the `Argument` model to handle the creation of new instances.
    """

    class Meta:
        model = Argument
        fields = ('text', 'side', 'debate')

    def validate(self, data):
        debate = data.get('debate')
        if debate.status != "Ongoing":
            raise serializers.ValidationError({"debate": "Arguments can only be submitted while the debate is ongoing."})
        return data


class DebateSerializer(serializers.ModelSerializer):
    """
    Handles the serialization of Debate model objects for data exchange purposes.

    This serializer is used to convert Debate instances to and from JSON as part
    of the application's API. It supports nested serialization for related fields,
    ensuring that complex data relationships are properly represented in API
    responses.
    """

    participants = UserStatSerializer(many=True, default=list)
    author = UserStatSerializer()
    category = CategorySerializer()
    debate_arguments = DebateArgumentSerializer(many=True, default=list)

    class Meta:
        model = Debate
        fields = ['id', 'title', 'description', 'category', 'author', 'created_at', 'start_time', 'end_time',
                  'status', 'participants', 'debate_arguments']


class CreateDebateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a Debate object.

    Provides validation and serialization for the Debate model, ensuring data integrity
    and enforcing specific business rules related to start and end times.
    """

    class Meta:
        model = Debate
        fields = ("title", "description", "category", "start_time", "end_time")

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        if start_time >= end_time:
            raise serializers.ValidationError({"start_time": "Start time must be before end time."})

        if start_time <= timezone.now():
            raise serializers.ValidationError({"start_time": "Start time must be in the future."})

        return data


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['argument']

    def validate(self, data):
        argument = data.get('argument')
        if argument.debate.status != "Ongoing":
            raise serializers.ValidationError({"debate": "Arguments can only be voted while the debate is ongoing."})
        return data
