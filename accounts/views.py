from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer,ChangePasswordSerializer,AddressSerializer,SetDefaultAddressSerializer,ForgotPasswordSerializer,ResetPasswordSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework import status, generics
from .models import Address
from .services import create_address,update_address,set_default_address,request_admin_password_reset,reset_admin_password




class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self,request):
        # 1. Serializer create
        serializer = RegisterSerializer(data=request.data)
        # 2. Validate requested data
        
        if not serializer.is_valid():
            
            return Response(
                {
                    
                    "success":False,
                    "error":serializer.errors
                },
                status = status.HTTP_400_BAD_REQUEST
                
            )
            
       
        user = serializer.save()
        
        
        # 4. Return response
        
        return Response(
            {
                "success": True,
                "message": "User registered successfully",
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            },
            status=status.HTTP_201_CREATED
        )
        
class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes  = []
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data,context={"request":request})
        
        if not serializer.is_valid():
            return Response(
                {
                    "success":False,
                    "error": serializer.errors,
                },
                status = status.HTTP_401_UNAUTHORIZED  ,
            )
            
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
       
        return Response(
            
            {
                
                "success": True,
                "message" : "Login successful",
                "data":{
                    "id": user.id,
                    "email":user.email,
                    "first_name":user.first_name,
                    "last_name":user.last_name,
                    "role":user.role
                },
                "tokens":{
                    "access":str(refresh.access_token),
                    "refresh": str(refresh),
                }
                
            },
            status= status.HTTP_200_OK
        )
        
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {
                    'success':False,
                    'error': 'refresh token is required'
                },
                status = status.HTTP_400_BAD_REQUEST
                
            )
        try:
            token = RefreshToken(refresh_token)
            
            if str(token['user_id']) != str(request.user.id):
                return Response(
                    {
                        "success": False,
                        "error": "This token does not belong to the logged-in-user"
                    },
                    status = status.HTTP_403_FORBIDDEN
                )
            token.blacklist()
            
            return Response(
                {
                    "success" : True,
                    "message":"Logout successful"
                },
                status = status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {
                    "success": False,
                    "error": "Invalid or expired token"
                },
                status = status.HTTP_400_BAD_REQUEST
            )
            
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class  = ProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get","patch","head","options"]
    
    def get_object(self):
        return self.request.user
        
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "error": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = request_admin_password_reset(
            email=serializer.validated_data["email"]
        )
        return Response(result, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "error": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reset_admin_password(
            uid=serializer.validated_data["uid"],
            token=serializer.validated_data["token"],
            new_password=serializer.validated_data["new_password"],
        )
        return Response(
            {
                "success": True,
                "message": "Password reset successful. Please login again.",
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request":request},)
        
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "error":serializer.errors
                },
                status = status.HTTP_400_BAD_REQUEST
            )
            
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=["password","updated_at"])
        return Response(
            {
            "success":True,
            "message": "Passsword changes successfully, Please login again."
           },
            status = status.HTTP_200_OK
        )
class AddressListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    def get_queryset(self):
        return Address.objects.filter(
            user=self.request.user
        ).order_by(
            "-is_default_shipping",
            "-is_default_billing",
            "-created_at",
            
        )
        
    def perform_create(self,serializer):
        address = create_address(
            user=self.request.user,
            validated_data = serializer.validated_data
            )
        
        serializer.instance=address


class AddressRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    http_method_names =  ["get","patch","delete","head","options"]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_update(self,serializer):
        address = update_address(
            user=self.request.user,
            address=serializer.instance,
            validated_data = serializer.validated_data,
        )

        serializer.instance=address

class SetDefaultAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,pk):
        serializer = SetDefaultAddressSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success":False,
                    "error":serializer.errors,
                },
                status = status.HTTP_400_BAD_REQUEST,
            )

        try:
            address = Address.objects.get(pk=pk,user=request.user)
        except Address.DoesNotExist:
            return Response(
                {
                "success": False,
                "error":"Address not found",
                },
                status = status.HTTP_404_NOT_FOUND,
            )
    

        address = set_default_address(
            user=request.user,
            address = address,
            kind = serializer.validated_data["kind"]
        )

        return Response({
            "success": True,
            "message":"Default address updated",
            "data":AddressSerializer(address).data,

        },
        status = status.HTTP_200_OK,
        )
