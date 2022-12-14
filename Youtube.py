import numpy as np
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup

class Youtube:
  API_KEY = None
  regionCode = None
  Data = None

  def __init__(self, key, maxResults, regionCode = 'US'):
    self.API_KEY = key
    self.regionCode = regionCode
    self.maxResults = maxResults
    init_data = np.array([None for i in range(9)]).reshape(1, 9)
    self.Data = pd.DataFrame(init_data, columns=['Id', 'URL', 'Keyword', 'Published At', 'Video Title', 'Rank', 'Channel', 'Thumbnail', 'Channel Url']).dropna()

  def get_search_data(self, keyword):
    params = {
    "key": self.API_KEY,
    "q": keyword,
    "part": "snippet",
    "regionCode": self.regionCode,
    "type": "video",
    "maxResults": self.maxResults
    }
    res = requests.get("https://youtube.googleapis.com/youtube/v3/search", params = params)

    return res

  def process_search_data(self, keyword = None, channel_id = None):
    if keyword:
      response = self.get_search_data(keyword)
    elif channel_id:
      response = self.get_channel_videos_data(channel_id)

    if response.status_code != 200:
      return {"status_code": response.status_code, "message": response.json()['error']['message']}

    search_data = response.json()["items"]

    if len(search_data) == 0:
      return "No results found"

    processed_data = {
        "Id": [],
        "URL": [],
        "Keyword": [],
        "Published At": [],
        "Video Title": [],
        "Rank": [],
        "Channel": [],
        "Thumbnail": [],
        "Channel Url": []
    }

    for i in range(len(search_data)):
      processed_data["Id"].append(search_data[i]['id']['videoId'])
      processed_data["URL"].append("https://www.youtube.com/watch?v=" + search_data[i]['id']['videoId'])
      processed_data["Keyword"].append(keyword)
      processed_data["Published At"].append(search_data[i]['snippet']['publishedAt'][:10])
      processed_data["Video Title"].append(search_data[i]['snippet']['title'])
      processed_data["Rank"].append(i+1)
      processed_data["Channel"].append(search_data[i]['snippet']['channelTitle'])
      processed_data["Thumbnail"].append(search_data[i]['snippet']['thumbnails']['default']['url'][:-11] + "maxresdefault.jpg")
      processed_data['Channel Url'].append("https://www.youtube.com/channel/" + search_data[i]['snippet']['channelId'])

    return pd.DataFrame(processed_data)

  def get_video_data(self, ids):
    views = []
    v_ids = ""

    # combining all Youtube Video ids
    for id in ids:
      v_ids += id + ","

    # fetching Youtube Video's data
    params = {
    "key": self.API_KEY,
    "id": v_ids[:-1],
    "part": "statistics"
    }
    res = requests.get("https://youtube.googleapis.com/youtube/v3/videos", params = params)

    return res


  def process_video_data(self):  # can be break into 2 methods
    # cannot fetch more than 50 videos data so here's the solution
    # below code can be added as another wrapper method
    if len(self.Data['Id']) > 50:
      responses = []
      len_of_ids = len(self.Data['Id'])
      start = 0
      end = 50
      while True:
        res = self.get_video_data(self.Data['Id'].iloc[start:end])
        if res.status_code != 200:
          return {"status_code": response.status_code, "message": response.json()['error']['message']}
        responses.append(res)
        start = end
        end += 50
        if end > len_of_ids:
          break
      if start+1 < len_of_ids:
        res = self.get_video_data(self.Data['Id'].iloc[start:])
        responses.append(res)

      response = []
      for res in responses:
        response.extend(res.json()['items'])

    else:
      response = self.get_video_data(self.Data['Id'])
      if response.status_code != 200:
        return {"status_code": response.status_code, "message": response.json()['error']['message']}
      response = response.json()["items"]


    video_statistics = {
    "Id": [],
    "Views": []
    }

    for video in response:
      video_statistics['Id'].append(video['id'])
      video_statistics['Views'].append(video['statistics']['viewCount'])

    video_statistics = pd.DataFrame(video_statistics)
    # self.Data = self.Data.join(video_statistics.set_index('Id').drop_duplicates(subset=['Id']), on='Id') # using below approach for faster computation
    self.Data = pd.merge(self.Data, video_statistics.drop_duplicates(subset=['Id']), on='Id', how='left')

  def process_kws(self, keywords):
    if "," in keywords:
      return list(set(keywords.split(",")))
    return [keywords]

  def search_videos(self, kws):
    for kw in self.process_kws(kws):
      data2 = self.process_search_data(kw.strip(), None)
      # if error
      if type(data2) == dict:
        print(data2['message'])
        return data2['message']
      self.Data = pd.concat([self.Data, data2])

    _ = self.process_video_data()

    # if error
    if type(_) == dict:
      print(_['message'])
      return _['message']

    self.calculate_metrices()

    # Giving a proper view to Data
    cols = ['Keyword', 'Rank', 'URL', 'Video Title', 'Thumbnail', 'Views', 'VPH', 'Channel', 'Channel Url']
    self.Data = self.Data[cols]

    return True

  # utility function for calculating VPH
  def time_diff(self, pub_time):
    diff = pub_time - datetime.now()
    diff_days = diff/np.timedelta64(1, 'D')
    diff_days = np.absolute(diff_days)
    diff_days = np.round(diff_days, 0)
    diff_hour = diff_days*24

    return np.int32(diff_hour)

  # calculate VPH
  def calculate_metrices(self):
    self.Data['Views'] = self.Data['Views'].apply(np.int32)
    self.Data['Published At'] = pd.to_datetime(self.Data['Published At'])
    self.Data['Hours since published'] = self.Data['Published At'].apply(self.time_diff)
    self.Data['VPH'] = self.Data['Views']/self.Data['Hours since published']

  # videos by channel
  def get_channel_videos_data(self, ch_id):
    params = {
    "key": self.API_KEY,
    "channelId": ch_id,
    "part": "snippet",
    "type": "video",
    "order": "viewCount",
    "maxResults": "100"
    }
    res = requests.get("https://youtube.googleapis.com/youtube/v3/search", params = params)

    return res

  # search channel videos
  def search_channel_videos(self, channel_urls):   # can be combine with `search_videos` method
    for channel_id in self.urls_to_ids(channel_urls):

      data2 = self.process_search_data(None, channel_id.strip())

      # if error
      if type(data2) == dict:
        print(data2['message'])
        return data2['message']

      self.Data = pd.concat([self.Data, data2])

    _ = self.process_video_data()

    # if error
    if type(_) == dict:
      print(_['message'])
      return _['message']

    self.calculate_metrices()

    # giving a proper view to Data
    channel_search_cols = ['Video Title', 'URL', 'Thumbnail', 'Views', 'VPH', 'Channel', 'Hours since published', 'Channel Url']
    self.Data = self.Data.sort_values(by = 'VPH', ascending = False)[channel_search_cols]

    return True

  # convert channel urls to channel ids
  def urls_to_ids(self, urls):

    ids = []

    if "," in urls:
      urls = list(set(urls.split(",")))
    else:
      urls = [urls]

    for url in urls:
      res = requests.get(url.strip())
      if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        id = soup.find("link", {"rel": "canonical"})['href'].replace("https://www.youtube.com/channel/", "")
        ids.append(id)

    return ids

  # rank tracker
  def rank_tracker(self, kws, channel_handle):

    url = "https://www.youtube.com/@" + channel_handle
    res = requests.get(url.strip())

    if res.status_code == 200:
      soup = BeautifulSoup(res.text, 'html.parser')
      channel_name = soup.find("title").text[:-10]
      self.search_videos(kws)

      channel_video_rank = self.Data[self.Data['Channel'] == channel_name]

      cols = self.Data.columns.tolist()
      cols.remove("Keyword")

      for col in cols:
        self.Data[col] = self.Data[col].apply(self.nothing)

      self.Data = pd.concat([channel_video_rank, self.Data]).drop_duplicates(subset=['Keyword']).drop('Channel Url', axis = 1)

  # utility function for rank_tracker method
  def nothing(self, x):
    return "N/A"
