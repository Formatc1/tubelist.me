import tornado.websocket
import json
from django.shortcuts import get_object_or_404
from playlists.models import Playlist

USERS = {}


def change_order(data):
    active_playlist = get_object_or_404(Playlist, pk=data["id"])
    active_video = active_playlist.video_set.get(pk=data["video_id"])
    if data["position"] > 0:
        for video in active_playlist.sorted_video_set.filter(order__gt=active_video.order)[:data["position"]]:
            video.order = video.order - 1
            video.save()
        active_video.order = active_playlist.sorted_video_set.filter(order__gte=active_video.order)[data["position"]].order + 1
    else:
        data["position"] = -data["position"]
        for video in active_playlist.video_set.order_by('-order').filter(order__lt=active_video.order)[:data["position"]]:
            video.order = video.order + 1
            video.save()
        active_video.order = active_playlist.video_set.order_by('-order').filter(order__lte=active_video.order)[data["position"]].order - 1
        data["position"] = -data["position"]
    active_video.save()
    if str(active_playlist.id) in USERS:
            for user in USERS[str(active_playlist.id)]:
                user.write_message(json.dumps({"task": "change_order",
                                               "id": active_video.id,
                                               "position": data["position"]
                                               }))


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def data_received(self, chunk):
        # Don't do anything for now
        pass

    def open(self, room=0):
        if room in USERS:
            USERS[room].append(self)
        else:
            USERS[room] = [self]
        # for client in USERS[room]:
            # client.write_message(u"new client connected to room %s" % room)
        self.write_message(u"ws-echo: 418 I'm a teapot (as per RFC 2324) %s" % room)

    def on_message(self, message):
        data = json.loads(message)
        if data["task"] == "change_order":
            change_order(data)
        # active_users = [client for client in USERS.values() if self in client]
        # for user in active_users[0]:
        #     user.write_message(u"ws-echo: %s" % message)
        # self.write_message(u"ws-echo: " + message)

    def on_close(self):
        active_room = [key for key, value in USERS.items() if self in value]
        USERS[active_room[0]].remove(self)

    def check_origin(self, origin):
        return True
