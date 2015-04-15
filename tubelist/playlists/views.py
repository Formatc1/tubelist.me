from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from playlists.models import Playlist, Video
from hashlib import md5
from datetime import datetime
from apiclient.discovery import build
# from apiclient.errors import HttpError


def index(request):
    return render(request, 'playlists/index.html')


def new(request):
    url = md5(str(datetime.now())).hexdigest()
    try:
        if request.POST['author'] != '':
            validate_email(request.POST['author'])
        p = Playlist(url=url, name=request.POST['name'],
            author=request.POST['author'])
        p.save()
    except (KeyError, ValidationError):
        return render(request, 'playlists/index.html')
    else:
        return HttpResponseRedirect(reverse('playlists:playlist',
            args=(p.url,)))


def playlist(request, playlist_id):
    p = get_object_or_404(Playlist, url=playlist_id)
    return render(request, 'playlists/playlist.html', {'playlist': p,
        'playlist_id': playlist_id})


def search(request, playlist_id):
    p = get_object_or_404(Playlist, url=playlist_id)
    query = request.GET.get('q', '')
    if query == '':
        return HttpResponseRedirect(reverse('playlists:playlist',
            args=(p.url,)))
    youtube = build("youtube", "v3",
        developerKey="AIzaSyBotPyfxhqOQqsmjLCW19UTKw6w2jIrQrI")
    search_response = youtube.search().list(q=query,
        part="id, snippet", type="video", maxResults=10).execute()
    videos = []
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            video = {}
            video["id"] = search_result["id"]["videoId"]
            video["name"] = search_result["snippet"]["title"]
            videos.append(video)
    return render(request, 'playlists/search.html', {'query': query,
        'videos': videos, 'playlist_id': playlist_id})


def add(request, playlist_id, video_id, video_name):
    p = get_object_or_404(Playlist, url=playlist_id)
    p.video_set.add(Video(identifier=video_id, name=video_name,
        order=len(p.video_set.all())+1))
    return HttpResponseRedirect(reverse('playlists:playlist',
            args=(p.url,)))
