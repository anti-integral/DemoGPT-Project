from inspect import stack
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from gpt.models import User
from serializers import (
    UserRegistgrationSerializer,
    UserLoginSerializer,
    UserChangePasswordSerializer,
    UserProfileSerializer,
)
from django.contrib.auth import authenticate
from gpt.services.create_token import get_tokens_for_user
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication


class UserRegistrationView(APIView):
    # permission_classes = [IsAdminUser]
    # authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = UserRegistgrationSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response(
                {
                    "token": tokens,
                    "message": "User registered successfully",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "message": "User registered failed",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserLoginView(APIView):
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get("email")
            password = serializer.data.get("password")

            user = authenticate(email=email, password=password)
            if user is not None:
                tokens = get_tokens_for_user(user)
                return Response(
                    {"token": tokens, "msg": "Login Success"}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "errors": {
                            "non_field_errors": ["Email or Password is not Valid"]
                        }
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"msg": "Password Changed Successfully"}, status=status.HTTP_200_OK
        )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"msg": "Password Changed Successfully"}, status=status.HTTP_200_OK
        )
