from rest_framework import serializers
from .models import JobApplication
from django.utils import timezone

class JobApplicationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = JobApplication
        fields = [
            'id',
            'user',
            'job_post',
            'job_description',
            'applied',
            'date_applied',
            'received_feedback',
            'feedback_description',
            'secured_job',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        # Set date_applied if applied is True and date not provided
        if data.get('applied', False) and not data.get('date_applied'):
            data['date_applied'] = timezone.now().date()
        return data
    
    