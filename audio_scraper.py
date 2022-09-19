import os
import random
import shutil
import subprocess

import pydub as pd
import requests
import vk_api
import vk_audio

SONGS_DIR = os.getcwd() + "\\songs"


def load_credentials() -> dict[str, str]:
    with open("credentials.txt") as file:
        return {k: v for k, v in [line.split() for line in file.readlines()]}


def captcha_handler(captcha):
    key = input(f"Enter captcha code {captcha.get_url()}:").strip()
    return captcha.try_again(key)


def cut_audio(song_dir: str):
    path = f"{song_dir}\\audio.mp3"
    try:
        with open(path, "rb") as file:
            audio = pd.AudioSegment.from_mp3(file)
    except:
        shutil.rmtree(song_dir)
        return

    if 60 <= audio.duration_seconds <= 6 * 60:
        with open(path, "wb") as file:
            audio[30*1000:60*1000].export(file, format="mp3")

    else:
        shutil.rmtree(song_dir)


def songs_with_cover(user_id: None | int) -> list[tuple[str, str]]:
    songs = []
    audios = vk.get_only_audios(user_id)
    for audio in audios:
        if audio.image != "" and not (any(e in audio.title for e in '\\/:*?"<>|')):
            songs.append((f"{audio.artist} - {audio.title}", audio.image))
    return songs


def download_songs(username: str, user_id: None | int, amount: None | int = None, shuffle: bool = False, redownload: bool = False):
    user_dir = SONGS_DIR + f"\\{username}\\"
    os.makedirs(user_dir, exist_ok=True)

    songs = songs_with_cover(user_id)

    if shuffle:
        random.shuffle(songs)
    if amount is not None:
        songs = songs[:amount]

    for song, image in songs:
        song_dir = user_dir + song

        try:
            os.makedirs(song_dir, exist_ok=redownload)
        except OSError:
            continue

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
            cut_audio(song_dir)
        else:
            shutil.rmtree(song_dir)


session = vk_api.VkApi(captcha_handler=captcha_handler, **load_credentials())
try:
    session.auth()
except vk_api.AuthError as err:
    print(err)
    exit()
vk = vk_audio.VkAudio(session)


download_songs("gcd", 96530526, 5, True)
# download_songs("vitos", 236793347, 5)
