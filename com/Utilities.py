class Utilities(object):

    playlist_path = "http://www.youtube.com/watch_videos?video_ids="

    def __init__(self):
        pass

    @staticmethod
    def sanitize_url(url_string):
        index = url_string.find("youtu.be")

        if index != -1:
            url_string = url_string[index + 9:]  # Get all after "youtu.be/" (9 characters)
        else:
            index = url_string.index("?")  # Find video id
            url_string = url_string[index + 3:]  # Get rid of "?v="

        index = url_string.find("?")  # Look for other arguments
        if index != -1:
            url_string = url_string[:index]  # Get rid of them if necessary

        index = url_string.find("&")  # The same as for "?"
        if index != -1:
            url_string = url_string[:index]

        return url_string

    @staticmethod
    def get_playlist_string_from_videos(videos_list):
        ready_string = Utilities.playlist_path
        for video_string in videos_list:
            video_string = Utilities.sanitize_url(video_string)
            ready_string += video_string + ","
        return ready_string[:-1]  # Don't pass the last comma

