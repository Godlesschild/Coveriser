import os
import shutil
import subprocess

import requests
import vk_api
import vk_audio

SONGS_DIR = os.getcwd() + "\\songs"


def load_credentials() -> dict[str, str]:
    with open("credentials.txt") as file:
        return {k: v for k, v in [line.split() for line in file.readlines()]}


def capcha_handler(capcha):
    key = input(f"Enter capcha code {capcha.get_url()}:").strip()
    return capcha.try_again(key)


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

        code = subprocess.run([
            "ytmdl",
            "--quiet",
            "--skip-meta",
            "--level", "ERROR",
            "--disable-file",
            "--output-dir", song_dir,
            song
        ]).returncode

        if code == 0:
            filename = next(i for i in os.listdir(song_dir) if i != "cover.jpg")
            os.rename(f"{song_dir}\\{filename}", f"{song_dir}\\audio.mp3")
        else:
            shutil.rmtree(song_dir)


session = vk_api.VkApi(captcha_handler=capcha_handler, **load_credentials())
try:
    session.auth()
except vk_api.AuthError as err:
    print(err)
    exit()
vk = vk_audio.VkAudio(session)

# download_songs("gcd", 96530526, 5)
download_songs("vitos", 236793347, 5)
