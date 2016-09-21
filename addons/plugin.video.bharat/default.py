# -*- coding: utf-8 -*-

import re
import os
import sys
import urllib2
import xbmcgui
import xbmcplugin
import xbmc
import HTMLParser
import urlresolver
import time

from t0mm0.common.addon import Addon
from BeautifulSoup import BeautifulSoup


#TODO :
#1. images needs to created
#2. migrate_to_mysql needs to tested.

addon_name = "bharat"

addon = Addon('plugin.video.'+addon_name, sys.argv)

try:
    DB_NAME =    addon.get_setting('db_name')
    DB_USER =    addon.get_setting('db_user')
    DB_PASS =    addon.get_setting('db_pass')
    DB_ADDRESS = addon.get_setting('db_address')

    if  addon.get_setting('use_remote_db')=='true' and \
        DB_ADDRESS is not None and \
        DB_USER    is not None and \
        DB_PASS    is not None and \
        DB_NAME    is not None:
        import mysql.connector as database
        addon.log('Loading MySQL as DB engine')
        DB = 'mysql'
    else:
        addon.log('MySQL not enabled or not setup correctly')
        raise ValueError('MySQL not enabled or not setup correctly')
except:
    try: 
        from sqlite3 import dbapi2 as database
        addon.log('Loading sqlite3 as DB engine')
    except: 
        from pysqlite2 import dbapi2 as database
        addon.log('pysqlite2 as DB engine')
    DB = 'sqlite'
    db_dir = os.path.join(xbmc.translatePath("special://database"), addon_name+'.db')

META_ON = addon.get_setting('use-meta') == 'true'
FANART_ON = addon.get_setting('enable-fanart') == 'true'
USE_POSTERS = addon.get_setting('use-posters') == 'true'
THEME_LIST = ['mikey1234', 'Glossy_Black']
THEME = THEME_LIST[int(addon.get_setting('theme'))]
THEME_PATH = os.path.join(addon.get_path(), 'resources', 'art', 'themes', THEME)
LOGO = os.path.join(addon.get_path(), 'resources', 'art', 'logo.png')
HOST = "www.bharatchannels.com"
BASE_URL = 'http://' + HOST
USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
AZ_DIRECTORIES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


def init_routines():
    addon.log('Building ' + addon_name + ' Database in ' + DB)
    if DB == 'mysql':
        print DB_NAME
        print DB_USER
        print DB_PASS
        print DB_ADDRESS
        db = database.connect(DB_NAME, DB_USER, DB_PASS, DB_ADDRESS, buffered=True)
        cur = db.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS favorites (video_type VARCHAR(10), title TEXT, url VARCHAR(255) UNIQUE, section VARCHAR(255), mode VARCHAR(255), img VARCHAR(512), fanart VARCHAR(512), is_folder bool)')
        cur.execute('CREATE TABLE IF NOT EXISTS url_cache (url VARCHAR(255), response TEXT, timestamp TEXT)')

        try:
            cur.execute('CREATE UNIQUE INDEX unique_bmk ON bookmarks (video_type, title, season, episode, year)')
        except:
            pass
    else:

        # Create the profile directory for storing addon specific files
        if not os.path.isdir(addon.get_profile()):
            os.makedirs(addon.get_profile())

        if not os.path.isdir(os.path.dirname(db_dir)):
            os.makedirs(os.path.dirname(db_dir))
        db = database.connect(db_dir)
        db.execute('CREATE TABLE IF NOT EXISTS url_cache (url UNIQUE, response, timestamp)')
        db.execute('CREATE TABLE IF NOT EXISTS favorites (video_type, title, url, section, mode, img, fanart, is_folder)')
        db.execute('CREATE UNIQUE INDEX IF NOT EXISTS unique_fav ON favorites (video_type, title, url)')
        db.execute('CREATE UNIQUE INDEX IF NOT EXISTS unique_url ON url_cache (url)')
        db.commit()
        db.close()


def add_directory(mode, section, url, title, page=None, letter=None, fanart='', img='',  is_folder=True, video_type=None, menu_mode=None, menu_title=None):
    queries = {'mode': mode, 'url': url, 'video_type': video_type}
    infolabels = {'title': title}
    if (section is not None):
        queries['section'] = section

    if (page is not None):
        queries['page'] = page

    if (letter is not None):
        queries['letter'] = letter

    if (not FANART_ON):
        fanart = ''

    if (menu_mode is not None):
        cm = add_contextmenu(video_type, menu_mode, menu_title, mode, section, url, title, img, fanart, is_folder)
    else:
        cm = None

    addon.add_directory(queries, infolabels, contextmenu_items=cm, context_replace=True,
                        img=img, fanart=fanart, total_items=0, is_folder=is_folder)


def set_view(content, viewType):
    # set content type so library shows more views and info
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if addon.get_setting('auto-view') == 'true':
        xbmc.executebuiltin("Container.SetViewMode(%s)" % addon.get_setting(viewType))


def get_html(url, params=None, referrer=HOST, silent=False, cache_limit=None):
    #addon.log('get_URL: %s' % url)
    if cache_limit is None:
        cache_limit = addon.get_setting('cache-hours')
    #print "Cache-limit " + cache_limit
    if DB == 'mysql': 
        db = database.connect(DB_NAME, DB_USER, DB_PASS, DB_ADDRESS, buffered=True)
    else: 
        db = database.connect(db_dir)
    cur = db.cursor()
    now = time.time()
    limit = 60 * 60 * int(cache_limit)

    if (params is not None):
        new_url = url+":"+params
    else:
        new_url = url
    if (DB == 'mysql'):
        cur.execute("SELECT url, response, unix_timestamp(current_timestamp())-timestamp FROM url_cache WHERE url = '%s'" % new_url)
    else:
        cur.execute("SELECT url, response, (strftime('%%s','now') - timestamp) FROM url_cache WHERE url = '%s'" % new_url)
    cached = cur.fetchone()
    if cached:
        age = float(cached[2])
        #print "Age - %s, limit - %s" % (str(age),str(limit))
        if age < limit:
            addon.log('Returning cached result for %s' % url)
            db.close()
            return cached[1]
        else:
            addon.log('Cache too old. Requesting from internet')
    else:
        addon.log('No cached response. Requesting from internet')

    if params is not None:
        req = urllib2.Request(url, params)
    else:
        req = urllib2.Request(url)

    req.add_header('User-Agent', USER_AGENT)
    req.add_header('Host', HOST)
    if referrer:
        req.add_header('Referer', referrer)

    try:
        response = urllib2.urlopen(req, timeout=10)
        body = response.read()
        h = HTMLParser.HTMLParser()
        body = h.unescape(body.decode('utf-8', 'ignore'))
    except:
        if not silent:
            dialog = xbmcgui.Dialog()
            dialog.ok("Connection failed", "Failed to connect to url", url)
            print "Failed to connect to URL %s" % url
        return ''
    response.close()
    sql = "REPLACE INTO url_cache (url,response,timestamp) VALUES(%s,%s,%s)"
    if DB == 'sqlite':
        sql = 'INSERT OR ' + sql.replace('%s', '?')
    if cache_limit > 0:  # Cache only if the cache limit is greater than 0
        if (params is not None):
            cur.execute(sql, (url+':'+params, body, now))
        else:
            cur.execute(sql, (url, body, now))
        db.commit()
        db.close()
    return body


def get_art(filename):
    img = os.path.join(THEME_PATH, filename)
    addon.log('get_art: %s' % img)
    return img


def save_favorites(video_type, mode, section, url, title, img, fanart, is_folder=True):
    addon.log('Saving video type: %s title: %s url: %s img: %s mode: %s' % (video_type, title, url, img, mode))
    statement = 'INSERT INTO favorites (video_type, title, url, section, mode, img, fanart, is_folder) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
    if DB == 'mysql':
        db = database.connect(DB_NAME, DB_USER, DB_PASS, DB_ADDRESS, buffered=True)
    else:
        db = database.connect(db_dir)
        statement = statement.replace("%s", "?")
    cursor = db.cursor()

    try:
        if (DB == 'mysql'):
            if is_folder == 'True':
                folder = 1
            else:
                folder = 0
            print "is folder" + str(is_folder)
            print "folder" + str(folder)
            cursor.execute(statement, (video_type, title, url, section, mode, img, fanart, folder))
        else:
            cursor.execute(statement, (video_type, title, url, section, mode, img, fanart, is_folder))
        addon.show_small_popup(addon_name, 'Added to Favorites', 4000, get_art('logo.png'))
    except database.IntegrityError:
        addon.show_small_popup(addon_name, 'Item already in Favorites', 4000, get_art('logo.png'))
    db.commit()
    db.close()


def delete_favorites(video_type, url, title):
    addon.log('Deleting Fav: %s, %s, %s' % (video_type, title, url))
    sql_del = 'DELETE FROM favorites WHERE video_type=%s AND title=%s AND url=%s'
    if DB == 'mysql':
        db = database.connect(DB_NAME, DB_USER, DB_PASS, DB_ADDRESS, buffered=True)
    else:
        db = database.connect(db_dir)
        sql_del = sql_del.replace('%s', '?')
    cursor = db.cursor()
    cursor.execute(sql_del, (video_type, title, url))
    addon.show_small_popup(addon_name, 'Deleted from Favorites Successfully.', 4000, get_art('logo.png'))
    xbmc.executebuiltin("XBMC.Container.Refresh")
    db.commit()
    db.close()


def browse_favorites(video_type):
    if (video_type == ''):
        sql = 'SELECT distinct video_type FROM favorites '
        if DB == 'mysql':
            db = database.connect(DB_NAME, DB_USER, DB_PASS, DB_ADDRESS, buffered=True)
            sql = sql.replace('?', '%s')
        else:
            db = database.connect(db_dir)
        cur = db.cursor()
        cur.execute(sql)
        video_types = cur.fetchall()
        for row in video_types:
            add_directory('browse_favorites', None, None, row[0], video_type=row[0])
        db.close()
    else:
        sql = 'SELECT video_type, title, url, section, mode, img, fanart, is_folder FROM favorites where video_type = ?'
        if DB == 'mysql':
            db = database.connect(DB_NAME, DB_USER, DB_PASS, DB_ADDRESS, buffered=True)
            sql = "SELECT video_type, title, url, section, mode, img, fanart, if(is_folder=1, 'True', 'False') FROM favorites where video_type = ?"
            sql = sql.replace('?', '%s')
        else:
            db = database.connect(db_dir)
        cur = db.cursor()
        cur.execute(sql, (video_type,))
        video_types = cur.fetchall()
        for row in video_types:
            video_type = row[0]
            title = row[1]
            url = row[2]
            section = row[3]
            mode = row[4]
            img = row[5]
            fanart = row[6]
            is_folder = True if row[7] == 'True' else False
            add_directory(mode, section, url, title, img=img, fanart=fanart, is_folder=is_folder, video_type=video_type, menu_mode='delete_favorites', menu_title='Delete From Favorites')
        db.close()


def migrate_to_mysql():
    try:
        from sqlite3 import dbapi2 as sqlite
        addon.log('Loading sqlite3 for migration')
    except:
        from pysqlite2 import dbapi2 as sqlite
        addon.log('pysqlite2 for migration')

    DB_NAME = addon.get_setting('db_name')
    DB_USER = addon.get_setting('db_user')
    DB_PASS = addon.get_setting('db_pass')
    DB_ADDRESS = addon.get_setting('db_address')
    sqlite_db = sqlite.connect(db_dir)
    mysql_db = database.connect(DB_NAME, DB_USER, DB_PASS, DB_ADDRESS, buffered=True)
    table_count = 1
    record_count = 1
    all_tables = ['favorites', 'url_cache']
    prog_ln1 = 'Migrating table %s of %s' % (table_count, 3)
    progress = xbmcgui.DialogProgress()
    ret = progress.create('Migrating DB to MySQL', prog_ln1)
    while not progress.iscanceled() and table_count < 2:
        for table in all_tables:
            mig_prog = int((table_count*100)/2)
            prog_ln1 = 'Migrating table %s of %s' % (table_count, 3)
            progress.update(mig_prog, prog_ln1)
            record_sql = 'SELECT * FROM %s' % table
            #print record_sql
            cur = mysql_db.cursor()
            all_records = sqlite_db.execute(record_sql).fetchall()
            for record in all_records:
                prog_ln1 = 'Migrating table %s of %s' % (table_count, 3)
                prog_ln2 = 'Record %s of %s' % (record_count, len(all_records))
                progress.update(mig_prog, prog_ln1, prog_ln2)
                args = ','.join('?'*len(record))
                args = args.replace('?', '%s')
                insert_sql = 'REPLACE INTO %s VALUES(%s)' % (table, args)
                #print insert_sql
                cur.execute(insert_sql, record)
                record_count += 1
            table_count += 1
            record_count = 1
            mysql_db.commit()
    sqlite_db.close()
    mysql_db.close()
    progress.close()
    dialog = xbmcgui.Dialog()
    ln1 = 'Do you want to permanantly delete'
    ln2 = 'the old database?'
    ln3 = 'THIS CANNOT BE UNDONE'
    yes = 'Keep'
    no = 'Delete'
    ret = dialog.yesno('Migration Complete', ln1, ln2, ln3, yes, no)
    if ret:
        os.remove(db_dir)


def add_contextmenu(video_type, menu_mode, menu_title, original_mode, section, url, title, img, fanart, is_folder):
    cm = []
    if (menu_mode == 'delete_favorites'):
        runstring = 'RunPlugin(%s)' % addon.build_plugin_url({'mode': 'delete_favorites', 'url': url, 'title': title, 'video_type': video_type})
        cm.append((menu_title, runstring))
    elif (menu_mode == 'save_favorites'):
        runstring = 'RunPlugin(%s)' % addon.build_plugin_url({'mode': 'save_favorites', 'original_mode': original_mode, 'url': url, 'title': title,
                                                             'video_type': video_type, 'section': section, 'is_folder': is_folder, 'img': img, 'fanart': fanart})
        cm.append((menu_title, runstring))
    return cm


def add_init_menu():
    addon.log('Initial Menu')
    init_routines()
    regexpr = '<a class="nav-\w*" href="(.+?)">(.+?)</a>'
    languages = search_page(BASE_URL, regexpr)
    if (languages):
        add_directory('browse_favorites', None, None, '[B][COLOR yellow]Browse Favorites[/COLOR][/B]', video_type='')
        for url, language in languages:
            add_directory('list_mainmenu', None, url, language)


def search_page(url, regexpr):
    addon.log('search_page : %s with %s' % (url, regexpr))
    html = get_html(url)
    match = re.compile(regexpr).findall(html)
    if match:
        addon.log("Match found ")
        return match
    else:
        addon.log("No Match found for the expression %s" % regexpr)
        return match


def list_mainmenu(url, section=None):
    addon.log('list_mainmenu : %s' % url)
    soup = BeautifulSoup(get_html(url), convertEntities=BeautifulSoup.HTML_ENTITIES)
    menulinks = soup.nav.ul
    if menulinks:
        for menuitem in menulinks:
            if (getattr(menuitem, 'name', None) is not None):
                if menuitem.a.text.lower() == 'home':
                    continue
                # if section is none we need to display the 1st submenu else display show them the mainmenu
                # agian but with a different section to display the 2nd level submenu
                if (section is None) or (section == ''):
                    if (menuitem.ul is not None):
                        add_directory('list_mainmenu', menuitem.a.text, url, menuitem.a.text)
                    else:
                        if (menuitem.a.text.lower() == "movies"):
                            add_directory('list_azdirectories', None, menuitem.a['href'], menuitem.a.text)
                        else:
                            add_directory('list_submenu', None, menuitem.a['href'], menuitem.a.text)
                else:
                    if (menuitem.a.text == section):
                        menusubitems = menuitem.findAll('a')
                        counter = 0
                        for menusubitem in menusubitems:
                            counter = counter + 1
                            if (counter > 1):
                                add_directory('list_submenu', section, menusubitem['href'], menusubitem.text)
    else:
        addon.log("************* Menulinks reterive Failed **********************")


def list_submenu(url, section):
    addon.log("list_submenu : %s,%s" % (url, section))
    soup = BeautifulSoup(get_html(url), convertEntities=BeautifulSoup.HTML_ENTITIES)  # cache get refreshed every 12 hours
    blocks = soup.findAll('div', attrs={'class': 'left'})
    if blocks:
        for block in blocks:
            # code to parse the blocks like ( Serials, Notable Shows & TV Shows) from the tv home page
            header = block.find(attrs={'class': 'header'}).contents[0]
            if (header.lower().find('sharing') < 0):
                add_directory('list_tv_categories', header, url, header)
    else:
        addon.log("************** DIV LOOKUP FAILED *******************")


def list_tv_categories(url, section):
    addon.log("list_submenu : %s,%s" % (url, section))
    soup = BeautifulSoup(get_html(url), convertEntities=BeautifulSoup.HTML_ENTITIES)  # cache get refreshed every 12 hours
    blocks = soup.findAll('div', attrs={'class': 'left'})
    if blocks:
        for block in blocks:
            # code to parse the blocks like ( Serials, Notable Shows & TV Shows) from the tv home page
            header = block.find(attrs={'class': 'header'}).contents[0]
            # code to parse the serial titles from the same tv home page
            #if ((header.lower().find('classic serials') > 0) and (section.lower().find('classic serials') > 0)):
            #    print "inside classic serials"
            #    list_initial_show_page(url, section, block)
            if ((header.lower().find('serials') > 0) and (section.lower().find('serials') > 0)):
                if (header.lower() == section.lower()):
                    titles = block.findAll('div', attrs={'class': 'folioBoxInside'})
                    for title in titles:
                        url = title.div.a['href']
                        if (url.lower().find(BASE_URL.lower()) < 0):
                            url = BASE_URL + '/' + url
                        add_directory('list_initial_show_page', title.div.a.text, url, title.div.a.text, fanart=title.a.img['src'],
                                      img=title.a.img['src'], video_type='Serials', menu_mode='save_favorites', menu_title='Save To Favorites')
                    set_view('tvshows', 'tvshows-view')
                    break
            # code to parse the notable tv shows from the same tv home page
            if ((header.lower().find('notable show') > 0) and (section.lower().find('notable show') > 0)):
                titles = block.findAll('div', attrs={'class': 'folioBoxInside'})
                for title in titles:
                    url = BASE_URL + '/' + title.div.a['href']
                    add_directory('list_initial_show_page', title.div.a.text, url, title.div.a.text, fanart=title.a.img['src'], img=title.a.img['src'],
                                  video_type='Super Hit TV Shows', menu_mode='save_favorites', menu_title='Save To Favorites')
                set_view('tvshows', 'tvshows-view')
                break
            # code to parse the other tv shows from the same tv home page
            if (header.lower().find('sharing') < 0):
                list_initial_show_page(url, section, block)


def list_initial_show_page(url, section, block=None):
    addon.log("list_initial_show_page : %s,%s" % (url, section))
    new_request = False
    if (block is None):   # If it is true meaning it is a new request
        new_request = True
        block = BeautifulSoup(get_html(url, cache_limit=1), convertEntities=BeautifulSoup.HTML_ENTITIES)   # cache get refreshed every 2 hours
    titles = block.findAll('div', attrs={'class': 'item'})
    urls = search_page(url, 'url: "(.+?)",')
    for url in urls:
        if (url.lower().find("scroll") > 0):
            break
    if (titles):
        for title in titles:
            show_name = title.find('span', attrs={'class': 'artist_name'}).text
            add_directory('locate_play_source', show_name, title.a['href'], show_name, fanart=title.a.img['src'], img=title.a.img['src'], is_folder=False,
                          video_type='Other Shows', menu_mode='save_favorites', menu_title='Save To Favorites')
        if (new_request):
            paging = block.find('ul', attrs={'class': 'appendvideos'})
            add_directory('list_more_shows', section, BASE_URL + url, 'Next Page >>', letter=paging.li['l'], page=paging.li['p'],
                          fanart=get_art('fanart.png'), img=get_art('next.png'))
        else:
            add_directory('list_more_shows', section, BASE_URL + url, 'Next Page >>', letter=block.div.ul.li['l'], page=block.div.ul.li['p'],
                          fanart=get_art('fanart.png'), img=get_art('next.png'))
        set_view('episodes', 'episodes-view')


def list_more_shows(url, section, letter, page):
    addon.log("list_more_shows : %s,%s,%s,%s" % (url, section, letter, page))
    query = "letter=%s&start=%s" % (letter.lower().replace(" ", "-"), page)
    #print get_html(url, query, cache_limit=1)
    soup = BeautifulSoup(get_html(url, query, cache_limit=1), convertEntities=BeautifulSoup.HTML_ENTITIES)   # cache get refreshed every 2 hours

    titles = soup.findAll('div', attrs={'class': 'item'})
    if (titles):
        for title in titles:
            show_name = title.find('span', attrs={'class': 'artist_name'}).text
            #TODO: cleanup
            #show_name = show_name.decode('utf-8')
            add_directory('locate_play_source', show_name, title.a['href'], show_name, fanart=title.a.img['src'], img=title.a.img['src'], is_folder=False,
                          video_type='Other Shows', menu_mode='save_favorites', menu_title='Save To Favorites')
        add_directory('list_more_shows', section, url, 'Next Page >>', letter=letter, page=soup.li['p'], fanart=get_art('fanart.png'), img=get_art('next.png'))
        set_view('episodes', 'episodes-view')


def list_azdirectories(url):
    addon.log('list_azdirectories : %s' % url)
    lists = search_page(url, 'url: "(.+?)",')
    movie_url = BASE_URL + lists[0]
    add_directory('list_movies', None, movie_url, '#123', letter='#', fanart=get_art('fanart.png'), img=get_art('123.png'))
    for char in AZ_DIRECTORIES:
        add_directory('list_movies', None, movie_url, char, letter=char, fanart=get_art('fanart.png'), img=get_art(char+'.png'))


def list_movies(url, letter):
    addon.log('list_movies : %s, %s' % (url, letter))
    soup = BeautifulSoup(get_html(url, "letter="+letter), convertEntities=BeautifulSoup.HTML_ENTITIES)   # cache get refreshed every 12 hours
    matchs = soup.findAll('div', attrs={'class': 'item'})
    if matchs:
        for match in matchs:
            add_directory('locate_play_source', None, match.a['href'], match.span.text, fanart=match.a.img['src'], img=match.a.img['src'], is_folder=False,
                          video_type='Movies', menu_mode='save_favorites', menu_title='Save To Favorites')
        set_view('movies', 'movies-view')


def locate_play_source(url, section, title, img, video_type):

    html = get_html(url, cache_limit=0)
    ythost = "youtube.com"
    # Handle iframe tags
    sourceVideos = re.compile('<iframe(.+?)>').findall(html)

    if len(sourceVideos) == 0:
        if (re.search('http://www.youtube.com/watch_popup', html)):
            media_id = re.compile("http://www.youtube.com/watch_popup\?v=(.+?)'").findall(html)[0]
            stream_url = urlresolver.HostedMediaFile(host=ythost, media_id=media_id).resolve()
            addon.resolve_url(stream_url)
            addon.log('Playing the popup video')
        elif (re.search('http://www.youtube.com/watch\?', html)):
            media_id = re.compile("http://www.youtube.com/watch\?v=(.+?)\&").findall(html)[0]
            stream_url = urlresolver.HostedMediaFile(host=ythost, media_id=media_id).resolve()
            addon.resolve_url(stream_url)
            addon.log('Playing the javascript popup video')
        else:
            addon.show_small_popup(addon_name, 'No Video sources found', 4000, get_art('logo.png'))
        return
    for sourceVideo in sourceVideos:
        if re.search('http://www.youtube.com/p/', sourceVideo):
            media_id = re.compile('http://www.youtube.com/p/(.+?)[&,\?]').findall(sourceVideo)[0]
            stream_url = urlresolver.HostedMediaFile(host=ythost, media_id=media_id).resolve()
            addon.resolve_url(stream_url)
            addon.log('Playing the playlist')
        elif re.search('http://www.youtube.com/v/', sourceVideo):
            media_id = re.compile('http://www.youtube.com/v/(.+?)\?').findall(sourceVideo)[0]
            stream_url = urlresolver.HostedMediaFile(host=ythost, media_id=media_id).resolve()
            addon.resolve_url(stream_url)
            addon.log('Playing the youtube video')
        elif re.search('http://www.youtube.com/embed/videoseries(.+?)', sourceVideo):
            try:
                addon.log("found embeded youtube video series")
                list_id = re.compile('http://www.youtube.com/embed/videoseries\?list=(.+?)"').findall(sourceVideo)[0]
                media_ids = re.compile("<media:player url='.+?v=(.+?)&.+?'/>").findall(get_html("http://gdata.youtube.com/feeds/api/playlists/"+str(list_id), cache_limit=0))
                partnum = 0
                sources = []
                for media_id in media_ids:
                    hosted_media = urlresolver.HostedMediaFile(host=ythost, media_id=media_id, title=title + '-' + str(partnum))
                    sources.append(hosted_media)
                    partnum += 1
                #source = urlresolver.choose_source(sources).get_url()
                addon.resolve_url(stream_url)
                addon.log('Playing from the youtube video series')
            except:
                pass
        elif re.search('http://www.youtube.com/embed/', sourceVideo):
            media_id = re.compile('http://www.youtube.com/embed/(.+?)[\?\"]').findall(sourceVideo)[0]
            stream_url = urlresolver.HostedMediaFile(host=ythost, media_id=media_id).resolve()
            addon.log("Streaming URL is %s" % stream_url)
            addon.resolve_url(stream_url)
            addon.log('Playing the youtube video')
        else:
            addon.show_small_popup(addon_name, 'Unable to parse the video source. ', 6000, get_art('logo.png'))


mode = addon.queries.get('mode', None)
is_folder = addon.queries.get('is_folder', True)
section = addon.queries.get('section', '')
letter = addon.queries.get('letter', '')
url = addon.queries.get('url', '')
title = addon.queries.get('title', '')
img = addon.queries.get('img', '')
page = addon.queries.get('page', '')
video_type = addon.queries.get('video_type', '')
original_mode = addon.queries.get('original_mode', '')
fanart = addon.queries.get('fanart', '')


addon.log(addon.queries)

if mode == 'main':
    add_init_menu()
elif mode == 'list_mainmenu':
    list_mainmenu(url, section)
elif mode == 'list_azdirectories':
    list_azdirectories(url)
elif mode == 'list_movies':
    list_movies(url, letter)
elif mode == 'list_submenu':
    list_submenu(url, section)
elif mode == 'list_tv_categories':
    list_tv_categories(url, section)
elif mode == 'list_initial_show_page':
    list_initial_show_page(url, section)
elif mode == 'list_more_shows':
    list_more_shows(url, section, letter, page)
elif mode == "locate_play_source":
    locate_play_source(url, section, title, img, video_type)
elif mode == 'delete_favorites':
    delete_favorites(video_type, url, title)
elif mode == 'save_favorites':
    save_favorites(video_type, original_mode, section, url, title, img, fanart, is_folder)
elif mode == 'browse_favorites':
    browse_favorites(video_type)


if (mode != 'locate_play_source' or mode != 'save_favorites' or mode != 'delete_favorites'):
    addon.end_of_directory()
