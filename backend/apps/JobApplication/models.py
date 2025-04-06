from django.db import models
from django.conf import settings
from django.utils import timezone

class JobApplication(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_applications'
    )
    job_post = models.CharField(max_length=255)
    job_description = models.TextField(blank=True)
    applied = models.BooleanField(default=False)
    date_applied = models.DateField(null=True, blank=True)
    received_feedback = models.BooleanField(default=False)
    feedback_description = models.TextField(blank=True)
    secured_job = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_applied']

    def __str__(self):
        return f"{self.user.email} - {self.job_post}"
    
    def get_queryset(self):
        # Handle schema generation requests
        if getattr(self, 'swagger_fake_view', False):
            return JobApplication.objects.none()
        
        # Regular requests
        return JobApplication.objects.filter(user=self.request.user)


    def save(self, *args, **kwargs):
        # Set date_applied to today if applied is True and date_applied is not set
        if self.applied and not self.date_applied:
            self.date_applied = timezone.now().date()
        super().save(*args, **kwargs)
