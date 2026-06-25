


from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
]

# Force serve media files on Railway even with DEBUG=False
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]


