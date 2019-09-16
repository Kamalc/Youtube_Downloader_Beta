import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager
import pytube
from pytube import Playlist
from pytube import YouTube
from threading import Thread
import os

class HomePage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total_size = 1
        self.percentageDownload = 0
        self.playlist = False
        self.cols = 3
        self.row = 2

        self.add_widget(Label(text="PlayList Link:"))

        self.PL_link = TextInput(multiline=False)
        self.add_widget(self.PL_link)

        self.pl_download = Button(text="Download")
        self.pl_download.bind(on_press=self.start_download)
        self.add_widget(self.pl_download)

        self.add_widget(Label(text="Video Link:"))

        self.V_link = TextInput(multiline=False)
        self.add_widget(self.V_link)

        self.v_download = Button(text="Download")
        self.v_download.bind(on_press=self.start_download)
        self.add_widget(self.v_download)

        self.add_widget(Label())
        self.percentageDownload_label = Label(text=f"{self.percentageDownload} %")
        self.add_widget(self.percentageDownload_label)

    def start_download(self, instance):
        if not self.playlist:
            download = Thread(target=self.downloadV_button)
        else:
            download = Thread(target=self.downloadPL_button)
        download.start()


    def downloadPL_button(self):
        print("DownloadingPlayList")
        #video_link = YouTube(self.V_link.text)
        #video_link.streams.filter(progressive=True).first().download('D:/download')


    def downloadV_button(self):
        print("DownloadingVideo")
        video_link = YouTube(self.V_link.text)
        video_link.register_on_progress_callback(self.show_progress_bar)
        video_link.streams.filter(progressive=True).first().download('D:/download')



    def show_progress_bar(self,stream, chunk, file_handle, bytes_remaining):
        self.total_size = max(bytes_remaining, self.total_size)
        self.percentageDownload = int(100 - (bytes_remaining / self.total_size * 100))
        self.percentageDownload_label.text = f"{self.percentageDownload} %"
        print(f"{self.percentageDownload} %")
        return

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