from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Matematika Sertifikati - Admin"
admin.site.site_title = "Matematika Admin"
admin.site.index_title = "Boshqaruv Paneli"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quiz.urls')),
]
