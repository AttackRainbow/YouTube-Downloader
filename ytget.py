from concurrent.futures import ThreadPoolExecutor
import os
import sys

for i in range(3):
    try:
        from pytube import YouTube, Playlist
        from pytube.exceptions import RegexMatchError, VideoUnavailable, VideoRegionBlocked, VideoPrivate
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

    only_audio = False
    if len(sys.argv) == 1:
        link = input("YouTube link: ")
        only_audio = True if input(
            "Download as audio? (y,n): ").strip().lower() == "y" else False
    else:
        link = sys.argv[1]
        if "-audio" in sys.argv:
            only_audio = True

    if only_audio:
        os.chdir(os.path.join(file_dir, downloaded_audios_folder))
    else:
        os.chdir(os.path.join(file_dir, downloaded_videos_folder))

    try:
        vid = filtered_video(link)
    except RegexMatchError:
        try:
            playlist = Playlist(link)
        except RegexMatchError:
            print("Invalid yt link. Try again later.")
            from time import sleep
            sleep(3)
            exit(1)
        else:
            print("Trying to download " + str(len(playlist)) + " video(s).")
            with ThreadPoolExecutor() as ex:
                ex.map(download_video_from_url, playlist.video_urls, [
                    only_audio for _ in range(len(playlist))])
    else:
        if not vid:  # cannot download this vid
            exit(1)
        download_video(vid, only_audio)


def filtered_video(url: str):
    # check if this video of this url can be downloaded or not
    # return YouTube(url) if available for download else None

    try:
        return YouTube(url)
    except (VideoPrivate, VideoRegionBlocked, VideoUnavailable):
        print(
            f'Video id, {url.split("youtu.be/")[1] if "youtu.be/" in url else url.split("v=")[1].split("&")[0]}, is not available to download.')
        return None


def download_video_from_url(url: str, only_audio=None):
    vid = filtered_video(url)
    if not vid:
        return
    download_video(vid, only_audio)


def download_video(vid: YouTube, only_audio=None):
    if only_audio:
        best_stream = vid.streams.get_audio_only()
        best_stream.download()
    else:
        vid.streams.first().download()
    print(f"Downloaded {vid.title}")


if __name__ == "__main__":
    os.chdir(file_dir)
    main()
