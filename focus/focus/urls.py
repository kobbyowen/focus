from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path("auth/", include('user_auth.urls')),
    path("api/v1/", include('focusapi.urls')),
    path("", admin.site.urls),
]

admin.site.site_header = "FOCUS ADMIN"
admin.site.site_title = "FOCUS ADMIN SITE"
admin.site.index_title = "focus admin site"

handler404 = "focus.views.page_not_found_view"
