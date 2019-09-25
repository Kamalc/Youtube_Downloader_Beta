from subprocess import run, call
import ffmpeg
from ffmpy import FFmpeg
import os

class MergeVA:
    def __init__(self):
        pass

    def merge_va(self, temp_full_video_path, temp_full_audio_path, full_video_path):
        try:
            run([
                        #r".\ffmpeg\bin\ffmpeg.exe",
                        r"C:\ffmpeg\bin\ffmpeg.exe",
                        "-i",
                        f"{temp_full_video_path}",
                        "-i",
                        f"{temp_full_audio_path}",
                        "-c",
                        "copy",
                        f"{full_video_path}"
                    ])
            return True
        except Exception as e:
            print(f"Merging Error: {e}")
            return False

    def merge(self, temp_full_video_path, temp_full_audio_path, full_video_path):
        try:
            #os.popen(f'ffmpeg -i {temp_full_video_path} -i {temp_full_audio_path} \
            #    -c:v copy -c:a aac -strict experimental {full_video_path}')
            #call(["ffmpeg", "-y", "-i", temp_full_audio_path, "-r", "30", "-i", temp_full_video_path, "-filter:a", "aresample=async=1", "-c:a",
             #    "flac", "-c:v", "copy", full_video_path])
            #cmd = r'ffmpeg -y -i D:\download\Aki Play\1_a.mp4  -r 30 -i D:\download\Aki Play\1_v.mp4  -filter:a aresample=async=1 -c:a flac -c:v copy D:\download\Aki Play\1.mp4'
            #call(cmd, shell=True)
            cmd = "avconv -i 1_v.mp4 -i 1_a.mp4 -c copy 1_v.mp4"
            call(cmd, shell=True)
            return True
        except Exception as e:
            print(f"Merging Error: {e}")
            return False
