import os
import math
from MergeVA import MergeVA
import re
from pytube import Playlist
from pytube import YouTube
from pytube.compat import unicode
from kivy.uix.label import Label
#import arabic_reshaper
#import bidi.algorithm


class Downloader:
    def __init__(self, percentage_download_label, viewer_video, def_directory):
        self.playlistLen = 0
        self.folder_path = ""
        self.total_size = 1
        self.max_qualities = ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']
        self.min_qualities = self.max_qualities[::-1]
        self.percentageDownload = 0
        self.percentageDownload_label = percentage_download_label
        self.viewerVideo = viewer_video
        self.video_label2 = Label(text="0 %", color=(0.5, 0.5, 0.5, 1),
                                         size_hint_y=None, height=40,
                                 halign="right", valign="middle")
        self.def_directory = def_directory
        self.kill_download = False
    def exit_my_prog(self):
        exit()

    def set_kill_download(self, kill):
        self.kill_download = kill

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
                print(self.kill_download)
                if self.kill_download:
                    return
                self.total_size = 1
                try:
                    yt = YouTube("https://www.youtube.com/" + x)
                    y_title = self.filename(yt.title)
                    yt.register_on_progress_callback(self.show_progress_bar)
                    video_name = self.get_cnt(counter) + y_title
                    video_path = video_name + "_v"
                    audio_path = video_name + "_a"

                    if quality_max.text == 'Max Quality':
                        quality_max.text = '2160p'
                    if quality_min.text == 'Min Quality':
                        quality_min.text = '144p'

                    mx_idx = self.max_qualities.index(quality_max.text)
                    mn_idx = self.max_qualities.index(quality_min.text)

                    # ---- Adding Label of Video Title --------
                    test = f' {y_title}   '
                    print(test)
                    #reshaped_text = arabic_reshaper.reshape(test)
                    #display_text = bidi.algorithm.get_display(reshaped_text)
                    self.video_label = Label(text=f"{counter}. {test}", color=(1, 0.9, 1, 1),
                        size_hint_y=None, height=60, halign="left", valign="middle",
                                        size_hint_x=0.6, font_name='Arial')
                    self.video_label.bind(size=self.video_label.setter('text_size'))
                    self.viewerVideo.height += self.video_label.height*2
                    self.viewerVideo.add_widget(self.video_label)

                    self.video_folder = Label(text=self.def_directory+folder_name, color=(1, 0.9, 1, 1),
                                              size_hint_y=None,
                                              height=40, halign="left", valign="middle",
                                              size_hint_x=0.2)
                    self.video_folder.bind(size=self.video_folder.setter('text_size'))
                    self.viewerVideo.add_widget(self.video_folder)

                    self.video_label2 = Label(text="", color=(1, 0.9, 1, 1),
                                         size_hint_y=None,
                                    height=40, halign="left", valign="middle",
                                              size_hint_x=0.1)
                    self.video_label2.bind(size=self.video_label2.setter('text_size'))
                    self.viewerVideo.add_widget(self.video_label2)

                    test2 = f"0 %"
                    self.video_label3 = Label(text=test2, color=(1, 0.9, 1, 1),
                                         size_hint_y=None,
                                    height=40, halign="right", valign="middle",
                                              size_hint_x=0.1)
                    self.video_label3.bind(size=self.video_label3.setter('text_size'))
                    self.viewerVideo.add_widget(self.video_label3)

                    # ---------------------------------------------------

                    file_extension_video = ""
                    video_done = False
                    audio_done = False
                    merge_done = False

                    if self.kill_download:
                        return
                    print(mx_idx, mn_idx)
                    if mx_idx > mn_idx:
                        mx_idx = mn_idx
                    for i in range(mx_idx, mn_idx+1):
                        try:
                            self.video_label2.text = self.max_qualities[i]
                            yt.streams.filter(adaptive=True, res=self.max_qualities[i]).first(). \
                                download(self.folder_path, filename=video_path)
                            sss = [stream.subtype for stream in
                                   yt.streams.filter(adaptive=True, res=self.max_qualities[i]).all()]
                            file_extension_video = sss[0]
                            video_done = True
                            break
                        except Exception as e:
                            print(f"Quality does not exist'|  {e}  |Quality:{self.max_qualities[i]}")

                    if video_done:
                        try:
                            yt.streams.filter(adaptive=True, only_audio=True).first().download(self.folder_path,
                                                                                               filename=audio_path)
                            sss2 = [stream.subtype for stream in yt.streams.filter(adaptive=True, only_audio=True).all()]
                            print(sss2)
                            file_extension_audio = sss2[0]
                            audio_done = True
                        except Exception as e:
                            print(f"audio does not exist' {e}")

                    if audio_done and video_done:
                        if MergeVA.merge_va(isinstance, f"{self.folder_path}/{video_path}.{file_extension_video}",
                                         f"{self.folder_path}/{audio_path}.{file_extension_audio}",
                                         f"{self.folder_path}/{video_name}.mkv"):
                            merge_done = True
                        else:
                            merge_done = False

                    # ---- Changing Label Color if Video is downloaded --------
                    if merge_done:
                        self.video_label.color = (0.13, 0.83, 0.25, 1)
                    else:
                        self.video_label.color = (1, 0, 0, 1)
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
                    #self.video_label.color = (1, 0, 0, 1)
                finally:
                    try:
                        os.remove(f"{self.folder_path}/{video_path}.{file_extension_video}")
                        os.remove(f"{self.folder_path}/{audio_path}.{file_extension_audio}")
                    except Exception as e:
                        print(f"can't Remove |  {e} ")
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
        self.video_label3.text = f"{self.percentageDownload} %"
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

