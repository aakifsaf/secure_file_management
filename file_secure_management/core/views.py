from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import FileUpload
from rest_framework.response import Response
from rest_framework import permissions, status
from .serializers import RegisterSerializer, FileUploadSerializer
from .models import FileUpload
from django.core.files.base import ContentFile
from .utils import FileEncryptor
import base64
from django.http import HttpResponse

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListFilesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        files = FileUpload.objects.filter(user=request.user)
        return Response(FileUploadSerializer(files, many=True).data)


class UploadFileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        file = request.FILES.get('file')
        
        if not file:
            return Response({'error': 'File is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            key = FileEncryptor.generate_key()
            
            file_content = file.read()
            encrypted_data = FileEncryptor.encrypt_file(file_content, key)
            
            # Create encrypted file with proper name
            encrypted_content = base64.b64decode(encrypted_data['encrypted_content'])
            encrypted_file = ContentFile(
                encrypted_content,
                name=f"{file.name}.enc"  # Add .enc extension to indicate encrypted file
            )
            
            file_obj = FileUpload.objects.create(
                user=request.user,
                original_file_name=file.name,
                encrypted_file=encrypted_file,
                encryption_key=encrypted_data['key'],
                file_size=file.size
            )
            
            return Response({
                'id': file_obj.id,
                'file_name': file.name,
                'size': file.size,
                'encrypted': True
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Upload error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DownloadFileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file_id = request.data.get('file_id')

        if not file_id:
            return Response({'error': 'File ID is required'}, status=400)

        try:
            file_obj = FileUpload.objects.get(id=file_id, user=request.user)

            encrypted_bytes = file_obj.encrypted_file.read()

            encrypted_data = {
                'encrypted_content': base64.b64encode(encrypted_bytes).decode('utf-8')
            }

            decrypted = FileEncryptor.decrypt_file(
                encrypted_data,
                file_obj.encryption_key
            )

            response = HttpResponse(decrypted, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{file_obj.original_file_name}"'
            return response

        except FileUpload.DoesNotExist:
            return Response({'error': 'File not found'}, status=404)
        except Exception as e:
            print(f"Download error: {str(e)}")
            return Response({'error': f'Decryption failed: {str(e)}'}, status=500)

class TestEncryptionView(APIView):
    def post(self, request):
        try:
            test_data = b"Test file content"
            key = FileEncryptor.generate_key()
            
            encrypted = FileEncryptor.encrypt_file(test_data, key)
            
            decrypted = FileEncryptor.decrypt_file(
                {'encrypted_content': encrypted['encrypted_content']},
                encrypted['key']
            )
            
            return Response({
                'success': True,
                'original': test_data.decode('utf-8'),
                'decrypted': decrypted.decode('utf-8')
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)