from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail import send_mail
from playlists.models import Playlist, Video
from base64 import urlsafe_b64encode
from struct import pack
from datetime import datetime
from apiclient.discovery import build
# from apiclient.errors import HttpError


def user_playlists(request):
    if 'playlists' in request.COOKIES.keys():
        playlists = request.COOKIES['playlists'].split(':')
        user_playlists = Playlist.objects.filter(url__in=playlists)
        return user_playlists
    return None


def index(request, error=None):
    user_playlists_list = user_playlists(request)
    return render(request, 'playlists/index.html', {'user_playlists': user_playlists_list, 'error': error})


def new(request):
    url = urlsafe_b64encode(pack(">Q", int(datetime.now().strftime('%y%m%d%H%M%S%f')))).replace('=', '')
    try:
        if request.POST['author'] != '':
            validate_email(request.POST['author'])
        p = Playlist(url=url, name=request.POST['name'],
            author=request.POST['author'])
        p.save()
    except (KeyError, ValidationError):
        return index(request, 'Incorrect e-mail adress')
    else:
        return HttpResponseRedirect(reverse('playlists:playlist',
            args=(p.url,)))


def playlist(request, playlist_id):
    p = get_object_or_404(Playlist, url=playlist_id)
    user_playlists_list = user_playlists(request)
    if 'playlists' in request.COOKIES.keys():
        playlists = request.COOKIES['playlists'].split(':')
        if playlist_id not in playlists:
            playlists.append(playlist_id)
            user_playlists_list = Playlist.objects.filter(url__in=playlists)
    else:
        user_playlists_list = p
        playlists = playlist_id
    playlists = ':'.join(playlists)

    response = render(request, 'playlists/playlist.html', {'playlist': p, 'user_playlists': user_playlists_list})

    response.set_cookie(key='playlists', value=playlists, max_age=31536000)
    return response


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
    user_playlists_list = user_playlists(request)
    return render(request, 'playlists/search.html', {'query': query,
        'videos': videos, 'playlist_id': playlist_id, 'user_playlists': user_playlists_list})


def add(request, playlist_id, video_id, video_name):
    p = get_object_or_404(Playlist, url=playlist_id)
    try:
        order = p.sorted_video_set.latest('order').order + 1
    except ObjectDoesNotExist:
        order = 1
    finally:
        p.video_set.add(Video(identifier=video_id, name=video_name,
            order=order))
    return HttpResponseRedirect(reverse('playlists:playlist',
        args=(p.url,)))


def delete(request, playlist_id, video_id):
    p = get_object_or_404(Playlist, url=playlist_id)
    try:
        p.video_set.filter(identifier=video_id)[0].delete()
    except (ObjectDoesNotExist, IndexError):
        pass
    return HttpResponseRedirect(reverse('playlists:playlist',
        args=(p.url,)))


def recover(request):
    user_playlists_list = user_playlists(request)
    if 'author' in request.POST.keys():
        playlists = Playlist.objects.filter(author=request.POST['author'])
        if not playlists:
            return render(request, 'playlists/recover.html', {'user_playlists': user_playlists_list})
        else:
            result = '\r\n'.join(['%s - %s' % (x.name, x.url) for x in playlists])
            send_mail('Playlisty', result, 'playlisty@tubelist.me', [request.POST['author']])
            return render(request, 'playlists/recover.html', {'message': request.POST['author'], 'user_playlists': user_playlists_list})
    else:
        return render(request, 'playlists/recover-form.html', {'playlists': user_playlists_list})
