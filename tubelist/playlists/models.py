from django.db import models


class Playlist(models.Model):
    """Class for playlists"""
    url = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=100)
    author = models.EmailField()

    def __unicode__(self):
        return self.name


class Video(models.Model):
    """Class for videos"""
    playlist = models.ForeignKey(Playlist)
    identifier = models.SlugField(max_length=20)
    name = models.CharField(max_length=200)
    order = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return self.name
