from vtt_to_srt import __main__
import os

def convert_vtt_to_srt(vtt_path):
    try:
        __main__.convert_vtt_to_str(vtt_path)
    except Exception as e:
        print(f"path not found: {e}")
    finally:
        os.remove(vtt_path)
