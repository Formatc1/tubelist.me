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
from playlists.web_socket_handler import USERS
import json
import re
from datetime import timedelta, date
# from apiclient.errors import HttpError


def get_user_playlists(request):
    """getting playlists identifiers from cookie"""
    if 'playlists' in request.COOKIES.keys():
        playlists = request.COOKIES['playlists'].split(':')
        user_playlists = Playlist.objects.filter(url__in=playlists)
        return user_playlists
    return False


def index(request, error=None):
    """index view"""
    user_playlists_list = get_user_playlists(request)
    return render(request, 'playlists/index.html', {
        'user_playlists': user_playlists_list,
        'error': error
    })


def new(request):
    """new view"""
    url = urlsafe_b64encode(
        pack(">Q", int(datetime.now().
                       strftime('%y%m%d%H%M%S%f')))).replace('=', '')
    try:
        if request.POST.get('author'):
            validate_email(request.POST.get('author'))
        name = request.POST.get('name') if request.POST.get(
            'name') else 'Playlist'
        active_playlist = Playlist(url=url,
                                   name=name,
                                   author=request.POST.get('author'))
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
        user_playlists_list = [active_playlist]
        playlists = [playlist_id]
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
    page_token = request.GET.get('page', '')
    if query == '':
        return HttpResponseRedirect(reverse('playlists:playlist',
                                            args=(active_playlist.url,)))
    youtube = build("youtube", "v3", developerKey=YT_DEVELOPER_KEY)
    # regex to look for links
    link_re = re.compile('(.*youtube\.com.*\?v=|.*youtu\.be\/)\
(?P<id>[a-zA-Z0-9_-]+)&?.*')
    lookup_id = link_re.match(query)
    user_playlists_list = get_user_playlists(request)
    if lookup_id:
        # link found
        video_id = lookup_id.group("id")
        search_response = youtube.videos().list(id=video_id,
                                                part='id, snippet').execute()
        videos = [video for video in search_response["items"]]
        request.GET = request.GET.copy()
        request.GET['name'] = videos[0]["snippet"]["title"]
        return add(request, playlist_id, video_id)
        # return render(request, 'playlists/search.html', {
        #     'playlist_id': playlist_id,
        #     'user_playlists': user_playlists_list
        # })
    else:
        # not found
        search_response = youtube.search().list(q=query,
                                                part="id, snippet",
                                                type="video",
                                                pageToken=page_token,
                                                maxResults=10).execute()
        videos = [video for video in search_response["items"]
                  if video["id"]["kind"] == "youtube#video"]
        return render(request, 'playlists/search.html', {
            'query': query,
            'videos': videos,
            'prev_page_token': search_response.get("prevPageToken"),
            'next_page_token': search_response.get("nextPageToken"),
            'playlist_id': playlist_id,
            'user_playlists': user_playlists_list
        })


def search_ajax(request, playlist_id):
    """search for video on YouTube view for AJAX request"""
    query = request.GET.get('q', '')
    page_token = request.GET.get('page', '')
    youtube = build("youtube", "v3", developerKey=YT_DEVELOPER_KEY)
    # regex to look for links
    link_re = re.compile('(.*youtube\.com.*\?v=|.*youtu\.be\/)\
(?P<id>[a-zA-Z0-9_-]+)&?.*')
    lookup_id = link_re.match(query)
    if lookup_id is not None:
        # link found
        video_id = lookup_id.group("id")
        search_response = youtube.videos().list(id=video_id,
                                                part='id, snippet').execute()
        videos = [video for video in search_response["items"]]
        request.GET = request.GET.copy()
        request.GET['name'] = videos[0]["snippet"]["title"]
        return add(request, playlist_id, video_id)
        # return render(request, 'playlists/search-ajax.html', {
        #     'playlist_id': playlist_id
        # })

    else:
        # not found
        search_response = youtube.search().list(q=query,
                                                part="id, snippet",
                                                type="video",
                                                pageToken=page_token,
                                                maxResults=10).execute()
        videos = [video for video in search_response["items"]
                  if video["id"]["kind"] == "youtube#video"]
        return render(request, 'playlists/search-ajax.html', {
            'query': query,
            'videos': videos,
            'prev_page_token': search_response.get("prevPageToken"),
            'next_page_token': search_response.get("nextPageToken"),
            'playlist_id': playlist_id
        })


def add(request, playlist_id, video_id):
    """add new video to playlist"""
    active_playlist = get_object_or_404(Playlist, url=playlist_id)
    video_name = request.GET.get('name')
    try:
        last_order = active_playlist.sorted_video_set.latest('order').order + 1
    except ObjectDoesNotExist:
        last_order = 1
    finally:
        new_video = Video(playlist=active_playlist,
                          identifier=video_id,
                          name=video_name,
                          order=last_order,
                          created=datetime.today())
        new_video.save()
        if str(active_playlist.id) in USERS:
            for user in USERS[str(active_playlist.id)]:
                user.write_message(json.dumps({"task": "add",
                                               "playlist": active_playlist.url,
                                               "id": new_video.pk,
                                               "identifier": video_id,
                                               "name": video_name,
                                               "order": last_order
                                               }))
    return HttpResponseRedirect(reverse('playlists:playlist',
                                        args=(active_playlist.url,)))


def delete(_, playlist_id, video_id):
    """delete video from playlist view"""
    active_playlist = get_object_or_404(Playlist, url=playlist_id)
    try:
        deleting_video = active_playlist.video_set.get(pk=video_id)
        if str(active_playlist.id) in USERS:
            for user in USERS[str(active_playlist.id)]:
                user.write_message(json.dumps({"task": "delete",
                                               "id": deleting_video.id,
                                               }))
        deleting_video.delete()
    except (ObjectDoesNotExist, IndexError):
        pass
    return HttpResponseRedirect(reverse('playlists:playlist',
                                        args=(active_playlist.url,)))


def change_name(request, playlist_id):
    """change name of existing playlists"""
    active_playlist = get_object_or_404(Playlist, url=playlist_id)
    name = request.GET.get('name', '')
    if name:
        active_playlist.name = name
        active_playlist.save()
    if str(active_playlist.id) in USERS:
        for user in USERS[str(active_playlist.id)]:
            user.write_message(json.dumps({"task": "change_name",
                                           "name": name,
                                           }))
    return HttpResponseRedirect(reverse('playlists:playlist',
                                        args=(active_playlist.url,)))


def recover(request):
    """recover playlists and send identifiers to email view"""
    user_playlists_list = get_user_playlists(request)
    if 'author' in request.POST.keys():
        playlists = Playlist.objects.filter(author=request.POST.get('author'))
        if not playlists:
            return render(request, 'playlists/recover.html', {
                'user_playlists': user_playlists_list
            })
        else:
            baseurl = "%s%s" % ('https://', request.site)
            txt_template = get_template('playlists/email.txt')
            html_template = get_template('playlists/email.html')
            email_context = Context({
                'user_playlists': user_playlists_list,
                'baseurl': baseurl
            })
            txt_content = txt_template.render(email_context)
            html_content = html_template.render(email_context)
            msg = EmailMultiAlternatives('Tubelist - Recover Playlists',
                                         txt_content,
                                         'playlisty@tubelist.me',
                                         [request.POST.get('author')])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return render(request, 'playlists/recover.html', {
                'message': request.POST.get('author'),
                'user_playlists': user_playlists_list
            })
    else:
        return render(request, 'playlists/recover-form.html', {
            'user_playlists': user_playlists_list
        })


def how_to(request):
    """View for How To page"""
    user_playlists_list = get_user_playlists(request)
    return render(request, 'playlists/how-to.html', {
         'user_playlists': user_playlists_list
    })


def statistics(request):
    """View for statistics page"""
    user_playlists_list = get_user_playlists(request)
    videos = Video.objects.all()
    videos_len = len(videos)
    playlists_len = len(Playlist.objects.all())
    videos = [video.created for video in videos]
    dates_values = prepare_dates_for_js(videos)
    return render(request, 'playlists/statistics.html', {
        'videos_len': videos_len,
        'playlists_len': playlists_len,
        'dates': dates_values[0][::-1],
        'values': dates_values[1][::-1],
        'user_playlists': user_playlists_list
    })


def prepare_dates_for_js(dates_list):
    """Prepare array for js chart"""
    today = date.today()
    dates = []
    values = []
    ret = []
    for back_day in xrange(10):
        back_date = today - timedelta(days=back_day)
        back_dates_len = len([vdate for vdate in dates_list
                              if vdate.month == back_date.month
                              and vdate.day == back_date.day])
        dates.append(back_date.isoformat())
        values.append(back_dates_len)

    ret.append(dates)
    ret.append(values)
    return ret
