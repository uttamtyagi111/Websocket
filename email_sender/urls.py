from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  SendEmailsView, SubjectFileList, UploadedFileDetails,UploadedFileList,UpdateUploadedFile,EmailStatusAnalyticsView,UserContactListView,DeleteContactListView
from . import views
from .views import CampaignListView,UploadedFileDetails,UploadedFileDelete,SubjectFileUploadView,SubjectFileList,DeleteSubjectFile,SubjectFileDetail,SubjectFileUpdateView
from .views import UploadHTMLToS3,EmailStatusByDateRangeView,ContactUploadView,CampaignView,ContactListView,ContactFileUpdateView,ContactUnsubscribeView,SubjectFileRowDeleteView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('send-emails/', SendEmailsView.as_view(), name='send-emails'),
    path('smtp-servers/', views.smtp_servers_list, name='smtp-servers-list'),
    path('smtp-servers/<int:pk>/', views.smtp_server_detail, name='smtp-server-detail'),
    path('smtp-server/create/', views.smtp_server_create, name='smtp-server-create'),
    path('smtp-servers/edit/<int:pk>/', views.smtp_server_edit, name='smtp-server-edit'),
    path('smtp-servers/delete/<int:pk>/', views.smtp_server_delete, name='smtp-server-delete'),
    path('upload-html/', UploadHTMLToS3.as_view(), name='upload-html'),
    path('uploaded-files/<int:file_id>/', UploadedFileDetails.as_view(), name='uploaded-file-detail'),
    path('uploaded-files/', UploadedFileList.as_view(), name='uploaded-file-list'),
    path('uploaded-files/update/<int:file_id>/', UpdateUploadedFile.as_view(), name='update-uploaded-file'),
    path('uploaded-files/<int:file_id>/delete/', UploadedFileDelete.as_view(), name='uploaded-file-delete'),
    path('email-status-analytics/',EmailStatusAnalyticsView.as_view(), name='email-status-analytics'),
    path('date-range/', EmailStatusByDateRangeView.as_view(), name='date-range'),
    path("upload-subject-file/", SubjectFileUploadView.as_view(), name="upload-subject-file"),
    path("subject-file-list/", SubjectFileList.as_view(), name="subject-file-list"),
    path("subject-file/<int:file_id>/", SubjectFileDetail.as_view(), name="subject-file-detail"),
    path("subject-file/<int:file_id>/rows/", SubjectFileUpdateView.as_view(), name="update-insert-multiple-rows"),
    path('subject-file/<int:file_id>/row/<int:row_id>/', SubjectFileRowDeleteView.as_view(), name='delete-subject-file-row'),
    path("delete-file/<int:file_id>/", DeleteSubjectFile.as_view(), name="delete-subject-file"),
    path('upload-contacts/', ContactUploadView.as_view(), name='upload-contacts'),
    path('user-contacts/', UserContactListView.as_view(), name='user-contacts'),
    path('contact-list/', ContactListView.as_view(), name='contact-list'),
    path('contact-update/<int:file_id>/', ContactFileUpdateView.as_view(), name='contact-update'),
    path('delete-contact-list/', DeleteContactListView.as_view(), name='delete-contact-list'),
    path('contact-files/<int:contact_file_id>/unsubscribe/<int:contact_id>/', ContactUnsubscribeView.as_view(), name='unsubscribe-contact'),
    path('campaign/', CampaignView.as_view(), name='create_campaign'),
    path('campaigns/<int:id>/', CampaignView.as_view(), name='campaign-detail'),
    path('campaigns-list/', CampaignListView.as_view(), name='all-campaigns'),
]
