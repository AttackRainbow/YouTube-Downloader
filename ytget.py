import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Iterable
from urllib.error import HTTPError

for i in range(3):
    try:
        from pytube import Playlist, YouTube
        from pytube.exceptions import (RegexMatchError, VideoPrivate,
                                       VideoRegionBlocked, VideoUnavailable)
        from youtubesearchpython import VideosSearch
    except ImportError:
        if i == 1:
            print("Cannot install dependencies...")
            exit(1)
        os.system(sys.executable + " -m pip install -r requirements.txt")
        os.system("cls")
    else:
        break

FILE_PATH = os.path.abspath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)
FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')


def main():
    here = False
    only_audio = True
    show = False
    if len(sys.argv) == 1:
        link = input("YouTube link: ")
        only_audio = True if input(
            "Download as audio? (y,n): ").strip().lower() == "y" else False
    else:
        link = sys.argv[1]
        if "-vid" in sys.argv:
            only_audio = False
        if "-here" in sys.argv:
            here = True
        if "-show" in sys.argv:
            show = True

    # select where to put downloaded files
    downloaded_videos_folder = "Downloaded Videos"
    downloaded_audios_folder = "Downloaded Audios"
    if here:
        os.chdir(FILE_DIR)
        # check to make folders in default folder
        if not os.path.exists(downloaded_videos_folder):
            os.makedirs(downloaded_videos_folder)
        if not os.path.exists(downloaded_audios_folder):
            os.makedirs(downloaded_audios_folder)
    elif only_audio:
        os.chdir(os.path.join(FILE_DIR, downloaded_audios_folder))
    else:
        os.chdir(os.path.join(FILE_DIR, downloaded_videos_folder))

    # link to video/playlist or title of a video
    downloaded = False
    if "youtube.com/watch?v=" in link or "youtu.be/" in link:
        print_where_to_download()
        download_video_from_url(link)
        downloaded = True
    elif "playlist?list=" in link:
        playlist = Playlist(link)
        try:
            download_playlist_from_urls(
                playlist.video_urls, only_audio=only_audio)
        # the problem is at Playlist.video_urls
        # maybe some videos are removed but still shown in playlist
        except HTTPError:
            # time to use good old method of parsing html lmao
            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/87.0.4280.66 Safari/537.36"
            }
            import requests
            r = requests.get(link, headers=headers)
            vid_ids = set([each.split('"')[0] for each in r.text.split(
                '"videoId":"')][1:-3])  # 3 duplicates of each id
            download_playlist_from_urls(
                list(map(lambda id: f"https://youtu.be/{id}", vid_ids)))
        downloaded = True
    else:
        results = VideosSearch(link).result()['result']
        try:
            print("ctrl + c to cancel.")
            for r in results:
                if 'y' in input(f"{r['title']}, {r['duration']}\n(y,n)?: "):
                    print_where_to_download()
                    download_video_from_url(r['link'], only_audio=only_audio)
                    downloaded = True
                    break
            else:
                print("No more result.")
        except KeyboardInterrupt:
            exit(0)

    if downloaded:  # ask wether to show in file explorer
        if show:
            explore(os.getcwd())
        else:
            if "y" in input("Show in File Explorer? (y,n): ").strip().lower():
                explore(os.getcwd())


def download_playlist_from_urls(urls: Iterable[str], only_audio=None, highest_resolution=False):
    print("Downloading " + str(len(urls)) + " video(s).")
    with ThreadPoolExecutor() as ex:
        print_where_to_download()
        ex.map(download_video_from_url, urls, [
            only_audio for _ in range(len(urls))])


def print_where_to_download():
    print("Downloading to " + os.getcwd() + ".")


def explore(path):
    # explorer would choke on forward slashes
    path = os.path.normpath(path)

    if os.path.isdir(path):
        subprocess.run([FILEBROWSER_PATH, path])
    elif os.path.isfile(path):
        subprocess.run([FILEBROWSER_PATH, '/select,', os.path.normpath(path)])


def filtered_video(url: str):
    # check if this video of this url can be downloaded or not
    # return YouTube(url) if available for download else None

    try:
        return YouTube(url)
    except (RegexMatchError, VideoPrivate, VideoRegionBlocked, VideoUnavailable):
        print(
            f'Video of {url} is not available for download.')
        return None


def download_video_from_url(url: str, only_audio=None, highest_resolution=False):
    """ will return True if downloaded else False """
    vid = filtered_video(url)
    if not vid:
        return False
    download_video(vid, only_audio, highest_resolution)
    return True


def download_video(vid: YouTube, only_audio=None, highest_resolution=False):
    if only_audio:
        best_stream = vid.streams.get_audio_only()
        best_stream.download()
    elif highest_resolution:
        vid.streams.get_highest_resolution().download()
    else:
        vid.streams.first().download()
    print(f"Downloaded {vid.title}")


if __name__ == "__main__":
    os.chdir(FILE_DIR)
    os.system("title YouTube-Get")
    main()
