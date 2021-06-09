import os, sys, time
from moviepy.editor import *
from nordvpn_switcher import initialize_VPN,rotate_VPN,terminate_VPN
from pytube import Playlist, YouTube
from shutil import rmtree
from pathlib import Path as p

def progress(count, total, status=''):
    
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush() 

def getPlaylist(url):
    YOUTUBE_STREAM_AUDIO = "140"
    pl = Playlist(url)    
    
    initialize_VPN(stored_settings=1)
    rotate_VPN()
    time.sleep(5)
    print('Starting download.')
    
    mp4_count = 1
    for video in pl.videos:
        totalSongs = len(pl.video_urls)
        progress(mp4_count, totalSongs, status='#')
        audioStream = video.streams.get_by_itag(YOUTUBE_STREAM_AUDIO)
        audioFile = '{0} - '.format(artist)
        audioStream.download(output_path=mp4_dir, filename_prefix=audioFile)
        mp4_count += 1
    
    terminate_VPN()
    print('Playlist downloaded!')  

def folderPrep():
    try:
        os.makedirs(mp4_dir)
        print("'{0}' created! Name of the Album is {1}.".format(mp4_dir,album_name))
    
    except FileExistsError:
        fileError = ("'{0}' already exisits! Nuking temp folder in 10 seconds.".format(mp4_dir))
        print(fileError)
        time.sleep(10)
        rmtree(mp4_dir, ignore_errors=True)
        print("'{0}' created! Name of the Album is {1}.".format(mp4_dir,album_name))
        
    if p(convert_dir).exists():
        rmtree(convert_dir, ignore_errors=True)
        os.makedirs(convert_dir)
    else:
        os.makedirs(convert_dir)
        
    return mp4_dir, convert_dir

def audioConversion(audio_format):
    audio_format = audio_format.lower()
    
    # convert from mp4 to user specified type
    mp3_count = 1    
    for songs in os.listdir(mp4_dir):
        mp4_file = mp4_dir +'\\' + songs
        convert_file = convert_dir + '\\' + songs.replace('mp4', audio_format)
        audioFile = AudioFileClip(mp4_file)
        audioFile.write_audiofile(convert_file)
        mp3_count += 1
    
    print('Audio converstion complete, deleting downloads ({0}).'.format(mp4_dir))
    rmtree(mp4_dir, ignore_errors=True)
    
# where all of the converted music lives, default is 'Music' folder in home
record_cabinet = str(p.home() / 'Music')

# where mp4's will be downloaded and then deleted once converstion is complete
downloads_path = str(p.home() / "Downloads")

# url of the YouTube Music playlist
playlist_url = input('Enter YouTube Music Playlist URL --> ')
pl = Playlist(playlist_url)

# get output format for files from user
output_format = input('Enter Desired Audio Output Format (WAV, MP3, etc) --> ')

# for getting the artist name
artist_url = list(pl).pop(0)
author_name = YouTube(artist_url).author
artist_list = author_name.split(' -', 1)
artist = artist_list.pop(0)

# artist and album title information
full_title = pl.title
title_list = full_title.split('- ', 1)
album_name = title_list.pop(1)

# folders based on name of playlist and artist
mp4_dir = '{0}\\{1} - {2}\\'.format(downloads_path, artist, album_name)
convert_dir = '{0}\\{1} - {2}\\'.format(record_cabinet, artist, album_name)

folderPrep()
getPlaylist(playlist_url)
audioConversion(output_format)
        

