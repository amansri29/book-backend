from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/', include('books.urls')),
    
    
    # Schema generation endpoint
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # ReDoc documentation endpoint
    path('api/docs/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
