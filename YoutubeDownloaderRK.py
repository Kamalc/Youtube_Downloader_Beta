from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from kivy.core.window import Window
from pytube import Playlist
from pytube import YouTube
from pytube.compat import unicode
import math
import re
import os
from threading import Thread
from MergeVA import MergeVA

# ---- Windows Settings UI ---------------------------
Window.clearcolor = (0.17, 0.17, 0.17, 1)
Window.size = (600, 400)
Config.set('graphics', 'resizable', False)
# -----------------------------------------------------


# -------- Download PlayList (Home Page) --------------


class DownloadPlayList(BoxLayout):
    # ------ UI Variable ------------------------------
    quality = ObjectProperty(None)
    link = ObjectProperty(None)
    percentage = ObjectProperty(None)
    btn = ObjectProperty(None)

    # ----- Global Variable (Self) --------------------
    playlistLen = 0
    total_size = 1
    folder_path = ""
    thread = Thread()

    # --------- Event Functions ------------------------
    #def __init__(self, **kwargs):
    #    super(BoxLayout, self).__init__(**kwargs)
    #    self.btn.bind(on_press=self.start_download_btn)

    def start_download_btn(self):
        print("0")
        self.thread = Thread(target=self.download())
        print("1")
        self.thread.start()
        print("2")
        print(self.thread.is_alive(), self.thread.isAlive())
        self.thread.join()
        print("3")

    # --------

    def get_quality(self):
        return self.quality.text

    def download(self):
        print(self.get_quality())
        playlist_url = self.link.text
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
                    video_path = video_name+"_v"
                    audio_path = video_name+"_a"
                    yt.streams.filter(adaptive=True, only_audio=True).first().download(self.folder_path, filename=audio_path)
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
                        my_file = open(self.folder_path + '/' + self.get_cnt(counter) + y_title + ".srt", "w+", encoding='UTF8')
                        my_file.writelines(caption.generate_srt_captions())
                        my_file.close()
                    else:
                        print("No Sub Found")
                except Exception as e:
                    print("Can't Download: " + str(e))

                counter += 1

    def create_new_folder(self, directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print('Error: Creating Folder. ' + directory)

    def show_progress_bar(self, stream, chunk, file_handle, bytes_remaining):
        self.total_size
        self.total_size = max(bytes_remaining, self.total_size)
        self.percentage.text = str(int(100 - (bytes_remaining / self.total_size * 100))) + " %"
        print(str(int(100 - (bytes_remaining / self.total_size * 100))) + "%")
        return

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


class Downloader(App):
    def build(self):
        return DownloadPlayList()


if __name__ == "__main__":
    Downloader().run()


