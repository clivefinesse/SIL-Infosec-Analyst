from django.contrib import admin
from .models import JobApplication
from django.utils.html import format_html

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'job_post', 'applied_status', 'date_applied', 
                    'feedback_status', 'secured_status', 'created_at')
    list_filter = ('applied', 'received_feedback', 'secured_job', 'date_applied')
    search_fields = ('user__email', 'job_post', 'job_description', 'feedback_description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Job Details', {
            'fields': ('job_post', 'job_description')
        }),
        ('Application Status', {
            'fields': ('applied', 'date_applied', 'secured_job')
        }),
        ('Feedback Information', {
            'fields': ('received_feedback', 'feedback_description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'

    def applied_status(self, obj):
        return obj.applied
    applied_status.short_description = 'Applied'
    applied_status.boolean = True

    def feedback_status(self, obj):
        return obj.received_feedback
    feedback_status.short_description = 'Feedback'
    feedback_status.boolean = True

    def secured_status(self, obj):
        return obj.secured_job
    secured_status.short_description = 'Secured'
    secured_status.boolean = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)

        