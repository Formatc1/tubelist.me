"""Views module"""
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from playlists.models import Playlist, Video
from base64 import urlsafe_b64encode
from struct import pack
from datetime import datetime
from apiclient.discovery import build
from tubelist.settings import YT_DEVELOPER_KEY
from django.template.loader import get_template
from django.template import Context
from django.contrib.sites.models import get_current_site
# from apiclient.errors import HttpError


def get_user_playlists(request):
    """getting playlists identifiers from cookie"""
    if 'playlists' in request.COOKIES.keys():
        playlists = request.COOKIES['playlists'].split(':')
        user_playlists = Playlist.objects.filter(url__in=playlists)
        return user_playlists
    return None


def index(request, error=None):
    """index view"""
    user_playlists_list = get_user_playlists(request)
    return render(request, 'playlists/index.html', {
        'user_playlists': user_playlists_list,
        'error': error
        })


def new(request):
    """new view"""
    url = urlsafe_b64encode(pack(">Q",
        int(datetime.now().strftime('%y%m%d%H%M%S%f')))).replace('=', '')
    try:
        if request.POST['author'] != '':
            validate_email(request.POST['author'])
        active_playlist = Playlist(url=url, name=request.POST['name'],
            author=request.POST['author'])
        active_playlist.save()
    except (KeyError, ValidationError):
        return index(request, 'Incorrect e-mail adress')
    else:
        return HttpResponseRedirect(reverse('playlists:playlist',
            args=(active_playlist.url,)))


def playlist(request, playlist_id):
    """show playlist view"""
    active_playlist = get_object_or_404(Playlist, url=playlist_id)
    user_playlists_list = get_user_playlists(request)
    if 'playlists' in request.COOKIES.keys():
        playlists = request.COOKIES['playlists'].split(':')
        if playlist_id not in playlists:
            playlists.append(playlist_id)
            user_playlists_list = Playlist.objects.filter(url__in=playlists)
    else:
        user_playlists_list = active_playlist
        playlists = playlist_id
    playlists = ':'.join(playlists)
    response = render(request, 'playlists/playlist.html', {
        'playlist': active_playlist,
        'user_playlists': user_playlists_list
        })
    response.set_cookie(key='playlists', value=playlists, max_age=31536000)
    return response


def search(request, playlist_id):
    """search for video on YouTube view"""
    active_playlist = get_object_or_404(Playlist, url=playlist_id)
    query = request.GET.get('q', '')
    if query == '':
        return HttpResponseRedirect(reverse('playlists:playlist',
            args=(active_playlist.url,)))
    youtube = build("youtube", "v3",
        developerKey=YT_DEVELOPER_KEY)
    search_response = youtube.search().list(q=query,
        part="id, snippet", type="video", maxResults=10).execute()
    videos = []
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            video = {}
            video["id"] = search_result["id"]["videoId"]
            video["name"] = search_result["snippet"]["title"]
            videos.append(video)
    user_playlists_list = get_user_playlists(request)
    return render(request, 'playlists/search.html', {
        'query': query,
        'videos': videos,
        'playlist_id': playlist_id,
        'user_playlists': user_playlists_list
        })


def add(request, playlist_id, video_id, video_name):
    """add new video to playlist view"""
    active_playlist = get_object_or_404(Playlist, url=playlist_id)
    try:
        order = active_playlist.sorted_video_set.latest('order').order + 1
    except ObjectDoesNotExist:
        order = 1
    finally:
        active_playlist.video_set.add(Video(identifier=video_id,
            name=video_name, order=order))
    return HttpResponseRedirect(reverse('playlists:playlist',
        args=(active_playlist.url,)))


def delete(request, playlist_id, video_id):
    """delete video from playlist view"""
    active_playlist = get_object_or_404(Playlist, url=playlist_id)
    try:
        active_playlist.video_set.filter(identifier=video_id)[0].delete()
    except (ObjectDoesNotExist, IndexError):
        pass
    return HttpResponseRedirect(reverse('playlists:playlist',
        args=(active_playlist.url,)))


def recover(request):
    """recover playlists and send identifiers to email view"""
    user_playlists_list = get_user_playlists(request)
    if 'author' in request.POST.keys():
        playlists = Playlist.objects.filter(author=request.POST['author'])
        if not playlists:
            return render(request, 'playlists/recover.html', {
                'user_playlists': user_playlists_list
                })
        else:
            baseurl = "%s%s" % ('https://', get_current_site(request).domain)
            txt_template = get_template('playlists/email.txt')
            html_template = get_template('playlists/email.html')
            email_context = Context({
                'user_playlists': user_playlists_list,
                'baseurl': baseurl
                })
            txt_content = txt_template.render(email_context)
            html_content = html_template.render(email_context)
            msg = EmailMultiAlternatives('Tubelist - Recover Playlists',
                txt_content, 'playlisty@tubelist.me', [request.POST['author']])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return render(request, 'playlists/recover.html', {
                'message': request.POST['author'],
                'user_playlists': user_playlists_list
                })
    else:
        return render(request, 'playlists/recover-form.html', {
            'user_playlists': user_playlists_list
            })
