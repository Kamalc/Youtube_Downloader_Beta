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
for x in v:
    z = 1
    try:
        yt = YouTube("https://www.youtube.com/"+x)
        YTitle=yt.title
        yt.register_on_progress_callback(show_progress_bar)
        yt.streams.filter(adaptive=True).first().download('D:/download',filename=get_cnt(counter)+YTitle)
        caption = yt.captions.get_by_language_code('en')
        if(caption):
             f = open("D:/download/" + get_cnt(counter)+ YTitle + ".srt", "w+")
             f.writelines(caption.generate_srt_captions())
             f.close()
        else:
            print("No Sub Find")
    except:
        print("Faild")
    counter+=1

print ("done")
