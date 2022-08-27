import os
import shutil
import subprocess

import requests
import vk_audio

vk = vk_audio.VkAudio(login='', password='')
SONGS_DIR = os.getcwd() + "\\songs"


# [("artist - title", "url"), ]
def songs_with_cover(user_id: None | int) -> list[tuple[str, str]]:
    songs = []
    audios = vk.get_only_audios(user_id)
    for audio in audios:
        if audio.image != "":
            songs.append((f"{audio.artist} - {audio.title}", audio.image))
    return songs


def download_songs(username: str, user_id: None | int, amount: None | int = None):
    user_dir = SONGS_DIR + f"\\{username}\\"
    os.makedirs(user_dir, exist_ok=True)

    songs = songs_with_cover(user_id)
    if amount is not None:
        songs = songs[:amount]

    for song, image in songs:
        song_dir = user_dir + song

        os.makedirs(song_dir, exist_ok=True)
        with open(f"{song_dir}\\cover.jpg", "wb") as file:
            file.write(requests.get(image).content)

        code = subprocess.run(["ytmdl", "--quiet", "--skip-meta",
                               "--output-dir", f"{song_dir}", song]).returncode
        if code == 0:
            filename = next(i for i in os.listdir(song_dir) if i != "cover.jpg")
            os.rename(f"{song_dir}\\{filename}", f"{song_dir}\\audio.mp3")
        else:
            shutil.rmtree(song_dir)


# download_songs("gcd", None, 5)
download_songs("vitos", 236793347, 5)
