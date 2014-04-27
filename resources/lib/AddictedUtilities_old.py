# -*- coding: utf-8 -*- 

import xbmc

LANGUAGES      = (
    
    # Full Language name[0]     podnapisi[1]  ISO 639-1[2]   ISO 639-1 Code[3]   Script Setting Language[4]   localized name id number[5]
    
    ("English"                    , "2",        "en",            "eng",                 "0",                     30212  ),
    ("Hebrew"                     , "22",       "he",            "heb",                 "1",                     30218  ),
    ("French"                     , "8",        "fr",            "fre",                 "2",                     30215  ),
    ("Russian"                    , "27",       "ru",            "rus",                 "3",                     30236  ),)


   
def log(module,msg):
  xbmc.log((u"### [%s-%s] - %s" % (__scriptname__,module,msg,)).encode('utf-8'),level=xbmc.LOGDEBUG ) 

def languageTranslate(lang, lang_from, lang_to):
  for x in LANGUAGES:
    if lang == x[lang_from] :
      return x[lang_to]
