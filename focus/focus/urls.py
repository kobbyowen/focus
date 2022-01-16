from django.urls import path, include

urlpatterns = [
    path("auth/", include('user_auth.urls')),
    path("api/v1/", include('focusapi.urls'))
]

handler404 = "focus.views.page_not_found_view"
