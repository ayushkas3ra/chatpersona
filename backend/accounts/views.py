from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer

@api_view(["POST"])
@permission_classes([AllowAny])
def Register_view(request):
    serializer = RegisterSerializer(data = request.data)

    serializer.is_valid(raise_exception=True)

    user = serializer.save()

    return Response(
        {
            "id": user.id,
            "username": user.username
        },
        status = status.HTTP_201_CREATED
    )

@api_view(["POST"])
@permission_classes([AllowAny])
def Login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(
        request,
        username = username,
        password = password
    )

    if user is None:
        return Response(
            {
                "error" : "Invalid username or password"
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    login(request, user)

    return Response(
        {
            "message":"login successful",
            "username":user.username
         }
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def Logout_view(request):
    logout(request)

    return Response(
        {
            "message":"Logged out successfully"
        }
    )