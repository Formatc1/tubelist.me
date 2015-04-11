from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from playlists.models import Playlist
from hashlib import md5
from datetime import datetime


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
    pass
