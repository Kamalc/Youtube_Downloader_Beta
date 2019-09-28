from __future__ import unicode_literals
import youtube_dl

ydl_opts = {
    'format': '160/133/240',
    #'formats': [{
    #    #'format_note': '1080p/720p/480p'
    #    'height': '480',
    #    'width': '570',
    #}]
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    meta = ydl.extract_info('https://www.youtube.com/watch?v=8EkOwZuMgfI', download=True)
    formats = meta.get('formats', [meta])
    print("Format_id", "Height", "EXT")
    for f in formats:
        print(f['format_id'], f['height'], f['ext'])
    print("\n\n")
    for f in formats:
        print(f)
    print("\n\n")
    for m in meta.items():
        print(m)
    print("\n\n")
    print(meta['title'])
    print(f"Format : {meta['format']}")

    quality_ids = {144: [160, 278],
                   240: [133, 242],
                   360: [243, 134, 43],
                   480: [244, 135],
                   720: [247, 136, 22],
                   1080: [248, 137],
                   1440: [271],
                   2160: [313]}
