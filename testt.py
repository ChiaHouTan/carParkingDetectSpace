from pytube import YouTube

youtube_url = "https://youtu.be/6LQ8mvxLPMI?si=CdzfcgDRZmLE5ZqZ"

try:
    yt = YouTube(youtube_url)
    print("Title:", yt.title)
    print("Author:", yt.author)
    print("Length:", yt.length)
    print("Views:", yt.views)
    print("Rating:", yt.rating)
    print("Streams:")
    for stream in yt.streams:
        print(stream)
except Exception as e:
    print("Error retrieving video information:", e)