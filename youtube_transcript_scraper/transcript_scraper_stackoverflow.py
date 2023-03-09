import scrapetube
import simplejson as json
from youtube_transcript_api import YouTubeTranscriptApi
from nltk.tokenize import sent_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.tokenize import word_tokenize
import os
import openai
import numpy
import pinecone
from datasets import load_dataset
from datasets import get_dataset_split_names
from tqdm.auto import tqdm
from pprint import pprint

#Define a function to read in a single line file
def read_api_key(input_file):
    # Open the file in read mode
    with open(input_file, 'r') as file:
        # Read the contents of the file as a string
        string_variable = file.read()
        return string_variable

# Define a function to split a list into chunks of a given size
def chunks(lst, size):
    return [lst[i:i+size] for i in range(0, len(lst), size)]

counter = 0
#openai_key
openai.api_key = read_api_key('config.txt')
#pinecone_key
pinecone_key = read_api_key('pinecone_config.txt')

#Connect to Pinecone API
pinecone.init(api_key=pinecone_key,environment = 'us-east1-gcp')

#check if index database already exists (only create index if it doesn't)
if 'index-test' not in pinecone.list_indexes():
    # print('vector database created')
    pinecone.create_index('index-test',dimension=len(embeds[0]))
    #else:
    #print("vector database already exists")

#assign pinecone Index object
index = pinecone.Index('index-test')
hasVectors = None

#check Index object stats (vector count)
indexStats = index.describe_index_stats()
#print(indexStats)


#assign vector count to variable
num_vectors = indexStats.total_vector_count
#print(num_vectors)
if num_vectors > 0 :   
    # print(f"The 'my-index' index contains {num_vectors} vectors.")
    hasVectors = True   
else:
    # print(f"The index does not contain any vectors")
    hasVectors = False

#declare ID for all transcript snippets in Vector Database
vector_batch_id = 0

#####SCRAPE YOUTUBE########
#create a collection of video objects containing the VideoID
videos = scrapetube.get_channel("UCv83tO5cePwHMt1952IVVHw", limit=2)

#Declare a vaiable to hold only the videoIDs
videoId_list = []

#declare vector total for increment
vectorTotal = 0

#vector list for every embedding
vector_list = []

for video in videos:
    #create list of video ids    
    videoId_list.append(video['videoId'])   

    joined_sentences = []

    total_number_of_videos = len(videoId_list)
    #print(total_number_of_videos)

for i in tqdm(range(0, total_number_of_videos, 1)):
    
    #iterate over the collection of video IDs and collect the transcripts 
    for videoId in videoId_list:
        #call the youtube api to return a video transcript object
        transcript = YouTubeTranscriptApi.get_transcript(videoId)
        #pprint(transcript)
        #create a list of sentences from the transcript
        sentences = [sentence['text'] for sentence in transcript]
        sentence_time = [sentence['start'] for sentence in transcript]
        #sentence_time = [sentence[''] for sentence in transcript] 
        #create a nested list with 5 sentence elements in each nested list
        chunks_of_five= chunks(sentences,5)
        sentence_time = chunks(sentence_time,5)
        #combine the 5 sentences in each nested list so that there is no nested list
        joined_sentences = [' '.join(chunk) for chunk in chunks_of_five]

        ############BEGIN EMBEDDING PROCESS###################################################################
        #thoughts:
        #we have already 'batched' our sentences into 5 sentences for each element, however 
        #the number of batches is unknown! We must use a range...we cannot add all loops up into one upsert.
        #we need to upload the embedded sentences, corresponding ID, and corresponding metadata

        for j in joined_sentences:
            #process everything in batches of 1

            #Call OpenAI embedding api and input the chunk of text        
            res = openai.Embedding.create(input=j, engine='text-embedding-ada-002')

            #Assign the embedded data to the embeds variable
            embeds = [record['embedding'] for record in res['data']]

            #prep metadata and upsert batch to Pinecone

            vectors = [{
            'id': counter,  # Set the ID key to an incremental value
            'values': res['data'][0]['embedding'],  # Set the values key to the embedded text
            'meta': {
            'url': 'https://www.youtube.com/watch?v=' + videoId,
            'text': j
            }
            }]

            vector_list.append(vectors)
            counter = counter + 1
        
batch_size = 100

# Split the vectors into batches of size batch_size
vector_batches = [vector_list[i:i+batch_size] for i in range(0, len(vector_list), batch_size)]

print(vector_batches[0])
#vector_batches_zipped = zip(vector_batches)
# Upsert each batch to Pinecone
for vb in vector_batches:
    vb_zipped = zip(vb)
    index.upsert(vectors=list(vb_zipped))

print("PINECONE UPSERT COMPLETE")

