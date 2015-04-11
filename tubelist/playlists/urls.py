from django.conf.urls import patterns, url
from playlists import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^new/$', views.new, name='new'),
    url(r'^(?P<playlist_id>\w+)/', views.playlist, name='playlist'),
    )
