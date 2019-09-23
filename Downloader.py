import os
import math
from MergeVA import MergeVA
import re
from pytube import Playlist
from pytube import YouTube
from pytube.compat import unicode
from kivy.uix.label import Label
import arabic_reshaper
import bidi.algorithm

class Downloader:
    def __init__(self, percentage_download_label, viewer_video):
        self.playlistLen = 0
        self.folder_path = ""
        self.total_size = 1
        self.max_qualities = ['2160p', '1440p', '1080p', '720p', '480p', '360', '240p', '144p']
        self.min_qualities = self.max_qualities[::-1]
        self.percentageDownload = 0
        self.percentageDownload_label = percentage_download_label
        self.viewerVideo = viewer_video
        self.video_label2 = Label(text="0 %", color=(0.5, 0.5, 0.5, 1),
                                         size_hint_y=None, height=40,
                                 halign="right", valign="middle")

    def playlist_download(self, play_list_link, folder_path, quality_max, quality_min):
        self.folder_path = folder_path
        playlist_url = play_list_link
        if playlist_url:
            pl = Playlist(playlist_url)
            folder_name = self.filename(pl.title())
            video_list = pl.parse_links()
            self.playlistLen = len(video_list)
            self.folder_path += folder_name
            self.create_new_folder(self.folder_path)
            counter = 1
            for x in video_list:
                self.total_size = 1
                try:
                    yt = YouTube("https://www.youtube.com/" + x)
                    y_title = self.filename(yt.title)
                    yt.register_on_progress_callback(self.show_progress_bar)
                    video_name = self.get_cnt(counter) + y_title
                    video_path = video_name + "_v"
                    audio_path = video_name + "_a"

                    mx_idx = self.max_qualities.index(quality_max)
                    mn_idx = self.max_qualities.index(quality_min)

                    # ---- Adding Label of Video Title --------
                    test = f" {y_title}   "
                    print(test)
                    reshaped_text = arabic_reshaper.reshape(test)
                    display_text = bidi.algorithm.get_display(reshaped_text)
                    video_label = Label(text=f"{counter}. {display_text}", color=(1, 0.5, 1, 1),
                        size_hint_y=None, height=60, halign="left", valign="middle", font_name='Arial')
                    video_label.bind(size=video_label.setter('text_size'))
                    self.viewerVideo.height += video_label.height*2
                    self.viewerVideo.add_widget(video_label)
                    test2 = f"0 %"
                    self.video_label2 = Label(text=test2, color=(0.5, 0.5, 0.5, 1),
                                         size_hint_y=None, height=40, halign="right", valign="middle")
                    self.video_label2.bind(size=self.video_label2.setter('text_size'))
                    self.viewerVideo.add_widget(self.video_label2)
                    # ---------------------------------------------------

                    file_extension_video = ""

                    for i in range(mx_idx, mn_idx):
                        try:
                            yt.streams.filter(adaptive=True, res=self.max_qualities[i]).first(). \
                                download(self.folder_path, filename=video_path)
                            sss = [stream.subtype for stream in
                                   yt.streams.filter(adaptive=True, res=self.max_qualities[i]).all()]
                            file_extension_video = sss[0]
                            break
                        except Exception as e:
                            # i += 1
                            print(f"Quality does not exist'|  {e}  |Quality:{self.max_qualities[i]}")

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

                    # ---- Changing Label Color if Video is downloaded --------
                    video_label.color = (0.13, 0.83, 0.25, 1)
                    # ---------------------------------------------------------

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
                    # ---- Changing Label Color if Video is not downloaded ----
                    video_label.color = (1, 0, 0, 1)
                    # ---------------------------------------------------------
                counter += 1

    def download_video(self):
        video_link = YouTube(self.V_link.text)
        video_link.register_on_progress_callback(self.show_progress_bar)
        video_link.streams.filter(only_audio=True).first().download('D:/download')

    def show_progress_bar(self, stream, chunk, file_handle, bytes_remaining):
        self.total_size = max(bytes_remaining, self.total_size)
        self.percentageDownload = int(100 - (bytes_remaining / self.total_size * 100))
        self.percentageDownload_label.text = f"{self.percentageDownload} %"
        self.video_label2.text = f"{self.percentageDownload} %"
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

    def filename(self, s="", max_length=255):
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

