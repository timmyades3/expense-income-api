from django.conf import settings
from django.shortcuts import render, redirect
from rest_framework import generics 
from authentication.renderers import UserRender
from .serializers import LogoutSerializer, RegisterSerializer,EmailVerificationSerializer,LoginSerializer, ResetPasswordEmailRequsetSerializer,SetNewPasswordSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema 
from drf_yasg import openapi
from rest_framework import permissions
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.http import HttpResponseRedirect
from decouple import config
# Create your views here.


class CustomRedirect(HttpResponseRedirect):
    allowed_schemes=[config('APP_SCHEME'),'http','https']


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    renderer_classes = (UserRender,)

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        
        user = User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')
        absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
        email_body = 'hi ' + user.username + ' use link bellow to verify your email \n' + absurl
        data = {'email_body':email_body, 'to_email':user.email, 'email_subject':"verify your email"}
        Util.send_email(data)
        return Response(user_data, status=status.HTTP_201_CREATED)
    

class VerifyEmail(APIView):
    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter('token',in_=openapi.IN_QUERY,description='description',type=openapi.TYPE_STRING)
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self,request):
        token = request.GET.get('token')
        print(settings.SECRET_KEY)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id = payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'message':'Email successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:   
            return Response({'error':'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:   
            return Response({'error':'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        

class LoginApiView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    renderer_classes = (UserRender,)
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequsetSerializer

    def post(self, request):
        serializer = self.serializer_class(data = request.data)
        email = request.data['email']
        if User.objects.filter(email = email).exists():
            user = User.objects.get(email = email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request).domain
            relativeLink = reverse('password-reset-confirm',kwargs={'uidb64': uidb64, 'token':token })
            absurl = 'http://'+current_site+relativeLink
            redirect_url= request.data.get('redirect_url', '')    
            email_body = 'hello, \n use link bellow to reset your password \n' + absurl+"?redirect_url="+redirect_url
            data = {'email_body':email_body, 'to_email':user.email, 'email_subject':"Reset your password"}
            Util.send_email(data)       
        return Response({"success": "we have sent you the link to reset your password"}, status=status.HTTP_200_OK)

class PasswordTokenCheckApiView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url+'?token_valid=False')
                else:
                    return CustomRedirect(config('FRONTEND_URL', '')+'?token_valid=False')

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(redirect_url+'?token_valid=True&message=Credentials Valid&uidb64='+uidb64+'&token='+token)
            else:
                return CustomRedirect(config('FRONTEND_URL', '')+'?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url+'?token_valid=False')
                    
            except UnboundLocalError as e:
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self,request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        return Response({'success':True, 'message':'Password reset success', },status=status.HTTP_200_OK)

class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    # permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message':'You have logged out successfully'},status=status.HTTP_204_NO_CONTENT)