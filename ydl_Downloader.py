from __future__ import unicode_literals
import youtube_dl
import os
import math
from MergeVA import MergeVA
import re
from pytube.compat import unicode


class Down:
    def __init__(self):
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
        pass

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
        with youtube_dl.YoutubeDL(video_opts) as ydl:
            ydl.extract_info(video, download=True)
        with youtube_dl.YoutubeDL(audio_opts) as ydl:
            ydl.extract_info(video, download=True)
        MergeVA().merge_va(video_opts['outtmpl'],
                           audio_opts['outtmpl'],
                           f"{self.folder_path}/{video_name}.mkv")

    def download(self, youtube_link, folder_path, quality_max, quality_min):
        self.folder_path = folder_path
        if youtube_link:
            opts = {}
            video_opts = {'format': '', 'outtmpl': ''}
            audio_opts = {'format': '140/249/250/251', 'outtmpl': ''}

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
                    finally:
                        os.remove(video_opts['outtmpl'])
                        os.remove(audio_opts['outtmpl'])
                    counter += 1

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


x = Down()
x.download(youtube_link='https://www.youtube.com/playlist?list=PLxL5AlqSq21IzKg3aL0TzftTPKSm0DNPD',
                        folder_path=r"D:/download/",
                        quality_max='720p',
                        quality_min='144p')
