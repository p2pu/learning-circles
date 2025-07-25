from django.db import models


class Image(models.Model):

    image_file = models.FileField(upload_to="uploads/images")
    uploader_uri = models.CharField(max_length=256)
