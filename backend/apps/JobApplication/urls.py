from django.urls import path
from .views import *


urlpatterns = [
    path('job-applications/', JobApplicationViewSet.as_view({'get': 'list', 'post': 'create'}), name='job-application-list'),
    path('job-applications/<int:pk>/', JobApplicationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='job-application-detail'),
]
