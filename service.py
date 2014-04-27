# -*- coding: utf-8 -*- 

import os
import sys
import xbmc
import urllib
import urllib2
import xbmcvfs
import xbmcaddon
import xbmcgui
import xbmcplugin
import shutil
import unicodedata
import re
from AddictedUtilities import log, languageTranslate
from BeautifulSoup import BeautifulSoup

__addon__ = xbmcaddon.Addon()
__author__     = __addon__.getAddonInfo('author')
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__cwd__        = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode("utf-8")
__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) ).decode("utf-8")
__temp__       = xbmc.translatePath( os.path.join( __profile__, 'temp') ).decode("utf-8")

sys.path.append (__resource__)

self_host = "http://www.addic7ed.com"
self_release_pattern = re.compile("Version (.+), ([0-9]+).([0-9])+ MBs")
self_release_filename_pattern = re.compile(".*\-(.*)\.")

def compare_columns(b,a):
    return cmp( a["sync"], b["sync"] ) or cmp( b["language_name"], a["language_name"] )
    
def get_url(url):
    req_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.A.B.C Safari/525.13',
    'Referer': 'http://www.addic7ed.com'}
    request = urllib2.Request(url, headers=req_headers)
    opener = urllib2.build_opener()
    response = opener.open(request)

    contents = response.read() 
    return contents    

def append_subtitle(item):
    listitem = xbmcgui.ListItem(label=item['lang']['name'],
                                label2=item['filename'],
                                iconImage=item['rating'],
                                thumbnailImage=item['lang']['2let'])

    listitem.setProperty("sync",  'true' if item["sync"] else 'false')
    listitem.setProperty("hearing_imp", 'true' if item["hearing_imp"] else 'false')

    ## below arguments are optional, it can be used to pass any info needed in download function
    ## anything after "action=download&" will be sent to addon once user clicks listed subtitle to downlaod
    url = "plugin://%s/?action=download&link=%s&filename=%s" % (__scriptid__,
                                                                item['link'],
                                                                item['filename'])
    if 'find' in item:
        url += "&find=%s" % item['find']
    ## add it to list, this can be done as many times as needed for all subtitles found
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)

def query_TvShow(name, season, episode, langs, file_original_path):
    sublinks = []
    name = name.lower().replace(" ", "_").replace("$#*!","shit").replace("'","") # need this for $#*! My Dad Says and That 70s show
    searchurl = "%s/serie/%s/%s/%s/addic7ed" %(self_host, name, season, episode)
    socket.setdefaulttimeout(3)
    page = urllib2.urlopen(searchurl)
    content = page.read()
    content = content.replace("The safer, easier way", "The safer, easier way \" />")
    soup = BeautifulSoup(content)
    for subs in soup("td", {"class":"NewsTitle", "colspan" : "3"}):
      try:
        langs_html = subs.findNext("td", {"class" : "language"})
        fullLanguage = str(langs_html).split('class="language">')[1].split('<a')[0].replace("\n","")
        subteams = self_release_pattern.match(str(subs.contents[1])).groups()[0]
        file_name = self_release_filename_pattern.match(str(os.path.basename(file_original_path))).groups()[0].lower()
        if (str(subteams.lower()).find(str(file_name))) > -1:
          hashed = True
        else:
          hashed = False
        try:
          lang = languageTranslate(fullLanguage, 0, 2)
        except:
          lang = ""
        statusTD = langs_html.findNext("td")
        status = statusTD.find("b").string.strip()
        link = "%s%s"%(self_host,statusTD.findNext("td").find("a")["href"])
        if status == "Completed" and (lang in langs) :
           sublinks.append({'rating': '0', 'filename': "%s.S%.2dE%.2d-%s" %(name.replace("_", ".").title(), int(season), int(episode),subteams ), 'sync': hashed, 'link': link,
                                 'lang': lang, 'hearing_imp': "0"})
           #sublinks.append({'filename':"%s.S%.2dE%.2d-%s" %(name.replace("_", ".").title(), int(season), int(episode),subteams ),'link':link,'language_name':fullLanguage,'language_id':lang,'language_flag':"flags/%s.gif" % (lang,),'movie':"movie","ID":"subtitle_id","rating":"0","format":"srt","sync":hashed})
      except:
        print "Error"        
        pass      
    sublinks.sort(key=lambda x: [not x['sync']])
    for s in sublinks:
        append_subtitle(s)
 
def query_Film(name, file_original_path,year, langs):
    sublinks = []
    name = urllib.quote(name.replace(" ", "_"))
    searchurl = "%s/film/%s_(%s)-Download" %(self_host,name, str(year))
    socket.setdefaulttimeout(5)
    page = urllib2.urlopen(searchurl)
    content = page.read()
    content = content.replace("The safer, easier way", "The safer, easier way \" />")
    soup = BeautifulSoup(content)
    for subs in soup("td", {"class":"NewsTitle", "colspan" : "3"}):
      try:
        langs_html = subs.findNext("td", {"class" : "language"})
        fullLanguage = str(langs_html).split('class="language">')[1].split('&nbsp;<a')[0].replace("\n","")
        subteams = self_release_pattern.match(str(subs.contents[1])).groups()[0].lower()
        file_name = os.path.basename(file_original_path).lower()
        if (file_name.find(str(subteams))) > -1:
          hashed = True
        else:
          hashed = False  
        try:
          lang = fullLanguage
        except:
          lang = ""
        statusTD = langs_html.findNext("td")
        status = statusTD.find("b").string.strip()
        link = "%s%s"%(self_host,statusTD.findNext("td").find("a")["href"])
        if status == "Completed" and (lang in langs) :
            sublinks.append({'filename':"%s-%s" %(name.replace("_", ".").title(),subteams ),'link':link,'language_name':fullLanguage,'language_id':lang,'language_flag':"flags/%s.gif" % (lang,),'movie':"movie","ID":"subtitle_id","rating":"0","format":"srt","sync":hashed})
      except:
        pass
    return sublinks    

def Search(item):
    filename = os.path.splitext(os.path.basename(item['file_original_path']))[0]
    log(__name__, "Search_subscene='%s', filename='%s', addon_version=%s" % (item, filename, __version__))

    if item['mansearch']:
        search_manual(item['mansearchstr'], item['3let_language'], filename)
    elif item['tvshow']:
        query_TvShow(item['tvshow'], item['season'], item['episode'], item['3let_language'], filename)
    elif item['title'] and item['year']:
        query_Film(item['title'], item['year'], item['3let_language'], filename)
    else:
        search_filename(filename, item['3let_language'])

  
def download(link):
    subtitle_list = []
    
    file = os.path.join(__temp__, "adic7ed.srt")

    f = get_url(link)

    local_file_handle = open(file, "w" + "b")
    local_file_handle.write(f)
    local_file_handle.close() 
    
    subtitle_list.append(file)
    
    if len(subtitle_list) == 0:
        if search_string:
            xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__ , __language__(32002))).encode('utf-8'))
        else:
            xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__ , __language__(32003))).encode('utf-8'))

    return subtitle_list


def normalizeString(str):
    return unicodedata.normalize(
        'NFKD', unicode(unicode(str, 'utf-8'))
    ).encode('ascii', 'ignore')


def get_params():
    param = {}
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = paramstring
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param


params = get_params()

if params['action'] == 'search' or params['action'] == 'manualsearch':
    item = {}
    item['temp'] = False
    item['rar'] = False
    item['mansearch'] = False
    item['year'] = xbmc.getInfoLabel("VideoPlayer.Year")                             # Year
    item['season'] = str(xbmc.getInfoLabel("VideoPlayer.Season"))                    # Season
    item['episode'] = str(xbmc.getInfoLabel("VideoPlayer.Episode"))                  # Episode
    item['tvshow'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))   # Show
    item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle"))  # try to get original title
    item['file_original_path'] = urllib.unquote(xbmc.Player().getPlayingFile().decode('utf-8'))  # Full path
    item['3let_language'] = []

    if 'searchstring' in params:
        item['mansearch'] = True
        item['mansearchstr'] = params['searchstring']

    for lang in urllib.unquote(params['languages']).decode('utf-8').split(","):
        item['3let_language'].append(xbmc.convertLanguage(lang, xbmc.ISO_639_2))

    if item['title'] == "":
        item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title"))      # no original title, get just Title

    if item['episode'].lower().find("s") > -1:                                      # Check if season is "Special"
        item['season'] = "0"                                                          #
        item['episode'] = item['episode'][-1:]

    if item['file_original_path'].find("http") > -1:
        item['temp'] = True

    elif item['file_original_path'].find("rar://") > -1:
        item['rar'] = True
        item['file_original_path'] = os.path.dirname(item['file_original_path'][6:])

    elif item['file_original_path'].find("stack://") > -1:
        stackPath = item['file_original_path'].split(" , ")
        item['file_original_path'] = stackPath[0][8:]

    search(item)

elif params['action'] == 'download':
    ## we pickup all our arguments sent from def Search()
    subs = download(params["link"])
    ## we can return more than one subtitle for multi CD versions, for now we are still working out how to handle that
    ## in XBMC core
    for sub in subs:
        listitem = xbmcgui.ListItem(label=sub)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sub, listitem=listitem, isFolder=False)

xbmcplugin.endOfDirectory(int(sys.argv[1]))  # send end of directory to XBMC

