"""Model for admin panel"""

from django.contrib import admin
from playlists.models import Playlist, Video


class VideosInLine(admin.TabularInline):
    """Class for view"""
    model = Video
    extra = 1


class PlaylistAdmin(admin.ModelAdmin):
    """Class for field set"""
    fieldset = [
        (None, {'fields': ['url', 'name', 'author']}),
    ]
    inlines = [VideosInLine]

admin.site.register(Playlist, PlaylistAdmin)
