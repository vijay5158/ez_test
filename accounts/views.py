from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate,login
from .token import create_jwt_pair_for_user
from django.http import FileResponse
from .models import CustomUser, File
from .serializers import CustomUserSerializer, ClientUserSignupSerializer, FileSerializer
from django.template.loader import get_template
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password, make_password
from ez_assignment.utils.helper import get_file_type, generate_secure_download_url
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.conf import settings
from .permissions import IsRoleOpUser, IsRoleClientUser
from django.core.signing import Signer, BadSignature

# Create your views here.


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            user = authenticate(email=email, password=password)
            
            if user is not None:

                login(request,user)
                serialized = CustomUserSerializer(user)
                tokens = create_jwt_pair_for_user(user)
                response = {'access_token': tokens["access"],
                            'refresh_token': tokens["refresh"], 
                            'user_data': serialized.data,
                            'status':True
                            }
                return Response(response, status=status.HTTP_200_OK)

            else:
                return Response({"message": "Invalid email or password","status":False}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": "Something wrong happend!","status":False}, status=status.HTTP_400_BAD_REQUEST)


class FileUploadAPIView(APIView):
    permission_classes = [IsAuthenticated, IsRoleOpUser]

    def post(self,request):
        try:
            files = request.FILES
            file = files.get('file', None)
            if not file or not file:
                return Response({"message": "File required!","status":False}, status=status.HTTP_400_BAD_REQUEST)

            if file.name == '':
                return Response({'message': 'No file selected for uploading', 'status': False}, status=status.HTTP_400_BAD_REQUEST)
        
            file_type = get_file_type(file.name)

            if not file_type:
                return Response({'msg': 'Unsupported file type !', 'status': False}, status=status.HTTP_400_BAD_REQUEST)

            file_obj = File.objects.create(user=request.user, file=file, file_type=file_type)
            serializer = FileSerializer(file_obj)

            return Response({"message": "File uploaded successfully!","status":True, "data": serializer.data}, status=status.HTTP_201_CREATED)

        except:
            return Response({"message": "Something wrong happend!","status":False}, status=status.HTTP_400_BAD_REQUEST)

class ClientUserSignupAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format='json'):
        try:
            data = request.data
            serializer = ClientUserSignupSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                
                token = user.signup_token

                # Send an email with the token link to the user
                # subject = 'Activate Your Account'
                # message = f'Click the following link to activate your account: {request.build_absolute_uri(f'/api/client-verify/{token}/')}'
                # from_email = 'help@ez.com'
                # recipient_list = [user.email]
                
                # send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                
                return Response({"url":f"{request.build_absolute_uri(f'/api/client-verify/{token}/')}", "status": True}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
            

        except:
            return Response({"message": "Something wrong happend!","status":False}, status=status.HTTP_400_BAD_REQUEST)

class ClientUserSignupVerifyAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, token, format='json'):

        try:
            signer = Signer()
            unsigned_token = signer.unsign(token)
            if not unsigned_token:
                return Response({"message": "Invalid url!","status":False}, status=status.HTTP_400_BAD_REQUEST)

            user = CustomUser.objects.get(signup_token=token)
            user.is_active = True
            user.signup_token = None
            user.save()

            return Response({"message":"Your account has been activated.", "status": True}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": "Something wrong happend!","status":False}, status=status.HTTP_400_BAD_REQUEST)

class ListFileAPIView(APIView):
    permission_classes = [IsAuthenticated, IsRoleClientUser]

    def get(self,request):
        try:

            files = File.objects.order_by("created_at").all()
            serializer = FileSerializer(files, many=True)
            return Response({"message":"Got All Data.", "data": serializer.data, "status": True}, status=status.HTTP_200_OK)

        except:
            return Response({"message": "Something wrong happend!","status":False}, status=status.HTTP_400_BAD_REQUEST)

class GetFileUrlAPIView(APIView):
    permission_classes = [IsAuthenticated, IsRoleClientUser]

    def get(self,request, file_id):
        try:
            try:
                file = File.objects.get(pk=file_id)
                secure_url = generate_secure_download_url(file, request.user)

                return Response({"secure_url": f"{request.build_absolute_uri(f'/api/download-file/{secure_url}/')}"}, status=status.HTTP_202_ACCEPTED)


            except File.DoesNotExist:
                return Response({"message": "File Doesn't exists!","status":False}, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({"message": "Something wrong happend!","status":False}, status=status.HTTP_400_BAD_REQUEST)

class DownloadFileAPIView(APIView):
    permission_classes = [IsAuthenticated, IsRoleClientUser]

    def post(self, request, signed_url):
        signer = Signer()
        try:

            file_data = signer.unsign(signed_url)
            file_id, user_id = map(int, file_data.split(':'))
            file = File.objects.get(pk=file_id)
            if user_id != request.user.pk:
                return Response({"message": "You are not authorized!", "status":False}, status=status.HTTP_401_UNAUTHORIZED)

            response = FileResponse(file.file, as_attachment=True, filename=file.file.name)
            return response
        
        except BadSignature:
            return Response({"message": "Invalid secure URL", "status":False}, status=status.HTTP_400_BAD_REQUEST)
        
        except File.DoesNotExist:
            return Response({"message": "File not found", "status":False}, status=status.HTTP_404_NOT_FOUND)
        
        except:
            return Response({"message": "Something wrong happend!","status":False}, status=status.HTTP_400_BAD_REQUEST)