from os import path, listdir, makedirs, remove
from time import sleep
from sys import stdout
from re import compile
from wget import download
from pydub import AudioSegment
from nordvpn_switcher import initialize_VPN,rotate_VPN,terminate_VPN
from pytube import Playlist, YouTube
from shutil import Error, rmtree
from pathlib import Path as p

def progress(count, total, status=''):
    
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    stdout.flush()  
      
def artistInfo(pl):
    # for getting the artist name
    artist_url = list(pl).pop(0)
    author_name = YouTube(artist_url).author
    artist_list = author_name.split(' -', 1)
    artist = artist_list.pop(0)
    # special char check in artist name
    if(special_char.search(artist) == None):
        pass
    else:
        artist = input('ERROR: ARTIST NAME! \nPlease Manually Enter Without Special Characters --> ')
    return artist
    
def albumInfo(pl):
    # album title information
    full_title = pl.title
    title_list = full_title.split('- ', 1)
    album = title_list.pop(1)
    # special char check in album name
    if(special_char.search(album) == None):
        pass
    else:
        album = input('ERROR: ALBUM NAME! \nPlease Manually Enter Without Special Characters --> ')
    return album

def folderPrep():
       
    try:
        makedirs(mp4_dir)
        print("'{0}' created! Name of the Album is {1}.".format(mp4_dir,album))
    
    except FileExistsError:
        fileError = ("'{0}' already exisits! Nuking temp folder in 10 seconds.".format(mp4_dir))
        print(fileError)
        sleep(10)
        rmtree(mp4_dir, ignore_errors=True)
        # print("'{0}' created! Name of the Album is {1}.".format(mp4_dir,album))
        
    try:
        # p(convert_dir).exists():
        # rmtree(convert_dir, ignore_errors=True)
        makedirs(convert_dir)
    except FileExistsError:
        rmtree(convert_dir, ignore_errors=True)
        makedirs(convert_dir)
        
    if path.exists(art_jpg):
        remove(art_jpg)
        print('Folder Prep Complete')
    else:
        print('Folder Prep Complete')
        
    return mp4_dir, convert_dir

def getPlaylist(url):
    YOUTUBE_STREAM_AUDIO = '140'
    pl = Playlist(url)
     
    try:
        rotate_VPN()

    except Error:
        initialize_VPN(stored_settings=1)
        rotate_VPN()

    sleep(3)
    print('Starting download of album art and songs.')
      
    mp4_count = 1
    for video in pl.videos:
        totalSongs = len(pl.video_urls)
        progress(mp4_count, totalSongs, status='#')
        audioStream = video.streams.get_by_itag(YOUTUBE_STREAM_AUDIO)
        audioFile = '{0} - '.format(artist)
        audioStream.download(output_path=mp4_dir, filename_prefix=audioFile)
        mp4_count += 1
        sleep(2)
        
    # download album art and show no progress bar
    download(art_url, out=downloads_path, bar=None)
    
    terminate_VPN()
    print('Playlist downloaded!')  

def audioConversion(audio_format):
    audio_format = audio_format.lower()
    print('Conversion Process to {0} Starting.'.format(audio_format))
            
    # convert from mp4 to user specified type
    convert_file_count = 1
    for songs in listdir(mp4_dir):
        track_title = songs.split('- ', 1)
        song = track_title.pop(1)
        song = song.replace('.mp4','')
        
        total_songs = len(listdir(mp4_dir))
        progress(convert_file_count, total_songs, status='#')
        
        mp4_file = '{0}\\{1}'.format(mp4_dir,songs)
        convert_file = '{0}\\{1} - {2}.{3}'.format(convert_dir, artist, song, audio_format)
        audioFile = AudioSegment.from_file(mp4_file, format='mp4')
        audioFile.export(convert_file,
                         format=audio_format, 
                         bitrate='320k',
                         tags={"album": album, "artist": artist, "title": song, "track": '{0}\{1}'.format(convert_file_count,total_songs)}
                        , cover=art_jpg
                        )
        convert_file_count += 1
        sleep(2)
    
    print('Audio converstion complete, deleting downloads ({0}).'.format(mp4_dir))
    rmtree(mp4_dir, ignore_errors=True)
    remove(art_jpg)
    
# urls related to the YouTube Music playlist
playlist_url = input('Enter YouTube Music Playlist URL --> ')
art_url = input('Enter URL For Album Art JPG --> ')
pl = Playlist(playlist_url)

# get output format for files from user
output_format = input('Enter Desired Audio Output Format (WAV, MP3, M4A, OGG) --> ')

# special characer checks
special_char = compile('[@_!#$%^&*()<>?/\|}{~:ミラクルミュージカル]')

# get a artist and album name
artist = artistInfo(pl)
album = albumInfo(pl)

# where all of the converted music lives, default is 'Music' folder in home
record_cabinet = str(p.home() / 'Music')

# where mp4's will be downloaded and then deleted once converstion is complete
downloads_path = str(p.home() / "Downloads")

# folders based on name of playlist and artist
mp4_dir = '{0}\\{1} - {2}'.format(downloads_path, artist, album)
convert_dir = '{0}\\{1} - {2}'.format(record_cabinet, artist, album)
art_jpg = '{0}\\unnamed.jpg'.format(downloads_path)

folderPrep()
getPlaylist(playlist_url)
audioConversion(output_format)