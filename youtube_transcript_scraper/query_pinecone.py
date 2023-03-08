import openai
import pinecone
from pprint import pprint

#Define a function to read in a single line file
def read_api_key(input_file):
    # Open the file in read mode
    with open(input_file, 'r') as file:
        # Read the contents of the file as a string
        string_variable = file.read()

    return string_variable

openai.api_key = read_api_key('config.txt')
pinecone_key = read_api_key('pinecone_config.txt')

#initialize connection to pinecone (get API key at app.pinecone.io)
pinecone.init(
    api_key=pinecone_key,
    environment = 'us-east1-gcp'
)

index = pinecone.Index("index-test")

query = input("Input Query:")

xq = openai.Embedding.create(input = query, engine = 'text-embedding-ada-002')['data'][0]['embedding']

res = index.query(xq, top_k=5, include_metadata=True)

pprint(res['text'])

for context in res['text'] 
    context_from_vector_database = context + '\n\n'

chat_gpt_query_user_input = input("Prompt:")
chat_gpt_query = openai.Completion.create(
    model="gpt-3.5-turbo", 
    prompt= f"<<Context:{context_from_vector_database} >> Answer the following prompt without using external sources of information outside of this prompt or making up any information. Strictly use the information presented in this prompt to respond to my prompt. Answer the question as truthfully as possible, and if you're unsure of the answer, say ""Sorry, I don't know"". My prompt is: {chat_gpt_query_user_input}"
    )
