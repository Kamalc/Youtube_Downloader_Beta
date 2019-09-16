import math
from pytube import Playlist
from pytube import YouTube
import math
"""from kivy.app import App
from kivy.uix.label import Label

class YoutubeDownloader(App):
    def build(self):
        return Label(Text="A7a")

if __name__ == "__main__":
    YoutubeDownloader().run()
"""
Play_List_Name = input()
pl = Playlist("https://www.youtube.com/watch?v=DFwuVPzVUPs&list=PLpGwX4KubWG8KOCRPJQ6snHtmTyxZRgKP")
v = pl.parse_links()
z = 1
playlistLenth = len(v)


def show_progress_bar(stream, chunk, file_handle, bytes_remaining):
    global z
    z = max(bytes_remaining, z)
    print(str(int(100-(bytes_remaining/z*100)))+"%")
    return  # do work


def get_cnt(cnt):
    x = ""
    for i in range(math.ceil(math.log10(playlistLenth))-len(str(cnt))):
        x += '0'
    return x+str(cnt)+'_'


counter = 0
import os

pl = Playlist("https://www.youtube.com/watch?v=DFwuVPzVUPs&list=PLpGwX4KubWG8KOCRPJQ6snHtmTyxZRgKP")
folder_name = pl.title()
v = pl.parse_links()
total_size = 1
playlistLen = len(v)
folder_path = ""


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
for x in v:
    total_size = 1
    try:
        yt = YouTube("https://www.youtube.com/" + x)
        YTitle = yt.title
        yt.register_on_progress_callback(show_progress_bar)
        yt.streams.filter(adaptive=True).first().download('D:/download',filename=get_cnt(counter)+YTitle)
        yt.streams.filter(progressive=True).first().download(folder_path, filename=(get_cnt(counter) + YTitle))
        caption = yt.captions.get_by_language_code('en')
        print(caption.generate_srt_captions())
        if caption:
            my_file = open(folder_path + '/' + get_cnt(counter) + YTitle + ".srt", "w+", encoding='UTF8')
            my_file.writelines(caption.generate_srt_captions())
            my_file.close()
        else:
            print("No Sub Find")
    except:
        print("Faild")
    counter+=1

    print ("done")
    #except AssertionError as error:
    #    print("Can't Download")
    counter += 1

print('done')
