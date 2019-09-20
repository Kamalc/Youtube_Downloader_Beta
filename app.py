import math
from pytube import Playlist
from pytube import YouTube
import os

playlistURl = input()
pl = Playlist(playlistURl)
folder_name = pl.title()
Video_List = pl.parse_links()
total_size = 1
playlistLen = len(Video_List)
folder_path = ""

print(folder_name)

def create_new_folder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating Folder. ' + directory)


def show_progress_bar(stream, chunk, file_handle, bytes_remaining):
    global total_size
    total_size = max(bytes_remaining, total_size)
    print(str(int(100 - (bytes_remaining / total_size * 100))) + "%")
    return


def get_cnt(cnt):
    cnt_str = ""
    for i in range(math.ceil(math.log10(playlistLen)) - len(str(cnt))):
        cnt_str += '0'
    return cnt_str + str(cnt) + '.'


folder_path = 'D:/download/' + folder_name
create_new_folder(folder_path)
counter = 1
for x in Video_List:
    total_size = 1
    try:
        yt = YouTube("https://www.youtube.com/" + x)
        YTitle = yt.title
        #yt.register_on_progress_callback(show_progress_bar)
        #yt.streams.filter().first().download(folder_path, filename=(get_cnt(counter) + YTitle))
        ll = [stream.resolution for stream in yt.streams.all()]
        print(ll)
        """caption = yt.captions.get_by_language_code('en')
        if caption:
            my_file = open(folder_path + '/' + get_cnt(counter) + YTitle + ".srt", "w+", encoding='UTF8')
            my_file.writelines(caption.generate_srt_captions())
            my_file.close()
        else:
            print("No Sub Found")"""
    except Exception as e:
        print("Can't Download"+str(e))

    counter += 1

print('Process is done')
