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
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooser, FileChooserListView, FileChooserIconView
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from Downloader import Downloader
from functools import partial

Config.set('graphics', 'resizable', False)
Window.clearcolor = (0.17, 0.17, 0.17, 1)
Window.size = (650, 400)


class HomePage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    # ............................Default Variables...........................
        self.percentageDownload = 0
        self.playlist = False
        self.playlist_url_dp = ""
        self.directory_window = Popup()
        self.show_popup = PopU()
        self.def_directory = 'D:/download/'
        # ........................................................................
    # UI Design
        self.orientation, self.font_size, self.spacing, self.padding = 'vertical', 15, 5, 5

        self.upperGrid = GridLayout()
        self.upperGrid.orientation = 'horizontal'
        self.upperGrid.cols = 3
        self.upperGrid.size_hint_y = 0.30

        self.upperGrid.add_widget(Label(text="", size_hint_x=0.2,
                                        size_hint_y=0.2))
        self.upperGrid.add_widget(Label(text="Youtube Downloader   |",
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
        self.midGrid.cols, self.midGrid.orientation = 4, 'vertical'
        self.midGrid.size_hint_y = 0.21

        self.q_drop_down_max = DropDown()
        self.q_drop_down_min = DropDown()

        self.max_qualities = ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']
        self.min_qualities = self.max_qualities[::-1]

        self.quality_max = Button(text='Max Quality', size_hint=(None, None), height='48dp', color=(1, 0.9, 1, 1))
        self.quality_max.bind(on_release=self.q_drop_down_max.open)
        self.q_drop_down_max.bind(on_select=lambda instance, q: setattr(self.quality_max, 'text', q))
        for quality in self.max_qualities:
            btn1 = Button(text=quality, size_hint_y=None, height=48, color=(1, 0.9, 1, 1))
            btn1.bind(on_release=lambda btn1: self.q_drop_down_max.select(btn1.text))
            self.q_drop_down_max.add_widget(btn1)
        self.midGrid.add_widget(self.quality_max)

        self.quality_min = Button(text='Min Quality', size_hint=(None, None), height='48dp', color=(1, 0.9, 1, 1))
        self.quality_min.bind(on_release=self.q_drop_down_min.open)
        self.q_drop_down_min.bind(on_select=lambda instance, q: setattr(self.quality_min, 'text', q))
        for quality in self.min_qualities:
            btn2 = Button(text=quality, size_hint_y=None, height=48, color=(1, 0.9, 1, 1))
            btn2.bind(on_release=lambda btn2: self.q_drop_down_min.select(btn2.text))
            self.q_drop_down_min.add_widget(btn2)
        self.midGrid.add_widget(self.quality_min)

        self.v_download = Button(text="Download", size_hint_x=0.6, color=(1, 0.9, 1, 1))
        self.v_download.bind(on_press=self.start_download)
        self.midGrid.add_widget(self.v_download)

        self.directory_btn = Button(text="Browse", size_hint_x=0.1, color=(1, 0.9, 1, 1))
        self.directory_btn.bind(on_release=self.choose_directory)
        self.midGrid.add_widget(self.directory_btn)

        self.scroll = ScrollView()

        self.viewerVideo = GridLayout(cols=4, size_hint_y=None, spacing=10, height=600)

        self.scroll.add_widget(self.viewerVideo)

        self.add_widget(self.scroll)

        self.lower_grid = GridLayout(cols=2, size_hint_y=0.1)
        self.clear_btn = Button(text="Clear", color=(1, 0.9, 1, 1))
        self.clear_btn.bind(on_press=self.clear_viewer)
        self.stop_btn = Button(text="Stop Download", color=(1, 0.9, 1, 1))
        self.lower_grid.add_widget(self.clear_btn)
        self.lower_grid.add_widget(self.stop_btn)

        self.add_widget(self.lower_grid)
        # --- Pop Up Screen -------------------------------------------
        self.directory_window = Popup(title="Directory", content=self.show_popup, size_hint=(None, None),
                                      size=(500, 400))
        self.show_popup.cancel_btn.bind(on_release=self.directory_window.dismiss)
        self.show_popup.load_btn.bind(on_release=self.choose_folder)
        # -------------------------------------------------------------
        self.download = Thread()
    # ...............................................................................
    # # -- Event Functions -- # #

    """def on_select(self, instance):
        t = Thread(target=self.stop_btn)
        t.daemon = True
        t.start()

    def stop_btn(self):
        sys.exit(0)
        if self.download.isAlive():
            self.download.st"""

    def choose_directory(self, instance):
        self.directory_window.open()

    def start_download(self, instance):
        downloader = Downloader(self.percentageDownload_label, self.viewerVideo, self.def_directory)
        if self.play_link.text:
            self.download = Thread(target=downloader.playlist_download,
                              args=(self.play_link.text,
                                    self.def_directory,
                                    self.quality_max,
                                    self.quality_min))
            self.download.daemon = True
            self.download.start()
            print("DownloadingVideo")
        else:
            print("No input to download")

    def clear_viewer(self, instance):
        #clear_viewer = Thread(target=self.viewerVideo.clear_widgets)
        clear_viewer = Thread(target=self.clearing)
        clear_viewer.daemon = True
        clear_viewer.start()

    def clearing(self):
        print(self.viewerVideo.children[:4])
        self.viewerVideo.clear_widgets(self.viewerVideo.children[0:4])
        #self.viewerVideo.remove_widget(self.viewerVideo.children[:4])

    def choose_folder(self, instance):
        print(self.show_popup.path)
        if self.show_popup.path:
            self.path_folder(self.show_popup.path)
        self.directory_window.dismiss()

    # # ---- Functions ---- # #

    def path_folder(self, path='D:/download'):
        self.def_directory = path+"/"
        print(self.def_directory)
        return self.def_directory


class PopU(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.partitions_caption = os.popen('wmic logicaldisk get caption').read()
        self.partitions_caption = self.partitions_caption.split()
        self.partitions_caption.remove('Caption')
        print(self.partitions_caption)
        self.partitions_btn = GridLayout(cols=10, rows=1, size_hint_y=0.1, spacing=2)
        for partition in self.partitions_caption:
            self.part_btn = Button(text=partition, id=partition+"\\")
            #self.part_btn.bind(on_release=lambda *args: self.change_main_direct(self.part_btn.id, *args))
            self.part_btn.bind(on_release=partial(self.change_main_direct, self.part_btn.id))
            #print(self.part_btn.id)
            self.partitions_btn.add_widget(self.part_btn)

        self.add_widget(self.partitions_btn)

        self.file_chooser_list = FileChooserIconView(size_hint_y=0.8)
        self.file_chooser_list.dirselect = True
        self.file_chooser_list.bind(selection=self.on_select)
        self.file_chooser_list.path = "D:\\"

        """self.file_chooser_list = FileChooserListView(size_hint_y=0.8)
        self.file_chooser_list.dirselect = True
        self.file_chooser_list.bind(selection=self.on_select)
        self.file_chooser_list.path = "D:\\"""

        self.buttons_grid = GridLayout(cols=2, rows=1, size_hint_y=0.1, spacing=2)
        self.load_btn = Button(text="Select", size_hint=(0.4, 0.1))
        self.cancel_btn = Button(text="Cancel", size_hint=(0.4, 0.1))

        self.buttons_grid.add_widget(self.load_btn)
        self.buttons_grid.add_widget(self.cancel_btn)

        self.orientation = 'vertical'
        self.add_widget(self.file_chooser_list)
        self.add_widget(self.buttons_grid)
        self.path = ""

    def on_select(self, instance, obj):
        try:
            if self.file_chooser_list.selection:
                self.path = self.file_chooser_list.selection[0]
                print(self.path)
        except Exception as e:
            print(f"Selecting Directory, Error: {e} ")


    def change_main_direct(self, path, *instance):
        print(path)
        try:
            self.file_chooser_list.path = path
        except Exception as e:
            print(f"Changing Path: error:{e}")


class YoutubeDownloader(App):
    def build(self):
        self.screen_manager = ScreenManager()

        self.home_page = HomePage()
        screen = Screen(name="Home")
        screen.add_widget(self.home_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

    def stop(self, *args):
        self.root_window.close()  # Fix app exit on Android.
        return super(YoutubeDownloader, self).stop(*args)


if __name__ == "__main__":
    YoutubeDownloader().run()
