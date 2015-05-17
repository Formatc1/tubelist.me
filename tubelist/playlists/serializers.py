from swampdragon.serializers.model_serializer import ModelSerializer


class PlaylistSerializer(ModelSerializer):
    """Serializer for playlist"""
    class Meta:
        model = 'playlists.Playlist'
        publish_fields = ('url', 'name', 'author')


class VideoSerializer(ModelSerializer):
    """Serializersfor videos"""
    class Meta:
        model = 'playlists.Video'
        publish_fields = ('identifier', 'name', 'order')
        update_fields = ('order')
