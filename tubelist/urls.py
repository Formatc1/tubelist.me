from django.conf.urls import patterns, include, url
from django.contrib import admin
# from tubelist import views

admin.autodiscover()
urlpatterns = patterns(
    '',
    # url(r'^$', views.index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('playlists.urls', namespace="playlists")),
)
