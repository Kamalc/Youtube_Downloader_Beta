from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from pytube import Playlist
from pytube import YouTube
from pytube.compat import unicode
from threading import Thread
import os
import math
from MergeVA import MergeVA
import re

Window.size = (500, 250)


class HomePage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    # ............................Default Variables...........................
        self.total_size = 1
        self.percentageDownload = 0
        self.playlist = False
        self.playlistLen = 0
        self.folder_path = ""
    # ........................................................................
    # UI Design
        self.upperGrid = GridLayout()
        self.upperGrid.cols = 2

        self.upperGrid.add_widget(Label(text="PlayList Link:"))

        self.PL_link = TextInput(multiline=False)
        self.upperGrid.add_widget(self.PL_link)

        self.upperGrid.add_widget(Label(text="Video Link:"))

        self.V_link = TextInput(multiline=False)
        self.upperGrid.add_widget(self.V_link)

        self.add_widget(self.upperGrid)
        self.cols, self.padding, self.spacing = 1, 10, 5

        self.v_download = Button(text="Download")
        self.v_download.bind(on_press=self.start_download)
        self.add_widget(self.v_download)

        self.add_widget(Label())
        self.percentageDownload_label = Label(text=f"{self.percentageDownload} %", font_size='80sp')
        self.add_widget(self.percentageDownload_label)
    # ...............................................................................
    # # -- Event Functions -- # #

    def start_download(self, instance):
        if self.PL_link.text:
            download = Thread(target=self.downloadPL_button)
            print("DownloadingVideo")
            download.start()
        else:
            print("No input to download")
    # # ---- Functions ---- # #

    def downloadPL_button(self):
        playlist_url = self.PL_link.text
        if playlist_url:
            pl = Playlist(playlist_url)
            folder_name = self.safe_filename(pl.title())
            video_list = pl.parse_links()
            self.playlistLen = len(video_list)
            self.folder_path = 'D:/download/' + folder_name

            self.create_new_folder(self.folder_path)
            counter = 1
            for x in video_list:
                self.total_size = 1
                try:
                    yt = YouTube("https://www.youtube.com/" + x)
                    y_title = self.safe_filename(yt.title)
                    yt.register_on_progress_callback(self.show_progress_bar)
                    video_name = self.get_cnt(counter) + y_title
                    video_path = video_name + "_v"
                    audio_path = video_name + "_a"
                    yt.streams.filter(adaptive=True, only_audio=True).first().download(self.folder_path,
                                                                                       filename=audio_path)
                    yt.streams.filter(adaptive=True).first().download(self.folder_path, filename=video_path)

                    sss = [stream.subtype for stream in yt.streams.filter(adaptive=True).all()]
                    file_extension_video = sss[0]
                    sss = [stream.subtype for stream in yt.streams.filter(adaptive=True, only_audio=True).all()]
                    file_extension_audio = sss[0]
                    MergeVA.merge_va(isinstance, f"{self.folder_path}/{video_path}.{file_extension_video}",
                                     f"{self.folder_path}/{audio_path}.{file_extension_audio}",
                                     f"{self.folder_path}/{video_name}.mkv")
                    os.remove(f"{self.folder_path}/{video_path}.{file_extension_video}")
                    os.remove(f"{self.folder_path}/{audio_path}.{file_extension_audio}")
                    caption = yt.captions.get_by_language_code('en')
                    if caption:
                        my_file = open(self.folder_path + '/' + self.get_cnt(counter) + y_title + ".srt", "w+",
                                       encoding='UTF8')
                        my_file.writelines(caption.generate_srt_captions())
                        my_file.close()
                    else:
                        print("No Sub Found")
                except Exception as e:
                    print("Can't Download: " + str(e))

                counter += 1

    def downloadV_button(self):
        video_link = YouTube(self.V_link.text)
        video_link.register_on_progress_callback(self.show_progress_bar)
        video_link.streams.filter(only_audio=True).first().download('D:/download')

    def show_progress_bar(self,stream, chunk, file_handle, bytes_remaining):
        self.total_size = max(bytes_remaining, self.total_size)
        self.percentageDownload = int(100 - (bytes_remaining / self.total_size * 100))
        self.percentageDownload_label.text = f"{self.percentageDownload} %"
        print(f"{self.percentageDownload} %")
        return

    def create_new_folder(self, directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print('Error: Creating Folder. ' + directory)

    def get_cnt(self, cnt):
        cnt_str = ""
        for i in range(math.ceil(math.log10(self.playlistLen)) - len(str(cnt))):
            cnt_str += '0'
        return cnt_str + str(cnt) + '.'

    def safe_filename(self, s, max_length=255):
        # Characters in range 0-31 (0x00-0x1F) are not allowed in ntfs filenames.
        ntfs_chrs = [chr(i) for i in range(0, 31)]
        chrs = [
            '\"', '\$', '\%', '\'', '\*', '\,', '\/', '\:', '"',
            '\;', '\<', '\>', '\?', '\\', '\^', '\|', '\~', '\\\\',
        ]
        pattern = '|'.join(ntfs_chrs + chrs)
        regex = re.compile(pattern, re.UNICODE)

        filename = regex.sub('', s)
        return unicode(filename[:max_length].rsplit(' ', 0)[0])

class YoutubeDownloader(App):
    def build(self):
        self.screen_manager = ScreenManager()

        self.home_page = HomePage()
        screen = Screen(name="Home")
        screen.add_widget(self.home_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager


if __name__ == "__main__":
    YoutubeDownloader().run()