from django.urls import path
from .views import RegisterView, UploadFileView, ListFilesView, DownloadFileView, TestEncryptionView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('token/', TokenObtainPairView.as_view()),       
    path('token/refresh/', TokenRefreshView.as_view()),
    path('upload/', UploadFileView.as_view()),
    path('files/', ListFilesView.as_view()),
    path("download/", DownloadFileView.as_view()),
    path("test-encryption/", TestEncryptionView.as_view()),

]
