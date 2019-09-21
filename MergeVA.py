from subprocess import run


class MergeVA:
    def __init__(self):
        pass

    def merge_va(self, temp_full_video_path, temp_full_audio_path, full_video_path):
        try:
            run([
                        r".\ffmpeg\bin\ffmpeg.exe",
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

    #merge_va(r"D:\download\testing\1.mp4", r"D:\download\testing\2.mp4", r"D:\download\testing\3.mp4")