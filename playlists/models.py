"""Models for playlists"""

from django.db import models


class Playlist(models.Model):
    """Class for playlists"""
    url = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=100)
    author = models.EmailField(blank=True)

    def __unicode__(self):
        return self.name

    @property
    def sorted_video_set(self):
        """Return videos sorted by order"""
        return self.video_set.order_by('order')

    @property
    def first_video_id(self):
        """Return id for first video"""
        return self.video_set.order_by('order')[0].identifier

    @property
    def sorted_video_id_set(self):
        """Return identifiers sorted by order from second to last"""
        return [x.identifier for x in self.video_set.order_by('order')[1:]]


class Video(models.Model):
    """Class for videos"""
    playlist = models.ForeignKey(Playlist)
    identifier = models.SlugField(max_length=20)
    name = models.CharField(max_length=200)
    order = models.PositiveSmallIntegerField()
    created = models.DateTimeField()
    
    def __unicode__(self):
        return self.name
