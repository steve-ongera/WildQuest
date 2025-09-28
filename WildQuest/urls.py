from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('traveling_agency.urls')),  
]

# Custom error handlers (optional)
handler404 = 'traveling_agency.views.custom_404'
handler500 = 'traveling_agency.views.custom_500'
handler403 = 'traveling_agency.views.custom_403'
handler400 = 'traveling_agency.views.custom_400'

# ✅ Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
# ❌ In production, use a proper web server to serve static and media files
# For example, with Nginx or Apache, or use a CDN.
# See https://docs.djangoproject.com/en/5.2/howto/static-files/deployment/ for more details.
# https://docs.djangoproject.com/en/5.2/topics/http/urls/
# https://docs.djangoproject.com/en/5.2/ref/settings/#std:setting-DEBUG
# https://docs.djangoproject.com/en/5.2/ref/settings/#std:setting-STATIC_URL
# https://docs.djangoproject.com/en/5.2/ref/settings/#std:setting-MEDIA_URL
# https://docs.djangoproject.com/en/5.2/ref/settings/#std:setting-STATIC