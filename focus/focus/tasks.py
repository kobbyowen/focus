import glob
import os
import io
from celery import shared_task
from focusapi.models import Photo, Album, LogOutput
from user_auth.models import User


def _save_log(logoutput: str) -> LogOutput:
    print(logoutput)
    m = LogOutput.objects.create(description=logoutput)
    m.save()


@shared_task
def save_user_changes(instance: User, *args, **kwargs):
    logoutput = f"Detected a change on User {instance['id']} {instance['email']} {instance['name']} {instance['username']}"
    previous = instance["previous"]

    if previous['username'] != instance['username']:
        logoutput = f"USER({instance['id']}): User {instance['id']} changed username from {previous['username']!r} to {instance['username']!r}"
    if previous['email'] != instance['email']:
        logoutput = f"USER({instance['id']}): User {instance['id']} changed email from {previous['email']!r} to {instance['email']!r}"
    if previous['name'] != instance["name"]:
        logoutput = f"USER({instance['id']}): User {instance['id']} changed name from {previous['name']!r} to {instance['name'] !r}"
    _save_log(logoutput)


@shared_task
def save_photo_changes(instance: Photo, *args, **kwargs):
    logoutput = f"Detected a change on Photo {instance['id']} {instance['title']}"
    previous = instance["previous"]
    if previous['title'] != instance['title']:
        logoutput = f"PHOTO({instance['id']}): User {instance['created_by']['id']} changed photo title from {previous['title']!r} to {instance['title']!r}"
    _save_log(logoutput)


@shared_task
def save_album_changes(instance: Album, *args, **kwargs):
    logoutput = f"Detected a change on Album {instance['id']} {instance['name']}"
    previous = instance["previous"]
    if instance['name'] != previous['name']:
        logoutput = f"ALBUM({instance['id']}): User {instance['created_by']['id']} changed album name from {previous['name']!r} to {instance['name']!r}"

    _save_log(logoutput)
