from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

# Swagger/ReDoc - API Documentation
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="SIL Infosec Analyst Assessment",
        default_version='v1',
        description="Chris Clive API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    
    # Auth Endpoints (Django built-in)
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # API Docs (Swagger & ReDoc)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
    
    # Your Apps
    path('api/users/', include('apps.users.urls')),
    path('api/job-applications/', include('apps.JobApplication.urls')),
]   