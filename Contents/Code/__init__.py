NAME = 'TVBDO'
BASE_URL = 'http://tvbdo.com'
HK_DRAMA_URL = '%s/hong-kong-drama/page/%%d/' % BASE_URL
MOVIES_URL = '%s/movies/page/%%d/' % BASE_URL
PREFIX = '/video/tvbdo'

ART = 'art-default.jpg'
ICON = 'icon-default.jpg'
VERSION = '1.0.0'

####################################################################################################
def Start():

  Log("Starting TVBDO Plex Plugin: " + VERSION)
  
  ObjectContainer.art = R(ART)
  ObjectContainer.title1 = NAME
  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  VideoClipObject.thumb = R(ICON)
  VideoClipObject.art = R(ART)

  HTTP.CacheTime = CACHE_1HOUR
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:27.0) Gecko/20100101 Firefox/27.0'
  HTTP.Headers['Referer'] = 'http://tvbdo.com'
  HTTP.Headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
  HTTP.Headers['Accept-Encoding'] = 'gzip, deflate'
  HTTP.Headers['Connection'] = 'keep-alive'
  HTTP.Headers['HOST'] = 'tvbdo.com'

####################################################################################################
@handler(PREFIX, NAME, thumb=ICON, art=ART)
def MainMenu():

  oc = ObjectContainer()
  oc.add(DirectoryObject(key = Callback(ShowCategory, title='HK Drama', page_url=HK_DRAMA_URL), title='HK Drama'))
  
  return oc

####################################################################################################
@route(PREFIX + '/showcategory', page=int)
def ShowCategory(title, page_url, page=1):

  oc = ObjectContainer(title2=title)
  call_url = page_url % page

  if page == 1:
    call_url = 'http://tvbdo.com/hong-kong-drama'

  data = HTTP.Request(call_url).content
  html = HTML.ElementFromString(data)

  for each in html.xpath('//a[@class="clip-link"]'):
    each_title = each.xpath('./@title')[0]
    each_url = each.xpath('./@href')[0]
    each_thumb = each.xpath('./span[@class="clip"]/img/@src')[0]
    
    oc.add(DirectoryObject(
      key = Callback(ListEpisodes, page_title=each_title, page_url=each_url), 
      title = each_title,
      thumb = each_thumb
      ))

  if len(html.xpath('//a[@class="next"]')) > 0:
    oc.extend(ShowCategory(title=title, page_url=page_url, page=page+1))

  #else:
  #  oc.add(NextPageObject(
  #    key = Callback(ShowCategory, title=title, page_url=page_url, page=page+1),
  #    title = L('More...')
  #  ))
    
  return oc

####################################################################################################
@route(PREFIX + "/listepisodes")
def ListEpisodes(page_title, page_url):

  oc = ObjectContainer(title2=page_title)
  
  data = HTTP.Request(page_url).content
  html = HTML.ElementFromString(data)
  
  ep_thumb = html.xpath('//img[@class="m-poster"]/@src')[0]
  
  for each in html.xpath('//span[@class="episode_loop"]'):

    ep_title = each.xpath('./a/text()')[0]
    ep_url = BASE_URL + each.xpath('./a/@href')[0]

    oc.add(VideoClipObject(
      url = ep_url,
      title = ep_title,
      thumb = ep_thumb
      ))

  return oc

######################################################################################
# deal with page refreshes.
@route(PREFIX + "/httprequest")
def HTMLElementFromURL(url):

  request = HTTP.Request(url)
  if 'http-equiv="refresh"' in request.content:
    request = HTTP.Request(url, cacheTime=None)

  return HTML.ElementFromString(request.content)
