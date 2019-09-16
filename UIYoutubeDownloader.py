#import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button


class YoutubeDownloader(App):
    def Build(self):
        return Label(text="YoutubeDownloader")


if __name__ == "__main__":
    YoutubeDownloader().run()