import openai
import pinecone

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