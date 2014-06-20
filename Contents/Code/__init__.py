TITLE = 'Fox News'
NEWS_CLIPS = 'http://video.foxnews.com/v/feed/page/news-clips.json'
SHOW_CLIPS = 'http://video.foxnews.com/v/feed/page/show-clips.json'

###################################################################################################
def Start():

  ObjectContainer.title1 = TITLE
  HTTP.CacheTime = 1800

###################################################################################################
@handler('/video/foxnews', TITLE)
def MainMenu():

  oc = ObjectContainer()
  oc.add(DirectoryObject(key=Callback(Sections, title='News Clips', type='news'), title='News Clips'))
  oc.add(DirectoryObject(key=Callback(Sections, title='Show Clips', type='show'), title='Show Clips'))
  oc.add(SearchDirectoryObject(identifier='com.plexapp.plugins.foxnews', title='Search', summary='Search Fox News Videos', prompt='Search:', thumb=R('search.png')))

  return oc

###################################################################################################
@route('/video/foxnews/sections/{type}')
def Sections(title, type):

  oc = ObjectContainer(title2=title)

  if type == 'news':
    feed_url = NEWS_CLIPS
  elif type == 'show':
    feed_url = SHOW_CLIPS

  json_obj = JSON.ObjectFromURL(feed_url)

  for section in json_obj['sub_sections']:
    title = section['title']
    feed_url = section['feed']

    oc.add(DirectoryObject(
      key = Callback(Content, title=title, url=feed_url),
      title = title
    ))

  return oc

###################################################################################################
@route('/video/foxnews/content')
def Content(title, url):

  oc = ObjectContainer(title2=title)
  json_obj = JSON.ObjectFromURL(url)

  for content in json_obj['contents']:

    if 'playlist' in content and 'feed' in content['playlist']:

      title = content['title']
      summary = content['description']
      feed_url = content['playlist']['feed']

      oc.add(DirectoryObject(
        key = Callback(Playlist, title=title, url=feed_url),
        title = title,
        summary = summary
      ))

    elif 'show' in content:

      id = content['show']['id']
      title = content['show']['name']
      summary = content['show']['description']

      oc.add(DirectoryObject(
        key = Callback(Show, id=id, title=title, url=url),
        title = title,
        summary = summary
      ))

    else:

      continue

  return oc

###################################################################################################
@route('/video/foxnews/show/{id}')
def Show(id, title, url):

  oc = ObjectContainer(title2=title)
  json_obj = JSON.ObjectFromURL(url)

  for content in json_obj['contents']:

    if content['show']['id'] == id:

      # If just 1 playlist, and not a list with playlists
      if 'name' in content['show']['playlists']:

        playlist = content['show']['playlists']

        title = playlist['name']
        summary = playlist['description']
        feed_url = playlist['feed']

        oc.add(DirectoryObject(
          key = Callback(Playlist, title=title, url=feed_url),
          title = title,
          summary = summary
        ))

      # If multiple playlists
      else:

        for playlist in content['show']['playlists']:

          title = playlist['name']
          summary = playlist['description']
          feed_url = playlist['feed']

          oc.add(DirectoryObject(
            key = Callback(Playlist, title=title, url=feed_url),
            title = title,
            summary = summary
          ))

      break

  return oc

###################################################################################################
@route('/video/foxnews/playlist')
def Playlist(title, url):

  oc = ObjectContainer(title2=title)
  json_obj = JSON.ObjectFromURL(url)

  for video in json_obj['channel']['item']:

    title = video['title']
    summary = video['media-content']['media-description']
    thumb = video['media-content']['media-thumbnail']
    duration = int(video['media-content']['mvn-duration']) * 1000
    originally_available_at = Datetime.ParseDate(video['media-content']['mvn-airDate'])
    id = video['media-content']['mvn-assetUUID']

    oc.add(VideoClipObject(
      url = 'http://video.foxnews.com/v/%s' % id,
      title = title,
      summary = summary,
      thumb = Resource.ContentsOfURLWithFallback(url=thumb),
      duration = duration,
      originally_available_at = originally_available_at
    ))

  return oc
