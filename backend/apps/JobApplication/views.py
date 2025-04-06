from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from .models import JobApplication
from .serializers import JobApplicationSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action

def standard_response(status=True, message="", data=None, status_code=status.HTTP_200_OK):
    """Standardized API response format"""
    return Response({
        "status": status,
        "message": message,
        "data": data or {}
    }, status=status_code)

class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['applied', 'received_feedback', 'secured_job']
    search_fields = ['job_post', 'job_description', 'feedback_description']
    ordering_fields = ['date_applied', 'created_at', 'updated_at']
    ordering = ['-date_applied']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return JobApplication.objects.none()
        return JobApplication.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return standard_response(
            status=True,
            message="Job applications retrieved successfully",
            data=serializer.data
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return standard_response(
            status=True,
            message="Job application retrieved successfully",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return standard_response(
            status=True,
            message="Job application created successfully",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return standard_response(
            status=True,
            message="Job application updated successfully",
            data=serializer.data
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return standard_response(
            status=True,
            message="Job application deleted successfully",
            data={}
        )

    @action(detail=True, methods=['post'])
    def mark_as_secured(self, request, pk=None):
        application = self.get_object()
        application.secured_job = True
        application.save()
        return standard_response(
            status=True,
            message="Job application marked as secured",
            data=self.get_serializer(application).data
        )
    