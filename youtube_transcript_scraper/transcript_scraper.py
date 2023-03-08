from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from pprint import pprint

def read_api_key(input_file):
# Open the file in read mode
    with open(input_file, 'r') as file:
        # Read the contents of the file as a string
        string_variable = file.read()

    return string_variable

api_key = read_api_key('/Users/yanni/Documents/youtube_api_key.txt')

youtube =  build(
    'youtube',
    'v3',
    developerKey = api_key
)

#Get a channel's upload playlist ID
#typically add "UU" to the channelID
'''request = youtube.channels().list(
    id = 'UCpV_X0VrL8-jg3t6wYGS-1g',
    part = 'contentDetails'
)

response = request.execute()

pprint(response)'''

#Use channel's upload playlist ID to query all videos and their IDs
video_id_list = youtube.playlistItems().list(
    playlistId  = 'UUpV_X0VrL8-jg3t6wYGS-1g',
    part = 'snippet'
)

response_video_id_list = video_id_list.execute()
pprint(response_video_id_list)

#tx = YouTubeTranscriptApi.get_transcript('s9ZOkiB_bbU')

#pprint(tx)
