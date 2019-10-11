# -*- coding: UTF-8 -*-

from __future__ import unicode_literals
import youtube_dl
import os
import math
from MergeVA import MergeVA
import re
from pytube.compat import unicode
from kivy.uix.label import Label
from HoverButton import HoverButton
from kivy.uix.image import Image, AsyncImage
#from Str_Converter import convert_vtt_to_srt
from functools import partial
import threading
import sys
from arabic_reshaper_new import reshape
import bidi.algorithm
from Options import get_list_sub_codes, get_actual_speed


class Down:
    def __init__(self, g_speed, viewer_video, status):
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
        self.g_speed = g_speed
        self.viewerVideo = viewer_video
        self.Quality_label = Label(text="", color=(0.5, 0.5, 0.5, 1),
                                   size_hint_y=None, height=40,
                                   halign="right", valign="middle")
        self.percentage_label = Label(text="0 %", color=(1, 0.9, 1, 1),
                                      size_hint_y=None,
                                      height=60, halign="right", valign="middle",
                                      size_hint_x=0.06)
        self.eta_speed = Label()
        self.eta = Label()
        self.speed = Label()
        self.video_btn_label = HoverButton()
        self.status = status

    def my_hook(self, d):
        try:
            if d['status'] == 'downloading':
                speed = f"_._KB/s"
                if d['speed'] is None:
                    self.g_speed.text = speed
                else:
                    speed = self.format_bytes(int(d['speed']))
                    self.g_speed.text = f"{speed}/s"
                if d['eta'] is None:
                    eta = "--:--"
                else:
                    eta = self.format_seconds(d['eta'])
                self.eta.text = f"{eta}"
                self.speed.text = f"{self.g_speed.text}"
                if d['total_bytes'] is None and d['downloaded_bytes'] is None:
                    percentage = "UnKnown"
                else:
                    percentage = round(d['downloaded_bytes']/d['total_bytes']*100, 2)
                self.percentage_label.text = f"{percentage} %"
            else:
                print(d['status'])
        except Exception as e:
            print(f"\nCan't Hook{{{e}}}Line: {sys.exc_info()[-1].tb_lineno}")

    def audio_download(self, audio_opts="", link="", counter=0, just_mp3=False):
        print("audio")
        with youtube_dl.YoutubeDL(audio_opts) as ydl:
            audio_meta = ydl.extract_info(link, download=False)

        audio_title = self.filename(audio_meta['title'])
        if counter:
            audio_name = f"{self.get_cnt(counter)}{audio_title}"
        else:
            audio_name = f"{audio_title}"
        audio_opts['outtmpl'] = f"{self.folder_path}/{audio_name}"
        print(audio_opts['outtmpl'].encode("utf-8"))
        if not just_mp3:
            audio_opts['outtmpl'] += "_a"

        audio_opts['outtmpl'] += ".mp3"

        try:
            if just_mp3:
                self.making_viewer_ui(counter, audio_title, f"{self.folder_path}/{audio_name}.mp3", f"{audio_meta['thumbnail']}",
                                      audio_meta['filesize'], 0)
                self.Quality_label.text = "MP3"
                if os.path.exists(audio_opts['outtmpl']):
                    os.remove(audio_opts['outtmpl'])
            audio_opts['ratelimit'] = get_actual_speed()
            with youtube_dl.YoutubeDL(audio_opts) as ydl:
                self.status.text = "Downloading Audio"
                ydl.extract_info(link, download=True)

            if just_mp3:
                self.video_btn_label.color = (0.13, 0.83, 0.25, 1)
        except Exception as e:
            print(f"Can't download Audio: {e}.\nLine: {sys.exc_info()[-1].tb_lineno}\n"
                  f"Type Error: {type(e).__name__}")
            self.status.text = "Failed"
            self.video_btn_label.color = (1, 0, 0, 1)

    def video_download(self, video_opts="", audio_opts="", video="", counter=0, sub_langs=[]):
        sub_langs = get_list_sub_codes()
        print("Languages:")
        print(sub_langs)
        try:
            with youtube_dl.YoutubeDL(video_opts) as ydl:
                video_meta = ydl.extract_info(video, download=False)
                subs = video_meta.get('subtitles', [video_meta])
                for l in sub_langs:
                    if l not in subs:
                        sub_langs.remove(l)
        except:
            sub_langs = []
            video_opts['writesubtitles'] = False
            with youtube_dl.YoutubeDL(video_opts) as ydl:
                video_meta = ydl.extract_info(video, download=False)
        print("Languages After")
        print(sub_langs)
        with youtube_dl.YoutubeDL(audio_opts) as ydl:
            audio_meta = ydl.extract_info(video, download=False)

        video_title = self.filename(video_meta['title'])
        if counter:
            video_name = f"{self.get_cnt(counter)}{video_title}"
        else:
            video_name = f"{video_title}"

        video_opts['writesubtitles'] = False
        video_opts['outtmpl'] = f"{self.folder_path}/{video_name}_v.mkv"
        audio_opts['outtmpl'] = f"{self.folder_path}/{video_name}_a.mp3"
        #sub_vtt = f"{self.folder_path}/{video_name}_v.en.vtt"
        print(video)
        try:
            self.making_viewer_ui(counter, video_title, f"{self.folder_path}/{video_name}.mkv", f"{video_meta['thumbnail']}",
                                  video_meta['filesize'], audio_meta['filesize'])
            video_opts['ratelimit'] = get_actual_speed()
            with youtube_dl.YoutubeDL(video_opts) as ydl:
                self.Quality_label.text = f"{video_meta['height']}P"
                self.status.text = "Downloading Video"
                ydl.extract_info(video, download=True)
            audio_opts['ratelimit'] = get_actual_speed()
            with youtube_dl.YoutubeDL(audio_opts) as ydl:
                self.status.text = "Downloading Audio"
                ydl.extract_info(video, download=True)
            if os.path.exists(f"{self.folder_path}/{video_name}.mkv"):
                os.remove(f"{self.folder_path}/{video_name}.mkv")
            self.status.text = "Merging Video&Audio"
            MergeVA().merge_va(video_opts['outtmpl'],
                               audio_opts['outtmpl'],
                               f"{self.folder_path}/{video_name}.mkv")
            sub_opts = {
                'writesubtitles': True, 'allsubtitles': False,
                'skip_download': True,
            }
            self.video_btn_label.color = (0.13, 0.83, 0.25, 1)
            if len(sub_langs) > 0:
                sub_opts['subtitleslangs'] = sub_langs
                sub_opts['outtmpl'] = f"{self.folder_path}/{video_name}.vtt"
                #sub_langs['outtmpl'] = sub_vtt
                with youtube_dl.YoutubeDL(sub_opts) as ydl:
                    sub_meta = ydl.extract_info(video, download=True)
        #convert_vtt_to_srt(sub_vtt)
        except Exception as e:
            print(f"Can't download Video/Audio: {e}.\nLine: {sys.exc_info()[-1].tb_lineno}\n"
                  f"Type Error: {type(e).__name__}")
            self.status.text = "Failed"
            self.video_btn_label.color = (1, 0, 0, 1)
        finally:
            if os.path.exists(video_opts['outtmpl']):
                os.remove(video_opts['outtmpl'])
            if os.path.exists(audio_opts['outtmpl']):
                os.remove(audio_opts['outtmpl'])

    def download(self, youtube_link, folder_path, quality_max, quality_min, audio_checker):
        self.folder_path = folder_path
        if youtube_link:
            opts = {}
            video_opts = {'format': '', 'outtmpl': '', 'progress_hooks': [self.my_hook],
                          'writesubtitles': True, 'allsubtitles': False
                          }
            audio_opts = {'format': '250/249/251', 'outtmpl': '', 'progress_hooks': [self.my_hook]}
            if quality_max[-1] == 'p' and quality_min[-1] == 'p':
                quality_max = int(quality_max[0:-1])
                quality_min = int(quality_min[0:-1])
                for k, v in self.quality_ids.items():
                    if int(quality_min) <= int(k) <= int(quality_max):
                        for vs in v:
                            video_opts['format'] += f"{vs}/"
            try:
                with youtube_dl.YoutubeDL(opts) as ydl:
                    self.status.text = "Fetching...."
                    meta = ydl.extract_info(youtube_link, download=False)
            except Exception as e:
                meta = None
                print(f"Can't Download: {e}.\nLine: {sys.exc_info()[-1].tb_lineno}\n"
                      f"Type Error: {type(e).__name__}")
                self.status.text = "Failed"
            print(meta['extractor']+'********************************************')
            if meta['extractor'] == 'youtube':# if u put link video at playlist will download play list not one video
                if audio_checker.active:
                    self.audio_download(audio_opts=audio_opts, link=youtube_link, just_mp3=True)
                else:
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
                        if audio_checker.active:
                            self.audio_download(audio_opts=audio_opts, link=video,
                                                counter=counter, just_mp3=True)
                        else:
                            self.video_download(video_opts=video_opts, audio_opts=audio_opts, video=video,
                                                counter=counter)
                    except Exception as e:
                        print(e)
                    counter += 1

    def making_viewer_ui(self, counter, y_title, folder_path, img_url, file_size_v, file_size_a):
        try:
            print("FileSize Audio & Video", file_size_a, file_size_v)
            if file_size_v is None or file_size_a is None:
                file_size = 0
            else:
                file_size = file_size_v+file_size_a
            file_size = round(file_size/1024/1024, 2)

            icon = AsyncImage(source=img_url, allow_stretch=True, size_hint_x=0.1,
                              size_hint_y=None, height=60)
            self.viewerVideo.add_widget(icon)
            title = f' {y_title}'
            if counter:
                title = f"{counter}. {title}"

            reshaped_text = reshape(title)
            display_text = bidi.algorithm.get_display(reshaped_text[0:min(52, len(reshaped_text))])
            self.video_btn_label = HoverButton(text=display_text, color=(0.18, 0.49, 0.60, 1),
                                               size_hint_y=None, height=50, font_size=16,
                                               valign="middle", halign="center",
                                               size_hint_x=0.4, font_name='Arial',
                                               background_color=(0.35, 0.35, 0.35, 1))
            self.video_btn_label.bind(size=self.video_btn_label.setter('text_size'))
            self.viewerVideo.height += self.video_btn_label.height * 2
            self.viewerVideo.add_widget(self.video_btn_label)
            self.video_btn_label.bind(on_release=partial(self.open_video, folder_path))
            # background_disabled_normal
            self.Quality_label = Label(text="", color=(0.18, 0.49, 0.60, 1),
                                       size_hint_y=None,
                                       height=60, halign="center", valign="middle",
                                       size_hint_x=0.06)
            self.Quality_label.bind(size=self.Quality_label.setter('text_size'))
            self.viewerVideo.add_widget(self.Quality_label)

            self.eta = Label(text="", color=(0.18, 0.49, 0.60, 1),
                             size_hint_y=None,
                             height=60, halign="center", valign="middle",
                             size_hint_x=0.05)
            self.eta.bind(size=self.eta.setter('text_size'))
            self.viewerVideo.add_widget(self.eta)

            self.speed = Label(text="", color=(0.18, 0.49, 0.60, 1),
                               size_hint_y=None,
                               height=60, halign="center", valign="middle",
                               size_hint_x=0.09)
            self.speed.bind(size=self.speed.setter('text_size'))
            self.viewerVideo.add_widget(self.speed)

            if file_size == '0':
                file_size = "Unknown Size"
            self.Size_label = Label(text=str(file_size)+"MB", color=(0.18, 0.49, 0.60, 1),
                                    size_hint_y=None,
                                    height=60, halign="center", valign="middle",
                                    size_hint_x=0.1)
            self.Size_label.bind(size=self.Size_label.setter('text_size'))
            self.viewerVideo.add_widget(self.Size_label)

            perc = f"0 %"
            self.percentage_label = Label(text=perc, color=(0.18, 0.49, 0.60, 1),
                                          size_hint_y=None,
                                          height=60, halign="center", valign="middle",
                                          size_hint_x=0.06)
            self.percentage_label.bind(size=self.percentage_label.setter('text_size'))
            self.viewerVideo.add_widget(self.percentage_label)
        except Exception as e:
            print(f"Viweing Error: {e}.\nLine: {sys.exc_info()[-1].tb_lineno}\n"
                  f"Type Error: {type(e).__name__}")
        # ---------------------------------------------------

    def open_video(self, path, *instance):
        print(f"opening video: {path}")
        if os.path.exists(path):
            threading.Thread(target=os.startfile(path)).start()

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

    @staticmethod
    def format_seconds(seconds):
        (mins, secs) = divmod(seconds, 60)
        (hours, mins) = divmod(mins, 60)
        if hours > 99:
            return '--:--:--'
        if hours == 0:
            return '%02d:%02d' % (mins, secs)
        else:
            return '%02d:%02d:%02d' % (hours, mins, secs)

    @staticmethod
    def format_bytes(bytes):
        if bytes is None:
            return 'N/A'
        if type(bytes) is str:
            bytes = float(bytes)
        if bytes == 0.0:
            exponent = 0
        else:
            exponent = int(math.log(bytes, 1024.0))
        suffix = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'][exponent]
        converted = float(bytes) / float(1024 ** exponent)
        return '%.2f%s' % (converted, suffix)

    def sub_language(self, lang):
        lang = "en,ar"
