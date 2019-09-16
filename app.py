from pytube import Playlist
from pytube import YouTube
import  math
#Play_List_Name = input()
pl = Playlist("https://www.youtube.com/playlist?list=PLxL5AlqSq21J4ksTlZ8HKbF0py8i43qPW")
v = pl.parse_links()
z = 1
playlistLenth=len(v)

def show_progress_bar(stream, chunk, file_handle, bytes_remaining):
    global z
    z = max(bytes_remaining, z)
    print(str(int(100-(bytes_remaining/z*100)))+"%")
    return  # do work
def get_cnt(cnt):
    x = ""
    for i in range (math.ceil(math.log10(playlistLenth))-len(str(cnt))):
        x += '0'
    return x+str(cnt)+'_'

counter = 0
for x in v:
    z = 1
    try:
        yt = YouTube("https://www.youtube.com/"+x)
        YTitle=yt.title
        yt.register_on_progress_callback(show_progress_bar)
        yt.streams.filter(progressive=True).first().download('D:/download',filename=get_cnt(counter)+YTitle)
        caption = yt.captions.get_by_language_code('en')
        if(caption):
             f = open("D:/download/" + get_cnt(counter)+ YTitle + ".srt", "w+")
             f.writelines(caption.generate_srt_captions())
             f.close()
        else:
            print("No Sub Find")
    except :
        print("Faild")
    counter+=1

print ("done")