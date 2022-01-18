from django.urls import path, include
from .views import (UserView, ListUsersView, AllPhotosView, PhotoView, PhotoDownloadView, MyProfileView,
                    UserPhotosView, AlbumView, SingleAlbumView, UserAlbumsView, SingleAlbumPhotosView, AlbumPhotosView)

urlpatterns = [
    path("user/<int:pk>", UserView.as_view(), name="user-crud"),
    path("user/me", MyProfileView.as_view(), name="my-profile"),
    path("user/<int:pk>/photos", UserPhotosView.as_view(), name="user-photos"),
    path("user/<int:pk>/albums", UserAlbumsView.as_view(), name="user-albums"),
    path("users", ListUsersView.as_view(), name="list-users"),
    path("photos", AllPhotosView.as_view(), name="all-photos"),
    path("photo/<int:pk>", PhotoView.as_view(), name="photo-crud"),
    path("photo/<int:pk>/download",
         PhotoDownloadView.as_view(), name="download-photo"),
    path("albums", AlbumView.as_view(), name="albums"),
    path("album/<int:pk>", SingleAlbumView.as_view(), name="single-album"),
    path("album/<int:pk>/photos", SingleAlbumPhotosView.as_view(),
         name="single-album-photos"),
    path("album/<int:album_id>/photo/<int:photo_id>", AlbumPhotosView.as_view(),
         name="single-album-photo"),



]
