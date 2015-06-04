"""Python tests file"""

from django.test import TestCase
from django.test import Client
from playlists.models import Playlist


class PlaylistsTestCase(TestCase):
    """Class for testing playlists module"""
    def setUp(self):
        """Init Client"""
        self.c = Client()

    def test_home(self):
        """Test Homepage"""
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Playlist')

    def test_new_playlist_without_email(self):
        """Test adding new playlist without email address"""
        response = self.c.post('/new/',
                               data={'name': 'Test Playlist', 'author': ''},
                               follow=True)
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Playlist')
        self.assertIsNotNone(response.context['playlist'])

    def test_new_playlist_with_wrong_email(self):
        """test adding new playlist with wrong email"""
        response = self.c.post('/new/',
                               data={'name': 'Test Playlist',
                                     'author': 'wrong_email'},
                               follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Playlist')
        self.assertContains(response, 'Incorrect e-mail adress')

        response = self.c.post('/new/',
                               data={'name': 'Test Playlist',
                                     'author': 'another@wrong@email'},
                               follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Playlist')
        self.assertContains(response, 'Incorrect e-mail adress')

    def test_new_playlist_with_correct_email(self):
        """test adding new playlist with correct email"""
        response = self.c.post('/new/',
                               data={'name': 'Test Playlist',
                                     'author': 'test@mail.com'},
                               follow=True)
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Playlist')
        self.assertIsNotNone(response.context['playlist'])

    def test_search(self):
        """test searching for new video"""
        response = self.c.post('/new/',
                               data={'name': 'Test Playlist',
                                     'author': 'test@mail.com'},
                               follow=True)
        url = response.context['playlist'].url
        response = self.c.get('/%s/search/' % (url),
                              {'q': 'Hardwell United We Are'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            'Search results for: Hardwell United We Are')
        self.assertIn('United We Are',
                      response.context['videos'][0]['snippet']['title'])

    def test_add_video(self):
        """test adding new video to playlist"""
        response = self.c.post('/new/',
                               data={'name': 'Test Playlist',
                                     'author': 'test@mail.com'},
                               follow=True)
        url = response.context['playlist'].url
        response = self.c.get('/%s/search/' % (url),
                              {'q': 'Hardwell United We Are'})
        video_id = response.context['videos'][0]['id']['videoId']
        video_name = response.context['videos'][0]['snippet']['title']
        response = self.c.get('/%s/add/%s/' % (url, video_id),
                              {'name': video_name},
                              follow=True)
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'United We Are')
        playlist = Playlist.objects.get(url=url)
        self.assertIn('United We Are',
                      " ".join([video.name for video
                                in playlist.video_set.all()]))

    def test_delete_video(self):
        """test deleting video from playlist"""
        response = self.c.post('/new/',
                               data={'name': 'Test Playlist',
                                     'author': 'test@mail.com'},
                               follow=True)
        url = response.context['playlist'].url
        response = self.c.get('/%s/search/' % (url),
                              {'q': 'Don Diablo Universe'})
        video_id = response.context['videos'][0]['id']['videoId']
        video_name = response.context['videos'][0]['snippet']['title']
        response = self.c.get('/%s/add/%s/' % (url, video_id),
                              {'name': video_name},
                              follow=True)
        video = Playlist.objects.get(url=url).\
            video_set.get(identifier=video_id)
        response = self.c.get('/%s/delete/%d/' % (url, video.pk), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(video, Playlist.objects.get(url=url).video_set.all())

# self.url = response.context['playlist'].url
