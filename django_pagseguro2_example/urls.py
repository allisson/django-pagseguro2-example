from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.tickets.urls', namespace='tickets')),
    path('pagseguro/', include('pagseguro.urls')),
]
