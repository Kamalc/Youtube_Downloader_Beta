from subprocess import run, call
import os


class MergeVA:
    def __init__(self):
        pass

    def merge_va(self, temp_full_video_path, temp_full_audio_path, full_video_path):
        try:
            run([
                        os.getcwd() + r"\ffmpeg\bin\ffmpeg.exe",
                        #os.getcwd() + r"\ffmpeg.exe",
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
