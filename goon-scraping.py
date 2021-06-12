from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time, os, random

def randomSong():
    cwd = os.getcwd()
    song_csv = '{0}\\songList.csv'.format(cwd)
    n = sum(1 for line in open(song_csv, encoding='utf8')) - 1 #number of records in file (excludes header)
    s = 1
    skip = sorted(random.sample(range(1,n+1),n-s))
    df = pd.read_csv(song_csv, skiprows=skip)
    df['song'] = df.astype('string')
    df = df.iloc[0]['song']
    return df
    
def songLink():
    
    random_track = randomSong()   
    youtube_base = u'https://www.youtube.com/'
    search_phrase = random_track

    browser = webdriver.Edge()
    url = 'https://music.youtube.com/search?q={0}'.format(search_phrase)
    browser.get(url)
    time.sleep(2)
 
    # Use Bs to Parse
    soup = BeautifulSoup(browser.page_source, 'lxml')
    watch_link = soup.findAll('a',attrs={'class':'yt-simple-endpoint style-scope yt-formatted-string'})[0]['href']
    # artist_raw = soup.findAll('a', attrs={'class':'yt-simple-endpoint style-scope yt-formatted-string'})[1]
    # track_raw = soup.findAll('a', attrs={'class':'yt-simple-endpoint style-scope yt-formatted-string'})[0]
    # print(artist_raw.get_text())
    # print(track_raw.get_text())
    
    song_link = (youtube_base + watch_link)
    browser.close()
    return song_link

songLink()
print(songLink())



