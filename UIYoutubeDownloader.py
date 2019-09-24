import os
import math
from MergeVA import MergeVA
import re
from pytube import Playlist
from pytube import YouTube
from pytube.compat import unicode
from threading import Thread
from kivy.config import Config
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from Downloader import Downloader
import sys

Config.set('graphics', 'resizable', False)
Window.clearcolor = (0.17, 0.17, 0.17, 1)
Window.size = (650, 400)


class HomePage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    # ............................Default Variables...........................
        self.total_size = 1
        self.percentageDownload = 0
        self.playlist = False
        self.playlistLen = 0
        self.folder_path = ""
        self.playlist_url_dp = ""
        #self.download = Thread()
        # ........................................................................
    # UI Design
        self.orientation, self.font_size, self.spacing, self.padding = 'vertical', 15, 5, 5

        self.upperGrid = GridLayout()
        self.upperGrid.orientation = 'horizontal'
        self.upperGrid.cols = 3
        self.upperGrid.size_hint_y = 0.30

        self.upperGrid.add_widget(Label(text="", size_hint_x=0.2,
                                        size_hint_y=0.2))
        self.upperGrid.add_widget(Label(text="Youtube Downloader |",
                                        font_size=35,
                                        size_hint_x=0.4, size_hint_y=.2, color=(1, 0.8, 1, 1)))
        self.percentageDownload_label = Label(text=f"{self.percentageDownload} %",
                                              font_size=20,
                                              size_hint_x=0.2, size_hint_y=0.2, color=(1, 0.8, 1, 1))
        self.upperGrid.add_widget(self.percentageDownload_label)
        self.add_widget(self.upperGrid)

        self.play_link = TextInput(multiline=False, size_hint_y=0.13)
        self.add_widget(self.play_link)

        self.midGrid = GridLayout()
        self.add_widget(self.midGrid)
        self.midGrid.cols, self.midGrid.orientation = 3, 'vertical'
        self.midGrid.size_hint_y = 0.21

        self.q_drop_down_max = DropDown()
        self.q_drop_down_min = DropDown()

        self.max_qualities = ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']
        self.min_qualities = self.max_qualities[::-1]

        self.quality_max = Button(text='Max Quality', size_hint=(None, None), height='48dp', color=(1, 0.9, 1, 1))
        self.quality_max.bind(on_release=self.q_drop_down_max.open)
        self.quality_max.bind(on_press=self.creating_drop_down)
        self.q_drop_down_max.bind(on_select=lambda instance, q: setattr(self.quality_max, 'text', q))
        for quality in self.max_qualities:
            btn1 = Button(text=quality, size_hint_y=None, height=48, color=(1, 0.9, 1, 1))
            btn1.bind(on_release=lambda btn1: self.q_drop_down_max.select(btn1.text))
            self.q_drop_down_max.add_widget(btn1)
        self.midGrid.add_widget(self.quality_max)

        self.quality_min = Button(text='Min Quality', size_hint=(None, None), height='48dp', color=(1, 0.9, 1, 1))
        self.quality_min.bind(on_release=self.q_drop_down_min.open)
        self.quality_min.bind(on_press=self.creating_drop_down)
        self.q_drop_down_min.bind(on_select=lambda instance, q: setattr(self.quality_min, 'text', q))
        for quality in self.min_qualities:
            btn2 = Button(text=quality, size_hint_y=None, height=48, color=(1, 0.9, 1, 1))
            btn2.bind(on_release=lambda btn2: self.q_drop_down_min.select(btn2.text))
            self.q_drop_down_min.add_widget(btn2)
        self.midGrid.add_widget(self.quality_min)

        self.v_download = Button(text="Download", color=(1, 0.9, 1, 1))
        self.v_download.bind(on_press=self.start_download)
        self.midGrid.add_widget(self.v_download)

        self.scroll = ScrollView()

        self.viewerVideo = GridLayout(cols=3, size_hint_y=None, spacing=10, height=600)

        self.scroll.add_widget(self.viewerVideo)

        self.add_widget(self.scroll)

        self.lower_grid = GridLayout(cols=2, size_hint_y=0.1)
        self.clear_btn = Button(text="Clear", color=(1, 0.9, 1, 1))
        self.clear_btn.bind(on_press=self.clear_viewer)
        self.stop_btn = Button(text="Stop Download", color=(1, 0.9, 1, 1))
        self.stop_btn.bind(on_press=self.on_select)
        self.lower_grid.add_widget(self.clear_btn)
        self.lower_grid.add_widget(self.stop_btn)

        self.add_widget(self.lower_grid)
        self.download = Thread()
    # ...............................................................................
    # # -- Event Functions -- # #

    def on_select(self, instance):
        t = Thread(target=self.o7a)
        t.daemon = True
        t.start()

    def o7a(self):
        sys.exit(0)
        if self.download.isAlive():
            self.download.st


    def start_download(self, instance):
        downloader = Downloader(self.percentageDownload_label, self.viewerVideo)
        if self.play_link.text:
            self.download = Thread(target=downloader.playlist_download,
                              args=(self.play_link.text,
                                    'D:/download/',
                                    self.quality_max.text,
                                    self.quality_min.text))
            self.download.daemon = True
            self.download.start()
            print("DownloadingVideo")
        else:
            print("No input to download")

    def clear_viewer(self, instance):
        clear_viewer = Thread(target=self.viewerVideo.clear_widgets)
        clear_viewer.daemon = True
        clear_viewer.start()

    # # ---- Functions ---- # #

    def creating_drop_down(self, instance, qualities=[]):
        pass

    def downloadPL_button(self):
        playlist_url = self.play_link.text
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

                    mx_idx = self.max_qualities.index(self.quality_max.text)
                    mn_idx = self.max_qualities.index(self.quality_min.text)

                    file_extension_video = "mp4"
                    file_extension_audio = "mp4"
                    for i in range(mx_idx, mn_idx):
                        try:
                            yt.streams.filter(adaptive=True, res=self.max_qualities[i]).first().\
                                download(self.folder_path, filename=video_path)
                            sss = [stream.subtype for stream in
                                   yt.streams.filter(adaptive=True, res=self.max_qualities[i]).all()]
                            file_extension_video = sss[0]
                            break
                        except Exception as e:
                            #i += 1
                            print(f"Quality doesn't exist'|  {e}  |Quality:{self.max_qualities[i]}")

                    yt.streams.filter(adaptive=True, only_audio=True).first().download(self.folder_path,
                                                                                       filename=audio_path)
                    sss2 = [stream.subtype for stream in yt.streams.filter(adaptive=True, only_audio=True).all()]
                    print(sss2)
                    file_extension_audio = sss2[0]

                    MergeVA.merge_va(isinstance, f"{self.folder_path}/{video_path}.{file_extension_video}",
                                     f"{self.folder_path}/{audio_path}.{file_extension_audio}",
                                     f"{self.folder_path}/{video_name}.mkv")
                    os.remove(f"{self.folder_path}/{video_path}.{file_extension_video}")
                    os.remove(f"{self.folder_path}/{audio_path}.{file_extension_audio}")

                    video_label = Label(text=y_title, color=(0.5, 0.5, 0.5, 1))
                    self.viewerVideo.add_widget(video_label)

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

    def stop(self, *args):
        #App.get_running_app().stop()
        #self.get_running_app().stop()
        self.root_window.close()  # Fix app exit on Android.
        return super(YoutubeDownloader, self).stop(*args)


if __name__ == "__main__":
    YoutubeDownloader().run()
