import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(api_key=API_KEY)

project_root = Path(__file__).resolve().parents[2]
persist_directory = str(project_root / "chroma_db")

vector_db = Chroma(embedding_function=embeddings, collection_name="tutor_gpt", persist_directory=persist_directory)

def add_document_to_chroma(file_path):
    loader = TextLoader(file_path)
    doc = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    text = text_splitter.split_documents(doc)

    vector_db.add_documents(text)

    print('Added text chucks from the file to the Chroma Vector Dabase')


def main():
    while True:
        file_path = input("Enter the path of the document that you want to add in the database: ")
        if file_path.lower() == 'q':
            break
        if os.path.exists(file_path):
            add_document_to_chroma(file_path)
        else:
            print('File path provided is not found')
        
if __name__ == "__main__":
    main()