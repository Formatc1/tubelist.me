from swampdragon import route_handler
from swampdragon.route_handler import ModelRouter
from playlists.models import Playlist, Video
from playlists.serializers import PlaylistSerializer, VideoSerializer


class PlaylistRouter(ModelRouter):
    """Router for playlist"""
    route_name = 'playlist'
    serializer_class = PlaylistSerializer
    model = Playlist

    def get_object(self, **kwargs):
        return self.model.objects.get(pk=kwargs['id'])

    def get_query_set(self, **kwargs):
        return self.model.objects.all()


class VideoRouter(ModelRouter):
    """Router for videos"""
    route_name = 'video'
    serializer_class = VideoSerializer
    model = Video

    def get_object(self, **kwargs):
        return self.model.objects.get(pk=kwargs['id'])

    def get_query_set(self, **kwargs):
        return self.model.objects.filter(playlist__id=kwargs['list_id']).\
            order_by('order')


route_handler.register(PlaylistRouter)
route_handler.register(VideoRouter)
