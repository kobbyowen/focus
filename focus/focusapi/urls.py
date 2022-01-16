from django.urls import path, include
from .views import UserView, ListUsersView

urlpatterns = [
    path("user/<int:pk>", UserView.as_view(), name="user-crud"),
    path("users", ListUsersView.as_view(), name="list-users")
]
