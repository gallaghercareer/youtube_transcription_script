import scrapetube
import simplejson as json
from youtube_transcript_api import YouTubeTranscriptApi
from pprint import pprint


#create a collection of video objects containing the VideoID
videos = scrapetube.get_channel("UCpV_X0VrL8-jg3t6wYGS-1g", limit=1)

#Declare a variable to hold only the videoIDs
videoId_list = []

#iterate over collection of video objects to isolate the videoIDs
for video in videos:
    videoId_list.append(video['videoId'])   

pprint(videoId_list)

all_channel_transcripts = []

#iterate over the collection of IDs and collect the transcripts
for videoId in videoId_list:
    tx = YouTubeTranscriptApi.get_transcript(videoId)
   


