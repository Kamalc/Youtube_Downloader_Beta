from __future__ import unicode_literals
import youtube_dl
import os
import math
from MergeVA import MergeVA
import re
from pytube.compat import unicode
from kivy.uix.label import Label
from kivy.uix.image import Image, AsyncImage


class Down:
    def __init__(self, percentageDownload_label, viewerVideo, def_directory):
        self.folder_path = ''
        self.playlistLen = 0
        self.quality_ids = {2160: [313],
                            1440: [271],
                            1080: [248, 137],
                            720: [247, 136],
                            480: [244, 135],
                            360: [243, 134],
                            240: [133, 242],
                            144: [160, 278]}
        self.percentageDownload_label = percentageDownload_label
        self.viewerVideo = viewerVideo
        self.def_directory = def_directory
        self.video_label2 = Label(text="", color=(0.5, 0.5, 0.5, 1),
                                         size_hint_y=None, height=40,
                                 halign="right", valign="middle")

    @staticmethod
    def my_hook(d):
        if d['status'] == 'downloading':
            p = d['downloaded_bytes']/d['total_bytes']*100
            print(' ')
            print(f"{p}        {d['speed']/1024}    {d['eta']/60}")
        else:
            print(d['status'])


    def video_download(self, video_opts="", audio_opts="", video="", counter=0):
        with youtube_dl.YoutubeDL(video_opts) as ydl:
            video_meta = ydl.extract_info(video, download=False)
        video_title = self.filename(video_meta['title'])
        if counter:
            video_name = f"{self.get_cnt(counter)}{video_title}"
        else:
            video_name = f"{video_title}"

        video_opts['outtmpl'] = f"{self.folder_path}/{video_name}_v.mkv"
        audio_opts['outtmpl'] = f"{self.folder_path}/{video_name}_a.mp3"
        print(video)
        try:
            self.making_viewer_ui(counter, video_title, self.folder_path, f"{video_meta['thumbnail']}")
            with youtube_dl.YoutubeDL(video_opts) as ydl:
                self.video_label2.text = f"{video_meta['height']}P"
                ydl.extract_info(video, download=True)
            with youtube_dl.YoutubeDL(audio_opts) as ydl:
                ydl.extract_info(video, download=True)
            if os.path.exists(f"{self.folder_path}/{video_name}.mkv"):
                os.remove(f"{self.folder_path}/{video_name}.mkv")
            MergeVA().merge_va(video_opts['outtmpl'],
                               audio_opts['outtmpl'],
                               f"{self.folder_path}/{video_name}.mkv")
            self.video_label.color = (0.13, 0.83, 0.25, 1)
        except Exception as e:
            print(f"Can't download Video/Audio: {e}")
            self.video_label.color = (1, 0, 0, 1)
        finally:
            if os.path.exists(video_opts['outtmpl']):
                os.remove(video_opts['outtmpl'])
            if os.path.exists(audio_opts['outtmpl']):
                os.remove(audio_opts['outtmpl'])

    def download(self, youtube_link, folder_path, quality_max, quality_min):
        self.folder_path = folder_path
        if youtube_link:
            opts = {}
            video_opts = {'format': '', 'outtmpl': '', 'progress_hooks': [self.my_hook]}
            audio_opts = {'format': '250/249/251', 'outtmpl': '', 'progress_hooks': [self.my_hook]}

            quality_max = int(quality_max[0:-1])
            quality_min = int(quality_min[0:-1])

            for k, v in self.quality_ids.items():
                if int(quality_min) <= int(k) <= int(quality_max):
                    for vs in v:
                        video_opts['format'] += f"{vs}/"

            with youtube_dl.YoutubeDL(opts) as ydl:
                meta = ydl.extract_info(youtube_link, download=False)
            print(meta['extractor']+'********************************************')
            if meta['extractor'] == 'youtube':# if u put link video at playlist will download play list not one video
                self.video_download(video_opts=video_opts, audio_opts=audio_opts, video=youtube_link)
            else:
                counter = 1
                video_list = []
                video = meta['entries']
                folder_name = self.filename(meta['title'])

                self.folder_path += folder_name
                self.create_new_folder(self.folder_path)
                for k in video:
                    video_list.append(k['webpage_url'])

                self.playlistLen = len(video_list)

                for video in video_list:
                    try:
                        self.video_download(video_opts=video_opts, audio_opts=audio_opts, video=video,
                                            counter=counter)
                    except Exception as e:
                        print(e)
                    counter += 1

    def making_viewer_ui(self, counter, y_title, folder_path, img_url):
        icon = AsyncImage(source=img_url, allow_stretch=True, size_hint_x=0.1,
                          size_hint_y=None, height=60)
        self.viewerVideo.add_widget(icon)
        title = f' {y_title}   '
        self.video_label = Label(text=f"{counter}. {title}", color=(1, 0.9, 1, 1),
                                 size_hint_y=None, height=60, halign="left", valign="middle",
                                 size_hint_x=0.59, font_name='Arial')
        self.video_label.bind(size=self.video_label.setter('text_size'))
        self.viewerVideo.height += self.video_label.height * 2
        self.viewerVideo.add_widget(self.video_label)

        self.video_folder = Label(text=folder_path, color=(1, 0.9, 1, 1),
                                  size_hint_y=None,
                                  height=60, halign="left", valign="middle",
                                  size_hint_x=0.2)
        self.video_folder.bind(size=self.video_folder.setter('text_size'))
        self.viewerVideo.add_widget(self.video_folder)

        self.video_label2 = Label(text="", color=(1, 0.9, 1, 1),
                                  size_hint_y=None,
                                  height=60, halign="right", valign="middle",
                                  size_hint_x=0.06)
        self.video_label2.bind(size=self.video_label2.setter('text_size'))
        self.viewerVideo.add_widget(self.video_label2)

        test2 = f"0 %"
        self.video_label3 = Label(text=test2, color=(1, 0.9, 1, 1),
                                  size_hint_y=None,
                                  height=60, halign="right", valign="middle",
                                  size_hint_x=0.06)
        self.video_label3.bind(size=self.video_label3.setter('text_size'))
        self.viewerVideo.add_widget(self.video_label3)

        # ---------------------------------------------------

    @staticmethod
    def filename(s="", max_length=255):
        # Characters in range 0-31 (0x00-0x1F) are not allowed in ntfs filenames.
        allow_chars = [chr(i) for i in range(0, 31)]
        chars = [
            '\"', '\$', '\%', '\'', '\*', '\,', '\/', '\:', '"',
            '\;', '\<', '\>', '\?', '\\', '\^', '\|', '\~', '\\\\',
        ]
        pattern = '|'.join(allow_chars + chars)
        regex = re.compile(pattern, re.UNICODE)

        filename = regex.sub('', s)
        return unicode(filename[:max_length].rsplit(' ', 0)[0])

    @staticmethod
    def create_new_folder(directory):
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
