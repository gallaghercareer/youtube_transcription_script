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


#openai_key
openai.api_key = read_api_key('config.txt')
#pinecone_key
pinecone_key = read_api_key('pinecone_config.txt')

#Connect to Pinecone API
pinecone.init(
    api_key=pinecone_key,
    environment = 'us-east1-gcp'
)

#check if index database already exists (only create index if it doesn't)
if 'index-test' not in pinecone.list_indexes():
    print('vector database created')
    pinecone.create_index('index-test',dimension=len(embeds[0]))
else:
    print("vector database already exists")

#assign pinecone Index object
index = pinecone.Index('index-test')
hasVectors = None

#check Index object stats (vector count)
indexStats = index.describe_index_stats()
print(indexStats)

#assign vector count to variable
num_vectors = indexStats.total_vector_count
print(num_vectors)
if num_vectors > 0 :
    print(f"The 'my-index' index contains {num_vectors} vectors.")
    hasVectors = True
else:
    print(f"The index does not contain any vectors")
    hasVectors = False


#####SCRAPE YOUTUBE########
#create a collection of video objects containing the VideoID
videos = scrapetube.get_channel("UCDRIjKy6eZOvKtOELtTdeUA", limit=1)

#Declare a variable to hold only the videoIDs
videoId_list = []

#iterate over collection of video objects to isolate the videoIDs
for video in videos:
    videoId_list.append(video['videoId'])   

pprint(videoId_list)

all_channel_transcripts = []
joined_sentences = []
#iterate over the collection of IDs and collect the transcripts 
for videoId in videoId_list:

    #call the youtube api to return a video transcript object
    transcript = YouTubeTranscriptApi.get_transcript(videoId)
    pprint(transcript)
    #create a list of sentences from the transcript
    sentences = [sentence['text'] for sentence in transcript]
    sentence_time = [sentence['start'] for sentence in transcript]
    #sentence_time = [sentence[''] for sentence in transcript] 
    #create a nested list with 5 sentence elements in each nested list
    chunks_of_five= chunks(sentences,5)
    sentence_time = chunks(sentence_time,5)
    
       
    #combine the 5 sentences in each nested list so that there is no nested list
    joined_sentences = [' '.join(chunk) for chunk in chunks_of_five]
    
    
####BEGIN EMBEDDING PROCESS###################################################################
    print("##############BEGIN EMBEDDING PROCESS###################################################################")    
    #unique IDs
    count = 0  

    #process everything in batches of 1
    batch_size = 1  
    
    for i in tqdm(range(0, len(joined_sentences), batch_size)):
        
        # set end position of batch
        i_end = min(i+batch_size, len(joined_sentences))
        
        # get batch of lines and IDs
        lines_batch = joined_sentences[i: i+batch_size]
        print(lines_batch)
        ids_batch = [str(n) for n in range(i, i_end)]
        pprint(ids_batch)

        #Call OpenAI embedding api and input the chunk of text        
        res = openai.Embedding.create(input=lines_batch, engine='text-embedding-ada-002')
        
        #Assign the embedded data to the embeds variable
        embeds = [record['embedding'] for record in res['data']]

        #prep metadata and upsert batch to Pinecone
        meta = [{'text': line, 'url':'https://www.youtube.com/watch?v=' + videoId} for line in lines_batch]
       
        #time =[{'time': subtime[0]} for subtime in sentence_time]
    
        to_upsert = zip(ids_batch, embeds, meta)

        # upsert to Pinecone
        index.upsert(vectors=list(to_upsert))
print("COMPLETE!!")
