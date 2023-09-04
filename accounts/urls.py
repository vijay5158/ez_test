from django.urls import path

from .views import UserLoginView, FileUploadAPIView, ClientUserSignupAPIView, ClientUserSignupVerifyAPIView, ListFileAPIView, GetFileUrlAPIView, DownloadFileAPIView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name="user_login"),
    path('file-upload/', FileUploadAPIView.as_view(), name="file_upload"),
    path('client-signup/', ClientUserSignupAPIView.as_view(), name="client_signup"),
    path('client-verify/<str:token>/', ClientUserSignupVerifyAPIView.as_view(), name="client_verify"),
    path('list-file/', ListFileAPIView.as_view(), name="list_files"),
    path('get-file-url/<int:file_id>/', GetFileUrlAPIView.as_view(), name="get_file_url"),
    path('download-file/<str:signed_url>/', DownloadFileAPIView.as_view(), name="download_file"),
]