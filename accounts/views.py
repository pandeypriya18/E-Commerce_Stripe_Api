from accounts.models import MyUser
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from accounts.serializers import RegisterSerializer,LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

class RegisterView(APIView):

  def post(self, request):
     serializer = RegisterSerializer(data = request.data)
     if serializer.is_valid():
        user = serializer.create_user(serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
     return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
   serializer_class = LoginSerializer
   def post(self ,request):
      serializer = self.serializer_class(data=request.data)
      if serializer.is_valid():
         user = serializer.validated_data["user"]

         refresh = RefreshToken.for_user(user)

         return Response({"message":"Login successful.", "refresh": str(refresh), "access": str(refresh.access_token)}, status=status.HTTP_200_OK)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_200_OK
            )

        except TokenError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

