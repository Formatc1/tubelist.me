from django.contrib import admin
from playlists.models import Playlist, Video


class VideosInLine(admin.TabularInline):
    model = Video
    extra = 1


class PlaylistAdmin(admin.ModelAdmin):
    fieldset = [
        (None, {'fields': ['url', 'name', 'author']}),
    ]
    inlines = [VideosInLine]

admin.site.register(Playlist, PlaylistAdmin)
