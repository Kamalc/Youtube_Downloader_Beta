import os
import sys
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
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.graphics import Rectangle, Color
from kivy.uix.image import AsyncImage
from kivy.uix.filechooser import FileChooser, FileChooserListView, FileChooserIconView
from HoverButton import HoverButton
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from ydl_Downloader import Down
from functools import partial
from MyThread import BaseThread, terminate_thread
from Options import get_list_sub, update_list_sub, get_directory, update_directory, \
    get_speed_unit, get_speed_limit

Window.borderless = 0
Window.clearcolor = (0.17, 0.17, 0.17, 1)
Window.size = (850, 400)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
# --------------------------------------------------------
# sys.stdout = open('log', 'w')


class HomePage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    # ............................Default Variables...........................
        self.percentageDownload = 0
        self.playlist = False
        self.playlist_url_dp = ""
        self.directory_window = Popup()
        self.show_popup_directory = PopDirectory()
        self.show_popup_options = PopOptions()
        # ........................................................................
    # UI Design
        self.orientation, self.font_size, self.spacing, self.padding = 'vertical', 15, 5, 5

        self.upperGrid = GridLayout()
        self.upperGrid.orientation = 'horizontal'
        self.upperGrid.cols = 3
        self.upperGrid.size_hint_y = 0.30

        self.options_btn = HoverButton(text="Settings", size_hint_x=0.2, font_size=25,
                                       color=(0.22, 0.63, 0.78, 1),
                                       background_color=(0.35, 0.35, 0.35, 1))
        self.options_btn.disabled = False
        self.options_btn.bind(on_release=self.open_options)
        self.upperGrid.add_widget(self.options_btn)
        self.upperGrid.add_widget(Label(text="Youtube Downloader",
                                        font_size=35,
                                        size_hint_x=0.6, size_hint_y=.2, color=(0.18, 0.49, 0.60, 1)))
        self.upperLeftGrid = GridLayout(cols=1, rows=2, size_hint_x=0.2)
        self.speed_header_label = Label(text=f"Speed",
                                        font_size=15, size_hint_y=0.5, color=(0.18, 0.49, 0.60, 1))
        self.speed_label = Label(text=f"_._KB/s",
                                 font_size=20, size_hint_y=0.5, color=(0.22, 0.63, 0.78, 1))
        self.upperLeftGrid.add_widget(self.speed_header_label)
        self.upperLeftGrid.add_widget(self.speed_label)
        self.upperGrid.add_widget(self.upperLeftGrid)
        self.add_widget(self.upperGrid)

        self.play_link = TextInput(multiline=False, size_hint=(1, 0.16))
        self.play_link.hint_text = "Put Url Video or Playlist Here"
        self.add_widget(self.play_link)

        self.grid_link_status = GridLayout(cols=4, size_hint=(1, 0.1))
        self.dir_label = Label(text=get_directory(), size_hint=(0.74, 1), halign='left',
                               color=(0.22, 0.63, 0.78, 1))
        self.dir_label.bind(size=self.dir_label.setter('text_size'))
        self.open_dir_folder_btn = HoverButton(text="F", font_size=18, size_hint=(0.04, 0.85),
                                               color=(0.22, 0.63, 0.78, 1),
                                               background_color=(0.35, 0.35, 0.35, 1))
        self.open_dir_folder_btn.bind(on_release=self.open_dir_folder_btn_fn)
        self.status = Label(text="Status", size_hint=(0.2, 1), halign='left',
                            color=(0.13, 0.83, 0.25, 1), font_size=18)
        self.grid_link_status.add_widget(self.dir_label)
        self.grid_link_status.add_widget(self.open_dir_folder_btn)
        self.grid_link_status.add_widget(Label(text="|", size_hint=(0.02, 1),
                                               color=(0.22, 0.63, 0.78, 1)))
        self.grid_link_status.add_widget(self.status)
        self.add_widget(self.grid_link_status)

        self.midGrid = GridLayout(cols=6)
        self.add_widget(self.midGrid)
        self.midGrid.orientation = 4, 'vertical'
        self.midGrid.size_hint_y = 0.21

        self.q_drop_down_max = DropDown()
        self.q_drop_down_min = DropDown()
        self.q_drop_down_sub = DropDown()

        self.max_qualities = ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']
        self.min_qualities = self.max_qualities[::-1]

        self.quality_max = HoverButton(text='Max Quality', size_hint=(None, None), height='48dp',
                                       color=(0.22, 0.63, 0.78, 1), background_color=(0.35, 0.35, 0.35, 1))
        self.quality_max.bind(on_release=self.q_drop_down_max.open)
        self.q_drop_down_max.bind(on_select=lambda instance, q: setattr(self.quality_max, 'text', q))
        for quality in self.max_qualities:
            btn1 = HoverButton(text=quality, size_hint_y=None, height=48, color=(0.22, 0.63, 0.78, 1)
                               , background_color=(0.35, 0.35, 0.35, 1))
            btn1.bind(on_release=lambda btn1: self.q_drop_down_max.select(btn1.text))
            self.q_drop_down_max.add_widget(btn1)
        self.midGrid.add_widget(self.quality_max)

        self.quality_min = HoverButton(text='Min Quality', size_hint=(None, None), height='48dp',
                                       color=(0.22, 0.63, 0.78, 1), background_color=(0.35, 0.35, 0.35, 1))
        self.quality_min.bind(on_release=self.q_drop_down_min.open)
        self.q_drop_down_min.bind(on_select=lambda instance, q: setattr(self.quality_min, 'text', q))
        for quality in self.min_qualities:
            btn2 = HoverButton(text=quality, size_hint_y=None, height=48, color=(0.22, 0.63, 0.78, 1)
                               , background_color=(0.35, 0.35, 0.35, 1))
            btn2.bind(on_release=lambda btn2: self.q_drop_down_min.select(btn2.text))
            self.q_drop_down_min.add_widget(btn2)
        self.midGrid.add_widget(self.quality_min)

        self.grid_audio_checker = GridLayout(cols=1, rows=2, size_hint_x=0.05)
        self.audio_checker = CheckBox()
        self.grid_audio_checker.add_widget(Label(text="MP3", color=(0.18, 0.49, 0.60, 1)))
        self.grid_audio_checker.add_widget(self.audio_checker)
        self.midGrid.add_widget(self.grid_audio_checker)

        self.v_download = HoverButton(text="Download", size_hint_x=0.6, color=(0.22, 0.63, 0.78, 1),
                                      font_size=20, background_color=(0.35, 0.35, 0.35, 1))

        self.v_download.bind(on_press=self.start_download)
        self.midGrid.add_widget(self.v_download)

        self.browse_btn = HoverButton(text="Browse", size_hint_x=0.1, color=(0.22, 0.63, 0.78, 1)
                                      , background_color=(0.35, 0.35, 0.35, 1))
        self.browse_btn.bind(on_release=self.choose_directory)
        self.midGrid.add_widget(self.browse_btn)

        self.viewer_header = GridLayout(cols=7, size_hint_y=0.2, spacing=10, padding=2)
        self.img_header_label = Label(text="Thumbnail", size_hint_x=0.1, color=(0.18, 0.49, 0.60, 1))
        self.viewer_header.add_widget(self.img_header_label)
        self.name_header_label = Label(text="Name", size_hint_x=0.4, color=(0.18, 0.49, 0.60, 1),
                                       halign='left')
        self.viewer_header.add_widget(self.name_header_label)
        self.q_header_label = Label(text="Quality", size_hint_x=0.06, color=(0.18, 0.49, 0.60, 1))
        self.viewer_header.add_widget(self.q_header_label)
        self.dir_header_label = Label(text="ETA", size_hint_x=0.05, color=(0.18, 0.49, 0.60, 1))
        self.viewer_header.add_widget(self.dir_header_label)
        self.dir_header_label = Label(text="Speed", size_hint_x=0.09, color=(0.18, 0.49, 0.60, 1))
        self.viewer_header.add_widget(self.dir_header_label)
        self.size_header_label = Label(text="Size", size_hint_x=0.1, color=(0.18, 0.49, 0.60, 1))
        self.viewer_header.add_widget(self.size_header_label)
        self.per_header_label = Label(text="  %  ", size_hint_x=0.06, color=(0.18, 0.49, 0.60, 1))
        self.viewer_header.add_widget(self.per_header_label)
        self.add_widget(self.viewer_header)

        self.scroll = ScrollView()

        self.viewerVideo = GridLayout(cols=7, size_hint_y=None, spacing=10, height=600, padding=2)

        self.scroll.add_widget(self.viewerVideo)

        self.add_widget(self.scroll)

        self.lower_grid = GridLayout(cols=2, size_hint_y=0.1)
        self.clear_btn = HoverButton(text="Clear", color=(0.22, 0.63, 0.78, 1)
                                     , background_color=(0.35, 0.35, 0.35, 1))
        self.clear_btn.bind(on_press=self.clear_viewer)
        self.clear_btn.disabled = True
        self.stop_btn = HoverButton(text="Stop Download", color=(0.22, 0.63, 0.78, 1)
                                    , background_color=(0.35, 0.35, 0.35, 1))
        self.stop_btn.bind(on_release=self.stop_fn_btn)
        self.stop_btn.disabled = True
        self.lower_grid.add_widget(self.clear_btn)
        self.lower_grid.add_widget(self.stop_btn)

        self.add_widget(self.lower_grid)
        # --- Pop Up Screens -------------------------------------------
        self.directory_window = Popup(title="Directory", content=self.show_popup_directory, size_hint=(None, None),
                                      size=(500, 400), title_color=(0.18, 0.49, 0.60, 1))
        self.show_popup_directory.cancel_btn.bind(on_release=self.directory_window.dismiss)
        self.show_popup_directory.select_btn.bind(on_release=self.choose_folder)
        self.show_popup_directory.path_Text.text = get_directory()
        self.show_popup_directory.file_chooser_list.path = get_directory()

        self.options_window = Popup(title="Settings", content=self.show_popup_options, size_hint=(None, None),
                                    size=(500, 400), title_color=(0.18, 0.49, 0.60, 1))
        self.show_popup_options.save_btn.bind(on_release=self.save_options_btn)
        self.show_popup_options.cancel_btn.bind(on_release=self.cancel_options_btn)
        # -------------------------------------------------------------
        self.downloader = Down(self.speed_label, self.viewerVideo, self.status)
        self.download = BaseThread
        self.subtitle_checkboxes = []
    # ...............................................................................
    # # -- Event Functions -- # #

    def stop_fn_btn(self, instance):
        terminate_thread(self.download)
        self.enable_fn()

    def start_download(self, instance):
        if self.audio_checker.active:
            self.quality_max.text = 'Max Quality'
            self.quality_min.text = 'Min Quality'
        else:
            if self.quality_max.text == 'Max Quality':
                self.quality_max.text = '1080p'
            if self.quality_min.text == 'Min Quality':
                self.quality_min.text = '144p'
            if int(self.quality_min.text[:-1]) > int(self.quality_max.text[:-1]):
                self.quality_max.text = self.quality_min.text
        if self.play_link.text:
            self.disable_fn()
            self.download = BaseThread(target=self.download_target, callback=self.enable_fn,
                                       callback_args=())
            print("Downloading")
            self.download.daemon = True
            self.download.start()
        else:
            print("No input to download")

    def download_target(self):
        self.downloader.download(self.play_link.text, get_directory(),
                                 self.quality_max.text, self.quality_min.text,
                                 self.audio_checker)

    def clear_viewer(self, instance):
        clear_viewer = Thread(target=self.viewerVideo.clear_widgets)
        clear_viewer.daemon = True
        clear_viewer.start()
        self.clear_btn.disabled = True

    def open_dir_folder_btn_fn(self, instance):
        path = self.dir_label.text
        if os.path.exists(path):
            os.startfile(path)

    """def clearing(self):
        print(self.viewerVideo.children[:4])
        self.viewerVideo.clear_widgets(self.viewerVideo.children[0:4])
        #self.viewerVideo.remove_widget(self.viewerVideo.children[:4])"""

    def disable_fn(self):
        self.v_download.disabled = True
        self.quality_max.disabled = True
        self.quality_min.disabled = True
        self.audio_checker.disabled = True
        self.stop_btn.disabled = False
        self.clear_btn.disabled = True

    def enable_fn(self):
        self.v_download.disabled = False
        self.quality_max.disabled = False
        self.quality_min.disabled = False
        self.audio_checker.disabled = False
        self.stop_btn.disabled = True
        self.clear_btn.disabled = False
        self.status.text = "Status"
        self.speed_label.text = f"_._KB/s"

    # ---- Browse Button --------------------
    def choose_directory(self, instance):
        self.show_popup_directory.path_Text.text = get_directory()
        self.directory_window.open()
    # # ---- Functions (PopUp Directory) ---- # #

    def choose_folder(self, instance):
        print(self.show_popup_directory.path_Text.text)
        if self.show_popup_directory.path_Text.text:
            update_directory(self.show_popup_directory.path_Text.text)
            self.dir_label.text = get_directory()
        self.directory_window.dismiss()
    # ------------------------------------------

    # ---- Browse Button --------------------
    def open_options(self, instance):
        ss = self.show_popup_options.grid_subtitle.children
        self.subtitle_checkboxes = ss[::2]
        self.subtitle_checkboxes = self.subtitle_checkboxes[::-1]
        list_lang_check = get_list_sub()
        for ch, l in zip(self.subtitle_checkboxes, list_lang_check):
            ch.active = l[1]
        self.show_popup_options.change_speed_unit_btn.text = get_speed_unit()
        self.options_window.open()
    # # ---- Functions (PopUp Options) ---- # #

    def save_options_btn(self, instance):
        lang_check = {}
        for l in self.subtitle_checkboxes:
            lang_check[l.id] = l.active
        unit = self.show_popup_options.change_speed_unit_btn.text
        speed_limit = self.show_popup_options.speed_limit.text
        update_list_sub(lang_check, unit, speed_limit)
        self.options_window.dismiss()

    def cancel_options_btn(self, instance):
        self.options_window.dismiss()


class PopDirectory(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.partitions_caption = os.popen('wmic logicaldisk get caption').read()
        self.partitions_caption = self.partitions_caption.split()
        self.partitions_caption.remove('Caption')
        print(self.partitions_caption)
        self.partitions_btn = GridLayout(cols=10, rows=1, size_hint_y=0.1, spacing=2)
        for partition in self.partitions_caption:
            self.part_btn = HoverButton(text=partition, id=partition+"\\", color=(0.22, 0.63, 0.78, 1)
                                        , background_color=(0.35, 0.35, 0.35, 1))
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
        self.select_btn = HoverButton(text="Select", size_hint=(0.4, 0.1), color=(0.22, 0.63, 0.78, 1)
                                      , background_color=(0.35, 0.35, 0.35, 1))
        self.cancel_btn = HoverButton(text="Cancel", size_hint=(0.4, 0.1), color=(0.22, 0.63, 0.78, 1)
                                      , background_color=(0.35, 0.35, 0.35, 1))

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
            print(f"Selecting Directory, Error: {e}.\nLine: {sys.exc_info()[-1].tb_lineno}\n"
                  f"Type Error: {type(e).__name__}")

    def change_main_direct(self, path, *instance):
        print(path)
        try:
            self.file_chooser_list.path = path
            self.path_Text.text = path
        except Exception as e:
            print(f"Changing Path: error: {e}.\nLine: {sys.exc_info()[-1].tb_lineno}\n"
                  f"Type Error: {type(e).__name__}")


class PopOptions(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = 'vertical'

        self.mid_grid = GridLayout(cols=3, rows=4, size_hint_y=0.4, spacing=2, padding=2)
        self.mid_grid.add_widget(Label(text="Default Directory ", size_hint=(0.4, 0.25),
                                       color=(0.18, 0.49, 0.60, 1)))
        self.def_dir_text = TextInput(multiline=False, size_hint=(0.4, 0.25), font_size=15)
        self.def_dir_text.disabled = True
        self.def_dir_text.text = r"C:\Users\Public\Downloads\\"
        self.mid_grid.add_widget(self.def_dir_text)
        self.mid_grid.add_widget(Label(text="", size_hint=(0.1, 0.25),
                                       color=(0.18, 0.49, 0.60, 1)))
        self.mid_grid.add_widget(Label(text="Downloading Speed Limit", size_hint=(0.4, 0.25),
                                       color=(0.18, 0.49, 0.60, 1)))
        self.speed_limit = TextInput(multiline=False, size_hint=(0.4, 0.25), font_size=15)
        self.speed_limit.text = get_speed_limit()
        self.speed_limit.hint_text = r"0 for Unlimited"
        self.mid_grid.add_widget(self.speed_limit)
        self.change_speed_unit_btn = HoverButton(text=get_speed_unit(), size_hint=(0.1, 0.25),
                                                 color=(0.22, 0.63, 0.78, 1),
                                                 background_color=(0.35, 0.35, 0.35, 1))
        self.change_speed_unit_btn.bind(on_release=self.change_unit_fn)
        self.mid_grid.add_widget(self.change_speed_unit_btn)
        self.mid_grid.add_widget(Label(text="Subtitles Languages ", size_hint=(0.4, 0.25),
                                       color=(0.18, 0.49, 0.60, 1)))
        self.def_dir_text = TextInput(multiline=False, size_hint=(0.4, 0.25), font_size=15)
        self.def_dir_text.disabled = True
        self.def_dir_text.hint_text = "ex:  en, ar, es, ..., etc"
        self.mid_grid.add_widget(self.def_dir_text)
        self.mid_grid.add_widget(Label(text="", size_hint=(0.1, 0.25),
                                       color=(0.18, 0.49, 0.60, 1)))
        self.mid_grid.add_widget(Label(text="Subtitles Languages ", size_hint=(0.4, 0.25),
                                       color=(0.18, 0.49, 0.60, 1)))
        self.def_dir_text = TextInput(multiline=False, size_hint=(0.4, 0.25), font_size=15)
        self.def_dir_text.disabled = True
        self.def_dir_text.hint_text = "ex:  en, ar, es, ..., etc"
        self.mid_grid.add_widget(self.def_dir_text)
        self.mid_grid.add_widget(Label(text="", size_hint=(0.1, 0.25),
                                       color=(0.18, 0.49, 0.60, 1)))

        self.add_widget(self.mid_grid)

        self.header_scroll = GridLayout(cols=3, size_hint=(1, 0.1), padding=3)
        self.header_scroll.add_widget(Label(text="Subtitle Language", size_hint_x=0.4,
                                            font_size=18,
                                            color=(0.18, 0.49, 0.60, 1)))
        self.checkall_btn = HoverButton(text="All", size_hint_x=0.1,
                                        color=(0.18, 0.49, 0.60, 1), background_color=(0.35, 0.35, 0.35, 1))
        self.checkall_btn.bind(on_release=self.checkall_btn_fn)
        self.header_scroll.add_widget(self.checkall_btn)
        self.header_scroll.add_widget(Label(text="", font_size=18, size_hint_x=0.5,
                                            color=(0.18, 0.49, 0.60, 1)))
        self.add_widget(self.header_scroll)

        self.scroll_language = ScrollView(size_hint=(0.5, 0.4))
        size_of_sub_list = (len(get_list_sub()) + 8) * 20
        self.grid_subtitle = GridLayout(cols=2, size_hint=(1, None), spacing=10, height=size_of_sub_list)
        for s in get_list_sub():
            lang_name = Label(text=s[0], size_hint=(0.8, None), height=20, color=(0.22, 0.63, 0.78, 1))
            lang_check = CheckBox(id=s[0], size_hint=(0.2, None), height=20,)
            self.grid_subtitle.add_widget(lang_name)
            self.grid_subtitle.add_widget(lang_check)
        self.scroll_language.add_widget(self.grid_subtitle)
        self.add_widget(self.scroll_language)

        self.lower_grid = GridLayout(cols=2, rows=1, size_hint_y=0.1, spacing=5, padding=2)
        self.save_btn = HoverButton(text="Save", size_hint=(0.4, 0.1), color=(0.22, 0.63, 0.78, 1)
                                    , background_color=(0.35, 0.35, 0.35, 1))
        self.cancel_btn = HoverButton(text="Cancel", size_hint=(0.4, 0.1), color=(0.22, 0.63, 0.78, 1)
                                      , background_color=(0.35, 0.35, 0.35, 1))
        self.lower_grid.add_widget(self.save_btn)
        self.lower_grid.add_widget(self.cancel_btn)

        self.add_widget(self.lower_grid)
        self.allTrue = False

    def checkall_btn_fn(self, instance):
        chl = self.grid_subtitle.children
        checklist = chl[::2]
        for ch in checklist:
            if not self.allTrue:
                ch.active = True
            else:
                ch.active = False
        if self.allTrue:
            self.allTrue = False
        else:
            self.allTrue = True

    def change_unit_fn(self, instance):
        unit = self.change_speed_unit_btn.text
        if unit == "KB":
            self.change_speed_unit_btn.text = "MB"
        else:
            self.change_speed_unit_btn.text = "KB"


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



