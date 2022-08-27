import os
import shutil
import subprocess

import requests
import vk_api
import vk_audio

import pydub as pd

SONGS_DIR = os.getcwd() + "\\songs"

def load_credentials() -> dict[str, str]:
    with open("credentials.txt") as file:
        return {k: v for k, v in [line.split() for line in file.readlines()]}


def captcha_handler(captcha):
    key = input(f"Enter captcha code {captcha.get_url()}:").strip()
    return captcha.try_again(key)


def cut_audio(song_dir, filename):
    audiofile = open(f"{song_dir}\\{filename}", "rb")
    audio = pd.AudioSegment.from_mp3(audiofile)
    if audio.duration_seconds > 60:
        audio[30*1000:60*1000].export(f"{song_dir}\\audio.mp3", format="mp3")
    else:
        shutil.rmtree(song_dir)


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
            cut_audio(song_dir, filename)
        else:
            shutil.rmtree(song_dir)


session = vk_api.VkApi(captcha_handler=captcha_handler, **load_credentials())
try:
    session.auth()
except vk_api.AuthError as err:
    print(err)
    exit()
vk = vk_audio.VkAudio(session)

download_songs("gcd", 96530526, 5)
# download_songs("vitos", 236793347, 5)
