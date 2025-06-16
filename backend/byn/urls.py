"""BYN URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def health_check(request):
    """Simple health check endpoint for Railway"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'BYN Backend API',
        'message': 'Build Your Network is running successfully!'
    })

urlpatterns = [
    # Health check for Railway
    path('api/', health_check, name='health_check'),
    
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Routes
    path('api/auth/', include('accounts.urls')),
    path('api/users/', include('accounts.user_urls')),
    path('api/companies/', include('companies.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/feed/', include('feed.urls')),
    path('api/connections/', include('connections.urls')),
]

# Media files serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 