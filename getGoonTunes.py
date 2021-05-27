import re, requests, os, sys, time
from nordvpn_switcher import initialize_VPN,rotate_VPN,terminate_VPN
from pytube import Playlist, YouTube
from moviepy.editor import *
from shutil import Error, rmtree
from tempfile import gettempdir
from pathlib import Path as p, PureWindowsPath as pp

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush() 

# where all of the music lives
record_cabinet = 'P:\\iPod'

# url of the YouTube Music playlist
url = input('Enter YouTube Music Playlist URL')
pl = Playlist(url)

# for getting the artist name
artistURL = list(pl).pop(0)
authorInfo = YouTube(artistURL).author
artistList = authorInfo.split(' -', 1)
artist = artistList.pop(0)

# artist and album title information
fullTitle = pl.title
titleList = fullTitle.split('- ', 1)
albumName = titleList.pop(1)

# some shit that we can easily delete after we're done
tmp = pp(gettempdir(), '.',artist)
if p(tmp).exists():
    rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
else:
    os.makedirs(tmp)

# for downloading the mp4 files, will be deleted later
mp4_dir = '{0}\\{1} - {2}\\'.format(tmp, artist, albumName)

# base folder where the converted audio files will live
mp3_dir = '{0}\\{1} - {2}\\'.format(record_cabinet, artist, albumName)
if p(mp3_dir).exists():
    rmtree(mp3_dir, ignore_errors=True)
    os.makedirs(mp3_dir)
else:
    os.makedirs(mp3_dir)

# check for download directory existing and make it, maybe
try:
    os.makedirs(mp4_dir)
    print("'{0}' created! Name of the Album is {1}.".format(mp4_dir,albumName))
except FileExistsError:
    fileError = ("'{0}' already exisits! Nuking temp folder in 10 seconds.".format(mp4_dir))
    print(fileError)
    time.sleep(10)
    rmtree(mp4_dir, ignore_errors=True)
    print("'{0}' created! Name of the Album is {1}.".format(mp4_dir,albumName))

# get in the tubes and go somewhere else for a bit (spoiler: canada is a possibility
try:
    rotate_VPN()
except Error:
    initialize_VPN(stored_settings=1)
    rotate_VPN()

# this fixes the empty playlist.videos list
# pl._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")

# modify the value to download a different stream
YOUTUBE_STREAM_AUDIO = "140"

# just a little info on what is about to be downloaded
print('The artist/band for this playlist is {0}.'.format(artist))
print('The album for this playlist is {0}.'.format(albumName))
print('Downloading......')

# get the audio tracks
mp4_count = 1
for video in pl.videos:
    totalSongs = len(pl.video_urls)
    progress(mp4_count, totalSongs, status='#')
    audioStream = video.streams.get_by_itag(YOUTUBE_STREAM_AUDIO)
    audioFile = '{0} - '.format(artist)
    audioStream.download(output_path=mp4_dir, filename_prefix=audioFile)
    mp4_count += 1

print('Starting the converstion from MP4 to MP3.')
print('Converting......')

# convert from mp4 to mp3
mp3_count = 1
for songs in os.listdir(mp4_dir):
    mp4_file = mp4_dir +'\\' + songs
    mp3_file = mp3_dir + '\\' + songs.replace('mp4', 'mp3')
    audioFile = AudioFileClip(mp4_file)
    audioFile.write_audiofile(mp3_file)
    mp3_count += 1

# remove the mp4 files since this project is for an iPod
if mp3_count == mp4_count:
    rmtree(tmp, ignore_errors=True)
    print('File converstion complete! Temp folder nuked.')
else:
    print('File converstion did not complete, please verify there were no errors.')

# disconnect from VPN and come back from wherever you were
terminate_VPN()