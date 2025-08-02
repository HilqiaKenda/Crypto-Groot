from django.http import JsonResponse
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView, DestroyAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import LoginSerializer, UserSerializer, RegisterUserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken

# User views (list only for demonstration)
class UserInfoView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class RegisterUserView(CreateAPIView):
    serializer_class = RegisterUserSerializer
    

class LoginView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        # generate user token
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)

            access_token = str(refresh.access_token)
            response = Response(
                {
                    "user": UserSerializer(user).data
                }, status=status.HTTP_200_OK
            )

            response.set_cookie(key="access_token", 
                                value=access_token, 
                                httponly=True, 
                                secure=True, 
                                samesite="Strict"
            )

            response.set_cookie(key="refresh_token", 
                                value=refresh, 
                                httponly=True,
                                secure=True,
                                samesite="Strict"
            )
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refres_token")

        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                refresh.blacklist()
            except Exception as exce:
                return Response({"error": "ivalidating token: "+ str(exce)})
            
        response = Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
    

class CookierefreshToken(TokenRefreshView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"error": "Refresh token not provided"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh_token)
            response = Response({"message": "Acces token refresh successfully"}, status=status.HTTP_200_OK)

            response.set_cookie("access_token", 
                                value=access_token,
                                httponly=True,
                                secure=True,
                                samesite="Strick")
            return response
        
        except InvalidToken as exce:
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED) 