"""Django urls file"""

from django.conf.urls import patterns, url
from playlists import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^new/$', views.new, name='new'),
    url(r'^recover/$', views.recover, name='recover'),
    url(r'^(?P<playlist_id>\w+)/$', views.playlist, name='playlist'),
    url(r'^(?P<playlist_id>\w+)/search/$', views.search, name='search'),
    url(r'^(?P<playlist_id>\w+)/add/(?P<video_id>[a-zA-z0-9_-]+)/\
(?P<video_name>.+)/$', views.add, name='add'),
    url(r'^(?P<playlist_id>\w+)/delete/(?P<video_id>\d+)/$',
        views.delete, name='delete'),
)
