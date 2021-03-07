import os
import sys
from concurrent.futures import ThreadPoolExecutor
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

file_path = os.path.abspath(__file__)
file_dir = os.path.dirname(file_path)


def main():
    downloaded_videos_folder = "Downloaded Videos"
    downloaded_audios_folder = "Downloaded Audios"
    if not os.path.exists(downloaded_videos_folder):
        os.makedirs(downloaded_videos_folder)
    if not os.path.exists(downloaded_audios_folder):
        os.makedirs(downloaded_audios_folder)

    only_audio = True
    here = False
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

    # select where to put downloaded files
    if here:
        os.chdir(file_dir)
    elif only_audio:
        os.chdir(os.path.join(file_dir, downloaded_audios_folder))
    else:
        os.chdir(os.path.join(file_dir, downloaded_videos_folder))

    # link to video/playlist or title of a video
    if "youtube.com/watch?v=" in link or "youtu.be/" in link:
        print_where_to_download()
        download_video_from_url(link)
    elif "playlist?list=" in link:
        playlist = Playlist(link)
        try:
            print("Trying to download " +
                  str(len(playlist.video_urls)) + " video(s).")
        except HTTPError:  # the problem is at Playlist.video_urls
            print("Cannot download this playlist. No idea why lol.")
        else:
            with ThreadPoolExecutor() as ex:
                print_where_to_download()
                ex.map(download_video_from_url, playlist.video_urls, [
                    only_audio for _ in range(len(playlist))])
    else:
        results = VideosSearch(link).result()['result']
        for r in results:
            if 'y' in input(f"{r['title']}, {r['duration']}\n(y,n)?: "):
                print_where_to_download()
                download_video_from_url(r['link'], only_audio=True)
                break
        else:
            print("No more result.")


def print_where_to_download():
    print("Downloading to " + os.getcwd() + ".")


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
    os.system("title YouTube-Get")
    main()
