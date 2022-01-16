from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from focusapi.models import Photo, Album
from user_auth.models import User
from focusapi.serializers import UserSerializer, PhotoSerializer, AlbumSerializer
from focus.tasks import save_user_changes, save_photo_changes, save_album_changes


@receiver(pre_save, sender=Photo)
def catch_photo_changes_response(sender, instance: Photo, **kwargs):
    previous = Photo.objects.get(id=instance.pk)
    data = PhotoSerializer(instance).data
    data["previous"] = PhotoSerializer(previous).data
    save_photo_changes.delay(data)


@receiver(pre_save, sender=User)
def catch_user_changes_response(sender, instance: User, **kwargs):
    previous = User.objects.get(id=instance.pk)
    data = UserSerializer(instance).data
    data["previous"] = UserSerializer(previous).data
    save_user_changes.delay(data)


@receiver(pre_save, sender=Album)
def catch_album_changes_response(sender, instance: Album, **kwargs):
    previous = Album.objects.get(id=instance.pk)
    data = AlbumSerializer(instance).data
    data["previous"] = AlbumSerializer(previous).data
    save_album_changes.delay(data)
