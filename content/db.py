from django.db import models


class Content(models.Model):

    latest = models.ForeignKey('content.ContentVersion', models.CASCADE, related_name='+', null=True, blank=True)
    based_on = models.ForeignKey('content.Content', models.SET_NULL, related_name='derived_content', null=True, blank=True)  #on_delete=SET_NULL might cause a problem here


class ContentVersion(models.Model):

    container = models.ForeignKey(Content, models.CASCADE, related_name='versions')
    title = models.CharField(max_length = 100)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length = 100)
    author_uri = models.CharField(max_length=256)
