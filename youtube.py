""" Simple YouTube downloader the best resolution video by URL """
from copy import copy
from pytube import YouTube


class MyYouTuBe(YouTube):
    """ Simple YouTube downloader the best resolution video by URL """
    FORMAT = {'format': None, 'qualityLabel': None, 'width': None, 'height': None, 'bitrate': None, 'fps': None,
              'audioChannels': None, 'audioSampleRate': None, 'size': None, 'itag': None}

    def __init__(self, url):
        super(MyYouTuBe, self).__init__(url=url)
        self.register_on_complete_callback(self.on_complete)
        self.register_on_progress_callback(self.on_progress)
        self.available_streams = list()

    def get_all_streams(self) -> list[dict]:
        """ Get a list of all available streams """
        temp = copy(self.FORMAT)

        for stream in self.streaming_data['formats']:
            temp['format'] = "Progressive"
            temp = self.reduce_stream_info(stream, temp)
            file_size = int(self.streams.get_by_itag(stream["itag"]).filesize)
            temp['size'] = file_size
            self.available_streams.append(temp)
            temp = copy(self.FORMAT)

        for stream in self.streaming_data['adaptiveFormats']:
            temp['format'] = "Adaptive"
            temp = self.reduce_stream_info(stream, temp)
            file_size = int(self.streams.get_by_itag(stream["itag"]).filesize)
            temp['size'] = file_size
            self.available_streams.append(temp)
            temp = copy(self.FORMAT)

        return self.available_streams

    def download_best_video(self, path='video/') -> None:
        """ Download the best video in progressive format

            :param path: path to save video (optional)
        """
        self.streams.filter(progressive=True,
                            file_extension='mp4').order_by('resolution').desc().first().download(path)

    @property
    def best_video_size(self) -> int:
        """ Get the best progressive video size in bytes """
        return int(self.streams.filter(progressive=True, file_extension='mp4').
                   order_by('resolution').desc().first().filesize)

    def on_progress(self, stream, chunk, bytes_remaining) -> None:
        """ Executed during the loading of the stream and displays the progress of its loading """
        percent = (self.best_video_size - bytes_remaining) / self.best_video_size
        print(f'Downloaded: {percent:.0%}', end='\r')

    @staticmethod
    def on_complete(stream, path: str):
        """ Will be executed after the download is complete """
        print("File saved as:\n" + path)

    @staticmethod
    def reduce_stream_info(stream: dict, temp: dict) -> dict:
        """ Reduces stream information

            :param stream: stream to reduce information
            :param temp: variable to add a shortened stream information
            :returns: dict: shorthand information about the stream
        """
        try:
            temp['qualityLabel'] = stream["qualityLabel"]
        except KeyError:
            pass
        try:
            temp['width'] = stream["width"]
        except KeyError:
            pass
        try:
            temp['height'] = stream["height"]
        except KeyError:
            pass
        try:
            temp['bitrate'] = stream["bitrate"]
        except KeyError:
            pass
        try:
            temp['fps'] = stream["fps"]
        except KeyError:
            pass
        try:
            temp['audioChannels'] = stream["audioChannels"]
        except KeyError:
            pass
        try:
            temp['audioSampleRate'] = stream["audioSampleRate"]
        except KeyError:
            pass
        temp['itag'] = stream["itag"]
        return temp


def main():
    # url = 'https://www.youtube.com/watch?v=t5Bo1Je9EmE'
    url = input('Enter the YouTube URL: ')
    video = MyYouTuBe(url)
    print(video.title)
    print(video.author)
    print(f'Best video size {video.best_video_size} bytes')
    # pprint(video.get_all_streams())
    video.download_best_video()


if __name__ == '__main__':
    main()
