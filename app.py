from pytube import Playlist
from pytube import YouTube
#Play_List_Name = input()
pl = Playlist("https://www.youtube.com/playlist?list=PLxL5AlqSq21IzKg3aL0TzftTPKSm0DNPD")
v = pl.parse_links()
z = 1
def show_progress_bar(stream, chunk, file_handle, bytes_remaining):
    global z
    z = max(bytes_remaining, z)
    print(str(100-(bytes_remaining/z*100))+"%.")
    return  # do work

for x in v:
    z = 1
    try:
        yt = YouTube("https://www.youtube.com/"+x)
#        print(yt.title)
        yt.streams.filter(progressive=True)
        yt.register_on_progress_callback(show_progress_bar)
        yt.streams.first().download('D:/download')
    except:
        print("Faild")
print ("done")