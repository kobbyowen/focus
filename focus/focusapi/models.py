from django.db import models
from user_auth.models import User


class BaseModel(models.Model):
    created_by = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Photo(BaseModel):
    title = models.CharField(max_length=512)
    file_path = models.CharField(max_length=1024)
    mimetype = models.CharField(
        max_length=512, default="application/octet-stream")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f'<Photo {self.file_path}>'


class Album(BaseModel):
    name = models.CharField(max_length=512)
    photos = models.ManyToManyField(Photo)

    class Meta:
        unique_together = ('name', 'created_by',)
        ordering = ["-created_at"]

    def __str__(self):
        return f'<Photo {self.name}>'
