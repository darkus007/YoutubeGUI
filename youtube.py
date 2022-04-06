""" Simple YouTube downloader video or audio by URL """
from copy import copy
from pytube import YouTube


class MyYouTuBe(YouTube):
    """ Simple YouTube downloader video or audio by URL """
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

    def download_best_video(self, path: str = 'video/') -> None:
        """ Download the best video in progressive format

            :param path: path to save video (optional)
        """
        self.streams.filter(progressive=True,
                            file_extension='mp4').order_by('resolution').desc().first().download(path)

    def download_video_by_itag(self, itag: int, path='video/', filename_prefix=None) -> None:
        """ Download video or audio by itag

            :param itag: video or audio by itag
            :param path: path to save video (optional)
            :param filename_prefix: a string that will be prepended to the filename (optional)
        """
        self.streams.get_by_itag(itag).download(output_path=path, filename_prefix=filename_prefix)

    @property
    def best_video_size(self) -> int:
        """ Get the best progressive video size in bytes """
        return int(self.streams.filter(progressive=True, file_extension='mp4').
                   order_by('resolution').desc().first().filesize)

    def on_progress(self, stream, chunk, bytes_remaining) -> None:
        """ Executed during the loading of the stream and displays the progress of its loading """
        # Visualizes the download progress
        # rows, columns = os.popen('stty size', 'r').read().split()
        fill_width = 48
        current_percent = (stream.filesize - bytes_remaining) / stream.filesize
        filled_length = int(fill_width * current_percent)
        empty_length = fill_width - filled_length
        bar = f'| {"#" * filled_length + " " * empty_length} | '
        print(f'Downloaded:{bar} {current_percent:.0%}', end='\n' if current_percent >= 1.0 else '\r')

    @staticmethod
    def on_complete(stream, path: str):
        """ Will be executed after the download is complete """
        print("File saved as:  \n" + path)

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


if __name__ == '__main__':
    print("Welcome to youtube video and audio downloader!")
    choice = -1
    while choice not in (0, 1, 2):
        try:
            choice = int(input("1 - to download the best video; 2 - select boot options; 0 - exit. "))
            if choice not in (0, 1, 2):
                print(f'Number is out of range (0 - 2)')
        except ValueError:
            print('Wrong value!')

    if choice == 0:
        exit()

    url = input('Enter the YouTube URL: ')
    video = MyYouTuBe(url)
    print(video.title)
    print(video.author)

    # download the best video
    if choice == 1:
        print(f'Best video size {video.best_video_size} bytes')
        video.download_best_video()
        exit()

    # select boot options
    if choice == 2:
        all_streams = video.get_all_streams()
        len_all_streams = len(all_streams)

        # print streams info
        for i, it in zip(range(len_all_streams), all_streams):
            print(f"{i}:\t{it['format']} | {it['qualityLabel']}({it['width']}/{it['height']}) "
                  f"| bitrate: {it['bitrate']} | fps: {it['fps']} | Audio channels: {it['audioChannels']} "
                  f"| Audio sample rate: {it['audioSampleRate']} | file size: {it['size']} bytes")

        # choice
        video_number = -1
        while video_number not in range(len_all_streams):
            try:
                video_number = int(input(f'Enter video or audio number to download (0 to {len_all_streams}): '))
                if video_number < 0 or video_number >= len_all_streams:
                    print(f'Number is out of range (0 - {len_all_streams})')
            except ValueError:
                print('Wrong value!')

        # download
        video.download_video_by_itag(itag=all_streams[video_number]["itag"],
                                     filename_prefix=None if not all_streams[video_number]["qualityLabel"] is None
                                     else 'Audio ')
