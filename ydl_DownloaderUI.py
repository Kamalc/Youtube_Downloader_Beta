import os
import math
import re
from threading import Thread
from kivy.config import Config
Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import AsyncImage
from kivy.uix.filechooser import FileChooser, FileChooserListView, FileChooserIconView
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from ydl_Downloader import Down
from functools import partial
from multiprocessing import Process

Window.borderless = 0
Window.clearcolor = (0.17, 0.17, 0.17, 1)
Window.size = (850, 400)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


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
                                        size_hint_x=0.4, size_hint_y=.2, color=(0.18, 0.49, 0.60, 1)))
        self.percentageDownload_label = Label(text=f"{self.percentageDownload} %",
                                              font_size=20,
                                              size_hint_x=0.2, size_hint_y=0.2, color=(0.18, 0.49, 0.60, 1))
        self.upperGrid.add_widget(self.percentageDownload_label)
        self.add_widget(self.upperGrid)

        self.play_link = TextInput(multiline=False, size_hint_y=0.15)
        self.add_widget(self.play_link)

        self.midGrid = GridLayout(cols=5)
        self.add_widget(self.midGrid)
        self.midGrid.orientation = 4, 'vertical'
        self.midGrid.size_hint_y = 0.21

        self.q_drop_down_max = DropDown()
        self.q_drop_down_min = DropDown()
        self.q_drop_down_sub = DropDown()

        self.max_qualities = ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']
        self.min_qualities = self.max_qualities[::-1]

        self.quality_max = Button(text='Max Quality', size_hint=(None, None), height='48dp', color=(0.22, 0.63, 0.78, 1))
        self.quality_max.bind(on_release=self.q_drop_down_max.open)
        self.q_drop_down_max.bind(on_select=lambda instance, q: setattr(self.quality_max, 'text', q))
        for quality in self.max_qualities:
            btn1 = Button(text=quality, size_hint_y=None, height=48, color=(0.22, 0.63, 0.78, 1))
            btn1.bind(on_release=lambda btn1: self.q_drop_down_max.select(btn1.text))
            self.q_drop_down_max.add_widget(btn1)
        self.midGrid.add_widget(self.quality_max)

        self.quality_min = Button(text='Min Quality', size_hint=(None, None), height='48dp', color=(0.22, 0.63, 0.78, 1))
        self.quality_min.bind(on_release=self.q_drop_down_min.open)
        self.q_drop_down_min.bind(on_select=lambda instance, q: setattr(self.quality_min, 'text', q))
        for quality in self.min_qualities:
            btn2 = Button(text=quality, size_hint_y=None, height=48, color=(0.22, 0.63, 0.78, 1))
            btn2.bind(on_release=lambda btn2: self.q_drop_down_min.select(btn2.text))
            self.q_drop_down_min.add_widget(btn2)
        self.midGrid.add_widget(self.quality_min)

        self.v_download = Button(text="Download", size_hint_x=0.6, color=(0.22, 0.63, 0.78, 1),
                                 font_size=20)

        self.v_download.bind(on_press=self.start_download)
        self.midGrid.add_widget(self.v_download)

        self.directory_btn = Button(text="Browse", size_hint_x=0.1, color=(0.22, 0.63, 0.78, 1))
        self.directory_btn.bind(on_release=self.choose_directory)
        self.midGrid.add_widget(self.directory_btn)

        self.viewer_header = GridLayout(cols=6, size_hint_y=0.1, spacing=10, padding=2)
        self.img_header_label = Label(text="Thumbnail", size_hint_x=0.1, color=(0.18, 0.49, 0.60, 1))
        self.viewer_header.add_widget(self.img_header_label)
        self.name_header_label = Label(text="Name", size_hint_x=0.4, color=(0.18, 0.49, 0.60, 1))
        self.viewer_header.add_widget(self.name_header_label)
        self.q_header_label = Label(text="Quality", size_hint_x=0.06, color=(0.18, 0.49, 0.60, 1))
        self.viewer_header.add_widget(self.q_header_label)
        self.dir_header_label = Label(text="Folder Path", size_hint_x=0.1, color=(0.18, 0.49, 0.60, 1))
        self.viewer_header.add_widget(self.dir_header_label)
        self.size_header_label = Label(text="Size", size_hint_x=0.1, color=(0.18, 0.49, 0.60, 1))
        self.viewer_header.add_widget(self.size_header_label)
        self.per_header_label = Label(text="Percentage", size_hint_x=0.1, color=(0.18, 0.49, 0.60, 1))
        self.viewer_header.add_widget(self.per_header_label)
        self.add_widget(self.viewer_header)

        self.scroll = ScrollView()

        self.viewerVideo = GridLayout(cols=6, size_hint_y=None, spacing=10, height=600, padding=2)

        self.scroll.add_widget(self.viewerVideo)

        self.add_widget(self.scroll)

        self.lower_grid = GridLayout(cols=2, size_hint_y=0.1)
        self.clear_btn = Button(text="Clear", color=(0.22, 0.63, 0.78, 1))
        self.clear_btn.bind(on_press=self.clear_viewer)
        self.stop_btn = Button(text="Pause Download", color=(0.22, 0.63, 0.78, 1))
        self.stop_btn.bind(on_release=self.stop_fn_btn)
        self.lower_grid.add_widget(self.clear_btn)
        self.lower_grid.add_widget(self.stop_btn)

        self.add_widget(self.lower_grid)
        # --- Pop Up Screen -------------------------------------------
        self.directory_window = Popup(title="Directory", content=self.show_popup, size_hint=(None, None),
                                      size=(500, 400), title_color=(0.18, 0.49, 0.60, 1))
        self.show_popup.cancel_btn.bind(on_release=self.directory_window.dismiss)
        self.show_popup.select_btn.bind(on_release=self.choose_folder)
        self.show_popup.path_Text.text = self.def_directory
        self.show_popup.file_chooser_list.path = self.def_directory
        self.kill_download = False
        # -------------------------------------------------------------
        self.downloader = Down(self.percentageDownload_label, self.viewerVideo, self.def_directory)
        self.download = Process()
        self.download2 = Process()
        self.paused = False
    # ...............................................................................
    # # -- Event Functions -- # #

    def on_select(self):
        t = Thread(target=self.stop_btn)
        t.daemon = True
        t.start()

    def stop_fn_btn(self, instance):
        if not self.paused:
            self.stop_btn.text = "Resume Download"
            self.paused = True
            #self.download2.terminate()
        else:
            self.stop_btn.text = "Pause Download"
            self.paused = False
            #self.download2.start()

    def choose_directory(self, instance):
        self.directory_window.open()

    def start_download(self, instance):
        if self.quality_max.text == 'Max Quality':
            self.quality_max.text = '2160p'
        if self.quality_min.text == 'Min Quality':
            self.quality_min.text = '144p'
        if self.play_link.text:
            self.download = Thread(target=self.downloader.download,
                                    args=(self.play_link.text,
                                          self.def_directory,
                                          self.quality_max.text,
                                          self.quality_min.text))
            print("Downloading")
            self.download.daemon = True
            #self.download2 = Process(target=self.download)
            self.download.start()
        else:
            print("No input to download")

    def clear_viewer(self, instance):
        clear_viewer = Thread(target=self.viewerVideo.clear_widgets)
        #clear_viewer = Thread(target=self.clearing)
        clear_viewer.daemon = True
        clear_viewer.start()

    def clearing(self):
        print(self.viewerVideo.children[:4])
        self.viewerVideo.clear_widgets(self.viewerVideo.children[0:4])
        #self.viewerVideo.remove_widget(self.viewerVideo.children[:4])

    def choose_folder(self, instance):
        print(self.show_popup.path_Text.text)
        if self.show_popup.path_Text.text:
            self.path_folder(self.show_popup.path_Text.text)
        self.directory_window.dismiss()

    # # ---- Functions ---- # #

    def path_folder(self, path='D:/download'):
        self.def_directory = path  # +"/"
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
            self.part_btn = Button(text=partition, id=partition+"\\", color=(0.22, 0.63, 0.78, 1))
            #self.part_btn.bind(on_release=lambda *args: self.change_main_direct(self.part_btn.id, *args))
            self.part_btn.bind(on_release=partial(self.change_main_direct, self.part_btn.id))
            #print(self.part_btn.id)
            self.partitions_btn.add_widget(self.part_btn)

        self.add_widget(self.partitions_btn)

        self.text_btn_grid = GridLayout(cols=1, rows=1, size_hint=(1, 0.09), spacing=5, padding=1)
        self.path_Text = TextInput(multiline=False, size_hint_x=1, font_size=11)
        #self.change_design_btn = Button(text="Lists", size_hint_x=0.2)
        #self.change_design_btn.bind(on_release=self.change_design_fn)
        self.text_btn_grid.add_widget(self.path_Text)
        #self.text_btn_grid.add_widget(self.change_design_btn)
        self.add_widget(self.text_btn_grid)

        self.file_chooser_list = FileChooserIconView(size_hint_y=0.8)
        self.file_chooser_list.dirselect = True
        self.file_chooser_list.bind(selection=self.on_select)
        self.file_chooser_list.path = "D:\\"
        self.add_widget(self.file_chooser_list)

        self.buttons_grid = GridLayout(cols=2, rows=2, size_hint_y=0.1, spacing=2)
        self.select_btn = Button(text="Select", size_hint=(0.4, 0.1), color=(0.22, 0.63, 0.78, 1))
        self.cancel_btn = Button(text="Cancel", size_hint=(0.4, 0.1), color=(0.22, 0.63, 0.78, 1))

        self.buttons_grid.add_widget(self.select_btn)
        self.buttons_grid.add_widget(self.cancel_btn)

        self.orientation = 'vertical'
        self.add_widget(self.buttons_grid)
        self.path = ""

    def on_select(self, instance, obj):
        try:
            if self.file_chooser_list.selection:
                self.path = self.file_chooser_list.selection[0]
                self.path_Text.text = self.path+"\\"
                print(self.path)
        except Exception as e:
            print(f"Selecting Directory, Error: {e} ")


    def change_main_direct(self, path, *instance):
        print(path)
        try:
            self.file_chooser_list.path = path
            self.path_Text.text = path
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
